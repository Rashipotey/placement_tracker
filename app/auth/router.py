from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password

from app.schemas.auth import LoginRequest, TokenResponse
from app.auth.security import verify_password
from app.auth.jwt_handler import create_access_token

router=APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register_user(user:UserCreate, db:Session=Depends(get_db)):
    existing_user=(db.query(User).filter(User.email==user.email).first())
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    db_user=User(name=user.name, email=user.email, hashed_password=hash_password(user.password))
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return{
        "message":"User registered successfully"
    }
    
@router.post("/login", response_model=TokenResponse)
def login(credentials:LoginRequest=Depends(), db:Session=Depends(get_db)):
    user=(
        db.query(User).filter(User.email==credentials.email).first()
    )
    if not user:
        raise HTTPException(
            status_code=401, detail="Invalid credentials"
        )
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token=create_access_token({"sub":str(user.id)})
    return{
        "access_token":token
    }
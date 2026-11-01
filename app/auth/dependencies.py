from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user import User
from app.auth.jwt_handler import decode_access_token

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db)):
    payload=decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id=payload.get("sub")
    user=db.query(User).filter(User.id==user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(user:User=Depends(get_current_user)):
    # Role is read from the database on every request, not from the JWT claim.
    if user.role!="ADMIN":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

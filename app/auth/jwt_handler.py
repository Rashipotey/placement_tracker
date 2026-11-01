from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_access_token(data:dict):
    payload=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload.update({"exp":expire})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token:str):
    try:
        payload=jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None

from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY="change_this"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60

def create_access_token(data:dict):
    payload=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp":expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token:str):
    try:
        payload=jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
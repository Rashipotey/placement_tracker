from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str
    
class UserResponse(BaseModel):
    id:UUID
    name:str
    email:EmailStr
    role:str
    
    class Config:
        from_attributes=True
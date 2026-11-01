from sqlalchemy import CheckConstraint, Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.base import Base

class User(Base):
    __tablename__="users"
    __table_args__=(CheckConstraint("role IN ('USER', 'ADMIN')", name="ck_users_role"),)
    
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name=Column(String, nullable=False)
    email=Column(String, unique=True, nullable=False)
    hashed_password=Column(String, nullable=False)
    role=Column(String, nullable=False, default="USER", server_default="USER")

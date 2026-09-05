from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.base import Base

class Application(Base):
    __tablename__="applications"
    
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id=Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    status=Column(String, nullable=False, default="APPLIED")
    notes=Column(String)
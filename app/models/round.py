from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.base import Base

class Round(Base):
    __tablename__="rounds"
    
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id=Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    round_name=Column(String, nullable=False)
    status=Column(String, default="PENDING")
    feedback=Column(String)
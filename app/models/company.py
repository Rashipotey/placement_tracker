from sqlalchemy import Column, Float, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.base import Base

class Company(Base):
    __tablename__="companies"
    
    id=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name=Column(String, nullable=False)
    role=Column(String, nullable=False)
    location=Column(String)
    package_lpa=Column(Float)
    application_link=Column(String)
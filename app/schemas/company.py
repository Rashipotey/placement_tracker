from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    location: Optional[str] = None
    package_lpa: Optional[float] = Field(default=None, ge=0)
    application_link: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    role: Optional[str] = Field(default=None, min_length=1)
    location: Optional[str] = None
    package_lpa: Optional[float] = Field(default=None, ge=0)
    application_link: Optional[str] = None


class CompanyRead(BaseModel):
    id: UUID
    name: str
    role: str
    location: Optional[str] = None
    package_lpa: Optional[float] = None
    application_link: Optional[str] = None

    model_config = {"from_attributes": True}

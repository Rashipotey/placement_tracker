from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel

ApplicationStatus = Literal["APPLIED", "INTERVIEWING", "OFFER", "REJECTED"]


class ApplicationCreate(BaseModel):
    company_id: UUID
    status: ApplicationStatus = "APPLIED"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company_id: Optional[UUID] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None


class ApplicationRead(BaseModel):
    id: UUID
    user_id: UUID
    company_id: UUID
    status: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}

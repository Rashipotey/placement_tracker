from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field

RoundStatus = Literal["PENDING", "PASSED", "FAILED"]


class RoundCreate(BaseModel):
    round_name: str = Field(min_length=1)
    status: RoundStatus = "PENDING"
    feedback: Optional[str] = None


class RoundUpdate(BaseModel):
    round_name: Optional[str] = Field(default=None, min_length=1)
    status: Optional[RoundStatus] = None
    feedback: Optional[str] = None


class RoundRead(BaseModel):
    id: UUID
    application_id: UUID
    round_name: str
    status: str
    feedback: Optional[str] = None

    model_config = {"from_attributes": True}

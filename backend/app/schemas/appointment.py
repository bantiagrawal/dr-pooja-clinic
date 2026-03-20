"""Pydantic schemas for appointments."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.appointment import AppointmentStatus
from app.schemas.availability import SlotOut
from app.schemas.user import UserOut


class AppointmentCreate(BaseModel):
    slot_id: int
    reason: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    status: AppointmentStatus
    reason: Optional[str]
    created_at: datetime
    slot: SlotOut
    user: UserOut

    model_config = {"from_attributes": True}


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut

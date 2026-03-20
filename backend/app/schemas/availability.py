"""Pydantic schemas for availability slots."""
from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


class SlotOut(BaseModel):
    id: int
    slot_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    price_usd: int
    is_booked: bool
    is_blocked: bool

    model_config = {"from_attributes": True}


class SlotCreate(BaseModel):
    slot_date: date
    start_time: time
    duration_minutes: int   # 15 or 30


class ScheduleTemplateCreate(BaseModel):
    day_of_week: int        # 0=Mon … 6=Sun
    start_time: time
    end_time: time
    slot_duration_minutes: int = 30


class ScheduleTemplateOut(ScheduleTemplateCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}

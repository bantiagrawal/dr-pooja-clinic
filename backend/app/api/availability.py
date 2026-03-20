"""Availability routes — view open slots, doctor manages schedule template."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from app.core.database import get_db
from app.core.config import get_settings
from app.models.availability import AvailabilitySlot
from app.models.schedule import DoctorScheduleTemplate
from app.schemas.availability import SlotOut, SlotCreate, ScheduleTemplateCreate, ScheduleTemplateOut
from typing import List, Optional

router = APIRouter(prefix="/availability", tags=["Availability"])
settings = get_settings()

PRICE_MAP = {15: settings.price_15min, 30: settings.price_30min}


@router.get("/slots", response_model=List[SlotOut])
def list_available_slots(
    from_date: date = Query(default=None),
    to_date: date = Query(default=None),
    duration: Optional[int] = Query(default=None, description="15 or 30"),
    db: Session = Depends(get_db),
):
    """Return open (not booked, not blocked) slots within the requested range."""
    today = date.today()
    from_date = from_date or today
    to_date = to_date or (today + timedelta(days=14))
    query = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.slot_date >= from_date,
        AvailabilitySlot.slot_date <= to_date,
        AvailabilitySlot.is_booked == False,
        AvailabilitySlot.is_blocked == False,
    )
    if duration:
        query = query.filter(AvailabilitySlot.duration_minutes == duration)
    return query.order_by(AvailabilitySlot.slot_date, AvailabilitySlot.start_time).all()


@router.post("/slots", response_model=SlotOut, status_code=201)
def create_slot(data: SlotCreate, db: Session = Depends(get_db)):
    """Doctor creates a single open slot (admin use)."""
    if data.duration_minutes not in (15, 30):
        raise HTTPException(status_code=400, detail="Duration must be 15 or 30 minutes")
    price = PRICE_MAP[data.duration_minutes]
    from datetime import datetime
    start_dt = datetime.combine(data.slot_date, data.start_time)
    end_dt = start_dt + timedelta(minutes=data.duration_minutes)
    slot = AvailabilitySlot(
        slot_date=data.slot_date,
        start_time=data.start_time,
        end_time=end_dt.time(),
        duration_minutes=data.duration_minutes,
        price_usd=price,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/slots/{slot_id}", status_code=204)
def block_slot(slot_id: int, db: Session = Depends(get_db)):
    """Doctor blocks/removes an open slot."""
    slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Cannot remove a booked slot")
    slot.is_blocked = True
    db.commit()


# --- Schedule template (used by SlotGeneratorAgent) ---

@router.get("/templates", response_model=List[ScheduleTemplateOut])
def list_templates(db: Session = Depends(get_db)):
    return db.query(DoctorScheduleTemplate).filter(DoctorScheduleTemplate.is_active == True).all()


@router.post("/templates", response_model=ScheduleTemplateOut, status_code=201)
def create_template(data: ScheduleTemplateCreate, db: Session = Depends(get_db)):
    tmpl = DoctorScheduleTemplate(**data.model_dump())
    db.add(tmpl)
    db.commit()
    db.refresh(tmpl)
    return tmpl


@router.delete("/templates/{tmpl_id}", status_code=204)
def deactivate_template(tmpl_id: int, db: Session = Depends(get_db)):
    tmpl = db.query(DoctorScheduleTemplate).filter(DoctorScheduleTemplate.id == tmpl_id).first()
    if not tmpl:
        raise HTTPException(status_code=404)
    tmpl.is_active = False
    db.commit()

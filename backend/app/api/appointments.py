"""Appointment routes — book, view, cancel."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_active_user
from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.availability import AvailabilitySlot
from app.schemas.appointment import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate
from typing import List

router = APIRouter(prefix="/appointments", tags=["Appointments"])

try:
    from app.agents.tasks import send_booking_confirmation_task
    _celery_available = True
except Exception:
    _celery_available = False


@router.post("", response_model=AppointmentOut, status_code=201)
def book_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == data.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    if slot.is_booked or slot.is_blocked:
        raise HTTPException(status_code=409, detail="Slot is not available")

    appt = Appointment(
        user_id=current_user.id,
        slot_id=slot.id,
        reason=data.reason,
        status=AppointmentStatus.confirmed,
    )
    slot.is_booked = True
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # Trigger async notification via Celery (if available)
    if _celery_available:
        send_booking_confirmation_task.delay(appt.id)

    return appt


@router.get("", response_model=List[AppointmentOut])
def list_my_appointments(
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == current_user.id)
        .order_by(Appointment.created_at.desc())
        .all()
    )


@router.get("/{appt_id}", response_model=AppointmentOut)
def get_appointment(
    appt_id: int,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    appt = db.query(Appointment).filter(
        Appointment.id == appt_id,
        Appointment.user_id == current_user.id,
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@router.patch("/{appt_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appt_id: int,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    appt = db.query(Appointment).filter(
        Appointment.id == appt_id,
        Appointment.user_id == current_user.id,
    ).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appt.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Already cancelled")
    if appt.status == AppointmentStatus.completed:
        raise HTTPException(status_code=400, detail="Cannot cancel a completed appointment")

    appt.status = AppointmentStatus.cancelled
    appt.slot.is_booked = False   # free the slot
    db.commit()
    db.refresh(appt)
    return appt

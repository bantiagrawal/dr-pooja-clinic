"""Appointment model — links a user to an availability slot."""
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slot_id: Mapped[int] = mapped_column(Integer, ForeignKey("availability_slots.id"), nullable=False, unique=True)

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.confirmed
    )
    reason: Mapped[str | None] = mapped_column(Text)                # patient's reason for visit
    notes: Mapped[str | None] = mapped_column(Text)                 # doctor's notes (future)
    reminder_24h_sent: Mapped[bool] = mapped_column(default=False)
    reminder_1h_sent: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="appointments")
    slot: Mapped["AvailabilitySlot"] = relationship("AvailabilitySlot", back_populates="appointment")

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} user={self.user_id} status={self.status}>"

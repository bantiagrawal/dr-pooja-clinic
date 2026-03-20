"""Availability slot model — represents doctor's open time blocks."""
from datetime import date, time, datetime
from sqlalchemy import Boolean, Date, Integer, String, Time, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # 15 or 30
    price_usd: Mapped[int] = mapped_column(Integer, nullable=False)          # 30 or 50
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)         # doctor blocked

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    appointment: Mapped["Appointment | None"] = relationship("Appointment", back_populates="slot", uselist=False)

    def __repr__(self) -> str:
        return f"<Slot {self.slot_date} {self.start_time}-{self.end_time} booked={self.is_booked}>"

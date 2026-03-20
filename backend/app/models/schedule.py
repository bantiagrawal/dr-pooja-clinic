"""Doctor schedule template — defines recurring weekly availability."""
from sqlalchemy import Integer, String, Time, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time, datetime
from app.core.database import Base


class DoctorScheduleTemplate(Base):
    """Weekly recurring schedule — used by SlotGeneratorAgent to create slots."""
    __tablename__ = "doctor_schedule_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon … 6=Sun
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)  # 15 or 30
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

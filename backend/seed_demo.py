"""Seed the demo database with slots and a test user."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, engine, SessionLocal
from app.models import *
from datetime import date, time, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)
print("✓ Tables created")

db = SessionLocal()

# Demo user (normally created via OAuth2)
if not db.query(User).first():
    user = User(
        email="demo@patient.com",
        full_name="Demo Patient",
        phone="+1-555-0100",
        provider="google",
        provider_id="demo-google-id-123",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✓ Demo user created: {user.email}")

# Generate slots for next 7 days
from app.core.config import get_settings
cfg = get_settings()
today = date.today()
created = 0
for day_offset in range(1, 8):
    slot_date = today + timedelta(days=day_offset)
    if slot_date.weekday() >= 5:   # skip weekends
        continue
    for hour in [10, 11, 14, 15, 16]:
        for duration, price in [(15, cfg.price_15min), (30, cfg.price_30min)]:
            start = time(hour, 0)
            from datetime import datetime
            end_dt = datetime.combine(slot_date, start) + timedelta(minutes=duration)
            exists = db.query(AvailabilitySlot).filter(
                AvailabilitySlot.slot_date == slot_date,
                AvailabilitySlot.start_time == start,
                AvailabilitySlot.duration_minutes == duration,
            ).first()
            if not exists:
                db.add(AvailabilitySlot(
                    slot_date=slot_date,
                    start_time=start,
                    end_time=end_dt.time(),
                    duration_minutes=duration,
                    price_usd=price,
                ))
                created += 1

db.commit()
print(f"✓ {created} demo slots seeded for next 7 weekdays")
db.close()
print("\nDemo credentials for JWT bypass endpoint:")
print("  User ID: 1  (use /api/dev/token?user_id=1 after server starts)")

"""
Background Agents
=================

Agent 1 — ReminderAgent   : sends appointment reminders at 24h and 1h before.
Agent 2 — SlotGeneratorAgent : auto-generates weekly availability slots from schedule template.
Agent 3 — NotificationAgent  : sends booking confirmation / cancellation emails.

All agents run as Celery tasks and are scheduled via Celery Beat.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone, time as dt_time
from app.agents.celery_app import celery_app

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────

def _get_db():
    """Return a fresh DB session (used inside Celery tasks)."""
    from app.core.database import SessionLocal
    return SessionLocal()


def _send_email(to: str, subject: str, body_html: str) -> bool:
    """Send an email via SMTP. Returns True on success."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from app.core.config import get_settings
    cfg = get_settings()
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg.email_from
        msg["To"] = to
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as server:
            server.starttls()
            server.login(cfg.smtp_user, cfg.smtp_password)
            server.sendmail(cfg.smtp_user, to, msg.as_string())
        return True
    except Exception as exc:
        logger.error("Email send failed to %s: %s", to, exc)
        return False


# ─────────────────────────────────────────────
# Agent 1 — ReminderAgent
# ─────────────────────────────────────────────

@celery_app.task(name="app.agents.tasks.check_appointment_reminders_task", bind=True, max_retries=3)
def check_appointment_reminders_task(self):
    """
    ReminderAgent — runs every 10 minutes.
    Finds upcoming confirmed appointments and sends email reminders at:
      • 24 hours before  (reminder_24h_sent flag)
      • 1 hour before    (reminder_1h_sent flag)
    """
    from app.models.appointment import Appointment, AppointmentStatus
    from app.models.availability import AvailabilitySlot
    from app.models.user import User

    db = _get_db()
    try:
        now = datetime.now(timezone.utc)
        window_24h_start = now + timedelta(hours=23, minutes=50)
        window_24h_end   = now + timedelta(hours=24, minutes=10)
        window_1h_start  = now + timedelta(minutes=50)
        window_1h_end    = now + timedelta(hours=1, minutes=10)

        confirmed = (
            db.query(Appointment)
            .filter(Appointment.status == AppointmentStatus.confirmed)
            .all()
        )

        sent_count = 0
        for appt in confirmed:
            slot = appt.slot
            appt_dt = datetime.combine(slot.slot_date, slot.start_time, tzinfo=timezone.utc)

            # 24-hour reminder
            if not appt.reminder_24h_sent and window_24h_start <= appt_dt <= window_24h_end:
                ok = _send_reminder_email(appt, hours_before=24)
                if ok:
                    appt.reminder_24h_sent = True
                    sent_count += 1

            # 1-hour reminder
            if not appt.reminder_1h_sent and window_1h_start <= appt_dt <= window_1h_end:
                ok = _send_reminder_email(appt, hours_before=1)
                if ok:
                    appt.reminder_1h_sent = True
                    sent_count += 1

        db.commit()
        logger.info("ReminderAgent: processed %d appointments, sent %d reminders", len(confirmed), sent_count)
        return {"reminders_sent": sent_count}
    except Exception as exc:
        db.rollback()
        logger.exception("ReminderAgent error: %s", exc)
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()


def _send_reminder_email(appt, hours_before: int) -> bool:
    from app.core.config import get_settings
    cfg = get_settings()
    user = appt.user
    slot = appt.slot
    label = "24 hours" if hours_before == 24 else "1 hour"
    subject = f"Reminder: Your appointment with {cfg.doctor_name} is in {label}"
    body = f"""
    <h2>Appointment Reminder</h2>
    <p>Dear {user.full_name},</p>
    <p>This is a reminder that your appointment with <strong>{cfg.doctor_name}</strong>
    ({cfg.doctor_specialization}) is scheduled in <strong>{label}</strong>.</p>
    <ul>
      <li><b>Date:</b> {slot.slot_date.strftime('%A, %d %B %Y')}</li>
      <li><b>Time:</b> {slot.start_time.strftime('%I:%M %p')}</li>
      <li><b>Duration:</b> {slot.duration_minutes} minutes</li>
    </ul>
    <p>Please arrive 5 minutes early. If you need to cancel, please do so via the app.</p>
    <p>Warm regards,<br>{cfg.doctor_name}'s Clinic</p>
    """
    return _send_email(user.email, subject, body)


# ─────────────────────────────────────────────
# Agent 2 — SlotGeneratorAgent
# ─────────────────────────────────────────────

@celery_app.task(name="app.agents.tasks.generate_weekly_slots_task", bind=True, max_retries=2)
def generate_weekly_slots_task(self, weeks_ahead: int = 2):
    """
    SlotGeneratorAgent — runs weekly (Monday 6 AM via Celery Beat).
    Reads DoctorScheduleTemplate rows and generates AvailabilitySlot entries
    for the next `weeks_ahead` weeks, skipping slots that already exist.
    """
    from app.models.schedule import DoctorScheduleTemplate
    from app.models.availability import AvailabilitySlot
    from app.core.config import get_settings
    cfg = get_settings()

    PRICE_MAP = {15: cfg.price_15min, 30: cfg.price_30min}

    db = _get_db()
    try:
        templates = (
            db.query(DoctorScheduleTemplate)
            .filter(DoctorScheduleTemplate.is_active == True)
            .all()
        )
        if not templates:
            logger.info("SlotGeneratorAgent: no active templates found")
            return {"slots_created": 0}

        today = date.today()
        created = 0

        for week_offset in range(weeks_ahead):
            week_start = today + timedelta(days=(7 - today.weekday() + week_offset * 7) % 7)

            for tmpl in templates:
                target_date = week_start + timedelta(days=tmpl.day_of_week)
                if target_date < today:
                    continue

                duration = tmpl.slot_duration_minutes
                price = PRICE_MAP.get(duration, cfg.price_30min)

                cursor_dt = datetime.combine(target_date, tmpl.start_time)
                end_dt    = datetime.combine(target_date, tmpl.end_time)

                while cursor_dt + timedelta(minutes=duration) <= end_dt:
                    slot_start = cursor_dt.time()
                    slot_end   = (cursor_dt + timedelta(minutes=duration)).time()

                    # Skip if already exists
                    exists = db.query(AvailabilitySlot).filter(
                        AvailabilitySlot.slot_date == target_date,
                        AvailabilitySlot.start_time == slot_start,
                        AvailabilitySlot.duration_minutes == duration,
                    ).first()

                    if not exists:
                        slot = AvailabilitySlot(
                            slot_date=target_date,
                            start_time=slot_start,
                            end_time=slot_end,
                            duration_minutes=duration,
                            price_usd=price,
                        )
                        db.add(slot)
                        created += 1

                    cursor_dt += timedelta(minutes=duration)

        db.commit()
        logger.info("SlotGeneratorAgent: created %d new slots for %d weeks ahead", created, weeks_ahead)
        return {"slots_created": created}
    except Exception as exc:
        db.rollback()
        logger.exception("SlotGeneratorAgent error: %s", exc)
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()


# ─────────────────────────────────────────────
# Agent 3 — NotificationAgent
# ─────────────────────────────────────────────

@celery_app.task(name="app.agents.tasks.send_booking_confirmation_task", bind=True, max_retries=3)
def send_booking_confirmation_task(self, appointment_id: int):
    """
    NotificationAgent — triggered immediately on booking/cancellation.
    Sends a confirmation or cancellation email to the patient.
    """
    from app.models.appointment import Appointment
    from app.core.config import get_settings
    cfg = get_settings()

    db = _get_db()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            logger.warning("NotificationAgent: appointment %d not found", appointment_id)
            return

        user = appt.user
        slot = appt.slot
        subject = f"Appointment Confirmed — {cfg.doctor_name}"
        body = f"""
        <h2>Appointment Confirmed ✓</h2>
        <p>Dear {user.full_name},</p>
        <p>Your appointment with <strong>{cfg.doctor_name}</strong>
        ({cfg.doctor_specialization}) has been confirmed.</p>
        <ul>
          <li><b>Date:</b> {slot.slot_date.strftime('%A, %d %B %Y')}</li>
          <li><b>Time:</b> {slot.start_time.strftime('%I:%M %p')}</li>
          <li><b>Duration:</b> {slot.duration_minutes} minutes</li>
          <li><b>Fee:</b> ${slot.price_usd}</li>
        </ul>
        <p>Please bring any relevant medical records. 
        You can cancel anytime via the app.</p>
        <p>Warm regards,<br>{cfg.doctor_name}'s Clinic</p>
        """
        ok = _send_email(user.email, subject, body)
        logger.info("NotificationAgent: confirmation email sent=%s for appt %d", ok, appointment_id)
        return {"email_sent": ok}
    except Exception as exc:
        logger.exception("NotificationAgent error: %s", exc)
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task(name="app.agents.tasks.send_cancellation_notification_task", bind=True, max_retries=3)
def send_cancellation_notification_task(self, appointment_id: int):
    """NotificationAgent — sends cancellation email to patient."""
    from app.models.appointment import Appointment
    from app.core.config import get_settings
    cfg = get_settings()

    db = _get_db()
    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appt:
            return
        user = appt.user
        slot = appt.slot
        subject = f"Appointment Cancelled — {cfg.doctor_name}"
        body = f"""
        <h2>Appointment Cancelled</h2>
        <p>Dear {user.full_name},</p>
        <p>Your appointment on <strong>{slot.slot_date.strftime('%d %B %Y')}</strong>
        at <strong>{slot.start_time.strftime('%I:%M %p')}</strong> has been cancelled.</p>
        <p>You can book another slot anytime via the app.</p>
        <p>Warm regards,<br>{cfg.doctor_name}'s Clinic</p>
        """
        ok = _send_email(user.email, subject, body)
        return {"email_sent": ok}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()

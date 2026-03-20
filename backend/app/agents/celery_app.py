"""Celery app configuration."""
from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "clinic_agents",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.agents.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Agent 2: Generate slots every Monday at 6 AM for the coming week
        "slot-generator-weekly": {
            "task": "app.agents.tasks.generate_weekly_slots_task",
            "schedule": 604800,   # 7 days in seconds — use celery beat cron in production
        },
        # Agent 1: Check reminders every 10 minutes
        "reminder-check": {
            "task": "app.agents.tasks.check_appointment_reminders_task",
            "schedule": 600,      # every 10 minutes
        },
    },
)

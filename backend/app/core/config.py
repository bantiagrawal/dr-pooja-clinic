"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Dr. Pooja Agrawal Clinic"
    app_secret_key: str = "changeme"
    environment: str = "development"
    backend_url: str = "http://localhost:8000"

    # Database
    database_url: str = "postgresql://clinic_user:clinic_pass@localhost:5432/clinic_db"

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # OAuth2 — Google
    google_client_id: str = ""
    google_client_secret: str = ""

    # OAuth2 — Facebook
    facebook_client_id: str = ""
    facebook_client_secret: str = ""

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Pricing (USD)
    price_15min: int = 30
    price_30min: int = 50

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "Dr. Pooja Agrawal Clinic <noreply@clinic.com>"

    # Doctor
    doctor_name: str = "Dr. Pooja Agrawal"
    doctor_email: str = "pooja@clinic.com"
    doctor_specialization: str = "General Physician & Consultant"


@lru_cache
def get_settings() -> Settings:
    return Settings()

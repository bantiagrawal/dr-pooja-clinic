# Architecture

## Components
- Mobile app: KivyMD (mobile/)
- Backend API: FastAPI + SQLAlchemy (ackend/)
- Data: PostgreSQL
- Async jobs: Celery + Redis

## Core Flows
1. Auth (OAuth / dev token)
2. Slot listing
3. Book appointment
4. View/cancel appointments
5. Profile update


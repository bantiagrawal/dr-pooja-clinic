# Project Handoff (Agent Read-First)

Last updated: 2026-03-20

## 0) Start Here (First 30 Minutes)
1. Read these files first:
   - `README.md`
   - `PROJECT_HANDOFF.md`
   - `mobile/main.py`
   - `mobile/screens/login_screen.py`
   - `mobile/services/api_client.py`
   - `backend/main.py`
   - `backend/app/api/auth.py`
2. Bring local stack up:
   - `docker compose up -d`
   - `docker compose exec api alembic upgrade head`
   - `docker compose exec api python seed_demo.py`
3. Run mobile app and verify baseline flow:
   - `cd mobile`
   - `pip install -r requirements.txt`
   - ensure `.env` has `BACKEND_URL=http://localhost:8000`
   - `python main.py`
   - test demo login, slot listing, booking, cancel, profile update
4. Continue with top priority gap:
   - implement OAuth deep-link callback completion in mobile

## Single Source Taskboard
- Delivery plan and persistent tasks live in `APP_DELIVERY_PLAN.md`.
- All agents must update task states there (`[ ]` -> `[~]` -> `[x]`).
- Always pick the first open task in **Current Sprint** unless blocked.

## 1) Current Architecture
- `mobile/` is a Python mobile app built with `kivy==2.3.0` and `kivymd==1.2.0`.
- `backend/` is a FastAPI API with SQLAlchemy + PostgreSQL, plus Celery/Redis agents.
- `docker-compose.yml` runs `db`, `redis`, `api`, `celery_worker`, `celery_beat`, and `flower`.
- `website/` is placeholder only (no active implementation yet).

## 2) What Is Implemented and Working (Code-Level)
- Mobile entrypoint is `mobile/main.py` with `ScreenManager` and token-based auto-login.
- Mobile screens implemented:
  - `login_screen.py`
  - `home_screen.py`
  - `book_screen.py`
  - `appointments_screen.py`
  - `profile_screen.py`
- Mobile API integration exists in `mobile/services/api_client.py`:
  - Auth URL generation
  - Profile read/update
  - Slot listing
  - Book/list/cancel appointments
- Backend routers are mounted in `backend/main.py` under `/api`:
  - `/auth`
  - `/users`
  - `/availability`
  - `/appointments`
  - `/dev` (dev-only helper route)
- Demo login path is implemented:
  - Mobile: `GET /api/dev/token?user_id=1`
  - Backend endpoint: `backend/app/api/dev.py`
  - Seed helper: `backend/seed_demo.py`

## 3) Important Gaps / Risks (Next Dev Focus)
1. OAuth mobile callback completion is not wired end-to-end in UI flow.
   - `login_screen.py` opens browser URLs.
   - `api_client.py` has `google_callback()` and `facebook_callback()`.
   - No in-app deep-link listener/handler currently calls these callback methods.
2. Mobile token storage is plain JSON file (`mobile/services/.tokens.json`) and not secure.
3. Android packaging config is missing from source (`buildozer.spec` not present).
4. Backend still has dev-friendly settings:
   - CORS allows all origins.
   - `/api/dev/token` is available and must be removed/guarded for production.
5. No repository test suite is currently present in `test/`.

## 4) Quick Start (Local)
1. Start backend stack from repo root:
   - `docker compose up -d`
2. Run migrations:
   - `docker compose exec api alembic upgrade head`
3. Seed demo user + slots (if needed):
   - `docker compose exec api python seed_demo.py`
4. Run mobile app locally:
   - `cd mobile`
   - `pip install -r requirements.txt`
   - ensure `.env` has `BACKEND_URL=http://localhost:8000`
   - `python main.py`

## 5) Suggested Next Steps (Priority)
1. Implement deep-link callback handling in mobile OAuth flow.
2. Add secure token storage (platform keychain/keystore approach).
3. Add `buildozer.spec` and Android packaging pipeline.
4. Disable/remove `/api/dev/token` and tighten CORS for non-dev environments.
5. Add smoke tests for critical API flows (auth, slots, booking/cancel, profile).

## 6) Key Files to Read First
- `README.md`
- `mobile/main.py`
- `mobile/screens/login_screen.py`
- `mobile/services/api_client.py`
- `backend/main.py`
- `backend/app/api/auth.py`
- `backend/app/api/availability.py`
- `backend/app/api/appointments.py`
- `backend/app/api/dev.py`
- `backend/app/agents/tasks.py`



# 🩺 Dr. Pooja Agrawal Clinic

> A Python-based mobile app and backend for **Dr. Pooja Agrawal** — General Physician & Consultant.  
> Patients can register via Google/Facebook OAuth2 and book in-person appointments.

## Development Handoff

- See `PROJECT_HANDOFF.md` for current implementation status, known gaps, and next steps for continuing development.
- See `APP_DELIVERY_PLAN.md` for the persistent cross-agent execution plan and taskboard.

---

## Collaboration

- Use Issues for tasks/bugs/feature requests.
- Use Discussions for architecture and product decisions.
- Use `APP_DELIVERY_PLAN.md` as the execution taskboard.
- Use Wiki for runbooks and architecture references.
- Wiki source pages are versioned in `wiki/` (publish helper: `scripts/publish_wiki.ps1`).

---
## Tech Stack

| Layer | Tech |
|---|---|
| Mobile App | KivyMD (Python, Material Design) |
| Backend API | FastAPI + SQLAlchemy + PostgreSQL |
| Auth | OAuth2 — Google & Facebook (Authlib) |
| Background Agents | Celery + Redis (3 agents) |
| Infra | Docker Compose |

---

## Project Structure

```
dr-pooja-clinic/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # Auth, Users, Availability, Appointments
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic v2 schemas
│   │   ├── agents/       # 3 Celery background agents
│   │   └── core/         # Config, DB, Security, OAuth2
│   ├── alembic/          # Database migrations
│   ├── Dockerfile
│   └── main.py
├── mobile/               # KivyMD mobile app
│   ├── screens/          # Login, Home, Book, Appointments, Profile
│   ├── services/         # API client + token storage
│   └── main.py
├── website/              # Companion website (coming soon)
├── docker-compose.yml
└── README.md
```

---

## Background Agents

| Agent | Schedule | Purpose |
|---|---|---|
| **ReminderAgent** | Every 10 min | Emails patients 24h & 1h before appointment |
| **SlotGeneratorAgent** | Weekly | Auto-generates availability slots from doctor's schedule template |
| **NotificationAgent** | On-demand | Sends booking confirmation & cancellation emails |

---

## Appointment Pricing

| Duration | Price |
|---|---|
| 15 minutes | $30 |
| 30 minutes | $50 |

---

## Setup

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local mobile dev)
- Google & Facebook OAuth2 app credentials

### 2. Backend (Docker — recommended)

```bash
cd backend
cp .env.example .env
# Fill in GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FACEBOOK_CLIENT_ID,
# FACEBOOK_CLIENT_SECRET, SMTP_* settings in .env

cd ..
docker compose up -d
```

The API will be live at **http://localhost:8000**  
Swagger docs: **http://localhost:8000/docs**  
Celery Flower (agent monitor): **http://localhost:5555**

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Mobile App (local dev)

```bash
cd mobile
pip install -r requirements.txt
# Create .env with BACKEND_URL=http://localhost:8000
python main.py
```

### 5. Build for Android (Buildozer)

```bash
cd mobile
pip install buildozer
buildozer android debug
```

---

## OAuth2 Setup

### Google
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create an OAuth2 client — add `drpooja://auth/google` as redirect URI
3. Copy Client ID & Secret → `.env`

### Facebook
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create an app → add `drpooja://auth/facebook` as redirect URI
3. Copy App ID & Secret → `.env`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/auth/google/url` | Get Google OAuth2 URL |
| GET | `/api/auth/google/callback` | Exchange code for JWT |
| GET | `/api/auth/facebook/url` | Get Facebook OAuth2 URL |
| GET | `/api/auth/facebook/callback` | Exchange token for JWT |
| POST | `/api/auth/refresh` | Refresh access token |
| GET | `/api/users/me` | Get my profile |
| PATCH | `/api/users/me` | Update my profile |
| GET | `/api/availability/slots` | List available slots |
| POST | `/api/appointments` | Book an appointment |
| GET | `/api/appointments` | List my appointments |
| PATCH | `/api/appointments/{id}/cancel` | Cancel an appointment |

---

## Doctor Admin

- Manage schedule templates: `POST /api/availability/templates`
- Create individual slots: `POST /api/availability/slots`
- Block slots: `DELETE /api/availability/slots/{id}`

> A full admin dashboard UI is planned for a future iteration.

---

*Made with ❤️ for Dr. Pooja Agrawal*










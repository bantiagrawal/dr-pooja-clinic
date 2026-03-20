from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api import auth, users, availability, appointments, dev

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Dr. Pooja Agrawal's clinic — appointments, scheduling, and patient management.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(availability.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(dev.router, prefix="/api")


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.app_name,
        "doctor": settings.doctor_name,
        "specialization": settings.doctor_specialization,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

"""Dev-only route — issues a JWT for any user_id without OAuth. Remove in production."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.appointment import TokenResponse

router = APIRouter(prefix="/dev", tags=["Dev (disable in prod)"])


@router.get("/token", response_model=TokenResponse)
def dev_get_token(user_id: int = 1, db: Session = Depends(get_db)):
    """Return a valid JWT for a user — for local demo only."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found — run seed_demo.py first")
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=user,
    )

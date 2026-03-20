"""User profile routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_active_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(require_active_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_my_profile(
    updates: UserUpdate,
    current_user: User = Depends(require_active_user),
    db: Session = Depends(get_db),
):
    for field, value in updates.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

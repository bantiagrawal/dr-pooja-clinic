"""Auth routes — OAuth2 Google/Facebook login, token refresh."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.oauth import get_google_user, get_facebook_user
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import get_settings
from app.models.user import User
from app.schemas.appointment import TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


def _get_or_create_user(db: Session, provider_data: dict) -> User:
    """Find existing user by provider+id or create a new one."""
    user = db.query(User).filter(
        User.provider == provider_data["provider"],
        User.provider_id == provider_data["provider_id"],
    ).first()
    if not user:
        # also check by email (user may have used another provider before)
        user = db.query(User).filter(User.email == provider_data["email"]).first()
    if not user:
        user = User(
            email=provider_data["email"],
            full_name=provider_data["full_name"] or "Patient",
            avatar_url=provider_data.get("avatar_url"),
            provider=provider_data["provider"],
            provider_id=provider_data["provider_id"],
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _build_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        user=user,
    )


@router.get("/google/callback", response_model=TokenResponse)
async def google_callback(
    code: str = Query(...),
    redirect_uri: str = Query(...),
    db: Session = Depends(get_db),
):
    """Exchange Google auth code for app JWT tokens."""
    try:
        provider_data = await get_google_user(code, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google auth failed: {e}")
    user = _get_or_create_user(db, provider_data)
    return _build_token_response(user)


@router.get("/facebook/callback", response_model=TokenResponse)
async def facebook_callback(
    access_token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Exchange Facebook access token for app JWT tokens."""
    try:
        provider_data = await get_facebook_user(access_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Facebook auth failed: {e}")
    user = _get_or_create_user(db, provider_data)
    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return _build_token_response(user)


@router.get("/google/url")
def google_auth_url(redirect_uri: str = Query(...)):
    """Return the Google OAuth2 authorization URL for mobile app deep-link."""
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    from urllib.parse import urlencode
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"}


@router.get("/facebook/url")
def facebook_auth_url(redirect_uri: str = Query(...)):
    """Return the Facebook OAuth2 dialog URL for mobile app deep-link."""
    params = {
        "client_id": settings.facebook_client_id,
        "redirect_uri": redirect_uri,
        "scope": "email,public_profile",
    }
    from urllib.parse import urlencode
    return {"url": f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"}

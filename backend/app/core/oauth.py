"""OAuth2 helpers for Google and Facebook using Authlib."""
from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.config import get_settings

settings = get_settings()

GOOGLE_CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/me"


async def get_google_user(code: str, redirect_uri: str) -> dict:
    async with AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    ) as client:
        token = await client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
            redirect_uri=redirect_uri,
        )
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            token=token,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "provider": "google",
            "provider_id": data["sub"],
            "email": data.get("email"),
            "full_name": data.get("name"),
            "avatar_url": data.get("picture"),
        }


async def get_facebook_user(access_token: str) -> dict:
    async with AsyncOAuth2Client() as client:
        resp = await client.get(
            FACEBOOK_GRAPH_URL,
            params={"fields": "id,name,email,picture", "access_token": access_token},
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "provider": "facebook",
            "provider_id": data["id"],
            "email": data.get("email"),
            "full_name": data.get("name"),
            "avatar_url": data.get("picture", {}).get("data", {}).get("url"),
        }

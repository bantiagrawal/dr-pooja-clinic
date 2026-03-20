"""API client for the Dr. Pooja Clinic backend."""
import requests
import os
from typing import Optional

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    def __init__(self):
        self.base = BASE_URL
        self.access_token: Optional[str] = None
        self.refresh_token_val: Optional[str] = None
        self.session = requests.Session()

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.access_token:
            h["Authorization"] = f"Bearer {self.access_token}"
        return h

    def _handle(self, resp: requests.Response) -> dict:
        resp.raise_for_status()
        return resp.json()

    def set_tokens(self, access: str, refresh: str):
        self.access_token = access
        self.refresh_token_val = refresh
        self.session.headers.update({"Authorization": f"Bearer {access}"})

    def clear_tokens(self):
        self.access_token = None
        self.refresh_token_val = None
        self.session.headers.pop("Authorization", None)

    # ── Auth ──────────────────────────────────────────────
    def get_google_auth_url(self, redirect_uri: str) -> str:
        r = self.session.get(f"{self.base}/api/auth/google/url", params={"redirect_uri": redirect_uri})
        return self._handle(r)["url"]

    def get_facebook_auth_url(self, redirect_uri: str) -> str:
        r = self.session.get(f"{self.base}/api/auth/facebook/url", params={"redirect_uri": redirect_uri})
        return self._handle(r)["url"]

    def google_callback(self, code: str, redirect_uri: str) -> dict:
        r = self.session.get(
            f"{self.base}/api/auth/google/callback",
            params={"code": code, "redirect_uri": redirect_uri},
        )
        data = self._handle(r)
        self.set_tokens(data["access_token"], data["refresh_token"])
        return data

    def facebook_callback(self, access_token: str) -> dict:
        r = self.session.get(
            f"{self.base}/api/auth/facebook/callback",
            params={"access_token": access_token},
        )
        data = self._handle(r)
        self.set_tokens(data["access_token"], data["refresh_token"])
        return data

    def refresh_tokens(self) -> bool:
        try:
            r = self.session.post(
                f"{self.base}/api/auth/refresh",
                params={"refresh_token": self.refresh_token_val},
            )
            data = self._handle(r)
            self.set_tokens(data["access_token"], data["refresh_token"])
            return True
        except Exception:
            return False

    # ── User ──────────────────────────────────────────────
    def get_my_profile(self) -> dict:
        r = self.session.get(f"{self.base}/api/users/me")
        return self._handle(r)

    def update_profile(self, **kwargs) -> dict:
        r = self.session.patch(f"{self.base}/api/users/me", json=kwargs)
        return self._handle(r)

    # ── Availability ──────────────────────────────────────
    def get_slots(self, from_date: str = None, to_date: str = None, duration: int = None) -> list:
        params = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        if duration:
            params["duration"] = duration
        r = self.session.get(f"{self.base}/api/availability/slots", params=params)
        return self._handle(r)

    # ── Appointments ──────────────────────────────────────
    def book_appointment(self, slot_id: int, reason: str = None) -> dict:
        r = self.session.post(
            f"{self.base}/api/appointments",
            json={"slot_id": slot_id, "reason": reason},
        )
        return self._handle(r)

    def get_my_appointments(self) -> list:
        r = self.session.get(f"{self.base}/api/appointments")
        return self._handle(r)

    def cancel_appointment(self, appt_id: int) -> dict:
        r = self.session.patch(f"{self.base}/api/appointments/{appt_id}/cancel")
        return self._handle(r)


# Singleton used throughout the app
api = APIClient()

"""Persistent token storage using a local JSON file."""
import json
import os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".tokens.json")


def save_tokens(access: str, refresh: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access": access, "refresh": refresh}, f)


def load_tokens() -> tuple[str | None, str | None]:
    if not os.path.exists(TOKEN_FILE):
        return None, None
    try:
        with open(TOKEN_FILE) as f:
            data = json.load(f)
        return data.get("access"), data.get("refresh")
    except Exception:
        return None, None


def clear_tokens():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

import json
import uuid
from copy import deepcopy
from pathlib import Path

from server.constants import DB_PATH, EMPTY_DB, USERS_PATH


def _user_path(email: str) -> str:
    return email.strip().lower()


def db_path(email: str) -> Path:
    return USERS_PATH / _user_path(email) / "db.json"


def _read(path):
    return json.loads(path.read_text())


def _write(path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _empty_db() -> dict:
    return deepcopy(EMPTY_DB)


# ─────────────────────────── Load / Save ───────────────────────────

def load(email: str | None = None) -> dict:
    if email:
        user_path = db_path(email)

        if not user_path.exists():
            data = _empty_db()
            _write(user_path, data)
            return data

        try:
            return _read(user_path)
        except json.JSONDecodeError:
            data = _empty_db()
            _write(user_path, data)
            return data

    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        save(_empty_db())
        return _empty_db()

    try:
        return _read(DB_PATH)
    except json.JSONDecodeError:
        # fallback if file is corrupted
        save(_empty_db())
        return _empty_db()


def save(data: dict, email: str | None = None) -> None:
    if email:
        _write(USERS_PATH / _user_path(email) / "db.json", data)
        return

    DB_PATH.write_text(json.dumps(data, indent=2))


# ─────────────────────────── ID Generation ───────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())

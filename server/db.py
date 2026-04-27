import json
import uuid

from server.constants import DB_PATH, EMPTY_DB


# ─────────────────────────── Load / Save ───────────────────────────

def load() -> dict:
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        save(dict(EMPTY_DB))
        return dict(EMPTY_DB)

    try:
        return json.loads(DB_PATH.read_text())
    except json.JSONDecodeError:
        # fallback if file is corrupted
        save(dict(EMPTY_DB))
        return dict(EMPTY_DB)


def save(data: dict) -> None:
    DB_PATH.write_text(json.dumps(data, indent=2))


# ─────────────────────────── ID Generation ───────────────────────────

def new_id() -> str:
    return str(uuid.uuid4())

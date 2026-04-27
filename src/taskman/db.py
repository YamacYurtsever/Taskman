import json
import uuid

from taskman.constants import DB_PATH, EMPTY_DB


def load() -> dict:
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        DB_PATH.write_text(json.dumps(EMPTY_DB, indent=2))
    return json.loads(DB_PATH.read_text())


def save(db: dict) -> None:
    DB_PATH.write_text(json.dumps(db, indent=2))


def new_id() -> str:
    return str(uuid.uuid4())

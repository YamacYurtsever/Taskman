import json
from copy import deepcopy
from pathlib import Path

from server.constants import CONFIG_PATH, USERS_PATH

SERVER_DEFAULTS = {
    "secretKey": None,
}

USER_DEFAULTS = {
    "calendars": [],
    "calendarTimezone": "UTC",
    "googleRefreshToken": None,
    "googleEmail": None,
}

DEFAULTS = {**SERVER_DEFAULTS, **USER_DEFAULTS}


def _user_path(email: str) -> str:
    return email.strip().lower()


def config_path(email: str | None = None) -> Path:
    if email:
        return USERS_PATH / _user_path(email) / "config.json"
    return CONFIG_PATH


def _read(path: Path) -> dict:
    return json.loads(path.read_text())


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _merge(defaults: dict, data: dict | None) -> dict:
    return {**defaults, **(data or {})}


def _split_user_state(data: dict) -> tuple[dict, dict]:
    user = {key: data.get(key) for key in USER_DEFAULTS}
    shared = {key: value for key, value in data.items() if key not in USER_DEFAULTS}
    return user, shared


def load(email: str | None = None) -> dict:
    if email:
        return load_user(email)

    if not CONFIG_PATH.exists():
        _write(CONFIG_PATH, deepcopy(SERVER_DEFAULTS))
        return deepcopy(SERVER_DEFAULTS)
    return _merge(SERVER_DEFAULTS, _read(CONFIG_PATH))


def load_user(email: str) -> dict:
    path = config_path(email)
    if path.exists():
        return _merge(USER_DEFAULTS, _read(path))

    shared = load()
    user_data, shared_data = _split_user_state(shared)
    if any(shared.get(key) is not None for key in USER_DEFAULTS):
        save(shared_data)
        save(user_data, email)
        return _merge(USER_DEFAULTS, user_data)

    _write(path, deepcopy(USER_DEFAULTS))
    return deepcopy(USER_DEFAULTS)


def save(data: dict, email: str | None = None) -> None:
    _write(config_path(email), data)


def migrate_legacy_user_state(email: str, shared_data: dict | None = None) -> dict:
    path = config_path(email)
    if path.exists():
        return _merge(USER_DEFAULTS, _read(path))

    shared = deepcopy(shared_data) if shared_data is not None else load()
    user_data, shared_data = _split_user_state(shared)

    save(shared_data)
    save(user_data, email)
    return _merge(USER_DEFAULTS, user_data)

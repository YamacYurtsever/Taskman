import json

from taskman.constants import CONFIG_PATH

DEFAULTS = {
    "calendars": [],
    "calendarTimezone": "UTC",
}


def load() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(DEFAULTS, indent=2))
        return dict(DEFAULTS)
    data = json.loads(CONFIG_PATH.read_text())
    return {**DEFAULTS, **data}

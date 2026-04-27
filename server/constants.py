from enum import Enum
from pathlib import Path


# ─────────────────────────── Paths ───────────────────────────

TASKMAN_DIR = Path.home() / ".taskman"
CONFIG_PATH = TASKMAN_DIR / "config.json"
DB_PATH = TASKMAN_DIR / "db.json"


# ─────────────────────────── Defaults ───────────────────────────

EMPTY_DB = {
    "groups": [],
    "lists": [],
    "tasks": [],
    "daysheet": [],
}


# ─────────────────────────── Date / Time ───────────────────────────

DATE_FORMAT = "%Y-%m-%d"
DATE_INPUT_FORMATS = (DATE_FORMAT, "%d/%m/%Y", "%d-%m-%Y")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


# ─────────────────────────── Domain ───────────────────────────

class DaysheetEntryType(str, Enum):
    LOG = "log"
    CONTINUE = "continue"
    DONE = "done"


# ─────────────────────────── Misc ───────────────────────────

COMPLETION_SOUND = "/System/Library/Sounds/Glass.aiff"

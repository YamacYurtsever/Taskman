from pathlib import Path


TASKMAN_DIR = Path.home() / ".taskman"
CONFIG_PATH = TASKMAN_DIR / "config.json"
DB_PATH = TASKMAN_DIR / "db.json"

EMPTY_DB = {"groups": [], "lists": [], "tasks": [], "daysheet": []}

DATE_FORMAT = "%Y-%m-%d"
DATE_INPUT_FORMATS = (DATE_FORMAT, "%d/%m/%Y", "%d-%m-%Y")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

COMPLETION_SOUND = "/System/Library/Sounds/Glass.aiff"

class DaysheetEntryType:
    LOG = "log"
    CONTINUE = "continue"
    DONE = "done"

    ALL = {LOG, CONTINUE, DONE}

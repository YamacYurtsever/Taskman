from server import db
from server.constants import DaysheetEntryType
from server.services.utils import (
    ServiceError,
    add_daysheet_entry,
    find_daysheet_entry,
    has_daysheet_entry,
    now,
    remove_daysheet_entries,
    require_list,
    require_name,
    require_task,
    service,
    today,
)


# ─────────────────────────── Logs ───────────────────────────

@service
def add_log(list_name: str, text: str):
    text = require_name(text, "text")

    data = db.load()
    lst = require_list(data, list_name)

    add_daysheet_entry(data, lst["id"], DaysheetEntryType.LOG, text, now())

    db.save(data)


@service
def edit_log(list_name: str, text: str, new_text: str):
    text = require_name(text, "text")
    new_text = require_name(new_text, "new text")

    data = db.load()
    lst = require_list(data, list_name)

    entry = find_daysheet_entry(data, lst["id"], DaysheetEntryType.LOG, text, today())
    if not entry:
        raise ServiceError(f"log entry '{text}' not found")

    entry["text"] = new_text
    db.save(data)


@service
def delete_log(list_name: str, text: str):
    text = require_name(text, "text")

    data = db.load()
    lst = require_list(data, list_name)

    deleted = remove_daysheet_entries(
        data,
        lst["id"],
        DaysheetEntryType.LOG,
        text,
        today(),
    )

    if not deleted:
        raise ServiceError(f"log entry '{text}' not found")

    db.save(data)


# ─────────────────────────── Continue Entries ───────────────────────────

@service
def continue_task(list_name: str, task_name: str):
    task_name = require_name(task_name, "task")

    data = db.load()
    lst = require_list(data, list_name)
    require_task(data, lst, task_name)

    if has_daysheet_entry(data, lst["id"], DaysheetEntryType.DONE, task_name, today()):
        raise ServiceError(f"'{task_name}' was already finished today")

    if has_daysheet_entry(data, lst["id"], DaysheetEntryType.CONTINUE, task_name, today()):
        raise ServiceError(f"'{task_name}' was already continued today")

    add_daysheet_entry(data, lst["id"], DaysheetEntryType.CONTINUE, task_name, now())

    db.save(data)

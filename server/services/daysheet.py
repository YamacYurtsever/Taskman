from datetime import date, datetime
from server import db
from server.constants import DATE_FORMAT, DaysheetEntryType
from server.services.utils import (
    _err, _now, _entry_date,
    _require_list, _require_task,
    _add_daysheet_entry, _find_daysheet_entry,
    _has_daysheet_entry, _remove_daysheet_entries,
)


def cmd_log(args):
    if not args:
        _err('usage: taskman log "list" "text"')

    if args[0] == "edit":
        if len(args) < 4:
            _err('usage: taskman log edit "list" "text" "new_text"')
        list_name, text, new_text = args[1], args[2], args[3]
        data = db.load()
        lst = _require_list(data, list_name)
        today = date.today().isoformat()
        entry = _find_daysheet_entry(data, lst["id"], DaysheetEntryType.LOG, text, today)
        if not entry:
            _err(f"log entry '{text}' not found")
        entry["text"] = new_text
        db.save(data)
        print(f"~ [{list_name}] {new_text}")
        return

    if args[0] in ("delete", "del"):
        if len(args) < 3:
            _err('usage: taskman log delete "list" "text"')
        list_name, text = args[1], args[2]
        data = db.load()
        lst = _require_list(data, list_name)
        today = date.today().isoformat()
        if not _remove_daysheet_entries(data, lst["id"], DaysheetEntryType.LOG, text, today):
            _err(f"log entry '{text}' not found")
        db.save(data)
        print(f"- [{list_name}] {text}")
        return

    if len(args) < 2:
        _err('usage: taskman log "list" "text"')
    list_name, text = args[0], args[1]
    data = db.load()
    lst = _require_list(data, list_name)
    _add_daysheet_entry(data, lst["id"], DaysheetEntryType.LOG, text, _now())
    db.save(data)
    print(f"+ [{list_name}] {text}")


def cmd_continue(args):
    if len(args) < 2:
        _err('usage: taskman continue "list" "task"')
    list_name, task_name = args[0], args[1]

    data = db.load()
    lst = _require_list(data, list_name)
    _require_task(data, lst, task_name)

    today = date.today().isoformat()
    if _has_daysheet_entry(data, lst["id"], DaysheetEntryType.DONE, task_name, today):
        _err(f"'{task_name}' was already finished today")
    if _has_daysheet_entry(data, lst["id"], DaysheetEntryType.CONTINUE, task_name, today):
        _err(f"'{task_name}' was already continued today")

    _add_daysheet_entry(data, lst["id"], DaysheetEntryType.CONTINUE, task_name, _now())
    db.save(data)
    print(f"↻ [{list_name}] {task_name}")

from datetime import date, datetime
from taskman import db
from taskman.constants import DATE_FORMAT, DaysheetEntryType
from taskman.commands.utils import (
    _err, _bold, _sort_name, _now, _entry_date,
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


def cmd_daysheet(args):
    target = args[0] if args else date.today().isoformat()
    try:
        datetime.strptime(target, DATE_FORMAT)
    except ValueError:
        _err(f"invalid date '{target}' — expected YYYY-MM-DD")

    data = db.load()
    entries = sorted(
        [e for e in data["daysheet"] if _entry_date(e) == target],
        key=lambda e: e["datetime"],
    )

    if not entries:
        print(f"No entries for {target}")
        return

    list_by_id = {l["id"]: l for l in data["lists"]}
    group_by_id = {g["id"]: g for g in data["groups"]}

    section_order = []
    by_section = {}
    for e in entries:
        lst = list_by_id.get(e["listId"])
        gid = lst["groupId"] if lst else None
        if gid:
            sid = ("group", gid)
            section_name = group_by_id[gid]["name"]
        else:
            sid = ("list", e["listId"])
            section_name = lst["name"] if lst else e["listId"]
        if sid not in by_section:
            section_order.append(sid)
            by_section[sid] = {"name": section_name, "entries": []}
        by_section[sid]["entries"].append(e)

    section_order.sort(key=lambda sid: _sort_name(by_section[sid]["name"]))

    print(f"Day Sheet · {target}\n")
    for sid in section_order:
        section = by_section[sid]
        is_group = sid[0] == "group"
        print(_bold(section["name"]))
        for e in section["entries"]:
            lst = list_by_id.get(e["listId"])
            prefix = f"[{lst['name']}] " if is_group and lst else ""
            if e["type"] == DaysheetEntryType.DONE:
                line = f"Finished {e['text']}"
            elif e["type"] == DaysheetEntryType.CONTINUE:
                line = f"Continued {e['text']}"
            else:
                line = e["text"]
            print(f"  {prefix}{line}")
        print()

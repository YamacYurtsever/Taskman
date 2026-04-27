from datetime import date, datetime
from taskman import db
from taskman.commands.utils import (
    _err, _bold, _sort_name, _now, _entry_date,
    _find_list, _find_task,
)


def cmd_log(args):
    if not args:
        _err('usage: taskman log "list" "text"')

    if args[0] == "edit":
        if len(args) < 4:
            _err('usage: taskman log edit "list" "text" "new_text"')
        list_name, text, new_text = args[1], args[2], args[3]
        data = db.load()
        lst = _find_list(data, list_name)
        if not lst:
            _err(f"list '{list_name}' not found")
        today = date.today().isoformat()
        entry = next(
            (e for e in data["daysheet"]
             if e["listId"] == lst["id"] and e["type"] == "log"
             and e["text"] == text and _entry_date(e) == today),
            None,
        )
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
        lst = _find_list(data, list_name)
        if not lst:
            _err(f"list '{list_name}' not found")
        today = date.today().isoformat()
        before = len(data["daysheet"])
        data["daysheet"] = [
            e for e in data["daysheet"]
            if not (e["listId"] == lst["id"] and e["type"] == "log"
                    and e["text"] == text and _entry_date(e) == today)
        ]
        if len(data["daysheet"]) == before:
            _err(f"log entry '{text}' not found")
        db.save(data)
        print(f"- [{list_name}] {text}")
        return

    if len(args) < 2:
        _err('usage: taskman log "list" "text"')
    list_name, text = args[0], args[1]
    data = db.load()
    lst = _find_list(data, list_name)
    if not lst:
        _err(f"list '{list_name}' not found")
    data["daysheet"].append({
        "id": db.new_id(),
        "datetime": _now(),
        "listId": lst["id"],
        "type": "log",
        "text": text,
    })
    db.save(data)
    print(f"+ [{list_name}] {text}")


def cmd_continue(args):
    if len(args) < 2:
        _err('usage: taskman continue "list" "task"')
    list_name, task_name = args[0], args[1]

    data = db.load()
    lst = _find_list(data, list_name)
    if not lst:
        _err(f"list '{list_name}' not found")

    if not _find_task(data, lst["id"], task_name):
        _err(f"task '{task_name}' not found in '{list_name}'")

    today = date.today().isoformat()
    if any(e for e in data["daysheet"]
           if e["listId"] == lst["id"] and e["type"] == "done"
           and e["text"] == task_name and _entry_date(e) == today):
        _err(f"'{task_name}' was already finished today")
    if any(e for e in data["daysheet"]
           if e["listId"] == lst["id"] and e["type"] == "continue"
           and e["text"] == task_name and _entry_date(e) == today):
        _err(f"'{task_name}' was already continued today")

    data["daysheet"].append({
        "id": db.new_id(),
        "datetime": _now(),
        "listId": lst["id"],
        "type": "continue",
        "text": task_name,
    })
    db.save(data)
    print(f"↻ [{list_name}] {task_name}")


def cmd_daysheet(args):
    target = args[0] if args else date.today().isoformat()
    try:
        datetime.strptime(target, "%Y-%m-%d")
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
            if e["type"] == "done":
                line = f"Finished {e['text']}"
            elif e["type"] == "continue":
                line = f"Continued {e['text']}"
            else:
                line = e["text"]
            print(f"  {prefix}{line}")
        print()

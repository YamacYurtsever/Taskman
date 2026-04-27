import re
import sys
from datetime import datetime

from taskman import db
from taskman.constants import DATE_FORMAT, DATE_INPUT_FORMATS, DATETIME_FORMAT


def _err(msg):
    print(f"taskman: {msg}", file=sys.stderr)
    sys.exit(1)


def _bold(s):
    return f"\033[1m{s}\033[0m"


def _parse_date(s):
    for fmt in DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime(DATE_FORMAT)
        except ValueError:
            pass
    _err(f"invalid date '{s}' — expected YYYY-MM-DD")


def _sort_name(name):
    return ('\xff', name) if re.match(r'^others?$', name, re.I) else ('', name)


def _now():
    return datetime.now().strftime(DATETIME_FORMAT)


def _entry_date(entry):
    return entry["datetime"][:10]


def _find_list(data, name):
    return next((l for l in data["lists"] if l["name"] == name), None)


def _find_group(data, name):
    return next((g for g in data["groups"] if g["name"] == name), None)


def _find_task(data, list_id, name):
    return next(
        (t for t in data["tasks"] if t["listId"] == list_id and t["name"] == name),
        None,
    )


def _require_list(data, name, message=None):
    lst = _find_list(data, name)
    if not lst:
        _err(message or f"list '{name}' not found")
    return lst


def _require_task(data, lst, name):
    task = _find_task(data, lst["id"], name)
    if not task:
        _err(f"task '{name}' not found in '{lst['name']}'")
    return task


def _get_or_create_list(data, name):
    lst = _find_list(data, name)
    if not lst:
        lst = {"id": db.new_id(), "name": name, "groupId": None}
        data["lists"].append(lst)
    return lst


def _get_or_create_group(data, name):
    group = _find_group(data, name)
    if not group:
        group = {"id": db.new_id(), "name": name}
        data["groups"].append(group)
    return group


def _prune_empty_group(data, group_id):
    if group_id and not any(l["groupId"] == group_id for l in data["lists"]):
        data["groups"] = [g for g in data["groups"] if g["id"] != group_id]


def _delete_group(data, group):
    for lst in data["lists"]:
        if lst["groupId"] == group["id"]:
            lst["groupId"] = None
    data["groups"] = [g for g in data["groups"] if g["id"] != group["id"]]


def _delete_list(data, lst):
    group_id = lst["groupId"]
    data["tasks"] = [t for t in data["tasks"] if t["listId"] != lst["id"]]
    data["daysheet"] = [e for e in data["daysheet"] if e["listId"] != lst["id"]]
    data["lists"] = [l for l in data["lists"] if l["id"] != lst["id"]]
    _prune_empty_group(data, group_id)


def _add_daysheet_entry(data, list_id, entry_type, text, timestamp=None):
    data["daysheet"].append({
        "id": db.new_id(),
        "datetime": timestamp or _now(),
        "listId": list_id,
        "type": entry_type,
        "text": text,
    })


def _has_daysheet_entry(data, list_id, entry_type, text, entry_day):
    return any(
        e for e in data["daysheet"]
        if e["listId"] == list_id
        and e["type"] == entry_type
        and e["text"] == text
        and _entry_date(e) == entry_day
    )


def _find_daysheet_entry(data, list_id, entry_type, text, entry_day):
    return next(
        (
            e for e in data["daysheet"]
            if e["listId"] == list_id
            and e["type"] == entry_type
            and e["text"] == text
            and _entry_date(e) == entry_day
        ),
        None,
    )


def _remove_daysheet_entries(data, list_id, entry_type, text=None, entry_day=None):
    before = len(data["daysheet"])
    data["daysheet"] = [
        e for e in data["daysheet"]
        if not (
            e["listId"] == list_id
            and e["type"] == entry_type
            and (text is None or e["text"] == text)
            and (entry_day is None or _entry_date(e) == entry_day)
        )
    ]
    return before - len(data["daysheet"])

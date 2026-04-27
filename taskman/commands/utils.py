import re
import sys
from datetime import datetime

from taskman import db


def _err(msg):
    print(f"taskman: {msg}", file=sys.stderr)
    sys.exit(1)


def _bold(s):
    return f"\033[1m{s}\033[0m"


def _parse_date(s):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    _err(f"invalid date '{s}' — expected YYYY-MM-DD")


def _sort_name(name):
    return ('\xff', name) if re.match(r'^others?$', name, re.I) else ('', name)


def _now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


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

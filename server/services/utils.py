from datetime import date, datetime

from server import db
from server.constants import DATE_FORMAT, DATE_INPUT_FORMATS, DATETIME_FORMAT


# ─────────────────────────── Errors & Validation ───────────────────────────

class ServiceError(Exception):
    pass


def service(fn):
    def wrapper(*args, **kwargs):
        try:
            fn(*args, **kwargs)
            return True, ""
        except ServiceError as e:
            return False, str(e)

    return wrapper


def require_name(value, field="name"):
    value = (value or "").strip()
    if not value:
        raise ServiceError(f"{field} is required")
    return value


# ─────────────────────────── Date / Time ───────────────────────────

def parse_date(s):
    for fmt in DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime(DATE_FORMAT)
        except ValueError:
            pass
    raise ServiceError(f"invalid date '{s}' — expected YYYY-MM-DD")


def now():
    return datetime.now().strftime(DATETIME_FORMAT)


def today():
    return date.today().isoformat()


def entry_date(entry):
    return entry["datetime"][:10]


# ─────────────────────────── Find Helpers ───────────────────────────

def find_list(data, name):
    return next((l for l in data["lists"] if l["name"] == name), None)


def find_group(data, name):
    return next((g for g in data["groups"] if g["name"] == name), None)


def find_task(data, list_id, name):
    return next(
        (t for t in data["tasks"] if t["listId"] == list_id and t["name"] == name),
        None,
    )


def find_daysheet_entry(data, list_id, entry_type, text, entry_day):
    return next(
        (
            e for e in data["daysheet"]
            if e["listId"] == list_id
            and e["type"] == entry_type
            and e["text"] == text
            and entry_date(e) == entry_day
        ),
        None,
    )


def has_daysheet_entry(data, list_id, entry_type, text, entry_day):
    return find_daysheet_entry(data, list_id, entry_type, text, entry_day) is not None


# ─────────────────────────── Require Helpers ───────────────────────────

def require_list(data, name, message=None):
    lst = find_list(data, name)
    if not lst:
        raise ServiceError(message or f"list '{name}' not found")
    return lst


def require_task(data, lst, name):
    task = find_task(data, lst["id"], name)
    if not task:
        raise ServiceError(f"task '{name}' not found in '{lst['name']}'")
    return task


# ─────────────────────────── Creation Helpers ───────────────────────────

def get_or_create_list(data, name):
    lst = find_list(data, name)
    if not lst:
        lst = {"id": db.new_id(), "name": name, "groupId": None}
        data["lists"].append(lst)
    return lst


def get_or_create_group(data, name):
    group = find_group(data, name)
    if not group:
        group = {"id": db.new_id(), "name": name}
        data["groups"].append(group)
    return group


def add_daysheet_entry(data, list_id, entry_type, text, timestamp=None):
    data["daysheet"].append({
        "id": db.new_id(),
        "datetime": timestamp or now(),
        "listId": list_id,
        "type": entry_type,
        "text": text,
    })


# ─────────────────────────── Deletion / Mutation Helpers ───────────────────────────

def prune_empty_group(data, group_id):
    if group_id and not any(l["groupId"] == group_id for l in data["lists"]):
        data["groups"] = [g for g in data["groups"] if g["id"] != group_id]


def delete_group(data, group):
    for lst in data["lists"]:
        if lst["groupId"] == group["id"]:
            lst["groupId"] = None

    data["groups"] = [g for g in data["groups"] if g["id"] != group["id"]]


def delete_list(data, lst):
    group_id = lst["groupId"]

    data["tasks"] = [t for t in data["tasks"] if t["listId"] != lst["id"]]
    data["daysheet"] = [e for e in data["daysheet"] if e["listId"] != lst["id"]]
    data["lists"] = [l for l in data["lists"] if l["id"] != lst["id"]]

    prune_empty_group(data, group_id)


def remove_daysheet_entries(data, list_id, entry_type, text=None, entry_day=None):
    before = len(data["daysheet"])

    data["daysheet"] = [
        e for e in data["daysheet"]
        if not (
            e["listId"] == list_id
            and e["type"] == entry_type
            and (text is None or e["text"] == text)
            and (entry_day is None or entry_date(e) == entry_day)
        )
    ]

    return before - len(data["daysheet"])

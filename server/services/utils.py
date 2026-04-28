from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from server import db
from server.constants import DATE_FORMAT, DATE_INPUT_FORMATS


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

UTC_SUFFIX = "Z"
UTC_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LEGACY_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_date(s):
    for fmt in DATE_INPUT_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime(DATE_FORMAT)
        except ValueError:
            pass
    raise ServiceError(f"invalid date '{s}' — expected YYYY-MM-DD")


def require_timezone(tz_name: str) -> str:
    try:
        ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as e:
        raise ServiceError(f"invalid timezone '{tz_name}'") from e
    return tz_name


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime(UTC_DATETIME_FORMAT)


def today_in_timezone(tz_name: str) -> str:
    tz = ZoneInfo(require_timezone(tz_name))
    return datetime.now(timezone.utc).astimezone(tz).date().isoformat()


def parse_utc_datetime(value: str) -> datetime:
    if value.endswith(UTC_SUFFIX):
        return datetime.strptime(value, UTC_DATETIME_FORMAT).replace(tzinfo=timezone.utc)

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("naive datetime")
    return parsed.astimezone(timezone.utc)


def parse_legacy_local_datetime(value: str, tz_name: str) -> datetime:
    tz = ZoneInfo(require_timezone(tz_name))
    return datetime.strptime(value, LEGACY_DATETIME_FORMAT).replace(tzinfo=tz)


def local_datetime_from_storage(value: str, tz_name: str) -> datetime:
    tz = ZoneInfo(require_timezone(tz_name))
    try:
        return parse_utc_datetime(value).astimezone(tz)
    except ValueError:
        return parse_legacy_local_datetime(value, tz_name)


def local_date_from_storage(value: str, tz_name: str) -> str:
    return local_datetime_from_storage(value, tz_name).date().isoformat()


def local_time_from_storage(value: str, tz_name: str) -> str:
    return local_datetime_from_storage(value, tz_name).strftime("%H:%M")


def legacy_datetime_to_utc(value: str, tz_name: str) -> str:
    return parse_legacy_local_datetime(value, tz_name).astimezone(timezone.utc).strftime(UTC_DATETIME_FORMAT)


def legacy_done_date_to_utc(value: str, tz_name: str) -> str:
    tz = ZoneInfo(require_timezone(tz_name))
    local_date = datetime.strptime(value, DATE_FORMAT).date()
    # Legacy completion dates had no time-of-day. Anchor them at local noon so
    # the derived local date remains stable for most timezone conversions.
    local_dt = datetime.combine(local_date, time(hour=12), tzinfo=tz)
    return local_dt.astimezone(timezone.utc).strftime(UTC_DATETIME_FORMAT)


def is_legacy_local_timestamp(value: str) -> bool:
    return len(value) == 19 and value[10] == "T" and not value.endswith(UTC_SUFFIX)


def migrate_user_data(data: dict, tz_name: str) -> bool:
    changed = False

    for task in data["tasks"]:
        if "description" not in task:
            task["description"] = ""
            changed = True

        if "doneAt" not in task or (task.get("doneAt") is None and task.get("done")):
            task["doneAt"] = legacy_done_date_to_utc(task["done"], tz_name) if task.get("done") else None
            changed = True

        if "done" in task:
            task.pop("done", None)
            changed = True

    for entry in data["daysheet"]:
        if is_legacy_local_timestamp(entry["datetime"]):
            entry["datetime"] = legacy_datetime_to_utc(entry["datetime"], tz_name)
            changed = True

    return changed


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


def find_daysheet_entry(data, list_id, entry_type, text, entry_day, tz_name):
    return next(
        (
            e for e in data["daysheet"]
            if e["listId"] == list_id
            and e["type"] == entry_type
            and e["text"] == text
            and local_date_from_storage(e["datetime"], tz_name) == entry_day
        ),
        None,
    )


def has_daysheet_entry(data, list_id, entry_type, text, entry_day, tz_name):
    return find_daysheet_entry(data, list_id, entry_type, text, entry_day, tz_name) is not None


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
        "datetime": timestamp or utc_now(),
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


def remove_daysheet_entries(data, list_id, entry_type, tz_name, text=None, entry_day=None):
    before = len(data["daysheet"])

    data["daysheet"] = [
        e for e in data["daysheet"]
        if not (
            e["listId"] == list_id
            and e["type"] == entry_type
            and (text is None or e["text"] == text)
            and (entry_day is None or local_date_from_storage(e["datetime"], tz_name) == entry_day)
        )
    ]

    return before - len(data["daysheet"])

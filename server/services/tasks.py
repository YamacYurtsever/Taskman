import subprocess
from datetime import date, datetime
from server import db
from server.constants import COMPLETION_SOUND, DATETIME_FORMAT, DaysheetEntryType
from server.services.utils import (
    _err, _parse_date,
    _find_group, _find_task,
    _require_list, _require_task,
    _get_or_create_list, _get_or_create_group,
    _add_daysheet_entry, _remove_daysheet_entries,
    _delete_group, _delete_list, _prune_empty_group,
)

def _play_sound():
    try:
        subprocess.Popen(["afplay", COMPLETION_SOUND], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        pass


def cmd_add(args):
    if len(args) < 1:
        _err('usage: taskman add "list" ["name"] [date]')
    list_name = args[0]

    data = db.load()
    lst = _get_or_create_list(data, list_name)

    if len(args) == 1:
        db.save(data)
        print(f"+ [{list_name}]")
        return

    task_name = args[1]
    due = _parse_date(args[2]) if len(args) >= 3 else None

    if _find_task(data, lst["id"], task_name):
        _err(f"task '{task_name}' already exists in '{list_name}'")

    data["tasks"].append({
        "id": db.new_id(),
        "name": task_name,
        "listId": lst["id"],
        "due": due,
        "done": None,
    })
    db.save(data)
    suffix = f" · due {due}" if due else ""
    print(f"+ [{list_name}] {task_name}{suffix}")


def cmd_done(args):
    if len(args) < 2:
        _err('usage: taskman done "list" "name"')
    list_name, task_name = args[0], args[1]

    data = db.load()
    lst = _require_list(data, list_name)
    task = _require_task(data, lst, task_name)
    if task["done"]:
        _err(f"task '{task_name}' is already done")

    today = date.today().isoformat()
    _remove_daysheet_entries(data, lst["id"], DaysheetEntryType.CONTINUE, task_name, today)
    _add_daysheet_entry(
        data,
        lst["id"],
        DaysheetEntryType.DONE,
        task_name,
        datetime.now().strftime(DATETIME_FORMAT),
    )
    task["done"] = today
    db.save(data)
    print(f"\033[32m✓ [{list_name}] {task_name}\033[0m")
    _play_sound()


def cmd_undo(args):
    if len(args) < 2:
        _err('usage: taskman undo "list" "name"')
    list_name, task_name = args[0], args[1]

    data = db.load()
    lst = _require_list(data, list_name)
    task = _require_task(data, lst, task_name)
    if not task["done"]:
        _err(f"task '{task_name}' is not done")

    task["done"] = None
    db.save(data)
    print(f"○ [{list_name}] {task_name}")


def cmd_edit(args):
    if len(args) < 2:
        _err('usage: taskman edit "list" "new_name" | taskman edit "list" "old_task" "new_task" [new_date]')

    data = db.load()

    if len(args) == 2:
        target, new_name = args[0], args[1]
        group = _find_group(data, target)
        if group:
            group["name"] = new_name
            db.save(data)
            print(f"~ group '{target}' → '{new_name}'")
            return
        lst = _require_list(data, target, f"'{target}' not found")
        lst["name"] = new_name
        db.save(data)
        print(f"~ [{target}] → [{new_name}]")
        return

    list_name, old_name, new_name = args[0], args[1], args[2]
    new_due = _parse_date(args[3]) if len(args) >= 4 else ...

    lst = _require_list(data, list_name)
    task = _require_task(data, lst, old_name)

    if new_name != old_name and _find_task(data, lst["id"], new_name):
        _err(f"task '{new_name}' already exists in '{list_name}'")

    task["name"] = new_name
    if new_due is not ...:
        task["due"] = new_due
    db.save(data)
    due_str = f" · due {task['due']}" if task["due"] else ""
    print(f"~ [{list_name}] {new_name}{due_str}")


def cmd_move(args):
    if len(args) < 2:
        _err('usage: taskman move "list" "group" | taskman move "list" "name" "new_list"')
    list_name = args[0]

    data = db.load()

    if len(args) == 2:
        group_name = args[1]
        lst = _require_list(data, list_name)
        if group_name == "":
            old_group_id = lst["groupId"]
            lst["groupId"] = None
            _prune_empty_group(data, old_group_id)
            db.save(data)
            print(f"↑ [{list_name}] ungrouped")
            return
        group = _get_or_create_group(data, group_name)
        lst["groupId"] = group["id"]
        db.save(data)
        print(f"→ [{list_name}] → group '{group_name}'")
    else:
        task_name, new_list_name = args[1], args[2]
        lst = _require_list(data, list_name)
        task = _require_task(data, lst, task_name)
        new_lst = _get_or_create_list(data, new_list_name)
        if _find_task(data, new_lst["id"], task_name):
            _err(f"task '{task_name}' already exists in '{new_list_name}'")
        task["listId"] = new_lst["id"]
        db.save(data)
        print(f"→ {task_name}  [{list_name}] → [{new_list_name}]")


def cmd_delete(args):
    if len(args) < 1:
        _err('usage: taskman delete "list" ["name"]')
    name = args[0]

    data = db.load()

    if len(args) == 1:
        group = _find_group(data, name)
        if group:
            _delete_group(data, group)
            db.save(data)
            print(f"- group '{name}'")
            return

        lst = _require_list(data, name, f"'{name}' not found")
        _delete_list(data, lst)
        db.save(data)
        print(f"- [{name}]")
    else:
        lst = _require_list(data, name)
        task_name = args[1]
        task = _require_task(data, lst, task_name)
        data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
        db.save(data)
        print(f"- [{name}] {task_name}")

import sys
from taskman import db


def _err(msg):
    print(f"taskman: {msg}", file=sys.stderr)
    sys.exit(1)


def _find_list(data, name):
    return next((l for l in data["lists"] if l["name"] == name), None)


def _find_group(data, name):
    return next((g for g in data["groups"] if g["name"] == name), None)


def _get_or_create_group(data, name):
    group = _find_group(data, name)
    if not group:
        group = {"id": db.new_id(), "name": name}
        data["groups"].append(group)
    return group


def cmd_group(args):
    if len(args) < 2:
        _err('usage: taskman group "list"+ "group_name"')
    list_names, group_name = args[:-1], args[-1]

    data = db.load()
    group = _get_or_create_group(data, group_name)

    for name in list_names:
        lst = _find_list(data, name)
        if not lst:
            _err(f"list '{name}' not found")
        lst["groupId"] = group["id"]

    db.save(data)
    lists_str = ", ".join(list_names)
    print(f"[{lists_str}] → group '{group_name}'")


def cmd_ungroup(args):
    if len(args) < 1:
        _err('usage: taskman ungroup "list"+')

    data = db.load()

    affected_group_ids = set()
    for name in args:
        lst = _find_list(data, name)
        if not lst:
            _err(f"list '{name}' not found")
        if not lst["groupId"]:
            _err(f"list '{name}' is not in a group")
        affected_group_ids.add(lst["groupId"])
        lst["groupId"] = None

    data["groups"] = [
        g for g in data["groups"]
        if g["id"] not in affected_group_ids or any(l["groupId"] == g["id"] for l in data["lists"])
    ]
    db.save(data)
    lists_str = ", ".join(args)
    print(f"[{lists_str}] ungrouped")

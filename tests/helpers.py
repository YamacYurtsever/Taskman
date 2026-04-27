import copy
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from unittest.mock import patch

from taskman.constants import DaysheetEntryType


def list_record(id="list-1", name="Work", group_id=None):
    return {"id": id, "name": name, "groupId": group_id}


def group_record(id="group-1", name="Group"):
    return {"id": id, "name": name}


def task_record(id="task-1", name="Task", list_id="list-1", due=None, done=None):
    return {"id": id, "name": name, "listId": list_id, "due": due, "done": done}


def daysheet_entry(
    id="entry-1",
    datetime="2026-04-26T10:00:00",
    list_id="list-1",
    type=DaysheetEntryType.LOG,
    text="Entry",
):
    return {"id": id, "datetime": datetime, "listId": list_id, "type": type, "text": text}


def db_record(groups=None, lists=None, tasks=None, daysheet=None):
    return {
        "groups": copy.deepcopy(groups or []),
        "lists": copy.deepcopy(lists or []),
        "tasks": copy.deepcopy(tasks or []),
        "daysheet": copy.deepcopy(daysheet or []),
    }


@contextmanager
def saved_db(data):
    saved = {}

    def save(data):
        saved.clear()
        saved.update(data)

    with patch("taskman.db.load", return_value=data), patch("taskman.db.save", side_effect=save):
        yield saved


def capture_stdout(fn, *args):
    buf = StringIO()
    with redirect_stdout(buf):
        fn(*args)
    return buf.getvalue()

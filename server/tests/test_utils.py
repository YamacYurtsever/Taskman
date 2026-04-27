import unittest
from unittest.mock import patch

from server.constants import DaysheetEntryType
from server.services.utils import (
    _add_daysheet_entry,
    _delete_group,
    _delete_list,
    _find_daysheet_entry,
    _has_daysheet_entry,
    _remove_daysheet_entries,
)
from server.tests.helpers import daysheet_entry, db_record, group_record, list_record, task_record


class CommandUtilsTest(unittest.TestCase):

    def test_delete_group_ungroups_lists(self):
        group = group_record(id="group-1", name="School")
        data = db_record(
            groups=[group],
            lists=[
                list_record(id="list-1", name="COMP3131", group_id="group-1"),
                list_record(id="list-2", name="Work"),
            ],
        )

        _delete_group(data, group)

        self.assertEqual(data["groups"], [])
        self.assertIsNone(data["lists"][0]["groupId"])
        self.assertIsNone(data["lists"][1]["groupId"])

    def test_delete_list_removes_related_records_and_empty_group(self):
        lst = list_record(id="list-1", name="COMP3131", group_id="group-1")
        data = db_record(
            groups=[group_record(id="group-1", name="School")],
            lists=[lst],
            tasks=[
                task_record(id="task-1", name="Lecture", list_id="list-1"),
                task_record(id="task-2", name="Errand", list_id="list-2"),
            ],
            daysheet=[
                daysheet_entry(id="e-1", datetime="2026-04-26T10:00:00", list_id="list-1"),
                daysheet_entry(id="e-2", datetime="2026-04-26T11:00:00", list_id="list-2"),
            ],
        )

        _delete_list(data, lst)

        self.assertEqual(data["groups"], [])
        self.assertEqual(data["lists"], [])
        self.assertEqual([t["id"] for t in data["tasks"]], ["task-2"])
        self.assertEqual([e["id"] for e in data["daysheet"]], ["e-2"])

    def test_daysheet_helpers_add_find_check_and_remove_entries(self):
        data = {"daysheet": []}

        with patch("server.db.new_id", return_value="entry-1"):
            _add_daysheet_entry(
                data,
                "list-1",
                DaysheetEntryType.CONTINUE,
                "Write report",
                "2026-04-26T10:00:00",
            )

        self.assertTrue(
            _has_daysheet_entry(
                data, "list-1", DaysheetEntryType.CONTINUE, "Write report", "2026-04-26"
            )
        )
        self.assertIs(
            _find_daysheet_entry(
                data, "list-1", DaysheetEntryType.CONTINUE, "Write report", "2026-04-26"
            ),
            data["daysheet"][0],
        )
        self.assertEqual(
            _remove_daysheet_entries(
                data, "list-1", DaysheetEntryType.CONTINUE, "Write report", "2026-04-26"
            ),
            1,
        )
        self.assertEqual(data["daysheet"], [])


if __name__ == "__main__":
    unittest.main()

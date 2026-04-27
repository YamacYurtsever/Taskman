import unittest
from unittest.mock import patch

from server.constants import DaysheetEntryType
from server.services.utils import (
    ServiceError,
    add_daysheet_entry,
    delete_group,
    delete_list,
    find_daysheet_entry,
    has_daysheet_entry,
    remove_daysheet_entries,
    service,
    today,
)
from server.tests.utils import (
    daysheet_entry,
    db_record,
    group_record,
    list_record,
    task_record,
)


class ServiceUtilsTest(unittest.TestCase):

    # ─────────────────────────── Service Helpers ───────────────────────────

    def test_service_wrapper_converts_success_and_service_errors(self):
        @service
        def succeeds():
            return "ignored"

        @service
        def fails():
            raise ServiceError("bad input")

        self.assertEqual(succeeds(), (True, ""))
        self.assertEqual(fails(), (False, "bad input"))

    def test_today_returns_current_iso_date(self):
        with patch("server.services.utils.date") as mock_date:
            mock_date.today.return_value.isoformat.return_value = "2026-04-26"

            self.assertEqual(today(), "2026-04-26")

    # ─────────────────────────── Group / List Deletion ───────────────────────────

    def test_delete_group_ungroups_all_lists(self):
        group = group_record(id="group-1", name="Group")
        data = db_record(
            groups=[group],
            lists=[
                list_record(id="list-1", name="List A", group_id="group-1"),
                list_record(id="list-2", name="List B"),
            ],
        )

        delete_group(data, group)

        self.assertEqual(data["groups"], [])
        self.assertIsNone(data["lists"][0]["groupId"])
        self.assertIsNone(data["lists"][1]["groupId"])

    def test_delete_list_removes_related_data_and_prunes_empty_group(self):
        lst = list_record(id="list-1", name="List A", group_id="group-1")
        data = db_record(
            groups=[group_record(id="group-1", name="Group")],
            lists=[lst],
            tasks=[
                task_record(id="task-1", name="Task A", list_id="list-1"),
                task_record(id="task-2", name="Task B", list_id="list-2"),
            ],
            daysheet=[
                daysheet_entry(id="e-1", list_id="list-1"),
                daysheet_entry(id="e-2", datetime="2026-04-26T11:00:00", list_id="list-2"),
            ],
        )

        delete_list(data, lst)

        self.assertEqual(data["groups"], [])
        self.assertEqual(data["lists"], [])
        self.assertEqual([t["id"] for t in data["tasks"]], ["task-2"])
        self.assertEqual([e["id"] for e in data["daysheet"]], ["e-2"])

    # ─────────────────────────── Daysheet Helpers ───────────────────────────

    def test_daysheet_entry_lifecycle(self):
        data = {"daysheet": []}

        with patch("server.db.new_id", return_value="entry-1"):
            add_daysheet_entry(
                data,
                "list-1",
                DaysheetEntryType.CONTINUE,
                "Task A",
                "2026-04-26T10:00:00",
            )

        self.assertTrue(
            has_daysheet_entry(
                data,
                "list-1",
                DaysheetEntryType.CONTINUE,
                "Task A",
                "2026-04-26",
            )
        )

        self.assertIs(
            find_daysheet_entry(
                data,
                "list-1",
                DaysheetEntryType.CONTINUE,
                "Task A",
                "2026-04-26",
            ),
            data["daysheet"][0],
        )

        removed = remove_daysheet_entries(
            data,
            "list-1",
            DaysheetEntryType.CONTINUE,
            "Task A",
            "2026-04-26",
        )

        self.assertEqual(removed, 1)
        self.assertEqual(data["daysheet"], [])

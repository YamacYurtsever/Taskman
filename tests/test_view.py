import unittest
from datetime import date
from unittest.mock import patch

from taskman.commands.view import cmd_ls, filter_tasks
from tests.helpers import capture_stdout, db_record, group_record, list_record, task_record

TODAY = date(2026, 4, 26)

LIST_1 = list_record(id="list-1", name="Work")
LIST_2 = list_record(id="list-2", name="Personal", group_id="group-1")
LIST_3 = list_record(id="list-3", name="Side", group_id="group-1")
GROUP_1 = group_record(id="group-1", name="Mine")

TASK_OVERDUE = task_record(id="t1", name="Overdue task", list_id="list-1", due="2026-04-20")
TASK_TODAY = task_record(id="t2", name="Today task", list_id="list-1", due="2026-04-26")
TASK_TOMORROW = task_record(id="t3", name="Tomorrow task", list_id="list-1", due="2026-04-27")
TASK_NEXT_WEEK = task_record(id="t4", name="Next week", list_id="list-1", due="2026-05-10")
TASK_DATELESS = task_record(id="t5", name="No due date", list_id="list-1")
TASK_DONE = task_record(id="t6", name="Done task", list_id="list-1", due="2026-04-26", done="2026-04-25")


class FilterTasksTest(unittest.TestCase):

    def _tasks(self):
        return [TASK_OVERDUE, TASK_TODAY, TASK_TOMORROW, TASK_NEXT_WEEK, TASK_DATELESS, TASK_DONE]

    # --- default mode ---

    def test_default_excludes_done(self):
        result = filter_tasks(self._tasks(), "list-1", "all", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("Done task", names)

    def test_default_dated_before_dateless(self):
        result = filter_tasks(self._tasks(), "list-1", "all", TODAY)
        names = [t["name"] for t in result]
        dateless_idx = names.index("No due date")
        for t in result[:dateless_idx]:
            self.assertIsNotNone(t["due"])

    def test_default_dated_sorted_by_due(self):
        result = filter_tasks(self._tasks(), "list-1", "all", TODAY)
        dated = [t for t in result if t["due"]]
        dues = [t["due"] for t in dated]
        self.assertEqual(dues, sorted(dues))

    def test_default_includes_dateless(self):
        result = filter_tasks(self._tasks(), "list-1", "all", TODAY)
        names = [t["name"] for t in result]
        self.assertIn("No due date", names)

    # --- today mode ---

    def test_today_includes_overdue(self):
        result = filter_tasks(self._tasks(), "list-1", "day", TODAY)
        names = [t["name"] for t in result]
        self.assertIn("Overdue task", names)

    def test_today_includes_due_today(self):
        result = filter_tasks(self._tasks(), "list-1", "day", TODAY)
        names = [t["name"] for t in result]
        self.assertIn("Today task", names)

    def test_today_excludes_future(self):
        result = filter_tasks(self._tasks(), "list-1", "day", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("Tomorrow task", names)
        self.assertNotIn("Next week", names)

    def test_today_excludes_dateless(self):
        result = filter_tasks(self._tasks(), "list-1", "day", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("No due date", names)

    def test_today_excludes_done(self):
        result = filter_tasks(self._tasks(), "list-1", "day", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("Done task", names)

    # --- week mode ---

    def test_week_includes_overdue(self):
        result = filter_tasks(self._tasks(), "list-1", "week", TODAY)
        names = [t["name"] for t in result]
        self.assertIn("Overdue task", names)

    def test_week_includes_within_7_days(self):
        result = filter_tasks(self._tasks(), "list-1", "week", TODAY)
        names = [t["name"] for t in result]
        self.assertIn("Tomorrow task", names)

    def test_week_excludes_beyond_7_days(self):
        result = filter_tasks(self._tasks(), "list-1", "week", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("Next week", names)

    def test_week_excludes_dateless(self):
        result = filter_tasks(self._tasks(), "list-1", "week", TODAY)
        names = [t["name"] for t in result]
        self.assertNotIn("No due date", names)


class CmdLsTest(unittest.TestCase):

    TASK_PERSONAL = task_record(id="t-p", name="Personal task", list_id="list-2")
    TASK_SIDE = task_record(id="t-s", name="Side task", list_id="list-3")

    def _make_db(self):
        return db_record(
            groups=[GROUP_1],
            lists=[LIST_1, LIST_2, LIST_3],
            tasks=[TASK_TODAY, TASK_DATELESS, self.TASK_PERSONAL, self.TASK_SIDE],
        )

    def _output_for(self, args, db=None):
        with patch("taskman.db.load", return_value=db or self._make_db()):
            return capture_stdout(cmd_ls, args)

    def test_unknown_filter_errors(self):
        with patch("taskman.db.load", return_value=self._make_db()):
            with self.assertRaises(SystemExit):
                cmd_ls(["NonExistent"])

    def test_list_filter(self, ):
        output = self._output_for(["Work"])
        self.assertIn("Work", output)
        self.assertNotIn("Personal", output)

    def test_group_filter(self):
        output = self._output_for(["Mine"])
        self.assertIn("Personal", output)
        self.assertIn("Side", output)
        self.assertNotIn("Work", output)

    def test_empty_list_hidden(self):
        db = db_record(lists=[LIST_1, LIST_2], tasks=[TASK_DATELESS])
        output = self._output_for([], db)
        self.assertIn("Work", output)
        self.assertNotIn("Personal", output)

    def test_empty_db_prints_message(self):
        output = self._output_for([], db_record())
        self.assertIn("no lists", output)


if __name__ == "__main__":
    unittest.main()

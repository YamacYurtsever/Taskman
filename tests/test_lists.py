import copy
import unittest
from unittest.mock import patch

from taskman.commands.lists import cmd_group, cmd_ungroup

LIST_1 = {"id": "list-1", "name": "Work", "groupId": None}
LIST_2 = {"id": "list-2", "name": "Personal", "groupId": None}
GROUP_1 = {"id": "group-1", "name": "Mine"}


def make_db(*lists, groups=None):
    return {
        "groups": copy.deepcopy(list(groups or [])),
        "lists": copy.deepcopy(list(lists)),
        "tasks": [],
        "daysheet": [],
    }


class GroupTest(unittest.TestCase):

    def test_group_assigns_list(self):
        db = make_db(LIST_1)
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)), \
             patch("taskman.db.new_id", return_value="group-new"):
            cmd_group(["Work", "Mine"])

        self.assertEqual(saved["lists"][0]["groupId"], "group-new")

    def test_group_creates_group_if_new(self):
        db = make_db(LIST_1)
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)), \
             patch("taskman.db.new_id", return_value="group-new"):
            cmd_group(["Work", "Mine"])

        self.assertEqual(len(saved["groups"]), 1)
        self.assertEqual(saved["groups"][0]["name"], "Mine")

    def test_group_reuses_existing_group(self):
        db = make_db(LIST_1, LIST_2, groups=[GROUP_1])
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)):
            cmd_group(["Work", "Personal", "Mine"])

        self.assertEqual(len(saved["groups"]), 1)
        self.assertEqual(saved["lists"][0]["groupId"], "group-1")
        self.assertEqual(saved["lists"][1]["groupId"], "group-1")

    def test_group_multiple_lists(self):
        db = make_db(LIST_1, LIST_2)
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)), \
             patch("taskman.db.new_id", return_value="group-new"):
            cmd_group(["Work", "Personal", "NewGroup"])

        self.assertTrue(all(l["groupId"] == "group-new" for l in saved["lists"]))

    def test_group_unknown_list_errors(self):
        db = make_db(LIST_1)
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save"):
            with self.assertRaises(SystemExit):
                cmd_group(["NoSuchList", "Mine"])


class UngroupTest(unittest.TestCase):

    def test_ungroup_clears_group(self):
        lst = {**LIST_1, "groupId": "group-1"}
        db = make_db(lst, groups=[GROUP_1])
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)):
            cmd_ungroup(["Work"])

        self.assertIsNone(saved["lists"][0]["groupId"])

    def test_ungroup_multiple_lists(self):
        lst1 = {**LIST_1, "groupId": "group-1"}
        lst2 = {**LIST_2, "groupId": "group-1"}
        db = make_db(lst1, lst2, groups=[GROUP_1])
        saved = {}
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save", side_effect=lambda d: saved.update(d)):
            cmd_ungroup(["Work", "Personal"])

        self.assertTrue(all(l["groupId"] is None for l in saved["lists"]))

    def test_ungroup_unknown_list_errors(self):
        db = make_db()
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save"):
            with self.assertRaises(SystemExit):
                cmd_ungroup(["Ghost"])

    def test_ungroup_list_not_in_group_errors(self):
        db = make_db(LIST_1)
        with patch("taskman.db.load", return_value=db), \
             patch("taskman.db.save"):
            with self.assertRaises(SystemExit):
                cmd_ungroup(["Work"])


if __name__ == "__main__":
    unittest.main()

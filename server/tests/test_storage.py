import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from server import config, db


class UserDbStorageTest(unittest.TestCase):

    def test_load_migrates_legacy_db_to_user_path(self):
        legacy_db = {
            "groups": [],
            "lists": [{"id": "list-1", "name": "List A", "groupId": None}],
            "tasks": [],
            "daysheet": [],
        }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy_path = root / "db.json"
            legacy_path.write_text(json.dumps(legacy_db))

            with (
                patch("server.db.DB_PATH", legacy_path),
                patch("server.db.USERS_PATH", root / "users"),
            ):
                loaded = db.load("User@Example.com")

            user_path = root / "users" / "user@example.com" / "db.json"

            self.assertEqual(loaded, legacy_db)
            self.assertFalse(legacy_path.exists())
            self.assertTrue(user_path.exists())
            self.assertEqual(json.loads(user_path.read_text()), legacy_db)


class UserConfigStorageTest(unittest.TestCase):

    def test_save_writes_user_config_path(self):
        data = {
            "calendars": [{"id": "calendar-id", "color": "#33B679"}],
            "calendarTimezone": "Australia/Sydney",
            "googleRefreshToken": "reftok",
            "googleEmail": "user@gmail.com",
        }

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            with (
                patch("server.config.CONFIG_PATH", root / "config.json"),
                patch("server.config.USERS_PATH", root / "users"),
            ):
                config.save(data, "User@Example.com")

            user_path = root / "users" / "user@example.com" / "config.json"

            self.assertTrue(user_path.exists())
            self.assertEqual(json.loads(user_path.read_text()), data)

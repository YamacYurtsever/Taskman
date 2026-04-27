import unittest
from unittest.mock import patch

from cli import main


class CliTest(unittest.TestCase):

    def test_help_prints_usage(self):
        with patch("sys.argv", ["taskman"]), patch("builtins.print") as mock_print:
            main()

        self.assertIn("Usage:", mock_print.call_args.args[0])

    def test_dispatches_task_command(self):
        with patch("sys.argv", ["taskman", "add", "Work", "Write report"]), \
             patch("taskman.commands.tasks.cmd_add") as mock_add:
            main()

        mock_add.assert_called_once_with(["Work", "Write report"])

    def test_unknown_command_exits(self):
        with patch("sys.argv", ["taskman", "unknown"]):
            with self.assertRaises(SystemExit):
                main()


if __name__ == "__main__":
    unittest.main()

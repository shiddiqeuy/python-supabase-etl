"""Tests for utils modules."""

import csv
import os
import re
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.utils.logger import save_error_log
from src.utils.messages import (
    BANNER_EXPENSE,
    BANNER_SALES,
    CONNECTION_FAILED,
    CONNECTION_SUCCESS,
    DRY_RUN_LABEL,
    ERROR_FILE_LABEL,
    MSG_EMPTY_COA,
    MSG_FILE_NOT_FOUND,
    MSG_INVALID_FORMAT,
    MSG_NO_DATA,
    MENU_ITEMS,
    PROMPT_BATCH_SIZE,
    PROMPT_DRY_RUN,
    PROMPT_FILE_PATH,
    PROMPT_SHEET,
    PROMPT_VERBOSE,
    SUMMARY_LABELS,
    SUCCESS_LABEL,
)
from src.utils.progress import run_progress


class TestProgress(unittest.TestCase):
    def test_run_progress_calls_process_fn_per_item(self):
        items = [1, 2, 3]
        processed = []
        def process_fn(item, index):
            processed.append((item, index))

        from rich.console import Console
        import io
        console = Console(file=io.StringIO(), force_terminal=True)
        run_progress(total=len(items), description="Test", items=items, process_fn=process_fn, console=console)
        self.assertEqual(len(processed), 3)
        self.assertEqual(processed[0], (1, 1))
        self.assertEqual(processed[2], (3, 3))

    def test_run_progress_empty_list(self):
        from rich.console import Console
        import io
        console = Console(file=io.StringIO(), force_terminal=True)
        run_progress(total=0, description="Test", items=[], process_fn=lambda item, index: None, console=console)
        # should not crash

    def test_run_progress_single_item(self):
        from rich.console import Console
        import io
        console = Console(file=io.StringIO(), force_terminal=True)
        results = []
        def process_fn(item, index):
            results.append(item)
        run_progress(total=1, description="Test", items=[42], process_fn=process_fn, console=console)
        self.assertEqual(results, [42])


class TestLogger(unittest.TestCase):
    def test_save_error_log_empty_returns_empty(self):
        result = save_error_log([])
        self.assertEqual(result, "")

    def test_save_error_log_creates_csv_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                errors = [
                    {"baris": 1, "error": "Test error"},
                    {"baris": 2, "error": "Another error"},
                ]
                result = save_error_log(errors, prefix="test_error")
                self.assertTrue(Path(result).name.startswith("test_error_"))
                self.assertTrue(Path(result).name.endswith(".csv"))
                self.assertTrue(os.path.exists(result))
                with open(result, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    self.assertEqual(len(rows), 2)
                    self.assertEqual(rows[0]["error"], "Test error")
            finally:
                os.chdir(old_cwd)

    def test_save_error_log_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                save_error_log([{"a": 1}], prefix="err")
                self.assertTrue(os.path.isdir("error_logs"))
            finally:
                os.chdir(old_cwd)

    def test_save_error_log_timestamp_in_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = save_error_log([{"x": "y"}], prefix="prefix")
                filename = Path(result).name
                self.assertRegex(filename, r"^prefix_\d{8}_\d{6}\.csv$")
            finally:
                os.chdir(old_cwd)


class TestMessages(unittest.TestCase):
    def test_banner_sales_non_empty(self):
        self.assertIn("Supabase", BANNER_SALES)
        self.assertIn("Penjualan", BANNER_SALES)

    def test_banner_expense_non_empty(self):
        self.assertIn("Supabase", BANNER_EXPENSE)
        self.assertIn("Pengeluaran", BANNER_EXPENSE)

    def test_summary_labels_keys(self):
        expected_keys = {"total", "success", "skipped", "errors", "duration", "total_amount"}
        self.assertEqual(set(SUMMARY_LABELS.keys()), expected_keys)

    def test_menu_items_has_four_items(self):
        self.assertEqual(len(MENU_ITEMS), 4)

    def test_connection_success_non_empty(self):
        self.assertIn("berhasil", CONNECTION_SUCCESS.lower())

    def test_connection_failed_non_empty(self):
        self.assertIn("gagal", CONNECTION_FAILED.lower())

    def test_dry_run_label_non_empty(self):
        self.assertIn("dry run", DRY_RUN_LABEL.lower())

    def test_success_label_non_empty(self):
        self.assertIn("tanpa error", SUCCESS_LABEL.lower())

    def test_error_file_label_format(self):
        formatted = ERROR_FILE_LABEL.format(errors=3, path="some/path.csv")
        self.assertIn("3", formatted)
        self.assertIn("some/path.csv", formatted)

    def test_msg_file_not_found_non_empty(self):
        self.assertIn("File", MSG_FILE_NOT_FOUND)

    def test_msg_no_data_non_empty(self):
        self.assertTrue(len(MSG_NO_DATA) > 0)

    def test_msg_empty_coa_non_empty(self):
        self.assertTrue(len(MSG_EMPTY_COA) > 0)


if __name__ == "__main__":
    unittest.main()

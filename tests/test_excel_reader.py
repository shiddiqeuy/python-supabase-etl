"""Tests for ExcelReader."""

import os
import platform
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from src.core.exceptions import FileReadError
from src.readers.excel_reader import ExcelReader


def _write_xlsx(path: str) -> None:
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df.to_excel(path, index=False, engine="openpyxl")


class TestExcelReader(unittest.TestCase):
    def test_read_csv_file(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", newline="", encoding="utf-8") as f:
            f.write("a,b,c\n1,2,3\n4,5,6\n")
            csv_path = f.name
        try:
            df = ExcelReader.read(csv_path)
            self.assertEqual(len(df), 2)
            self.assertIn("a", df.columns)
        finally:
            os.unlink(csv_path)

    @unittest.skipIf(platform.system() == "Windows", "openpyxl locks files on Windows, skipping xlsx write test")
    def test_read_xlsx_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = os.path.join(tmpdir, "test.xlsx")
            _write_xlsx(tmp_path)
            result = ExcelReader.read(tmp_path)
            self.assertEqual(len(result), 2)
            self.assertIn("a", result.columns)

    @unittest.skipIf(platform.system() == "Windows", "openpyxl locks files on Windows, skipping xlsx write test")
    def test_read_xlsx_from_existing_file(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
        try:
            os.close(fd)
            _write_xlsx(tmp_path)
            result = ExcelReader.read(tmp_path)
            self.assertEqual(len(result), 2)
            self.assertIn("a", result.columns)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @unittest.skipIf(platform.system() == "Windows", "openpyxl locks files on Windows, skipping xlsx write test")
    def test_read_xlsx_with_sheet_name(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
        try:
            os.close(fd)
            with pd.ExcelWriter(tmp_path, engine="openpyxl") as writer:
                pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="Sheet1", index=False)
                pd.DataFrame({"b": [2]}).to_excel(writer, sheet_name="Sheet2", index=False)
            result = ExcelReader.read(tmp_path, sheet_name="Sheet2")
            self.assertIn("b", result.columns)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_file_not_found(self):
        with self.assertRaises(FileReadError):
            ExcelReader.read("/nonexistent/path/file.xlsx")

    def test_read_unsupported_format(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("hello")
            # path is already closed
            with self.assertRaises(FileReadError):
                ExcelReader.read(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_corrupted_xlsx_raises_file_read_error(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(b"not a real xlsx file")
            with self.assertRaises(FileReadError):
                ExcelReader.read(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_empty_xlsx_raises_file_read_error(self):
        fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
        try:
            os.close(fd)
            with self.assertRaises(FileReadError):
                ExcelReader.read(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_read_returns_dataframe(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", newline="", encoding="utf-8") as f:
            f.write("x,y\n10,20\n")
            csv_path = f.name
        try:
            result = ExcelReader.read(csv_path)
            self.assertIsInstance(result, pd.DataFrame)
        finally:
            os.unlink(csv_path)

    def test_read_path_object(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w", newline="", encoding="utf-8") as f:
            f.write("a\n1\n")
            csv_path = f.name
        try:
            result = ExcelReader.read(Path(csv_path))
            self.assertEqual(len(result), 1)
        finally:
            os.unlink(csv_path)

    def test_read_case_insensitive_suffix(self):
        with tempfile.NamedTemporaryFile(suffix=".CSV", delete=False, mode="w", newline="", encoding="utf-8") as f:
            f.write("a\n1\n")
            csv_path = f.name
        try:
            result = ExcelReader.read(csv_path)
            self.assertEqual(len(result), 1)
        finally:
            os.unlink(csv_path)


if __name__ == "__main__":
    unittest.main()

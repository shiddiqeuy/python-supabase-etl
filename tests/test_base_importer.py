"""Tests untuk BaseImporter."""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.core.models import FileSource, ImportResult
from src.core.interfaces import DataRepository, MasterDataCache
from src.importers.base_importer import BaseImporter


class ConcreteImporter(BaseImporter):
    def transform_record(self, row):
        return row.to_dict()

    def validate(self, record, index):
        return None

    def _build_error_row(self, index, record, error):
        return {"index": index, "error": error}

    def _insert_record(self, record):
        return self._repository.insert_record("dummy_table", record)

    def get_error_prefix(self):
        return "test_error"


class TestBaseImporter(unittest.TestCase):
    def setUp(self):
        self.repo = MagicMock(spec=DataRepository)
        self.cache = MagicMock(spec=MasterDataCache)
        self.importer = ConcreteImporter(self.repo, self.cache)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_dry_run(self, mock_reader):
        df = pd.DataFrame([{"a": 1}, {"b": 2}])
        mock_reader.read.return_value = df

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=True)

        self.assertEqual(result.total, 2)
        self.assertEqual(result.success, 0)
        self.assertEqual(result.errors, 0)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_inserts_success(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.total, 1)
        self.assertEqual(result.success, 1)
        self.assertEqual(result.errors, 0)
        self.repo.insert_record.assert_called_once()


if __name__ == "__main__":
    unittest.main()

"""Tests untuk BaseImporter."""

import time
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

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_handles_validation_failure(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df
        self.importer.validate = MagicMock(return_value="invalid data")

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.success, 0)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_handles_insert_exception(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df
        self.repo.insert_record.side_effect = Exception("DB down")

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.errors, 1)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_empty_dataframe(self, mock_reader):
        df = pd.DataFrame()
        mock_reader.read.return_value = df

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.total, 0)
        self.assertEqual(result.success, 0)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_stats_success_skipped_errors(self, mock_reader):
        df = pd.DataFrame([{"a": 1}, {"b": 2}, {"c": 3}])
        mock_reader.read.return_value = df
        self.importer.validate = MagicMock(side_effect=[None, "bad", None])
        self.repo.insert_record.side_effect = [1, Exception("fail")]

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.total, 3)
        self.assertEqual(result.success, 1)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.errors, 1)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_inserts_relations_for_successful_records(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df

        importer = ConcreteImporter(self.repo, self.cache)
        importer._insert_relations = MagicMock()

        source = FileSource(path="dummy.xlsx")
        result = importer.run(source, dry_run=False)

        importer._insert_relations.assert_called_once()
        self.assertEqual(result.success, 1)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_warns_on_relation_insert_failure(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df
        self.repo.insert_record.return_value = 1

        importer = ConcreteImporter(self.repo, self.cache)
        importer._insert_relations = MagicMock(side_effect=Exception("relation fail"))

        source = FileSource(path="dummy.xlsx")
        result = importer.run(source, dry_run=False)

        self.assertEqual(result.success, 1)
        importer._insert_relations.assert_called_once()

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_sets_duration(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertGreaterEqual(result.duration, 0.0)

    @patch("src.importers.base_importer.ExcelReader")
    def test_run_accumulates_total_amount(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.total_amount, 0.0)

    @patch("src.importers.base_importer.ExcelReader")
    def test_transformation_exception_skipped(self, mock_reader):
        df = pd.DataFrame([{"a": 1}])
        mock_reader.read.return_value = df
        self.importer.transform_record = MagicMock(side_effect=Exception("transform fail"))

        source = FileSource(path="dummy.xlsx")
        result = self.importer.run(source, dry_run=False)

        self.assertEqual(result.total, 0)


if __name__ == "__main__":
    unittest.main()

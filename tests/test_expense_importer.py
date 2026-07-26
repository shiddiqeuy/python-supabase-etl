"""Tests untuk ExpenseImporter."""

import unittest
from unittest.mock import MagicMock

import pandas as pd

from src.core.interfaces import DataRepository, MasterDataCache
from src.core.models import ExpenseRecord
from src.importers.expense_importer import ExpenseImporter


class FakeRepo(DataRepository):
    def test_connection(self): return True
    def get_id_by_name(self, table, name): return None
    def insert_record(self, table, data): return 1
    def insert_batch(self, table, records): return []
    def upsert(self, table, records, on_conflict): return []
    def count(self, table): return 0
    def select_one(self, table, filters):
        return None


class TestExpenseImporter(unittest.TestCase):
    def test_parse_coa_with_separator(self):
        importer = ExpenseImporter(MagicMock(), MagicMock())
        kode, nama = importer._parse_coa("5001 - Biaya Listrik")
        self.assertEqual(kode, "5001")
        self.assertEqual(nama, "Biaya Listrik")

    def test_parse_coa_without_separator(self):
        importer = ExpenseImporter(MagicMock(), MagicMock())
        kode, nama = importer._parse_coa("5001")
        self.assertEqual(kode, "5001")
        self.assertEqual(nama, "5001")

    def test_parse_coa_empty_string(self):
        importer = ExpenseImporter(MagicMock(), MagicMock())
        kode, nama = importer._parse_coa("")
        self.assertEqual(kode, "")
        self.assertEqual(nama, "")

    def test_transform_row_coa3_hierarchy(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        row = pd.Series({
            "COA 3": "5001 - Biaya Listrik",
            "COA 2": "",
            "COA": "",
            "Kategori": "Operasional",
            "Pengeluaran": "PLN",
            "Deskripsi": "Bulanan",
            "Tanggal": pd.Timestamp("2024-01-01"),
            "Jumlah": 150000.0,
            "Bukti Tf": "tf123",
        })

        record = importer.transform_record(row)
        self.assertIsNotNone(record)
        self.assertEqual(record.kode_coa, "5001")
        self.assertEqual(record.nama_coa, "Biaya Listrik")
        self.assertEqual(record.coa_level, 3)
        self.assertEqual(record.jumlah, 150000.0)

    def test_transform_row_coa2_hierarchy(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        row = pd.Series({
            "COA 3": "",
            "COA 2": "5002 - Biaya Telepon",
            "COA": "",
            "Kategori": "Operasional",
            "Pengeluaran": "Telkomsel",
            "Deskripsi": "Bulanan",
            "Tanggal": pd.Timestamp("2024-01-01"),
            "Jumlah": 50000.0,
            "Bukti Tf": "tf456",
        })

        record = importer.transform_record(row)
        self.assertIsNotNone(record)
        self.assertEqual(record.kode_coa, "5002")
        self.assertEqual(record.nama_coa, "Biaya Telepon")
        self.assertEqual(record.coa_level, 2)

    def test_transform_row_coa1_hierarchy(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        row = pd.Series({
            "COA 3": "",
            "COA 2": "",
            "COA": "5003 - Biaya Transport",
            "Kategori": "Operasional",
            "Pengeluaran": "Gojek",
            "Deskripsi": "Kantor",
            "Tanggal": pd.Timestamp("2024-01-01"),
            "Jumlah": 25000.0,
            "Bukti Tf": "tf789",
        })

        record = importer.transform_record(row)
        self.assertIsNotNone(record)
        self.assertEqual(record.kode_coa, "5003")
        self.assertEqual(record.nama_coa, "Biaya Transport")
        self.assertEqual(record.coa_level, 1)

    def test_transform_row_all_coa_empty_returns_none(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        row = pd.Series({
            "COA 3": "",
            "COA 2": "nan",
            "COA": "",
            "Kategori": "Ops",
            "Pengeluaran": "X",
            "Deskripsi": "Y",
            "Tanggal": pd.Timestamp("2024-01-01"),
            "Jumlah": 0.0,
            "Bukti Tf": "",
        })
        self.assertIsNone(importer.transform_record(row))

    def test_validate_missing_tanggal(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        record = type("Record", (), {"tanggal": None, "kode_coa": "5001"})()
        error = importer.validate(record, 1)
        self.assertIsNotNone(error)

    def test_validate_missing_kode_coa(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        record = type("Record", (), {"tanggal": "2024-01-01", "kode_coa": ""})()
        error = importer.validate(record, 1)
        self.assertIsNotNone(error)

    def test_validate_valid_record(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        record = type("Record", (), {"tanggal": "2024-01-01", "kode_coa": "5001"})()
        error = importer.validate(record, 1)
        self.assertIsNone(error)

    def test_build_error_row_returns_dict(self):
        importer = ExpenseImporter(MagicMock(), MagicMock())
        record = ExpenseRecord(
            tanggal="2024-01-01",
            kode_coa="5001",
            nama_coa="Biaya Listrik",
            coa_level=3,
            kategori="Ops",
            nama_pengeluaran="PLN",
            deskripsi="x",
            jumlah=100.0,
            bukti_tf="tf",
        )
        row = importer._build_error_row(1, record, "test error")
        self.assertIn("baris", row)
        self.assertIn("error", row)
        self.assertEqual(row["baris"], 1)

    def test_get_error_prefix(self):
        importer = ExpenseImporter(MagicMock(), MagicMock())
        self.assertEqual(importer.get_error_prefix(), "error_expense_log")


if __name__ == "__main__":
    unittest.main()

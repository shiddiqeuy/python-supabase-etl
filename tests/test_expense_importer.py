"""Tests untuk ExpenseImporter."""

import unittest
from unittest.mock import MagicMock

import pandas as pd

from src.core.interfaces import DataRepository, MasterDataCache
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

    def test_validate_missing_tanggal(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = ExpenseImporter(repo, cache)

        record = type("Record", (), {"tanggal": None, "kode_coa": "5001"})()
        error = importer.validate(record, 1)
        self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()

"""Tests untuk SalesImporter."""

import unittest
from unittest.mock import MagicMock

import pandas as pd

from src.core.interfaces import DataRepository, MasterDataCache
from src.importers.sales_importer import SalesImporter


class FakeRepo(DataRepository):
    def test_connection(self): return True
    def get_id_by_name(self, table, name): return None
    def insert_record(self, table, data): return 1
    def insert_batch(self, table, records): return [1, 2]
    def upsert(self, table, records, on_conflict): return []
    def count(self, table): return 0
    def select_one(self, table, filters):
        if filters.get("no_invoice") == "INV-1":
            return {"invoice_id": 1}
        return None


class TestSalesImporter(unittest.TestCase):
    def test_transform_row_valid(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({
            "No. Invoice": "INV-1",
            "Tanggal": pd.Timestamp("2024-01-01"),
            "Nama Customer": "Toko A",
            "Sales": "Andi",
            "Discount": 0.0,
            "Ongkir": 0.0,
            "Jumlah Tagihan": 100.0,
            "Total COGS": 80.0,
            "Down Payment": 20.0,
            "Sisa Tagihan": 80.0,
            "Keterangan": "",
            "Catatan": "",
            "Bukti Transfer": "",
            "Produk 1": "Buku",
            "Qty 1": 2.0,
            "Harga 1": 50.0,
            "COGS 1": 40.0,
        })

        invoice = importer.transform_record(row)
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.no_invoice, "INV-1")
        self.assertEqual(len(invoice.products), 1)
        self.assertEqual(invoice.products[0].produk, "Buku")

    def test_transform_row_empty_invoice_returns_none(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({"No. Invoice": ""})
        self.assertIsNone(importer.transform_record(row))


if __name__ == "__main__":
    unittest.main()

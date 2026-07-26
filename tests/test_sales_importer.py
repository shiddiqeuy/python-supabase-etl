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

    def test_transform_row_nan_invoice_returns_none(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({"No. Invoice": float("nan")})
        self.assertIsNone(importer.transform_record(row))

    def test_transform_row_with_multiple_products(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({
            "No. Invoice": "INV-2",
            "Tanggal": pd.Timestamp("2024-01-02"),
            "Nama Customer": "Toko B",
            "Sales": "Budi",
            "Discount": 10.0,
            "Ongkir": 5000.0,
            "Jumlah Tagihan": 150000.0,
            "Total COGS": 120000.0,
            "Down Payment": 50000.0,
            "Sisa Tagihan": 100000.0,
            "Keterangan": "catatan",
            "Catatan": "internal",
            "Bukti Transfer": "bukti",
            "Produk 1": "Buku",
            "Qty 1": 2.0,
            "Harga 1": 50000.0,
            "COGS 1": 40000.0,
            "Produk 2": "Pensil",
            "Qty 2": 5.0,
            "Harga 2": 2000.0,
            "COGS 2": 1500.0,
        })

        invoice = importer.transform_record(row)
        self.assertIsNotNone(invoice)
        self.assertEqual(len(invoice.products), 2)
        self.assertEqual(invoice.products[1].produk, "Pensil")

    def test_transform_row_no_products_returns_none(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({
            "No. Invoice": "INV-3",
            "Tanggal": pd.Timestamp("2024-01-03"),
            "Nama Customer": "Toko C",
            "Sales": "Siti",
            "Discount": 0.0,
            "Ongkir": 0.0,
            "Jumlah Tagihan": 0.0,
            "Total COGS": 0.0,
            "Down Payment": 0.0,
            "Sisa Tagihan": 0.0,
            "Keterangan": "",
            "Catatan": "",
            "Bukti Transfer": "",
        })
        self.assertIsNone(importer.transform_record(row))

    def test_transform_row_validates_string_date(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)

        row = pd.Series({
            "No. Invoice": "INV-4",
            "Tanggal": "2024-01-05",
            "Nama Customer": "Toko D",
            "Sales": "Doni",
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
            "Qty 1": 1.0,
            "Harga 1": 100.0,
            "COGS 1": 80.0,
        })

        invoice = importer.transform_record(row)
        self.assertEqual(invoice.tanggal, "2024-01-05")

    def test_validate_detects_duplicate_invoice(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)
        invoice = MagicMock()
        invoice.no_invoice = "INV-1"
        error = importer.validate(invoice, 0)
        self.assertIsNotNone(error)

    def test_validate_passes_unique_invoice(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)
        invoice = MagicMock()
        invoice.no_invoice = "INV-NEW"
        error = importer.validate(invoice, 0)
        self.assertIsNone(error)

    def test_safe_float_with_nan(self):
        import math
        result = SalesImporter._safe_float(float("nan"))
        self.assertTrue(math.isnan(result) or result == 0.0)

    def test_safe_float_with_valid(self):
        self.assertEqual(SalesImporter._safe_float(10.5), 10.5)

    def test_safe_float_with_none(self):
        self.assertEqual(SalesImporter._safe_float(None), 0.0)

    def test_safe_float_with_invalid_string(self):
        self.assertEqual(SalesImporter._safe_float("abc"), 0.0)

    def test_get_error_prefix(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)
        self.assertEqual(importer.get_error_prefix(), "error_log")

    def test_build_error_row_returns_dict(self):
        repo = FakeRepo()
        cache = MagicMock(spec=MasterDataCache)
        importer = SalesImporter(repo, cache)
        row = importer._build_error_row(5, MagicMock(no_invoice="INV-1", customer_name="A", jumlah_tagihan=100.0), "error here")
        self.assertIn("baris", row)
        self.assertIn("error", row)
        self.assertEqual(row["baris"], 5)


if __name__ == "__main__":
    unittest.main()

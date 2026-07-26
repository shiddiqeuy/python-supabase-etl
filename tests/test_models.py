"""Tests for core.models."""

from pathlib import Path
import unittest
from datetime import datetime
from decimal import Decimal

from src.core.models import (
    ExpenseRecord,
    FileSource,
    ImportResult,
    Invoice,
    InvoiceItem,
)


class TestFileSource(unittest.TestCase):
    def test_format_csv(self):
        fs = FileSource(path=Path("data.csv"))
        self.assertEqual(fs.format, "csv")

    def test_format_xlsx(self):
        fs = FileSource(path=Path("data.xlsx"))
        self.assertEqual(fs.format, "xlsx")

    def test_format_unsupported_raises(self):
        fs = FileSource(path=Path("data.txt"))
        with self.assertRaises(ValueError):
            _ = fs.format

    def test_format_case_insensitive(self):
        fs = FileSource(path=Path("data.CSV"))
        self.assertEqual(fs.format, "csv")
        fs2 = FileSource(path=Path("data.XLSX"))
        self.assertEqual(fs2.format, "xlsx")


class TestInvoice(unittest.TestCase):
    def test_invoice_creation(self):
        inv = Invoice(
            no_invoice="INV-1",
            tanggal="2024-01-01",
            customer_name="Toko A",
            sales_name="Andi",
            discount=0.0,
            ongkir=0.0,
            jumlah_tagihan=100.0,
            total_cogs=80.0,
            down_payment=20.0,
            sisa_tagihan=80.0,
            keterangan="",
            catatan="",
            bukti_transfer="",
            products=[],
        )
        self.assertEqual(inv.no_invoice, "INV-1")
        self.assertEqual(len(inv.products), 0)

    def test_invoice_with_products(self):
        item = InvoiceItem(produk="Buku", qty=2.0, harga=50.0, cogs=40.0)
        inv = Invoice(
            no_invoice="INV-1",
            tanggal="2024-01-01",
            customer_name="Toko A",
            sales_name="Andi",
            discount=0.0,
            ongkir=0.0,
            jumlah_tagihan=100.0,
            total_cogs=80.0,
            down_payment=20.0,
            sisa_tagihan=80.0,
            keterangan="",
            catatan="",
            bukti_transfer="",
            products=[item],
        )
        self.assertEqual(len(inv.products), 1)
        self.assertEqual(inv.products[0].produk, "Buku")
        self.assertEqual(inv.products[0].qty, 2.0)


class TestExpenseRecord(unittest.TestCase):
    def test_expense_record_creation(self):
        rec = ExpenseRecord(
            tanggal="2024-01-01",
            kode_coa="5001",
            nama_coa="Biaya Listrik",
            coa_level=3,
            kategori="Operasional",
            nama_pengeluaran="PLN",
            deskripsi="Bulanan",
            jumlah=150000.0,
            bukti_tf="tf123",
        )
        self.assertEqual(rec.kode_coa, "5001")
        self.assertEqual(rec.jumlah, 150000.0)


class TestImportResult(unittest.TestCase):
    def test_import_result_defaults(self):
        result = ImportResult(
            total=10,
            success=8,
            skipped=1,
            errors=1,
            total_amount=1000.0,
            duration=1.5,
        )
        self.assertEqual(result.total, 10)
        self.assertEqual(result.success, 8)
        self.assertEqual(result.error_file, "")

    def test_import_result_with_error_file(self):
        result = ImportResult(
            total=10,
            success=9,
            skipped=0,
            errors=1,
            total_amount=900.0,
            duration=2.0,
            error_file="error_logs/error_20240101.csv",
        )
        self.assertIn("error_logs", result.error_file)


if __name__ == "__main__":
    unittest.main()

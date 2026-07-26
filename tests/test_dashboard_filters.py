"""Unit tests - Parameterized Filters & Error Handling (Test 23 - 33)."""

import unittest
import pandas as pd
from src.reports.filter import apply_filters


class TestDashboardParameterizedFilters(unittest.TestCase):
    def setUp(self):
        self.df_invoices = pd.DataFrame([
            {"no_invoice": "INV-1", "customer_name": "Toko A", "sales_name": "Budi", "jumlah_tagihan": 100000.0, "sisa_tagihan": 0.0},
            {"no_invoice": "INV-2", "customer_name": "Toko B", "sales_name": "Unassigned", "jumlah_tagihan": 200000.0, "sisa_tagihan": 200000.0},
            {"no_invoice": "INV-3", "customer_name": "Toko C", "sales_name": "Budi", "jumlah_tagihan": 300000.0, "sisa_tagihan": 150000.0},
            {"no_invoice": "INV-4", "customer_name": "Toko A", "sales_name": "Ani", "jumlah_tagihan": 500000.0, "sisa_tagihan": 0.0},
        ])

        self.df_items = pd.DataFrame([
            {"no_invoice": "INV-1", "product_name": "Kopi Arabika", "qty": 2.0, "harga": 50000.0, "cogs": 30000.0},
            {"no_invoice": "INV-2", "product_name": "Kopi Robusta", "qty": 4.0, "harga": 50000.0, "cogs": 30000.0},
            {"no_invoice": "INV-3", "product_name": "Teh Hijau", "qty": 6.0, "harga": 50000.0, "cogs": 30000.0},
        ])

    # Test 23: test_filter_by_single_customer
    def test_filter_by_single_customer(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, customer="Toko A")
        self.assertEqual(len(res), 2)
        self.assertTrue((res["customer_name"] == "Toko A").all())

    # Test 24: test_filter_by_multiple_customers_comma_separated
    def test_filter_by_multiple_customers_comma_separated(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, customer="Toko A, Toko B")
        self.assertEqual(len(res), 3)
        self.assertTrue(set(res["customer_name"]).issubset({"Toko A", "Toko B"}))

    # Test 25: test_filter_by_product
    def test_filter_by_product(self):
        _, res_items = apply_filters(self.df_invoices, self.df_items, product="Kopi Arabika")
        self.assertEqual(len(res_items), 1)
        self.assertEqual(res_items.iloc[0]["product_name"], "Kopi Arabika")

    # Test 26: test_filter_by_sales_unassigned
    def test_filter_by_sales_unassigned(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, sales="unassigned")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]["no_invoice"], "INV-2")

    # Test 27: test_filter_by_status_lunas
    def test_filter_by_status_lunas(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, status="lunas")
        self.assertEqual(len(res), 2)
        self.assertTrue((res["sisa_tagihan"] == 0).all())

    # Test 28: test_filter_by_status_belum_lunas
    def test_filter_by_status_belum_lunas(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, status="belum_lunas")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]["no_invoice"], "INV-2")

    # Test 29: test_filter_by_status_sebagian
    def test_filter_by_status_sebagian(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, status="sebagian")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]["no_invoice"], "INV-3")

    # Test 30: test_filter_by_amount_range
    def test_filter_by_amount_range(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, min_amount=150000.0, max_amount=350000.0)
        self.assertEqual(len(res), 2)
        amounts = res["jumlah_tagihan"].tolist()
        self.assertIn(200000.0, amounts)
        self.assertIn(300000.0, amounts)

    # Test 31: test_filter_combination_is_and_not_or
    def test_filter_combination_is_and_not_or(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, customer="Toko A", sales="Budi", status="lunas")
        self.assertEqual(len(res), 1)
        self.assertEqual(res.iloc[0]["no_invoice"], "INV-1")

    # Test 32: test_filter_invalid_name_returns_clear_error
    def test_filter_invalid_name_returns_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            apply_filters(self.df_invoices, self.df_items, customer="Toko Fiktif")
        self.assertIn("Customer 'Toko Fiktif' tidak ditemukan", str(ctx.exception))

    # Test 33: test_menu_filter_prompts_are_optional
    def test_menu_filter_prompts_are_optional(self):
        res, _ = apply_filters(self.df_invoices, self.df_items, customer="", sales="", status=None)
        self.assertEqual(len(res), 4)


if __name__ == "__main__":
    unittest.main()

"""Unit tests - Logika agregasi reports.py (Test 1 - 7)."""

import unittest
import pandas as pd
from src.reports import reports


class TestReportsAggregation(unittest.TestCase):
    def setUp(self):
        self.dummy_invoices = pd.DataFrame([
            {
                "no_invoice": "INV-001",
                "tanggal": "2026-01-10",
                "customer_name": "Toko A",
                "sales_name": "Budi",
                "jumlah_tagihan": 100000.0,
                "total_cogs": 60000.0,
                "sisa_tagihan": 0.0,
            },
            {
                "no_invoice": "INV-002",
                "tanggal": "2026-01-05",
                "customer_name": "Toko B",
                "sales_name": None,  # Unassigned
                "jumlah_tagihan": 200000.0,
                "total_cogs": 120000.0,
                "sisa_tagihan": 200000.0,
            },
            {
                "no_invoice": "INV-003",
                "tanggal": "2026-02-15",
                "customer_name": "Toko A",
                "sales_name": "Budi",
                "jumlah_tagihan": 300000.0,
                "total_cogs": 180000.0,
                "sisa_tagihan": 100000.0,  # Sebagian
            },
        ])

        self.dummy_items = pd.DataFrame([
            {"no_invoice": "INV-001", "product_name": "Kopi A", "qty": 2.0, "harga": 25000.0, "cogs": 15000.0},
            {"no_invoice": "INV-001", "product_name": "Kopi B", "qty": 1.0, "harga": 50000.0, "cogs": 30000.0},
            {"no_invoice": "INV-002", "product_name": "Kopi A", "qty": 4.0, "harga": 25000.0, "cogs": 15000.0},
        ])

    # Test 1: test_summary_calculates_correct_totals
    def test_summary_calculates_correct_totals(self):
        res = reports.summary(self.dummy_invoices)
        self.assertEqual(res["total_omzet"], 600000.0)
        self.assertEqual(res["total_cogs"], 360000.0)
        self.assertEqual(res["total_margin"], 240000.0)
        self.assertAlmostEqual(res["margin_pct"], 40.0, places=1)
        self.assertEqual(res["total_invoices"], 3)
        self.assertEqual(res["avg_invoice"], 200000.0)

    # Test 2: test_summary_handles_empty_period
    def test_summary_handles_empty_period(self):
        empty_df = pd.DataFrame()
        res = reports.summary(empty_df)
        self.assertEqual(res["total_omzet"], 0.0)
        self.assertEqual(res["total_cogs"], 0.0)
        self.assertEqual(res["total_margin"], 0.0)
        self.assertEqual(res["total_invoices"], 0)

    # Test 3: test_by_sales_groups_unassigned_correctly
    def test_by_sales_groups_unassigned_correctly(self):
        res = reports.by_sales(self.dummy_invoices)
        sales_names = res["sales_name"].tolist()
        self.assertIn("Unassigned", sales_names)
        unassigned_row = res[res["sales_name"] == "Unassigned"].iloc[0]
        self.assertEqual(unassigned_row["total_omzet"], 200000.0)

    # Test 4: test_by_product_margin_calculation
    def test_by_product_margin_calculation(self):
        res = reports.by_product(self.dummy_items)
        # Kopi A: 2*25000 + 4*25000 = 150000 omzet, 2*15000 + 4*15000 = 90000 cogs -> margin 60000
        kopi_a = res[res["product_name"] == "Kopi A"].iloc[0]
        self.assertEqual(kopi_a["total_omzet"], 150000.0)
        self.assertEqual(kopi_a["total_cogs"], 90000.0)
        self.assertEqual(kopi_a["margin"], 60000.0)

    # Test 5: test_by_customer_outstanding_matches_sisa_tagihan
    def test_by_customer_outstanding_matches_sisa_tagihan(self):
        res = reports.by_customer(self.dummy_invoices)
        toko_a = res[res["customer_name"] == "Toko A"].iloc[0]
        # Toko A: 0 + 100000 = 100000 sisa tagihan
        self.assertEqual(toko_a["sisa_tagihan"], 100000.0)

    # Test 6: test_payment_status_sorts_oldest_first
    def test_payment_status_sorts_oldest_first(self):
        res = reports.payment_status(self.dummy_invoices)
        dates = res["tanggal"].tolist()
        self.assertEqual(dates, ["2026-01-05", "2026-01-10", "2026-02-15"])

    # Test 7: test_trend_daily_weekly_monthly_bucketing
    def test_trend_daily_weekly_monthly_bucketing(self):
        res_m = reports.trend(self.dummy_invoices, interval="monthly")
        self.assertIn("2026-01", res_m["periode"].tolist())
        self.assertIn("2026-02", res_m["periode"].tolist())

        res_d = reports.trend(self.dummy_invoices, interval="daily")
        self.assertIn("2026-01-05", res_d["periode"].tolist())


if __name__ == "__main__":
    unittest.main()

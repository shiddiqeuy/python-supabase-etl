"""Integration tests - CLI Commands & Export (Test 10 - 12)."""

import os
import unittest
from pathlib import Path
import pandas as pd

from src.reports.exporter import export_csv, export_xlsx


class TestDashboardCLIAndExport(unittest.TestCase):
    def setUp(self):
        self.dummy_df = pd.DataFrame([
            {"no_invoice": "INV-001", "jumlah_tagihan": 100000.0, "total_omzet": 100000.0}
        ])
        self.test_dir = Path("tests/scratch")
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        for f in self.test_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass

    # Test 10: test_cli_summary_command_output
    def test_cli_summary_command_output(self):
        from src.reports import reports
        res = reports.summary(self.dummy_df)
        self.assertIn("total_omzet", res)
        self.assertEqual(res["total_omzet"], 100000.0)

    # Test 11: test_cli_export_csv_creates_file
    def test_cli_export_csv_creates_file(self):
        target_path = str(self.test_dir / "test_out.csv")
        res_path = export_csv(self.dummy_df, target_path)
        self.assertTrue(Path(res_path).exists())

        read_df = pd.read_csv(res_path)
        self.assertEqual(len(read_df), 1)

    # Test 12: test_cli_export_xlsx_creates_file
    def test_cli_export_xlsx_creates_file(self):
        target_path = str(self.test_dir / "test_out.xlsx")
        res_path = export_xlsx(self.dummy_df, target_path)
        self.assertTrue(Path(res_path).exists())

        read_df = pd.read_excel(res_path)
        self.assertEqual(len(read_df), 1)


if __name__ == "__main__":
    unittest.main()

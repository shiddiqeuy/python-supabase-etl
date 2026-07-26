"""Unit tests - Database layer (Test 8 - 9)."""

import os
import unittest
from unittest.mock import MagicMock, patch

from src.repositories.dashboard_repository import DashboardRepository


class TestDashboardDatabaseLayer(unittest.TestCase):
    # Test 8: test_db_connection_uses_env_var
    @patch.dict(os.environ, {"DATABASE_URL": "https://test-env.supabase.co"})
    def test_db_connection_uses_env_var(self):
        repo = DashboardRepository()
        self.assertEqual(repo.repo._settings.supabase_url, "https://test-env.supabase.co")

    # Test 9: test_query_uses_parameterized_input
    def test_query_uses_parameterized_input(self):
        mock_supabase = MagicMock()
        mock_supabase.client.table().select().execute.return_value.data = [
            {"invoice_id": 1, "jumlah_tagihan": 50000, "customers": {"nama_customer": "Toko A"}}
        ]
        repo = DashboardRepository(repository=mock_supabase)
        df = repo.get_invoices_df()

        mock_supabase.client.table.assert_called_with("invoices")
        self.assertFalse(df.empty)
        self.assertEqual(df.iloc[0]["customer_name"], "Toko A")


if __name__ == "__main__":
    unittest.main()

"""Tests for SupabaseRepository."""

import unittest
from unittest.mock import MagicMock, patch

from src.core.config import Settings
from src.core.exceptions import ImportError
from src.repositories.supabase_repository import SupabaseRepository


class FakeResponse:
    def __init__(self, data=None, count=None):
        self.data = data or []
        self.count = count


class TestSupabaseRepository(unittest.TestCase):
    def setUp(self):
        settings = Settings(
            supabase_url="https://fake.supabase.co",
            supabase_service_role_key="fake-key",
        )
        self.repo = SupabaseRepository(settings)

    def test_client_creates_once(self):
        with patch("src.repositories.supabase_repository.create_client") as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            self.repo._client = None
            _ = self.repo.client
            mock_create.assert_called_once_with("https://fake.supabase.co", "fake-key")

    def test_client_setter(self):
        mock_client = MagicMock()
        self.repo.client = mock_client
        self.assertEqual(self.repo.client, mock_client)

    def test_test_connection_true(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.execute.return_value = FakeResponse()
        self.assertTrue(self.repo.test_connection())

    def test_test_connection_false_on_exception(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.execute.side_effect = Exception("Network error")
        self.assertFalse(self.repo.test_connection())

    def test_insert_record_returns_id(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.insert.return_value.execute.return_value = FakeResponse(data=[{"id": 99}])
        self.assertEqual(self.repo.insert_record("invoices", {"no_invoice": "INV-1"}), 99)

    def test_insert_record_raises_on_exception(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")
        with self.assertRaises(ImportError):
            self.repo.insert_record("invoices", {"no_invoice": "INV-1"})

    def test_insert_batch_returns_ids(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.insert.return_value.execute.return_value = FakeResponse(data=[{"id": 1}, {"id": 2}])
        self.assertEqual(self.repo.insert_batch("invoices", [{"a": 1}, {"a": 2}]), [1, 2])

    def test_insert_batch_returns_empty_on_empty_records(self):
        self.repo.client = MagicMock()
        self.assertEqual(self.repo.insert_batch("invoices", []), [])

    def test_count_returns_count(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.execute.return_value = FakeResponse(count=5)
        self.assertEqual(self.repo.count("invoices"), 5)

    def test_count_returns_zero_on_exception(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.execute.side_effect = Exception("error")
        self.assertEqual(self.repo.count("invoices"), 0)

    def test_select_one_returns_record(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.limit.return_value.eq.return_value.execute.return_value = FakeResponse(data=[{"id": 1, "nama": "test"}])
        result = self.repo.select_one("customers", {"nama": "test"})
        self.assertEqual(result["id"], 1)

    def test_select_one_returns_none_when_empty(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.limit.return_value.eq.return_value.execute.return_value = FakeResponse(data=[])
        self.assertIsNone(self.repo.select_one("customers", {"nama": "missing"}))

    def test_select_one_returns_none_on_exception(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.limit.return_value.eq.return_value.execute.side_effect = Exception("error")
        self.assertIsNone(self.repo.select_one("customers", {"nama": "test"}))

    def test_upsert_returns_ids(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.upsert.return_value.execute.return_value = FakeResponse(data=[{"id": 1}])
        self.assertEqual(self.repo.upsert("x", [{"a": 1}], "id"), [1])

    def test_upsert_returns_empty_on_empty_records(self):
        self.repo.client = MagicMock()
        self.assertEqual(self.repo.upsert("x", [], "id"), [])

    def test_get_id_by_name_returns_id(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = FakeResponse(data=[{"id": 10}])
        self.assertEqual(self.repo.get_id_by_name("customers", "Toko A"), 10)

    def test_get_id_by_name_returns_none_when_empty(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = FakeResponse(data=[])
        self.assertIsNone(self.repo.get_id_by_name("customers", "Toko B"))

    def test_get_id_by_name_returns_none_on_exception(self):
        self.repo.client = MagicMock()
        self.repo.client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = Exception("error")
        self.assertIsNone(self.repo.get_id_by_name("customers", "Toko C"))


if __name__ == "__main__":
    unittest.main()

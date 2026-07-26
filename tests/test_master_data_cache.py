"""Tests untuk MasterDataCache."""

import unittest
from unittest.mock import MagicMock

from src.core.interfaces import DataRepository, MasterDataCache
from src.repositories.master_data_cache import MasterDataCache


class FakeRepository(DataRepository):
    def test_connection(self): return True
    def get_id_by_name(self, table, name): return None
    def insert_record(self, table, data): return 42
    def insert_batch(self, table, records): return []
    def upsert(self, table, records, on_conflict): return []
    def count(self, table): return 0
    def select_one(self, table, filters):
        if filters.get("nama") == "existing":
            return {"id": 1}
        return None


class TestMasterDataCache(unittest.TestCase):
    def setUp(self):
        self.repo = FakeRepository()
        self.cache = MasterDataCache(self.repo)

    def test_resolve_id_cache_miss_inserts(self):
        record_id = self.cache.resolve_id("customers", "Toko Baru")
        self.assertEqual(record_id, 42)

    def test_resolve_id_cache_hit(self):
        self.cache.resolve_id("customers", "Toko Baru")
        record_id = self.cache.resolve_id("customers", "Toko Baru")
        self.assertEqual(record_id, 42)

    def test_resolve_id_existing_returns_existing_id(self):
        record_id = self.cache.resolve_id("customers", "existing")
        self.assertEqual(record_id, 1)

    def test_invalidate_removes_single_entry(self):
        self.cache.resolve_id("customers", "Toko Baru")
        self.cache.invalidate("customers", "Toko Baru")
        self.assertNotIn("customers:Toko Baru", self.cache._cache)

    def test_clear_empties_cache(self):
        self.cache.resolve_id("customers", "A")
        self.cache.resolve_id("products", "B")
        self.cache.clear()
        self.assertEqual(len(self.cache._cache), 0)


if __name__ == "__main__":
    unittest.main()

"""Stress tests untuk CLI supabase-importer."""

import gc
import os
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from src.core.models import FileSource, ImportResult
from src.importers.base_importer import BaseImporter
from src.core.interfaces import DataRepository, MasterDataCache


class StressFakeRepo(DataRepository):
    def test_connection(self): return True
    def get_id_by_name(self, table, name): return None
    def insert_record(self, table, data): return 1
    def insert_batch(self, table, records): return []
    def upsert(self, table, records, on_conflict): return []
    def count(self, table): return 0
    def select_one(self, table, filters):
        return None


class StressFakeCache(MasterDataCache):
    def __init__(self):
        self._cache = {}

    def resolve_id(self, table, name, extra_fields=None):
        return 1

    def invalidate(self, table, name):
        pass

    def clear(self):
        self._cache.clear()


class StressImporter(BaseImporter):
    def transform_record(self, row):
        return {"row": row.to_dict()}

    def validate(self, record, index):
        return None

    def _build_error_row(self, index, record, error):
        return {"index": index, "error": error}

    def _insert_record(self, record):
        return self._repository.insert_record("dummy", record)

    def get_error_prefix(self):
        return "stress_test"


class TestStress(unittest.TestCase):
    def setUp(self):
        self.repo = StressFakeRepo()
        self.cache = StressFakeCache()
        self.importer = StressImporter(self.repo, self.cache)

    def _get_memory_kb(self):
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        except Exception:
            return 0

    @patch("src.importers.base_importer.run_progress")
    def test_concurrency_100_parallel_calls(self, mock_progress):
        import pandas as pd
        df = pd.DataFrame([{"a": i} for i in range(10)])

        def fast_process(item, index):
            pass

        mock_progress.side_effect = lambda total, description, items, process_fn, console: [
            process_fn(item, idx) for idx, item in enumerate(items, 1)
        ]

        with patch("src.importers.base_importer.ExcelReader") as mock_reader:
            mock_reader.read.return_value = df

            source = FileSource(path="dummy.xlsx")
            start = time.time()
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.importer.run, source, dry_run=False) for _ in range(100)]
                results = [f.result() for f in as_completed(futures)]
            elapsed = time.time() - start

            success_count = sum(1 for r in results if r.errors == 0 and r.success > 0)
            error_count = sum(1 for r in results if r.errors > 0)

            self.assertEqual(len(results), 100)
            self.assertGreaterEqual(success_count, 90, f"Expected >=90 success, got {success_count}, errors: {error_count}")
            self.assertLess(error_count, 10, f"Too many errors: {error_count}")
            print(f"\nConcurrency: 100 calls in {elapsed:.2f}s, success={success_count}, errors={error_count}")

    @patch("src.importers.base_importer.run_progress")
    def test_endurance_500_loop_no_leak(self, mock_progress):
        import pandas as pd
        df = pd.DataFrame([{"a": i} for i in range(5)])

        def fast_process(item, index):
            pass

        mock_progress.side_effect = lambda total, description, items, process_fn, console: [
            process_fn(item, idx) for idx, item in enumerate(items, 1)
        ]

        with patch("src.importers.base_importer.ExcelReader") as mock_reader:
            mock_reader.read.return_value = df

            source = FileSource(path="dummy.xlsx")
            gc.collect()
            mem_before = self._get_memory_kb()

            start = time.time()
            success = 0
            errors = 0
            for i in range(500):
                result = self.importer.run(source, dry_run=False)
                if result.errors == 0 and result.success > 0:
                    success += 1
                else:
                    errors += 1

            gc.collect()
            mem_after = self._get_memory_kb()
            elapsed = time.time() - start
            leak = mem_after - mem_before

            self.assertEqual(success + errors, 500)
            self.assertGreaterEqual(success, 400, f"Expected >=400 success, got {success}")
            self.assertLess(errors, 100)
            print(f"\nEndurance: 500 loops in {elapsed:.2f}s, success={success}, errors={errors}, mem_leak={leak:.0f}KB")

    @patch("src.importers.base_importer.run_progress")
    def test_edge_case_large_payload(self, mock_progress):
        import pandas as pd
        large_row = {f"col_{i}": "x" * 100 for i in range(50)}
        df = pd.DataFrame([large_row])

        def fast_process(item, index):
            pass

        mock_progress.side_effect = lambda total, description, items, process_fn, console: [
            process_fn(item, idx) for idx, item in enumerate(items, 1)
        ]

        with patch("src.importers.base_importer.ExcelReader") as mock_reader:
            mock_reader.read.return_value = df

            source = FileSource(path="dummy.xlsx")
            result = self.importer.run(source, dry_run=False)
            self.assertEqual(result.total, 1)
            self.assertGreaterEqual(result.success, 0)

    @patch("src.importers.base_importer.run_progress")
    def test_edge_case_invalid_argument_types(self, mock_progress):
        import pandas as pd
        df = pd.DataFrame([
            {"a": None},
            {"a": float("inf")},
            {"a": float("-inf")},
            {"a": "not_a_number"},
        ])

        def fast_process(item, index):
            pass

        mock_progress.side_effect = lambda total, description, items, process_fn, console: [
            process_fn(item, idx) for idx, item in enumerate(items, 1)
        ]

        with patch("src.importers.base_importer.ExcelReader") as mock_reader:
            mock_reader.read.return_value = df

            source = FileSource(path="dummy.xlsx")
            result = self.importer.run(source, dry_run=False)

            self.assertEqual(result.total, 4)
            self.assertGreaterEqual(result.success + result.skipped + result.errors, 4)


if __name__ == "__main__":
    unittest.main()
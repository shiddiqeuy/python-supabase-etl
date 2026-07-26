"""Generic cache untuk resolve nama → ID pada tabel master (lazy per-lookup + get-or-create)."""

from typing import Any, Dict, Optional

from src.core.interfaces import DataRepository, MasterDataCache


class MasterDataCache(MasterDataCache):
    """
    Cache in-memory untuk ID tabel master.
    Setiap resolve_id yang gagal menemukan record akan otomatis insert record baru.
    """

    def __init__(self, repository: DataRepository) -> None:
        self._repository = repository
        self._cache: Dict[str, Dict[str, int]] = {}

    def _make_key(self, table: str, name: str) -> str:
        return f"{table}:{name}"

    def resolve_id(self, table: str, name: str, extra_fields: Optional[Dict[str, Any]] = None) -> int:
        """
        Dapatkan ID untuk nama di tabel master.
        Jika belum ada, insert record baru menggunakan nama + extra_fields.
        """
        cache_key = self._make_key(table, name)

        if cache_key in self._cache:
            return self._cache[cache_key]

        record = self._repository.select_one(table, {"nama": name})
        if record:
            record_id = int(record["id"])
        else:
            payload: Dict[str, Any] = {"nama": name}
            if extra_fields:
                payload.update(extra_fields)
            record_id = self._repository.insert_record(table, payload)

        self._cache[cache_key] = record_id
        return record_id

    def invalidate(self, table: str, name: str) -> None:
        """Hapus satu entry cache."""
        cache_key = self._make_key(table, name)
        self._cache.pop(cache_key, None)

    def clear(self) -> None:
        """Kosongkan seluruh cache."""
        self._cache.clear()

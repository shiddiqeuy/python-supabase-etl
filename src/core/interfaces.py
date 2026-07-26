"""Abstract Base Classes yang mendefinisikan kontrak antar modul."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.models import FileSource, ImportResult


class DataRepository(ABC):
    """Kontrak untuk operasi akses data ke database."""

    @abstractmethod
    def test_connection(self) -> bool:
        """Uji koneksi database. Return True jika berhasil."""
        ...

    @abstractmethod
    def get_id_by_name(self, table: str, name: str) -> Optional[int]:
        """Ambil ID record dari tabel master berdasarkan nama."""
        ...

    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, Any]) -> int:
        """Insert satu record, return ID yang di-generate."""
        ...

    @abstractmethod
    def insert_batch(self, table: str, records: List[Dict[str, Any]]) -> List[int]:
        """Insert banyak record secara batch, return list ID."""
        ...

    @abstractmethod
    def upsert(
        self,
        table: str,
        records: List[Dict[str, Any]],
        on_conflict: str,
    ) -> List[int]:
        """Upsert record berdasarkan kolom konflik."""
        ...

    @abstractmethod
    def count(self, table: str) -> int:
        """Kembalikan jumlah record di tabel."""
        ...


class MasterDataCache(ABC):
    """Kontrak untuk cache nama → ID pada tabel master."""

    @abstractmethod
    def resolve_id(self, table: str, name: str, extra_fields: Optional[Dict[str, Any]] = None) -> int:
        """
        Dapatkan ID untuk nama di tabel master.
        Jika belum ada, insert record baru (get-or-create).
        """
        ...

    @abstractmethod
    def invalidate(self, table: str, name: str) -> None:
        """Hapus satu entry cache."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Kosongkan seluruh cache."""
        ...


class Importer(ABC):
    """Kontrak untuk semua modul impor (sales, expense, dst)."""

    @abstractmethod
    def run(
        self,
        source: FileSource,
        dry_run: bool = False,
        batch_size: int = 100,
        verbose: bool = False,
    ) -> ImportResult:
        """
        Jalankan pipeline impor.
        Return ImportResult berisi statistik dan path error log.
        """
        ...

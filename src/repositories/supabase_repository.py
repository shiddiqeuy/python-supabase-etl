"""Implementasi DataRepository menggunakan Supabase client."""

from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from src.core.config import Settings
from src.core.exceptions import ImportError, SupabaseConfigError
from src.core.interfaces import DataRepository


class SupabaseRepository(DataRepository):
    """
    Implementasi konkret DataRepository untuk Supabase.

    Catatan penting:
    - Operasi insert/upsert **tidak dijalankan dalam transaction**.
    - Kegagalan parsial dapat mengakibatkan data tidak konsisten.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = create_client(
                self._settings.supabase_url,
                self._settings.supabase_service_role_key,
            )
        return self._client

    @client.setter
    def client(self, value: Optional[Client]) -> None:
        self._client = value

    def test_connection(self) -> bool:
        """Uji koneksi dengan query count ke tabel invoices."""
        try:
            self.client.table("invoices").select("count", count="exact").execute()
            return True
        except Exception:
            return False

    def get_id_by_name(self, table: str, name: str) -> Optional[int]:
        """Ambil ID record dari tabel master berdasarkan nama kolom."""
        try:
            result = self.client.table(table).select("*").eq("nama", name).limit(1).execute()
            if result.data:
                return int(result.data[0]["id"])
        except Exception:
            pass
        return None

    def insert_record(self, table: str, data: Dict[str, Any], id_column: str = "id") -> int:
        """Insert satu record, return ID yang di-generate."""
        try:
            result = self.client.table(table).insert(data).execute()
            return int(result.data[0][id_column])
        except Exception as exc:
            raise ImportError(f"Gagal insert ke tabel '{table}': {exc}") from exc

    def insert_batch(self, table: str, records: List[Dict[str, Any]]) -> List[int]:
        """Insert banyak record secara batch, return list ID."""
        if not records:
            return []
        try:
            result = self.client.table(table).insert(records).execute()
            return [int(row["id"]) for row in result.data]
        except Exception as exc:
            raise ImportError(f"Gagal batch insert ke tabel '{table}': {exc}") from exc

    def upsert(
        self,
        table: str,
        records: List[Dict[str, Any]],
        on_conflict: str,
    ) -> List[int]:
        """Upsert record berdasarkan kolom konflik."""
        if not records:
            return []
        try:
            result = (
                self.client.table(table)
                .upsert(records, onconflict=on_conflict)
                .execute()
            )
            return [int(row["id"]) for row in result.data]
        except Exception as exc:
            raise ImportError(f"Gagal upsert ke tabel '{table}': {exc}") from exc

    def count(self, table: str) -> int:
        """Kembalikan jumlah record di tabel."""
        try:
            result = self.client.table(table).select("count", count="exact").execute()
            return result.count or 0
        except Exception:
            return 0

    def select_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ambil satu record dengan filter kolom=nilai."""
        query = self.client.table(table).select("*").limit(1)
        for key, value in filters.items():
            query = query.eq(key, value)
        try:
            result = query.execute()
            if result.data:
                return result.data[0]
        except Exception:
            pass
        return None

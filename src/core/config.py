"""Konfigurasi aplikasi dan pengaturan lingkungan."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.core.exceptions import SupabaseConfigError


@dataclass
class Settings:
    """Pengaturan aplikasi yang dimuat dari variabel lingkungan."""

    supabase_url: str
    supabase_service_role_key: str

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Settings":
        """Muat pengalaman dari file .env dan variabel lingkungan."""
        if env_file:
            load_dotenv(dotenv_path=env_file)
        else:
            load_dotenv()

        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

        if not url:
            raise SupabaseConfigError(
                "SUPABASE_URL tidak ditemukan. Salin .env.example ke .env dan isi kredensial."
            )
        if not key:
            raise SupabaseConfigError(
                "SUPABASE_SERVICE_ROLE_KEY tidak ditemukan. Salin .env.example ke .env dan isi kredensial."
            )

        return cls(supabase_url=url, supabase_service_role_key=key)

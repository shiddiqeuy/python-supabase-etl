"""Tests for core.config Settings loading."""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from src.core.config import Settings
from src.core.exceptions import SupabaseConfigError


class TestSettings(unittest.TestCase):
    @patch("src.core.config.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "fake-key",
        },
        clear=True,
    )
    def test_from_env_loads_from_env_vars(self, mock_load_dotenv):
        settings = Settings.from_env()
        self.assertEqual(settings.supabase_url, "https://example.supabase.co")
        self.assertEqual(settings.supabase_service_role_key, "fake-key")

    @patch("src.core.config.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "  https://example.supabase.co  ",
            "SUPABASE_SERVICE_ROLE_KEY": "  fake-key  ",
        },
        clear=True,
    )
    def test_from_env_strips_whitespace(self, mock_load_dotenv):
        settings = Settings.from_env()
        self.assertEqual(settings.supabase_url, "https://example.supabase.co")
        self.assertEqual(settings.supabase_service_role_key, "fake-key")

    @patch("src.core.config.load_dotenv")
    def test_from_env_loads_custom_env_file(self, mock_load_dotenv):
        with patch.dict(
            os.environ,
            {
                "SUPABASE_URL": "https://custom.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "custom-key",
            },
            clear=True,
        ):
            Settings.from_env(env_file=Path(".env.custom"))
        mock_load_dotenv.assert_called_once_with(dotenv_path=Path(".env.custom"))

    @patch("src.core.config.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "fake-key",
        },
        clear=True,
    )
    def test_from_env_loads_default_dotenv_when_no_file(self, mock_load_dotenv):
        Settings.from_env()
        mock_load_dotenv.assert_called_once_with()

    def test_settings_dataclass_fields(self):
        settings = Settings(
            supabase_url="https://example.supabase.co",
            supabase_service_role_key="key-123",
        )
        self.assertEqual(settings.supabase_url, "https://example.supabase.co")
        self.assertEqual(settings.supabase_service_role_key, "key-123")

    @patch("src.core.config.load_dotenv")
    @patch.dict(os.environ, {"SUPABASE_SERVICE_ROLE_KEY": "key-only"}, clear=True)
    def test_from_env_raises_when_url_missing(self, mock_load_dotenv):
        with self.assertRaises(SupabaseConfigError):
            Settings.from_env()

    @patch("src.core.config.load_dotenv")
    @patch.dict(os.environ, {"SUPABASE_URL": "https://x.co"}, clear=True)
    def test_from_env_raises_when_key_missing(self, mock_load_dotenv):
        with self.assertRaises(SupabaseConfigError):
            Settings.from_env()

    @patch("src.core.config.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_raises_when_both_missing(self, mock_load_dotenv):
        with self.assertRaises(SupabaseConfigError):
            Settings.from_env()

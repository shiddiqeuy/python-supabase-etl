"""Tests for CLI commands and argument parsing."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from src.cli.app import app
from src.cli.sales_command import app as sales_app
from src.cli.expense_command import app as expense_app


runner = CliRunner(mix_stderr=False)


class TestCliApp(unittest.TestCase):
    def test_app_help(self):
        result = runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("supabase-importer", result.output)

    def test_app_has_sales_command(self):
        result = runner.invoke(app, ["sales", "--help"])
        self.assertEqual(result.exit_code, 0)

    def test_app_has_expense_command(self):
        result = runner.invoke(app, ["expense", "--help"])
        self.assertEqual(result.exit_code, 0)


class TestSalesCommand(unittest.TestCase):
    @patch("src.cli.sales_command.SalesImporter")
    @patch("src.cli.sales_command.MasterDataCache")
    @patch("src.cli.sales_command.SupabaseRepository")
    @patch("src.cli.sales_command.Settings")
    def test_sales_import_invokes_importer(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx"])
        self.assertEqual(result.exit_code, 0)
        mock_importer.run.assert_called_once()

    @patch("src.cli.sales_command.Settings")
    def test_sales_import_handles_config_error(self, mock_settings_cls):
        mock_settings_cls.from_env.side_effect = Exception("Config missing")
        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx"])
        self.assertNotEqual(result.exit_code, 0)

    @patch("src.cli.sales_command.SalesImporter")
    @patch("src.cli.sales_command.MasterDataCache")
    @patch("src.cli.sales_command.SupabaseRepository")
    @patch("src.cli.sales_command.Settings")
    def test_sales_import_dry_run_flag(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx", "--dry-run"])
        self.assertEqual(result.exit_code, 0)
        _, kwargs = mock_importer.run.call_args
        self.assertTrue(kwargs["dry_run"])

    @patch("src.cli.sales_command.SalesImporter")
    @patch("src.cli.sales_command.MasterDataCache")
    @patch("src.cli.sales_command.SupabaseRepository")
    @patch("src.cli.sales_command.Settings")
    def test_sales_import_batch_size_option(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx", "--batch-size", "50"])
        self.assertEqual(result.exit_code, 0)
        _, kwargs = mock_importer.run.call_args
        self.assertEqual(kwargs["batch_size"], 50)

    @patch("src.cli.sales_command.SalesImporter")
    @patch("src.cli.sales_command.MasterDataCache")
    @patch("src.cli.sales_command.SupabaseRepository")
    @patch("src.cli.sales_command.Settings")
    def test_sales_import_verbose_flag(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx", "--verbose"])
        self.assertEqual(result.exit_code, 0)
        _, kwargs = mock_importer.run.call_args
        self.assertTrue(kwargs["verbose"])

    @patch("src.cli.sales_command.SalesImporter")
    @patch("src.cli.sales_command.MasterDataCache")
    @patch("src.cli.sales_command.SupabaseRepository")
    @patch("src.cli.sales_command.Settings")
    def test_sales_import_exits_on_errors(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=3)

        result = runner.invoke(app, ["sales", "import-data", "dummy.xlsx"])
        self.assertEqual(result.exit_code, 1)


class TestExpenseCommand(unittest.TestCase):
    @patch("src.cli.expense_command.ExpenseImporter")
    @patch("src.cli.expense_command.MasterDataCache")
    @patch("src.cli.expense_command.SupabaseRepository")
    @patch("src.cli.expense_command.Settings")
    def test_expense_import_invokes_importer(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["expense", "import-expense", "dummy.csv"])
        self.assertEqual(result.exit_code, 0)
        mock_importer.run.assert_called_once()

    @patch("src.cli.expense_command.ExpenseImporter")
    @patch("src.cli.expense_command.MasterDataCache")
    @patch("src.cli.expense_command.SupabaseRepository")
    @patch("src.cli.expense_command.Settings")
    def test_expense_import_sheet_option(
        self, mock_settings_cls, mock_repo_cls, mock_cache_cls, mock_importer_cls
    ):
        mock_settings = MagicMock()
        mock_settings_cls.from_env.return_value = mock_settings
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache
        mock_importer = MagicMock()
        mock_importer_cls.return_value = mock_importer
        mock_importer.run.return_value = MagicMock(errors=0)

        result = runner.invoke(app, ["expense", "import-expense", "dummy.xlsx", "--sheet", "Data"])
        self.assertEqual(result.exit_code, 0)
        args, kwargs = mock_importer.run.call_args
        self.assertEqual(args[0].sheet_name, "Data")


if __name__ == "__main__":
    unittest.main()
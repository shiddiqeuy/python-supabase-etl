"""CLI command untuk impor data pengeluaran."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from src.core.config import Settings
from src.core.exceptions import SupabaseImporterError
from src.importers.expense_importer import ExpenseImporter
from src.repositories.master_data_cache import MasterDataCache
from src.repositories.supabase_repository import SupabaseRepository
from src.utils.messages import BANNER_EXPENSE
from src.utils.progress import run_progress

app = typer.Typer(name="expense", help="Impor data pengeluaran keuangan")
console = Console()


@app.command()
def import_expense(
    file_path: str = typer.Argument(..., help="Path ke file Excel (.xlsx) atau CSV yang akan diimpor"),
    sheet: Optional[str] = typer.Option(None, "--sheet", "-s", help="Nama sheet untuk file Excel (default: sheet pertama)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validasi data tanpa memasukkan ke database"),
    batch_size: int = typer.Option(100, "--batch-size", "-b", help="Ukuran batch untuk pengelompokan operasi database"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Aktifkan output verbose untuk debugging"),
):
    """Impor data pengeluaran keuangan ke tabel Supabase yang dinormalisasi."""
    from src.core.models import FileSource
    from src.cli.interactive_prompts import print_banner_sales

    console.print(Panel(BANNER_EXPENSE, border_style="cyan", padding=(0, 1)))

    try:
        settings = Settings.from_env()
    except SupabaseImporterError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)

    repository = SupabaseRepository(settings)
    cache = MasterDataCache(repository)
    importer = ExpenseImporter(repository, cache)

    source = FileSource(path=Path(file_path), sheet_name=sheet)
    result = importer.run(source, dry_run=dry_run, batch_size=batch_size, verbose=verbose)

    if result.errors > 0:
        raise typer.Exit(1)

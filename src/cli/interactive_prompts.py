"""Fungsi-fungsi interaktif untuk menu Bahasa Indonesia."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.core.config import Settings
from src.core.exceptions import SupabaseImporterError
from src.repositories.supabase_repository import SupabaseRepository
from src.utils.messages import (
    BANNER_SALES,
    CONNECTION_FAILED,
    CONNECTION_SUCCESS,
    MENU_ITEMS,
    MSG_FILE_NOT_FOUND,
    PROMPT_BATCH_SIZE,
    PROMPT_DRY_RUN,
    PROMPT_FILE_PATH,
    PROMPT_SHEET,
    PROMPT_VERBOSE,
)

console = Console()


def print_banner_sales() -> None:
    console.print(Panel(BANNER_SALES, border_style="cyan", padding=(0, 1)))


def print_menu() -> None:
    print_banner_sales()
    table = Table(show_header=False, border_style="cyan", padding=(0, 2))
    table.add_column("No", style="bold cyan", width=6, justify="center")
    table.add_column("Menu", style="bold white", width=50)

    for no, text in MENU_ITEMS:
        table.add_row(no, text)

    console.print(table)


def get_user_choice(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            choice = typer.prompt(prompt, type=int)
            if min_val <= choice <= max_val:
                return choice
            console.print(f"[red]Pilihan harus antara {min_val} dan {max_val}[/red]")
        except typer.Abort:
            console.print("\n[yellow]Dibatalkan oleh pengguna.[/yellow]")
            raise typer.Exit(0)
        except ValueError:
            console.print("[red]Masukkan angka yang valid[/red]")


def get_file_path() -> str:
    while True:
        try:
            file_path = typer.prompt(PROMPT_FILE_PATH)
            path = Path(file_path)
            if path.exists() and path.suffix.lower() in [".xlsx", ".csv"]:
                return str(path)
            console.print(MSG_FILE_NOT_FOUND)
        except typer.Abort:
            console.print("\n[yellow]Dibatalkan oleh pengguna.[/yellow]")
            raise typer.Exit(0)


def get_sheet_name(file_path: str) -> Optional[str]:
    if file_path.lower().endswith(".csv"):
        return None

    try:
        excel_file = typer.prompt(f"File Excel. {PROMPT_SHEET}", default="")
        if not excel_file:
            return None
        return excel_file
    except typer.Abort:
        raise typer.Exit(0)
    except Exception as exc:
        console.print(f"[yellow]Tidak dapat membaca sheet: {exc}. Menggunakan sheet pertama.[/yellow]")
        return None


def get_batch_size() -> int:
    try:
        batch_size = typer.prompt(PROMPT_BATCH_SIZE, default=100, type=int)
        return max(1, batch_size)
    except typer.Abort:
        raise typer.Exit(0)


def get_dry_run_choice() -> bool:
    try:
        return typer.confirm(PROMPT_DRY_RUN, default=False)
    except typer.Abort:
        raise typer.Exit(0)


def get_verbose_choice() -> bool:
    try:
        return typer.confirm(PROMPT_VERBOSE, default=False)
    except typer.Abort:
        raise typer.Exit(0)


def print_environment_details(settings: Settings) -> None:
    table = Table(title="Detail Environment", show_header=True, border_style="blue", padding=(0, 1))
    table.add_column("Property", style="bold cyan", width=25)
    table.add_column("Value", style="bold white", width=50)

    from datetime import datetime
    import platform

    table.add_row("Waktu", datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"))
    table.add_row("Direktori Kerja", str(Path.cwd()))
    table.add_row("Python Version", platform.python_version())
    table.add_row("Sistem Operasi", f"{platform.system()} {platform.release()}")
    table.add_row("Machine", platform.machine())

    url = settings.supabase_url
    if url.startswith("https://"):
        parts = url.split(".")
        masked = f"{parts[0]}.***" if len(parts) > 1 else "***"
    else:
        masked = url
    table.add_row("Supabase URL", masked)
    table.add_row("Service Role Key", "***Diatur***" if settings.supabase_service_role_key else "Tidak diatur")

    console.print(table)


def check_supabase_connection(settings: Settings) -> None:
    console.print("\n[bold cyan]═══ Pemeriksaan Koneksi Supabase ═══[/bold cyan]\n")
    print_environment_details(settings)
    console.print()

    repository = SupabaseRepository(settings)
    try:
        with console.status("[bold green]Menghubungkan ke Supabase...", spinner="dots"):
            if repository.test_connection():
                console.print(CONNECTION_SUCCESS)
            else:
                console.print(CONNECTION_FAILED)
    except SupabaseImporterError as exc:
        console.print(f"[red]{CONNECTION_FAILED}: {exc}[/red]\n")

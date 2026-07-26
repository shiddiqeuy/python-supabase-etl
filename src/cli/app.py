"""Typer app dan registrasi command."""

import typer
from rich.console import Console

from src.cli.sales_command import app as sales_app
from src.cli.expense_command import app as expense_app

console = Console()
app = typer.Typer(
    name="supabase-importer",
    help="Impor data Excel/CSV berformat lebar ke tabel Supabase yang dinormalisasi",
    add_completion=False,
)

app.add_typer(sales_app, name="sales", help="Impor data penjualan/invoice")
app.add_typer(expense_app, name="expense", help="Impor data pengeluaran")

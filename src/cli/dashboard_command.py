"""CLI Typer commands untuk Sales Dashboard."""

from typing import Optional
import typer
from rich import box
from rich.console import Console
from rich.table import Table

from src.repositories.dashboard_repository import DashboardRepository
from src.reports.filter import apply_filters
from src.reports.exporter import export_csv, export_xlsx
from src.reports import reports

console = Console()
app = typer.Typer(name="dashboard", help="Fitur Sales Dashboard CLI")


def _get_data():
    repo = DashboardRepository()
    return repo.get_invoices_df(), repo.get_invoice_items_df()


@app.command("summary")
def summary_cmd(
    date_from: Optional[str] = typer.Option(None, "--from", help="Tanggal awal (YYYY-MM-DD)"),
    date_to: Optional[str] = typer.Option(None, "--to", help="Tanggal akhir (YYYY-MM-DD)"),
    customer: Optional[str] = typer.Option(None, "--customer", help="Filter customer"),
    product: Optional[str] = typer.Option(None, "--product", help="Filter produk"),
    sales: Optional[str] = typer.Option(None, "--sales", help="Filter sales person"),
    status: Optional[str] = typer.Option(None, "--status", help="Filter status (lunas|belum_lunas|sebagian)"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount", help="Minimum omzet"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount", help="Maksimum omzet"),
    export: Optional[str] = typer.Option(None, "--export", help="Ekspor hasil (csv|xlsx)"),
):
    """Tampilkan ringkasan penjualan (omzet, COGS, margin)."""
    df_inv, df_itm = _get_data()
    df_inv_filtered, _ = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )

    res = reports.summary(df_inv_filtered)

    table = Table(title="Ringkasan Penjualan Periode", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("Metrik", style="bold cyan", width=25)
    table.add_column("Nilai", justify="right", style="bold white", width=20)

    table.add_row("Total Omzet", f"Rp{res['total_omzet']:,.2f}")
    table.add_row("Total COGS", f"Rp{res['total_cogs']:,.2f}")
    table.add_row("Total Margin", f"Rp{res['total_margin']:,.2f}")
    table.add_row("Margin %", f"{res['margin_pct']:.2f}%")
    table.add_row("Rata-rata Invoice", f"Rp{res['avg_invoice']:,.2f}")
    table.add_row("Total Invoice", str(res['total_invoices']))

    console.print(table)

    if export:
        import pandas as pd
        df_res = pd.DataFrame([res])
        if export.lower() == "csv":
            path = export_csv(df_res, "reports/summary.csv")
            console.print(f"[green]File CSV berhasil dibuat di: {path}[/green]")
        elif export.lower() == "xlsx":
            path = export_xlsx(df_res, "reports/summary.xlsx")
            console.print(f"[green]File Excel berhasil dibuat di: {path}[/green]")


@app.command("by-sales")
def by_sales_cmd(
    date_from: Optional[str] = typer.Option(None, "--from"),
    date_to: Optional[str] = typer.Option(None, "--to"),
    customer: Optional[str] = typer.Option(None, "--customer"),
    product: Optional[str] = typer.Option(None, "--product"),
    sales: Optional[str] = typer.Option(None, "--sales"),
    status: Optional[str] = typer.Option(None, "--status"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount"),
):
    """Tampilkan performa per Sales Person."""
    df_inv, df_itm = _get_data()
    df_inv_f, _ = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )
    res = reports.by_sales(df_inv_f)

    table = Table(title="Performa Sales Person", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("Sales Person", style="cyan", width=25)
    table.add_column("Omzet", justify="right", style="green", width=18)
    table.add_column("COGS", justify="right", style="yellow", width=18)
    table.add_column("Margin", justify="right", style="magenta", width=18)
    table.add_column("Invoice", justify="center", style="white", width=10)

    for _, row in res.iterrows():
        table.add_row(
            str(row["sales_name"]),
            f"Rp{row['total_omzet']:,.2f}",
            f"Rp{row['total_cogs']:,.2f}",
            f"Rp{row['margin']:,.2f}",
            str(row["total_invoices"]),
        )
    console.print(table)


@app.command("by-product")
def by_product_cmd(
    date_from: Optional[str] = typer.Option(None, "--from"),
    date_to: Optional[str] = typer.Option(None, "--to"),
    customer: Optional[str] = typer.Option(None, "--customer"),
    product: Optional[str] = typer.Option(None, "--product"),
    sales: Optional[str] = typer.Option(None, "--sales"),
    status: Optional[str] = typer.Option(None, "--status"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount"),
):
    """Tampilkan performa per Produk."""
    df_inv, df_itm = _get_data()
    _, df_itm_f = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )
    res = reports.by_product(df_itm_f)

    table = Table(title="Performa Produk", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("Produk", style="cyan", width=25)
    table.add_column("Qty", justify="center", style="white", width=10)
    table.add_column("Omzet", justify="right", style="green", width=18)
    table.add_column("COGS", justify="right", style="yellow", width=18)
    table.add_column("Margin", justify="right", style="magenta", width=18)

    for _, row in res.iterrows():
        table.add_row(
            str(row["product_name"]),
            f"{row['qty']:.0f}",
            f"Rp{row['total_omzet']:,.2f}",
            f"Rp{row['total_cogs']:,.2f}",
            f"Rp{row['margin']:,.2f}",
        )
    console.print(table)


@app.command("by-customer")
def by_customer_cmd(
    date_from: Optional[str] = typer.Option(None, "--from"),
    date_to: Optional[str] = typer.Option(None, "--to"),
    customer: Optional[str] = typer.Option(None, "--customer"),
    product: Optional[str] = typer.Option(None, "--product"),
    sales: Optional[str] = typer.Option(None, "--sales"),
    status: Optional[str] = typer.Option(None, "--status"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount"),
):
    """Tampilkan performa per Customer."""
    df_inv, df_itm = _get_data()
    df_inv_f, _ = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )
    res = reports.by_customer(df_inv_f)

    table = Table(title="Performa Customer", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("Customer", style="cyan", width=25)
    table.add_column("Omzet", justify="right", style="green", width=18)
    table.add_column("Outstanding Piutang", justify="right", style="red", width=20)
    table.add_column("Invoice", justify="center", style="white", width=10)

    for _, row in res.iterrows():
        table.add_row(
            str(row["customer_name"]),
            f"Rp{row['total_omzet']:,.2f}",
            f"Rp{row['sisa_tagihan']:,.2f}",
            str(row["total_invoices"]),
        )
    console.print(table)


@app.command("payment-status")
def payment_status_cmd(
    date_from: Optional[str] = typer.Option(None, "--from"),
    date_to: Optional[str] = typer.Option(None, "--to"),
    customer: Optional[str] = typer.Option(None, "--customer"),
    product: Optional[str] = typer.Option(None, "--product"),
    sales: Optional[str] = typer.Option(None, "--sales"),
    status: Optional[str] = typer.Option(None, "--status"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount"),
):
    """Tampilkan status pembayaran (piutang)."""
    df_inv, df_itm = _get_data()
    df_inv_f, _ = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )
    res = reports.payment_status(df_inv_f, status_filter=status)

    table = Table(title="Status Pembayaran (Piutang)", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("No. Invoice", style="cyan", width=20)
    table.add_column("Tanggal", style="white", width=12)
    table.add_column("Customer", style="magenta", width=20)
    table.add_column("Tagihan", justify="right", style="yellow", width=15)
    table.add_column("Sisa Tagihan", justify="right", style="red", width=15)
    table.add_column("Status", justify="center", style="green", width=12)

    for _, row in res.iterrows():
        table.add_row(
            str(row["no_invoice"]),
            str(row["tanggal"]),
            str(row["customer_name"]),
            f"Rp{row['jumlah_tagihan']:,.2f}",
            f"Rp{row['sisa_tagihan']:,.2f}",
            str(row["status_pembayaran"]),
        )
    console.print(table)


@app.command("trend")
def trend_cmd(
    interval: str = typer.Option("monthly", "--interval", "-i", help="Interval (daily|weekly|monthly)"),
    date_from: Optional[str] = typer.Option(None, "--from"),
    date_to: Optional[str] = typer.Option(None, "--to"),
    customer: Optional[str] = typer.Option(None, "--customer"),
    product: Optional[str] = typer.Option(None, "--product"),
    sales: Optional[str] = typer.Option(None, "--sales"),
    status: Optional[str] = typer.Option(None, "--status"),
    min_amount: Optional[float] = typer.Option(None, "--min-amount"),
    max_amount: Optional[float] = typer.Option(None, "--max-amount"),
):
    """Tampilkan tren penjualan (Grafik/Tabel)."""
    df_inv, df_itm = _get_data()
    df_inv_f, _ = apply_filters(
        df_inv, df_itm, customer, product, sales, status, min_amount, max_amount, date_from, date_to
    )
    res = reports.trend(df_inv_f, interval=interval)

    table = Table(title=f"Tren Penjualan ({interval.capitalize()})", show_header=True, border_style="cyan", box=box.ASCII)
    table.add_column("Periode", style="cyan", width=15)
    table.add_column("Omzet", justify="right", style="green", width=20)
    table.add_column("Jumlah Invoice", justify="center", style="white", width=15)

    for _, row in res.iterrows():
        table.add_row(
            str(row["periode"]),
            f"Rp{row['total_omzet']:,.2f}",
            str(row["total_invoices"]),
        )
    console.print(table)

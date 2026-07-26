"""Importer untuk data Penjualan/Invoice."""

from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.core.models import Invoice, InvoiceItem, ImportResult
from src.core.interfaces import DataRepository, MasterDataCache
from src.importers.base_importer import BaseImporter
from src.utils.messages import BANNER_SALES, SUMMARY_LABELS

console = Console()

MAX_PRODUCTS = 16


class SalesImporter(BaseImporter):
    """Importer khusus untuk data penjualan/invoice."""

    def __init__(self, repository: DataRepository, cache: MasterDataCache) -> None:
        super().__init__(repository, cache)
        self._show_total_amount = False

    def transform_record(self, row: pd.Series) -> Optional[Invoice]:
        no_invoice = str(row.get("No. Invoice", "")).strip()
        if not no_invoice or no_invoice.lower() == "nan":
            return None

        tanggal = row.get("Tanggal")
        if pd.isna(tanggal):
            tanggal = None
        elif hasattr(tanggal, "strftime"):
            tanggal = tanggal.strftime("%Y-%m-%d")
        else:
            tanggal = str(tanggal)

        products: List[InvoiceItem] = []
        for i in range(1, MAX_PRODUCTS + 1):
            produk = str(row.get(f"Produk {i}", "")).strip()
            if not produk or produk.lower() == "nan":
                continue
            qty = self._safe_float(row.get(f"Qty {i}", 0))
            harga = self._safe_float(row.get(f"Harga {i}", 0))
            cogs = self._safe_float(row.get(f"COGS {i}", 0))
            products.append(InvoiceItem(produk=produk, qty=qty, harga=harga, cogs=cogs))

        if not products:
            return None

        return Invoice(
            no_invoice=no_invoice,
            tanggal=tanggal,
            customer_name=str(row.get("Nama Customer", "")).strip(),
            sales_name=str(row.get("Sales", "")).strip(),
            discount=self._safe_float(row.get("Discount", 0)),
            ongkir=self._safe_float(row.get("Ongkir", 0)),
            jumlah_tagihan=self._safe_float(row.get("Jumlah Tagihan", 0)),
            total_cogs=self._safe_float(row.get("Total COGS", 0)),
            down_payment=self._safe_float(row.get("Down Payment", 0)),
            sisa_tagihan=self._safe_float(row.get("Sisa Tagihan", 0)),
            keterangan=str(row.get("Keterangan", "")).strip(),
            catatan=str(row.get("Catatan", "")).strip(),
            bukti_transfer=str(row.get("Bukti Transfer", "")).strip(),
            products=products,
        )

    def validate(self, record: Invoice, index: int) -> Optional[str]:
        if self._repository.select_one("invoices", {"no_invoice": record.no_invoice}):
            return "Nomor invoice duplikat"
        return None

    def _build_error_row(self, index: int, record: Invoice, error: str) -> Dict[str, Any]:
        return {
            "baris": index,
            "no_invoice": record.no_invoice,
            "error": error,
            "pelanggan": record.customer_name,
            "total": record.jumlah_tagihan,
        }

    def _insert_record(self, record: Invoice) -> int:
        customer_id = self._cache.resolve_id("customers", record.customer_name)
        sales_person_id = self._cache.resolve_id("sales_persons", record.sales_name)

        invoice_data = {
            "no_invoice": record.no_invoice,
            "tanggal": record.tanggal,
            "customer_id": customer_id,
            "sales_person_id": sales_person_id,
            "discount": record.discount,
            "ongkir": record.ongkir,
            "jumlah_tagihan": record.jumlah_tagihan,
            "total_cogs": record.total_cogs,
            "down_payment": record.down_payment,
            "sisa_tagihan": record.sisa_tagihan,
            "keterangan": record.keterangan,
            "catatan": record.catatan,
            "bukti_transfer": record.bukti_transfer,
        }
        return self._repository.insert_record("invoices", invoice_data, id_column="invoice_id")

    def _insert_relations(self, record: Invoice, invoice_id: int) -> None:
        items = []
        for product in record.products:
            try:
                product_id = self._cache.resolve_id("products", product.produk)
                items.append({
                    "invoice_id": invoice_id,
                    "product_id": product_id,
                    "qty": product.qty,
                    "harga": product.harga,
                    "cogs": product.cogs,
                })
            except Exception as exc:
                console.print(
                    f"[yellow]Peringatan: Gagal menyelesaikan produk '{product.produk}': {exc}[/yellow]"
                )
        if items:
            self._repository.insert_batch("invoice_items", items)

    def get_error_prefix(self) -> str:
        return "error_log"

    def _print_preview(self, records: List[Invoice]) -> None:
        from rich import box
        table = Table(
            title=f"Pratinjau Top 5 Data Pertama (dari {len(records)} Record)",
            show_header=True,
            show_lines=False,
            box=box.ASCII,
        )
        table.add_column("No. Invoice", style="cyan", width=25)
        table.add_column("Pelanggan", style="magenta", width=30)
        table.add_column("Produk", justify="center", style="green", width=10)
        table.add_column("Total", justify="right", style="yellow", width=15)

        for inv in records[:5]:
            table.add_row(
                inv.no_invoice,
                inv.customer_name,
                str(len(inv.products)),
                f"Rp{inv.jumlah_tagihan:,.2f}",
            )

        console.print(table)
        console.print(f"\n[green]Dry run selesai. Akan memproses {len(records)} invoice.[/green]")

    def _print_summary(
        self,
        stats: Dict[str, int],
        duration: float,
        error_file: str,
        total_amount: float,
    ) -> None:
        table = Table(title="Ringkasan Impor", show_header=True, border_style="cyan")
        table.add_column("Metrik", style="bold cyan", width=25)
        table.add_column("Nilai", justify="right", style="bold white", width=15)

        table.add_row(SUMMARY_LABELS["total"], str(stats.get("total", 0)))
        table.add_row(SUMMARY_LABELS["success"], f"[green]{stats['success']}[/green]")
        table.add_row(SUMMARY_LABELS["skipped"], f"[yellow]{stats['skipped']}[/yellow]")
        table.add_row(SUMMARY_LABELS["errors"], f"[red]{stats['errors']}[/red]")
        table.add_row(SUMMARY_LABELS["duration"], f"{duration:.2f} detik")

        console.print(table)

        if error_file:
            console.print(f"\n[yellow]{stats['errors']} error terjadi. Log error disimpan di: {error_file}[/yellow]")
        else:
            console.print("\n[green]+ Impor selesai tanpa error![/green]")

    def _get_amount(self, record: Invoice) -> float:
        return record.jumlah_tagihan

    @staticmethod
    def _safe_float(value: Any) -> float:
        if pd.isna(value):
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

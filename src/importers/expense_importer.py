"""Importer untuk data Pengeluaran."""

from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

from src.core.models import ExpenseRecord, ImportResult
from src.core.interfaces import DataRepository, MasterDataCache
from src.importers.base_importer import BaseImporter
from src.utils.messages import BANNER_EXPENSE, SUMMARY_LABELS

console = Console()


class ExpenseImporter(BaseImporter):
    """Importer khusus untuk data pengeluaran."""

    def __init__(self, repository: DataRepository, cache: MasterDataCache) -> None:
        super().__init__(repository, cache)
        self._show_total_amount = True

    def transform_record(self, row: pd.Series) -> Optional[ExpenseRecord]:
        coa3 = str(row.get("COA 3", "")).strip()
        coa2 = str(row.get("COA 2", "")).strip()
        coa1 = str(row.get("COA", "")).strip()

        selected_coa = ""
        selected_level = 0
        if coa3 and coa3.lower() != "nan":
            selected_coa = coa3
            selected_level = 3
        elif coa2 and coa2.lower() != "nan":
            selected_coa = coa2
            selected_level = 2
        elif coa1 and coa1.lower() != "nan":
            selected_coa = coa1
            selected_level = 1
        else:
            return None

        kode_coa, nama_coa = self._parse_coa(selected_coa)

        kategori = str(row.get("Kategori", "")).strip()
        pengeluaran = str(row.get("Pengeluaran", "")).strip()
        deskripsi = str(row.get("Deskripsi", "")).strip()
        bukti_tf = str(row.get("Bukti Tf", "")).strip()

        tanggal = row.get("Tanggal")
        if pd.isna(tanggal):
            tanggal_str = None
        elif hasattr(tanggal, "strftime"):
            tanggal_str = tanggal.strftime("%Y-%m-%d")
        else:
            tanggal_str = str(tanggal)

        jumlah = row.get("Jumlah")
        try:
            jumlah_float = float(jumlah) if not pd.isna(jumlah) else 0.0
        except (ValueError, TypeError):
            jumlah_float = 0.0

        return ExpenseRecord(
            tanggal=tanggal_str,
            kode_coa=kode_coa,
            nama_coa=nama_coa,
            coa_level=selected_level,
            kategori=kategori,
            nama_pengeluaran=pengeluaran,
            deskripsi=deskripsi,
            jumlah=jumlah_float,
            bukti_tf=bukti_tf,
        )

    def validate(self, record: ExpenseRecord, index: int) -> Optional[str]:
        if not record.tanggal or not record.kode_coa:
            return "Data tidak lengkap (tanggal/COA kosong)"
        return None

    def _build_error_row(self, index: int, record: ExpenseRecord, error: str) -> Dict[str, Any]:
        return {
            "baris": index,
            "tanggal": record.tanggal,
            "coa": record.kode_coa,
            "kategori": record.kategori,
            "pengeluaran": record.nama_pengeluaran,
            "jumlah": record.jumlah,
            "error": error,
        }

    def _insert_record(self, record: ExpenseRecord) -> int:
        coa_id = self._cache.resolve_id(
            "coa", record.kode_coa, extra_fields={"nama_coa": record.nama_coa, "level": record.coa_level}
        )
        kategori_id = self._cache.resolve_id(
            "kategori_pengeluaran", record.kategori
        )

        expense_data = {
            "tanggal": record.tanggal,
            "coa_id": coa_id,
            "kategori_id": kategori_id,
            "nama_pengeluaran": record.nama_pengeluaran,
            "deskripsi": record.deskripsi,
            "jumlah": record.jumlah,
            "bukti_tf": record.bukti_tf,
            "created_at": pd.Timestamp.now().isoformat(),
        }
        return self._repository.insert_record("pengeluaran", expense_data, id_column="pengeluaran_id")

    def get_error_prefix(self) -> str:
        return "error_expense_log"

    def _print_preview(self, records: List[ExpenseRecord]) -> None:
        from rich import box
        table = Table(
            title=f"Pratinjau Top 5 Data Pertama (dari {len(records)} Record)",
            show_header=True,
            show_lines=False,
            box=box.ASCII,
        )
        table.add_column("Tanggal", style="cyan", width=12)
        table.add_column("COA", style="magenta", width=20)
        table.add_column("Kategori", style="green", width=20)
        table.add_column("Pengeluaran", style="yellow", width=25)
        table.add_column("Jumlah", justify="right", style="red", width=15)

        for rec in records[:5]:
            table.add_row(
                str(rec.tanggal),
                rec.kode_coa,
                rec.kategori,
                rec.nama_pengeluaran,
                f"Rp{rec.jumlah:,.2f}",
            )

        console.print(table)
        console.print(f"\n[green]Dry run selesai. Akan memproses {len(records)} pengeluaran.[/green]")

    def _print_summary(
        self,
        stats: Dict[str, int],
        duration: float,
        error_file: str,
        total_amount: float,
    ) -> None:
        table = Table(title="Ringkasan Impor Pengeluaran", show_header=True, border_style="cyan")
        table.add_column("Metrik", style="bold cyan", width=30)
        table.add_column("Nilai", justify="right", style="bold white", width=20)

        table.add_row(SUMMARY_LABELS["total"], str(stats.get("total", 0)))
        table.add_row(SUMMARY_LABELS["success"], f"[green]{stats['success']}[/green]")
        table.add_row(SUMMARY_LABELS["skipped"], f"[yellow]{stats['skipped']}[/yellow]")
        table.add_row(SUMMARY_LABELS["errors"], f"[red]{stats['errors']}[/red]")
        table.add_row(SUMMARY_LABELS["total_amount"], f"Rp {total_amount:,.2f}")
        table.add_row(SUMMARY_LABELS["duration"], f"{duration:.2f} detik")

        console.print(table)

        if error_file:
            console.print(f"\n[yellow]{stats['errors']} error terjadi. Log error disimpan di: {error_file}[/yellow]")
        else:
            console.print("\n[green]+ Impor pengeluaran selesai tanpa error![/green]")

    def _get_amount(self, record: ExpenseRecord) -> float:
        return record.jumlah

    @staticmethod
    def _parse_coa(value: str) -> tuple[str, str]:
        if pd.isna(value):
            return ("", "")
        value = str(value).strip()
        if not value or value.lower() == "nan":
            return ("", "")
        if " - " in value:
            parts = value.split(" - ", 1)
            return (parts[0].strip(), parts[1].strip())
        return (value, value)

"""Base importer dengan logika ETL generik."""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console

from src.core.models import FileSource, ImportResult
from src.core.interfaces import DataRepository, MasterDataCache
from src.readers.excel_reader import ExcelReader
from src.utils.logger import save_error_log
from src.utils.messages import (
    DRY_RUN_LABEL,
    MSG_NO_DATA,
    SUMMARY_LABELS,
    ERROR_FILE_LABEL,
    SUCCESS_LABEL,
)
from src.utils.progress import run_progress


console = Console()


class BaseImporter:
    """
    Base class untuk semua importer.
    Menggunakan Template Method pattern untuk menghindari duplikasi ETL.
    """

    def __init__(
        self,
        repository: DataRepository,
        cache: MasterDataCache,
    ) -> None:
        self._repository = repository
        self._cache = cache

    @abstractmethod
    def transform_record(self, row: pd.Series) -> Optional[Any]:
        """Transform satu baris DataFrame menjadi model bisnis."""
        ...

    @abstractmethod
    def validate(self, record: Any, index: int) -> Optional[str]:
        """
        Validasi record sebelum insert.
        Return pesan error jika tidak valid, None jika valid.
        """
        ...

    @abstractmethod
    def _build_error_row(self, index: int, record: Any, error: str) -> Dict[str, Any]:
        """Bangun dictionary baris error untuk log CSV."""
        ...

    @abstractmethod
    def _insert_record(self, record: Any) -> int:
        """Insert record utama ke database, return ID."""
        ...

    def _insert_relations(self, record: Any, record_id: int) -> None:
        """Insert data relasi tambahan (override di subclass jika diperlukan)."""
        pass

    @abstractmethod
    def get_error_prefix(self) -> str:
        """Prefix untuk nama file error log."""
        ...

    def _transform_dataframe(self, df: pd.DataFrame) -> List[Any]:
        """Transform seluruh DataFrame menjadi daftar model bisnis."""
        records: List[Any] = []
        for _, row in df.iterrows():
            try:
                record = self.transform_record(row)
                if record is not None:
                    records.append(record)
            except Exception as exc:
                console.print(f"[yellow]Peringatan: Gagal transformasi baris: {exc}[/yellow]")
        return records

    def _get_amount(self, record: Any) -> float:
        return 0.0

    def run(
        self,
        source: FileSource,
        dry_run: bool = False,
        batch_size: int = 100,
        verbose: bool = False,
    ) -> ImportResult:
        """
        Jalankan pipeline impor end-to-end.
        """
        start_time = time.time()
        stats = {"success": 0, "skipped": 0, "errors": 0}
        error_rows: List[Dict[str, Any]] = []
        amounts: List[float] = []

        console.print("[cyan]Memeriksa koneksi Supabase...[/cyan]")
        if self._repository.test_connection():
            console.print("[bold green]+ Status Koneksi Supabase: Terhubung (OK)[/bold green]\n")
        else:
            console.print("[bold red]- Status Koneksi Supabase: Gagal / Offline![/bold red]")

        df = ExcelReader.read(str(source.path), source.sheet_name)
        console.print(f"[green]+ Memuat {len(df)} baris dari {source.path}[/green]")

        records = self._transform_dataframe(df)
        console.print(f"[green]+ Mentransformasi {len(records)} record yang valid[/green]")

        if not records:
            console.print(f"[yellow]{MSG_NO_DATA}[/yellow]")
            return ImportResult(
                total=0,
                success=0,
                skipped=0,
                errors=0,
                total_amount=0.0,
                duration=time.time() - start_time,
            )

        if dry_run:
            console.print(f"\n[yellow]{DRY_RUN_LABEL}[/yellow]\n")
            self._print_preview(records)
            return ImportResult(
                total=len(records),
                success=0,
                skipped=0,
                errors=0,
                total_amount=0.0,
                duration=time.time() - start_time,
            )

        def _process(record: Any, index: int) -> None:
            try:
                validation_error = self.validate(record, index)
                if validation_error:
                    stats["skipped"] += 1
                    error_rows.append(self._build_error_row(index, record, validation_error))
                    return

                record_id = self._insert_record(record)
                try:
                    self._insert_relations(record, record_id)
                except Exception as exc:
                    console.print(
                        f"[yellow]Peringatan: Gagal insert relasi untuk record {index}: {exc}[/yellow]"
                    )

                stats["success"] += 1
                amounts.append(self._get_amount(record))

            except Exception as exc:
                error_msg = str(exc)
                stats["errors"] += 1
                error_rows.append(self._build_error_row(index, record, error_msg))

                if verbose:
                    console.print(f"[red]Error memproses baris {index}: {error_msg}[/red]")

        run_progress(
            total=len(records),
            description="[bold green]Memproses record...",
            items=records,
            process_fn=_process,
            console=console,
        )

        duration = time.time() - start_time
        error_file = save_error_log(error_rows, prefix=self.get_error_prefix()) if error_rows else ""

        console.print()
        self._print_summary(stats, duration, error_file, sum(amounts))

        return ImportResult(
            total=len(records),
            success=stats["success"],
            skipped=stats["skipped"],
            errors=stats["errors"],
            total_amount=sum(amounts),
            duration=duration,
            error_file=error_file,
        )

    def _print_preview(self, records: List[Any]) -> None:
        """Tampilkan preview 10 record pertama. Override di subclass."""
        console.print(f"[cyan]Total record yang akan diproses: {len(records)}[/cyan]")

    def _print_summary(
        self,
        stats: Dict[str, int],
        duration: float,
        error_file: str,
        total_amount: float,
    ) -> None:
        """Tampilkan ringkasan impor. Override di subclass jika perlu format khusus."""
        from rich import box
        from rich.table import Table

        table = Table(title="Ringkasan Impor", show_header=True, border_style="cyan", box=box.ASCII)
        table.add_column("Metrik", style="bold cyan", width=30)
        table.add_column("Nilai", justify="right", style="bold white", width=20)

        table.add_row(SUMMARY_LABELS["total"], str(stats.get("total", 0)))
        table.add_row(SUMMARY_LABELS["success"], f"[green]{stats['success']}[/green]")
        table.add_row(SUMMARY_LABELS["skipped"], f"[yellow]{stats['skipped']}[/yellow]")
        table.add_row(SUMMARY_LABELS["errors"], f"[red]{stats['errors']}[/red]")
        table.add_row(SUMMARY_LABELS["duration"], f"{duration:.2f} detik")

        console.print(table)

        if error_file:
            console.print(f"\n[yellow]{ERROR_FILE_LABEL.format(errors=stats['errors'], path=error_file)}[/yellow]")
        else:
            console.print(f"\n[green]{SUCCESS_LABEL}[/green]")

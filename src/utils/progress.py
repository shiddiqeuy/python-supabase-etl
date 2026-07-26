"""Wrapper untuk rich.progress agar bisa dipakai generik."""

from typing import Callable, List

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


def run_progress(
    total: int,
    description: str,
    items: List[Any],
    process_fn: Callable[[Any, int], None],
    console: Console,
) -> None:
    """
    Jalankan proses dalam progress bar.

    Args:
        total: Total item yang akan diproses.
        description: Deskripsi task pada progress bar.
        items: Daftar item yang akan diproses.
        process_fn: Fungsi yang dipanggil untuk setiap item. Signature: (item, index) -> None.
        console: Instance Rich Console untuk output.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=total)
        for idx, item in enumerate(items, 1):
            progress.update(
                task,
                description=f"{description} | Baris {idx} dari {total}",
            )
            process_fn(item, idx)
            progress.advance(task)

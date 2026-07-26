"""Modul ekspor data hasil laporan ke CSV dan Excel (XLSX)."""

from pathlib import Path
import pandas as pd


def export_csv(df: pd.DataFrame, filepath: str) -> str:
    """Ekspor DataFrame ke berkas CSV."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)


def export_xlsx(df: pd.DataFrame, filepath: str) -> str:
    """Ekspor DataFrame ke berkas Excel (XLSX)."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False, engine="openpyxl")
    return str(path)

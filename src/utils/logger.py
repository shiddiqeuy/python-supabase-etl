"""Logger dan helper pencatatan error ke CSV."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def save_error_log(errors: List[Dict[str, Any]], prefix: str = "error_log") -> str:
    """
    Simpan baris error ke file CSV bertimestamp.

    Args:
        errors: Daftar dictionary yang berisi informasi error.
        prefix: Prefix nama file log error.

    Returns:
        Path ke file log error yang disimpan.
    """
    if not errors:
        return ""

    error_log_dir = Path("error_logs")
    error_log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    filepath = error_log_dir / filename

    df = pd.DataFrame(errors)
    df.to_csv(filepath, index=False)

    return str(filepath)

"""Reader untuk file Excel dan CSV."""

from pathlib import Path
from typing import Optional

import pandas as pd

from src.core.exceptions import FileReadError


class ExcelReader:
    """Membaca file Excel atau CSV menjadi DataFrame pandas."""

    @staticmethod
    def read(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
        path = Path(file_path)

        if not path.exists():
            raise FileReadError(f"File '{file_path}' tidak ditemukan.")

        ext = path.suffix.lower()
        try:
            if ext == ".xlsx":
                if sheet_name:
                    return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
                excel_file = pd.ExcelFile(file_path, engine="openpyxl")
                if len(excel_file.sheet_names) > 0:
                    return pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
                raise FileReadError("File Excel tidak mengandung sheet.")
            if ext == ".csv":
                return pd.read_csv(file_path)
            raise FileReadError(
                f"Format file tidak didukung '{ext}'. Gunakan .xlsx atau .csv"
            )
        except FileReadError:
            raise
        except Exception as exc:
            raise FileReadError(f"Error membaca file: {exc}") from exc

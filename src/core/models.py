"""Data models menggunakan dataclasses untuk kejelasan tipe."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FileSource:
    """Representasi sumber file yang akan diimpor."""

    path: Path
    sheet_name: Optional[str] = None

    @property
    def format(self) -> str:
        """Format file berdasarkan ekstensi."""
        if self.path.suffix.lower() == ".csv":
            return "csv"
        if self.path.suffix.lower() == ".xlsx":
            return "xlsx"
        raise ValueError(f"Format file tidak didukung: {self.path.suffix}")


@dataclass
class InvoiceItem:
    """Satu item produk dalam invoice."""

    produk: str
    qty: float
    harga: float
    cogs: float


@dataclass
class Invoice:
    """Data invoice yang terstruktur."""

    no_invoice: str
    tanggal: Optional[str]
    customer_name: str
    sales_name: str
    discount: float
    ongkir: float
    jumlah_tagihan: float
    total_cogs: float
    down_payment: float
    sisa_tagihan: float
    keterangan: str
    catatan: str
    bukti_transfer: str
    products: List[InvoiceItem] = field(default_factory=list)


@dataclass
class ExpenseRecord:
    """Data record pengeluaran yang terstruktur."""

    tanggal: Optional[str]
    kode_coa: str
    nama_coa: str
    coa_level: int
    kategori: str
    nama_pengeluaran: str
    deskripsi: str
    jumlah: float
    bukti_tf: str


@dataclass
class ImportResult:
    """Hasil akhir dari proses impor."""

    total: int
    success: int
    skipped: int
    errors: int
    total_amount: float
    duration: float
    error_file: str = ""

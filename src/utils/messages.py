"""Semua string Bahasa Indonesia terpusat untuk aplikasi."""

BANNER_SALES = """
[bold cyan]+----------------------------------------------------------+[/bold cyan]
[bold cyan]|[/bold cyan]  [bold white]   Impor Data Penjualan ke Supabase[/bold white]            [bold cyan]|[/bold cyan]
[bold cyan]|[/bold cyan]  [dim]Impor Excel/CSV -> Tabel Invoice Ter-normalisasi[/dim]  [bold cyan]|[/bold cyan]
[bold cyan]+----------------------------------------------------------+[/bold cyan]
"""

BANNER_EXPENSE = """
[bold cyan]+----------------------------------------------------------+[/bold cyan]
[bold cyan]|[/bold cyan]  [bold white]   Impor Data Pengeluaran ke Supabase[/bold white]         [bold cyan]|[/bold cyan]
[bold cyan]|[/bold cyan]  [dim]Impor Excel/CSV -> Tabel Pengeluaran[/dim]            [bold cyan]|[/bold cyan]
[bold cyan]+----------------------------------------------------------+[/bold cyan]
"""

MENU_ITEMS = [
    ("1", "[bold green]Upload Batch Data Penjualan[/bold green]"),
    ("2", "[bold yellow]Upload Batch Pengeluaran[/bold yellow]"),
    ("3", "[bold blue]Cek Koneksi[/bold blue]"),
    ("4", "[bold magenta]Keluar[/bold magenta]"),
]

SUMMARY_LABELS = {
    "total": "Total Baris",
    "success": "Berhasil Diimpor",
    "skipped": "Dilewati",
    "errors": "Error",
    "duration": "Durasi Total",
    "total_amount": "Total Jumlah Diimpor",
}

ERROR_FILE_LABEL = "{errors} error terjadi. Log error disimpan di: {path}"
SUCCESS_LABEL = "Impor selesai tanpa error!"
DRY_RUN_LABEL = "MODE DRY RUN - Tidak ada data yang akan dimasukkan"
CONNECTION_SUCCESS = "[green]+ Koneksi Supabase berhasil![/green]"
CONNECTION_FAILED = "[red]- Gagal terhubung ke Supabase[/red]"

PROMPT_FILE_PATH = "Masukkan path file Excel atau CSV"
PROMPT_SHEET = "Masukkan nama sheet"
PROMPT_BATCH_SIZE = "Masukkan ukuran batch (default: 100)"
PROMPT_DRY_RUN = "Jalankan dalam mode dry-run? (hanya validasi, tanpa insert)"
PROMPT_VERBOSE = "Tampilkan output verbose?"

MSG_FILE_NOT_FOUND = "[red]File tidak ditemukan atau format tidak didukung (.xlsx atau .csv)[/red]"
MSG_INVALID_FORMAT = "[red]Format file tidak didukung '{ext}'. Gunakan .xlsx atau .csv[/red]"
MSG_NO_DATA = "[yellow]Tidak ada record yang valid ditemukan di file[/yellow]"
MSG_EMPTY_COA = "Data tidak lengkap (tanggal/COA kosong)"
MSG_DUPLICATE = "Nomor invoice duplikat"

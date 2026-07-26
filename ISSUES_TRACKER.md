# Daftar Issue & Rekomendasi

## Bugs
### [BUG-001] Rich LiveDisplay crash saat CLI dijalankan paralel (concurrent)
- **Label:** bug
- **Prioritas:** P1 - High
- **Deskripsi:** Ketika CLI dipanggil secara bersamaan (concurrent), Rich `Progress` live display mengakibatkan `LiveError: Only one live display may be active at once`. Ini menyebabkan crash seluruh thread pool jika tidak di-mock.
- **Bukti/Log:** `rich.errors.LiveError: Only one live display may be active at once` muncul selama Stress Test concurrency.
- **Saran Perbaikan:** Tambahkan flag `--no-progress` atau deteksi otomatis untuk non-TTY. Konversi `run_progress` menjadi optional, atau gunakan `Progress` dengan `transient=True` agar bisa overlap.

### [BUG-002] openpyxl mengunci file .xlsx di Windows
- **Label:** bug
- **Prioritas:** P2 - Medium
- **Deskripsi:** File Excel yang ditulis oleh pandas/openpyxl terkunci oleh proses dan tidak bisa dihapus/di-overwrite di Windows sampai Python process selesai.
- **Bukti/Log:** `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`
- **Saran Perbaikan:** Gunakan `pd.ExcelWriter` dengan context manager yang explicit, atau fallback ke `xlsxwriter`. Dokumentasikan di README tentang pembatasan Windows.

### [BUG-003] MasterDataCache resolve_id() belum thread-safe
- **Label:** bug
- **Prioritas:** P2 - Medium
- **Deskripsi:** `_cache` dict dan operasi DB `select_one()` + `insert_record()` di dalam `resolve_id()` tidak aman jika dipanggil dari thread berbeda, berpotensi race condition atau duplikasi record.
- **Bukti/Log:** Potensi double-insert untuk record master yang sama saat concurrent writes.
- **Saran Perbaikan:** Tambahkan `threading.Lock` pada `MasterDataCache` atau pindahkan logic get-or-create ke dalam transaksi/upsert database.

## Enhancements
### [ENH-001] Tambahkan Transaction Eksplisit untuk Atomicity
- **Label:** enhancement
- **Prioritas:** P1 - High
- **Deskripsi:** Saat ini insert invoice + relasi `invoice_items` tidak dijalankan dalam transaction. Kegagalan parsial mengakibatkan data inkonsisten.
- **Manfaat:** Menjamin data integrity pada failure, terutama penting untuk ETL batch production.
- **Saran Implementasi:** Gunakan Supabase PostgREST transaction via `rpc('begin')` atau pindah ke SQLAlchemy + psycopg3 dengan explicit `BEGIN/COMMIT`.

### [ENH-002] Tambahkan Soft-Batching / Chunking untuk File Besar
- **Label:** enhancement
- **Prioritas:** P2 - Medium
- **Deskripsi:** Saat ini seluruh DataFrame dimuat ke memori lalu diproses berurutan. Untuk file >100k baris, ini akan boros memori.
- **Manfaat:** Pengurangan peak memory, stabil untuk input besar.
- **Saran Implementasi:** Gunakan `pd.read_excel(..., chunksize=N)` atau `pd.read_csv(..., chunksize=N)` dan proses per-chunk.

### [ENH-003] Tambahkan Retry + Circuit Breaker pada SupabaseRepository
- **Label:** enhancement
- **Prioritas:** P2 - Medium
- **Deskripsi:** Tidak ada retry untuk kegagalan sementara (timeout, 5xx, network blip).
- **Manfaat:** Meningkatkan reliabilitas impor batch yang berjalan lama.
- **Saran Implementasi:** Tambahkan `tenacity` atau `urllib3.util.retry` pada `SupabaseRepository`. Tambahkan timeout 30 detik default pada `create_client`.

### [ENH-004] Tambahkan Schema Validation (Pandera / Pydantic) sebelum Insert
- **Label:** enhancement
- **Prioritas:** P3 - Low
- **Deskripsi:** Saat ini `transform_record()` dan `validate()` sudah ada, tetapi tidak ada schema enforcement yang ketat. Nilai negatif, NaN, atau tipe yang salah bisa lolos.
- **Manfaat:** Mencegah garbage in/out dari Excel/CSV berantakan.
- **Saran Implementasi:** Tambahkan `pandera` DataFrameSchema validation layer di `ExcelReader.read()` sebelum transformasi.

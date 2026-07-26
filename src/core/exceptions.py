"""Custom exception classes untuk aplikasi."""


class SupabaseImporterError(Exception):
    """Base exception untuk semua error di aplikasi ini."""


class SupabaseConfigError(SupabaseImporterError):
    """Kesalahan konfigurasi atau kredensial."""


class FileReadError(SupabaseImporterError):
    """Kesalahan membaca file sumber."""


class DataValidationError(SupabaseImporterError):
    """Kesalahan validasi data."""


class ImportError(SupabaseImporterError):
    """Kesalahan selama proses impor."""


class DuplicateInvoiceError(ImportError):
    """Invoice duplikat ditemukan."""

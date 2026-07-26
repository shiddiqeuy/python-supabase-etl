"""Entry point: python -m src"""

import sys
from datetime import datetime

from src.cli.app import app
from src.cli.interactive_prompts import check_supabase_connection


def interactive_dashboard_submenu() -> None:
    """Submenu Sales Dashboard (Level 2)."""
    from src.cli.interactive_prompts import print_dashboard_submenu
    from src.cli.dashboard_command import (
        summary_cmd,
        by_sales_cmd,
        by_product_cmd,
        by_customer_cmd,
        payment_status_cmd,
        trend_cmd,
    )
    from src.reports.exporter import export_csv, export_xlsx
    from src.repositories.dashboard_repository import DashboardRepository

    while True:
        try:
            print_dashboard_submenu()
            choice = input("\nPilih fitur dashboard (0-7): ").strip()

            if choice == "0":
                # Kembali ke Menu Utama
                break

            elif choice == "1":
                # Summary
                now = datetime.now()
                default_from = f"{now.year}-{now.month:02d}-01"
                date_from = input(f"Tanggal awal [default: {default_from}]: ").strip() or default_from
                date_to = input("Tanggal akhir (YYYY-MM-DD) [default: semua]: ").strip() or None
                cust = input("Filter customer (opsional, pisahkan koma): ").strip() or None
                prod = input("Filter produk (opsional, pisahkan koma): ").strip() or None
                sales = input("Filter sales (opsional, pisahkan koma): ").strip() or None
                status = input("Filter status (lunas|belum_lunas|sebagian) [opsional]: ").strip() or None

                summary_cmd(
                    date_from=date_from,
                    date_to=date_to,
                    customer=cust,
                    product=prod,
                    sales=sales,
                    status=status,
                    min_amount=None,
                    max_amount=None,
                    export=None,
                )

            elif choice == "2":
                by_sales_cmd(date_from=None, date_to=None, customer=None, product=None, sales=None, status=None, min_amount=None, max_amount=None)

            elif choice == "3":
                by_product_cmd(date_from=None, date_to=None, customer=None, product=None, sales=None, status=None, min_amount=None, max_amount=None)

            elif choice == "4":
                by_customer_cmd(date_from=None, date_to=None, customer=None, product=None, sales=None, status=None, min_amount=None, max_amount=None)

            elif choice == "5":
                st = input("Filter status (lunas|belum_lunas|sebagian) [opsional]: ").strip() or None
                payment_status_cmd(date_from=None, date_to=None, customer=None, product=None, sales=None, status=st, min_amount=None, max_amount=None)

            elif choice == "6":
                interval = input("Interval (daily|weekly|monthly) [default: monthly]: ").strip() or "monthly"
                trend_cmd(interval=interval, date_from=None, date_to=None, customer=None, product=None, sales=None, status=None, min_amount=None, max_amount=None)

            elif choice == "7":
                fmt = input("Format ekspor (csv|xlsx) [default: csv]: ").strip().lower() or "csv"
                repo = DashboardRepository()
                df_inv = repo.get_invoices_df()
                if fmt == "xlsx":
                    path = export_xlsx(df_inv, "reports/invoices_export.xlsx")
                else:
                    path = export_csv(df_inv, "reports/invoices_export.csv")
                print(f"Data berhasil diekspor ke: {path}")

            else:
                print("\n[Pilihan tidak valid. Silakan pilih 0 - 7]\n")
                continue

            input("\nTekan Enter untuk kembali ke Submenu Dashboard...")

        except KeyboardInterrupt:
            break
        except Exception as exc:
            print(f"\nError: {exc}")
            input("Tekan Enter untuk melanjutkan...")


def interactive_menu() -> None:
    """Menu Utama (Level 1)."""
    from src.cli.interactive_prompts import (
        get_batch_size,
        get_dry_run_choice,
        get_file_path,
        get_sheet_name,
        get_verbose_choice,
        print_menu,
    )
    from src.core.config import Settings
    from src.importers.expense_importer import ExpenseImporter
    from src.importers.sales_importer import SalesImporter
    from src.repositories.master_data_cache import MasterDataCache
    from src.repositories.supabase_repository import SupabaseRepository
    from src.core.models import FileSource

    while True:
        try:
            print_menu()
            choice = input("\nPilih menu: ").strip()

            if choice == "1":
                file_path = get_file_path()
                sheet_name = get_sheet_name(file_path)
                dry_run = get_dry_run_choice()
                batch_size = get_batch_size()
                verbose = get_verbose_choice()

                settings = Settings.from_env()
                repository = SupabaseRepository(settings)
                cache = MasterDataCache(repository)
                importer = SalesImporter(repository, cache)
                source = FileSource(path=file_path, sheet_name=sheet_name)
                importer.run(source, dry_run=dry_run, batch_size=batch_size, verbose=verbose)
                input("\nTekan Enter untuk kembali ke menu utama...")

            elif choice == "2":
                file_path = get_file_path()
                sheet_name = get_sheet_name(file_path)
                dry_run = get_dry_run_choice()
                batch_size = get_batch_size()
                verbose = get_verbose_choice()

                settings = Settings.from_env()
                repository = SupabaseRepository(settings)
                cache = MasterDataCache(repository)
                importer = ExpenseImporter(repository, cache)
                source = FileSource(path=file_path, sheet_name=sheet_name)
                importer.run(source, dry_run=dry_run, batch_size=batch_size, verbose=verbose)
                input("\nTekan Enter untuk kembali ke menu utama...")

            elif choice == "3":
                settings = Settings.from_env()
                check_supabase_connection(settings)
                input("\nTekan Enter untuk kembali ke menu utama...")

            elif choice == "4":
                interactive_dashboard_submenu()

            elif choice == "5":
                print("Terima kasih! Sampai jumpa.")
                sys.exit(0)

            else:
                print("\nPilihan tidak valid.")
                input("Tekan Enter untuk melanjutkan...")

        except KeyboardInterrupt:
            print("\nProgram dihentikan oleh pengguna.")
            sys.exit(130)
        except Exception as exc:
            print(f"Error tak terduga: {exc}")
            input("Tekan Enter untuk melanjutkan...")


def main() -> None:
    if len(sys.argv) == 1:
        interactive_menu()
    else:
        app()


if __name__ == "__main__":
    main()

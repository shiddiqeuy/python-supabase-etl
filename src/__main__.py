"""Entry point: python -m src"""

import sys

from src.cli.app import app
from src.cli.interactive_prompts import check_supabase_connection, print_banner_sales


def interactive_menu() -> None:
    from src.cli.interactive_prompts import (
        get_batch_size,
        get_dry_run_choice,
        get_file_path,
        get_sheet_name,
        get_verbose_choice,
        print_menu,
    )
    from src.core.config import Settings
    from src.core.exceptions import SupabaseImporterError
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

            elif choice == "3":
                settings = Settings.from_env()
                check_supabase_connection(settings)

            elif choice == "4":
                print("Terima kasih! Sampai jumpa.")
                sys.exit(0)

            else:
                print("Pilihan tidak valid.")

            input("\nTekan Enter untuk kembali ke menu utama...")

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

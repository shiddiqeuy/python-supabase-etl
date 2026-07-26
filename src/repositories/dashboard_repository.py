"""Repository khusus untuk kueri data dashboard penjualan dari Supabase / PostgreSQL."""

import os
from typing import Any, Dict, List, Optional
import pandas as pd

from src.core.config import Settings
from src.repositories.supabase_repository import SupabaseRepository


class DashboardRepository:
    """Repository layer untuk mengambil data transaksi invoice dan relasi untuk dashboard."""

    def __init__(self, repository: Optional[SupabaseRepository] = None) -> None:
        if repository is None:
            # Check DATABASE_URL from environment variable
            db_url = os.getenv("DATABASE_URL")
            settings = Settings.from_env()
            if db_url:
                settings.supabase_url = db_url
            self.repo = SupabaseRepository(settings)
        else:
            self.repo = repository

    def get_invoices_df(self) -> pd.DataFrame:
        """Ambil data seluruh invoice beserta nama customer dan sales person."""
        try:
            res = self.repo.client.table("invoices").select(
                "*, customers(nama_customer), sales_persons(nama_sales)"
            ).execute()
            if not res.data:
                return pd.DataFrame()

            rows = []
            for row in res.data:
                r = dict(row)
                cust_data = r.pop("customers", {}) or {}
                sales_data = r.pop("sales_persons", {}) or {}
                r["customer_name"] = cust_data.get("nama_customer", "Unknown")
                r["sales_name"] = sales_data.get("nama_sales", "Unassigned")
                rows.append(r)
            return pd.DataFrame(rows)
        except Exception:
            return pd.DataFrame()

    def get_invoice_items_df(self) -> pd.DataFrame:
        """Ambil data detail produk invoice (invoice_items)."""
        try:
            res = self.repo.client.table("invoice_items").select(
                "*, products(nama_produk), invoices(no_invoice)"
            ).execute()
            if not res.data:
                return pd.DataFrame()

            rows = []
            for row in res.data:
                r = dict(row)
                prod_data = r.pop("products", {}) or {}
                inv_data = r.pop("invoices", {}) or {}
                r["product_name"] = prod_data.get("nama_produk", "Unknown")
                r["no_invoice"] = inv_data.get("no_invoice", "")
                rows.append(r)
            return pd.DataFrame(rows)
        except Exception:
            return pd.DataFrame()

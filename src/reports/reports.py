"""Fungsi-fungsi agregasi data dan kalkulasi metrik laporan penjualan."""

from typing import Any, Dict, Optional
import pandas as pd


def summary(df_invoices: pd.DataFrame) -> Dict[str, Any]:
    """
    Hitung ringkasan omzet, COGS, margin, dan rata-rata invoice.
    Jika DataFrame kosong / periode tanpa data, kembalikan nilai 0.
    """
    if df_invoices is None or df_invoices.empty:
        return {
            "total_omzet": 0.0,
            "total_cogs": 0.0,
            "total_margin": 0.0,
            "margin_pct": 0.0,
            "avg_invoice": 0.0,
            "total_invoices": 0,
        }

    total_omzet = float(df_invoices["jumlah_tagihan"].sum())
    total_cogs = float(df_invoices["total_cogs"].sum()) if "total_cogs" in df_invoices.columns else 0.0
    total_margin = total_omzet - total_cogs
    margin_pct = (total_margin / total_omzet * 100.0) if total_omzet > 0 else 0.0
    total_invoices = len(df_invoices)
    avg_invoice = (total_omzet / total_invoices) if total_invoices > 0 else 0.0

    return {
        "total_omzet": total_omzet,
        "total_cogs": total_cogs,
        "total_margin": total_margin,
        "margin_pct": margin_pct,
        "avg_invoice": avg_invoice,
        "total_invoices": total_invoices,
    }


def by_sales(df_invoices: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi performa penjualan per Sales Person.
    Invoice dengan sales_person_id == NULL / sales_name kosong dikelompokkan sebagai 'Unassigned'.
    """
    if df_invoices is None or df_invoices.empty:
        return pd.DataFrame(columns=["sales_name", "total_omzet", "total_cogs", "margin", "total_invoices"])

    df = df_invoices.copy()
    if "sales_name" not in df.columns:
        df["sales_name"] = "Unassigned"
    else:
        df["sales_name"] = df["sales_name"].fillna("Unassigned").replace("", "Unassigned").replace("nan", "Unassigned")

    if "total_cogs" not in df.columns:
        df["total_cogs"] = 0.0

    grouped = df.groupby("sales_name", as_index=False).agg(
        total_omzet=("jumlah_tagihan", "sum"),
        total_cogs=("total_cogs", "sum"),
        total_invoices=("jumlah_tagihan", "count"),
    )
    grouped["margin"] = grouped["total_omzet"] - grouped["total_cogs"]
    return grouped.sort_values(by="total_omzet", ascending=False).reset_index(drop=True)


def by_product(df_items: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi performa per Produk.
    Margin per produk = SUM(qty * harga) - SUM(qty * cogs).
    """
    if df_items is None or df_items.empty:
        return pd.DataFrame(columns=["product_name", "qty", "total_omzet", "total_cogs", "margin"])

    df = df_items.copy()
    if "product_name" not in df.columns:
        df["product_name"] = df.get("produk", "Unknown")

    df["omzet"] = df["qty"] * df["harga"]
    df["cogs_total"] = df["qty"] * df["cogs"]

    grouped = df.groupby("product_name", as_index=False).agg(
        qty=("qty", "sum"),
        total_omzet=("omzet", "sum"),
        total_cogs=("cogs_total", "sum"),
    )
    grouped["margin"] = grouped["total_omzet"] - grouped["total_cogs"]
    return grouped.sort_values(by="total_omzet", ascending=False).reset_index(drop=True)


def by_customer(df_invoices: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi performa dan outstanding piutang per Customer.
    Outstanding per customer cocok dengan SUM(sisa_tagihan).
    """
    if df_invoices is None or df_invoices.empty:
        return pd.DataFrame(columns=["customer_name", "total_omzet", "sisa_tagihan", "total_invoices"])

    df = df_invoices.copy()
    if "customer_name" not in df.columns:
        df["customer_name"] = "Unknown"

    if "sisa_tagihan" not in df.columns:
        df["sisa_tagihan"] = 0.0

    grouped = df.groupby("customer_name", as_index=False).agg(
        total_omzet=("jumlah_tagihan", "sum"),
        sisa_tagihan=("sisa_tagihan", "sum"),
        total_invoices=("jumlah_tagihan", "count"),
    )
    return grouped.sort_values(by="total_omzet", ascending=False).reset_index(drop=True)


def payment_status(df_invoices: pd.DataFrame, status_filter: Optional[str] = None) -> pd.DataFrame:
    """
    Daftar status pembayaran invoice (terurut tanggal paling lama ke baru).
    Status: 'lunas' (sisa_tagihan == 0), 'belum_lunas' (sisa_tagihan == jumlah_tagihan), 'sebagian' (0 < sisa_tagihan < jumlah_tagihan).
    """
    if df_invoices is None or df_invoices.empty:
        return pd.DataFrame(columns=[
            "no_invoice", "tanggal", "customer_name", "jumlah_tagihan", "down_payment", "sisa_tagihan", "status_pembayaran"
        ])

    df = df_invoices.copy()
    if "sisa_tagihan" not in df.columns:
        df["sisa_tagihan"] = 0.0
    if "down_payment" not in df.columns:
        df["down_payment"] = 0.0

    def calc_status(row):
        jumlah = row["jumlah_tagihan"]
        sisa = row["sisa_tagihan"]
        if sisa <= 0:
            return "lunas"
        elif sisa >= jumlah:
            return "belum_lunas"
        else:
            return "sebagian"

    df["status_pembayaran"] = df.apply(calc_status, axis=1)

    if status_filter:
        s_clean = status_filter.lower().strip()
        df = df[df["status_pembayaran"] == s_clean]

    df["tanggal_dt"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.sort_values(by="tanggal_dt", ascending=True).drop(columns=["tanggal_dt"])

    return df.reset_index(drop=True)


def trend(df_invoices: pd.DataFrame, interval: str = "monthly") -> pd.DataFrame:
    """
    Bucketing tren waktu penjualan (daily, weekly, monthly).
    """
    if df_invoices is None or df_invoices.empty:
        return pd.DataFrame(columns=["periode", "total_omzet", "total_invoices"])

    df = df_invoices.copy()
    df["tanggal_dt"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal_dt"])

    if df.empty:
        return pd.DataFrame(columns=["periode", "total_omzet", "total_invoices"])

    if interval.lower() == "daily":
        df["periode"] = df["tanggal_dt"].dt.strftime("%Y-%m-%d")
    elif interval.lower() == "weekly":
        df["periode"] = df["tanggal_dt"].dt.to_period("W").astype(str)
    else:  # monthly
        df["periode"] = df["tanggal_dt"].dt.strftime("%Y-%m")

    grouped = df.groupby("periode", as_index=False).agg(
        total_omzet=("jumlah_tagihan", "sum"),
        total_invoices=("jumlah_tagihan", "count"),
    )
    return grouped.sort_values(by="periode", ascending=True).reset_index(drop=True)

"""Filter parameterize untuk menyaring data invoice dan items berdasarkan kombinasi AND logic."""

from typing import List, Optional, Tuple
import pandas as pd


def validate_filter_names(
    existing_names: List[str], requested_names: List[str], filter_type: str
) -> None:
    """Validasi apakah nama yang diminta dalam filter benar-benar ada di data."""
    existing_lower = [str(n).strip().lower() for n in existing_names if n]
    for req in requested_names:
        req_clean = req.strip()
        if not req_clean:
            continue
        if req_clean.lower() == "unassigned" and filter_type == "sales":
            continue
        if req_clean.lower() not in existing_lower:
            raise ValueError(
                f"{filter_type.capitalize()} '{req_clean}' tidak ditemukan di database."
            )


def apply_filters(
    df_invoices: pd.DataFrame,
    df_items: Optional[pd.DataFrame] = None,
    customer: Optional[str] = None,
    product: Optional[str] = None,
    sales: Optional[str] = None,
    status: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Terapkan filter kombinasi (AND logic) pada DataFrame invoices dan items.
    """
    if df_invoices is None or df_invoices.empty:
        return pd.DataFrame(), pd.DataFrame() if df_items is not None else None

    df_inv = df_invoices.copy()

    # Filter Customer (comma-separated support)
    if customer and customer.strip():
        cust_list = [c.strip() for c in customer.split(",") if c.strip()]
        if "customer_name" in df_inv.columns:
            validate_filter_names(
                df_inv["customer_name"].dropna().unique().tolist(),
                cust_list,
                "customer",
            )
            pattern = "|".join([c.lower() for c in cust_list])
            df_inv = df_inv[
                df_inv["customer_name"].str.lower().str.contains(pattern, na=False)
            ]

    # Filter Sales (comma-separated & 'unassigned' support)
    if sales and sales.strip():
        sales_list = [s.strip() for s in sales.split(",") if s.strip()]
        if "sales_name" in df_inv.columns:
            existing_sales = df_inv["sales_name"].dropna().unique().tolist()
            validate_filter_names(existing_sales, sales_list, "sales")

            conditions = []
            for s_item in sales_list:
                if s_item.lower() == "unassigned":
                    conditions.append(
                        df_inv["sales_name"].isna()
                        | (df_inv["sales_name"].str.lower() == "unassigned")
                        | (df_inv["sales_name"] == "")
                    )
                else:
                    conditions.append(
                        df_inv["sales_name"].str.lower() == s_item.lower()
                    )
            combined_cond = conditions[0]
            for c in conditions[1:]:
                combined_cond = combined_cond | c
            df_inv = df_inv[combined_cond]

    # Filter Tanggal (Date From & To)
    if "tanggal" in df_inv.columns:
        df_inv["tanggal_dt"] = pd.to_datetime(df_inv["tanggal"], errors="coerce")
        if date_from and str(date_from).strip():
            df_inv = df_inv[df_inv["tanggal_dt"] >= pd.to_datetime(date_from)]
        if date_to and str(date_to).strip():
            df_inv = df_inv[df_inv["tanggal_dt"] <= pd.to_datetime(date_to)]
        df_inv = df_inv.drop(columns=["tanggal_dt"])

    # Filter Min & Max Amount
    if min_amount is not None:
        df_inv = df_inv[df_inv["jumlah_tagihan"] >= float(min_amount)]
    if max_amount is not None:
        df_inv = df_inv[df_inv["jumlah_tagihan"] <= float(max_amount)]

    # Filter Status Pembayaran
    if status and status.strip():
        st_clean = status.strip().lower()
        if "sisa_tagihan" not in df_inv.columns:
            df_inv["sisa_tagihan"] = 0.0

        if st_clean == "lunas":
            df_inv = df_inv[df_inv["sisa_tagihan"] <= 0]
        elif st_clean == "belum_lunas":
            df_inv = df_inv[df_inv["sisa_tagihan"] >= df_inv["jumlah_tagihan"]]
        elif st_clean == "sebagian":
            df_inv = df_inv[
                (df_inv["sisa_tagihan"] > 0)
                & (df_inv["sisa_tagihan"] < df_inv["jumlah_tagihan"])
            ]

    # Filter Product (pada items & invoices)
    df_itm_res = None
    if df_items is not None and not df_items.empty:
        df_itm = df_items.copy()
        if product and product.strip():
            prod_list = [p.strip() for p in product.split(",") if p.strip()]
            col_name = "product_name" if "product_name" in df_itm.columns else "produk"
            if col_name in df_itm.columns:
                validate_filter_names(
                    df_itm[col_name].dropna().unique().tolist(),
                    prod_list,
                    "produk",
                )
                pattern = "|".join([p.lower() for p in prod_list])
                df_itm = df_itm[
                    df_itm[col_name].str.lower().str.contains(pattern, na=False)
                ]

        # Filter items so they match the remaining invoices
        if "no_invoice" in df_itm.columns and "no_invoice" in df_inv.columns:
            df_itm_res = df_itm[df_itm["no_invoice"].isin(df_inv["no_invoice"])]
        else:
            df_itm_res = df_itm

    return df_inv, df_itm_res

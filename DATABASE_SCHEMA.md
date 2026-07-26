# Dokumentasi Skema Database Supabase

Dokumen ini berisi struktur tabel, kolom, tipe data, constraint, dan RLS Policies pada database PostgreSQL Supabase untuk dibaca oleh agent (AI) dan human developer.

---

## Table `ms_produk`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id_produk` | `varchar` | Primary |
| `nama_produk` | `varchar` |  Unique |
| `harga_standar` | `numeric` |  |
| `cogs_standar` | `numeric` |  |

## Table `ms_pelanggan`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id_pelanggan` | `int4` | Primary Identity |
| `nama_pelanggan` | `varchar` |  Unique |

## Table `ms_sales`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id_sales` | `int4` | Primary Identity |
| `nama_sales` | `varchar` |  Unique |

## Table `tr_invoice`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `no_invoice` | `varchar` | Primary |
| `tanggal` | `date` |  |
| `id_pelanggan` | `int4` |  |
| `id_sales` | `int4` |  |
| `diskon_persen` | `numeric` |  Nullable |
| `ongkir` | `numeric` |  Nullable |
| `dp` | `numeric` |  Nullable |
| `total_bayar` | `numeric` |  |
| `status_bayar` | `varchar` |  |
| `link_bukti` | `text` |  Nullable |
| `catatan` | `text` |  Nullable |

## Table `tr_invoice_detail`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `id_detail` | `int4` | Primary Identity |
| `no_invoice` | `varchar` |  |
| `id_produk` | `varchar` |  |
| `qty` | `numeric` |  |
| `harga_jual_historis` | `numeric` |  |
| `cogs_historis` | `numeric` |  |

## Table `customers`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `customer_id` | `int4` | Primary |
| `nama_customer` | `varchar` |  Unique |
| `created_at` | `timestamptz` |  Nullable |
| `updated_at` | `timestamptz` |  Nullable |

## Table `products`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `product_id` | `int4` | Primary |
| `nama_produk` | `varchar` |  Unique |
| `cogs_default` | `numeric` |  |
| `created_at` | `timestamptz` |  Nullable |
| `updated_at` | `timestamptz` |  Nullable |

## Table `sales_persons`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `sales_person_id` | `int4` | Primary |
| `nama_sales` | `varchar` |  Unique |
| `created_at` | `timestamptz` |  Nullable |
| `updated_at` | `timestamptz` |  Nullable |

## Table `coa`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `coa_id` | `int4` | Primary |
| `kode_coa` | `varchar` |  Unique |
| `nama_coa` | `varchar` |  |
| `parent_id` | `int4` |  Nullable |
| `level` | `int2` |  |
| `created_at` | `timestamptz` |  Nullable |

## Table `kategori_pengeluaran`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `kategori_id` | `int4` | Primary |
| `nama_kategori` | `varchar` |  Unique |
| `created_at` | `timestamptz` |  Nullable |

## Table `invoices`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `invoice_id` | `int4` | Primary |
| `no_invoice` | `varchar` |  Unique |
| `tanggal` | `date` |  |
| `customer_id` | `int4` |  |
| `sales_person_id` | `int4` |  Nullable |
| `discount` | `numeric` |  |
| `ongkir` | `numeric` |  |
| `keterangan` | `text` |  Nullable |
| `catatan` | `text` |  Nullable |
| `created_at` | `timestamptz` |  Nullable |
| `updated_at` | `timestamptz` |  Nullable |
| `jumlah_tagihan` | `numeric` |  Nullable |
| `total_cogs` | `numeric` |  Nullable |
| `down_payment` | `numeric` |  Nullable |
| `sisa_tagihan` | `numeric` |  Nullable |
| `bukti_transfer` | `varchar` |  Nullable |

## Table `invoice_items`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `invoice_item_id` | `int4` | Primary |
| `invoice_id` | `int4` |  |
| `product_id` | `int4` |  |
| `qty` | `numeric` |  |
| `harga` | `numeric` |  |
| `cogs` | `numeric` |  |
| `created_at` | `timestamptz` |  Nullable |

## Table `payments`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `payment_id` | `int4` | Primary |
| `invoice_id` | `int4` |  |
| `tanggal_bayar` | `date` |  |
| `jumlah` | `numeric` |  |
| `metode` | `varchar` |  Nullable |
| `bukti_transfer` | `varchar` |  Nullable |
| `keterangan` | `text` |  Nullable |
| `created_at` | `timestamptz` |  Nullable |

## Table `pengeluaran`

### Columns

| Name | Type | Constraints |
|------|------|-------------|
| `pengeluaran_id` | `int4` | Primary |
| `tanggal` | `date` |  |
| `coa_id` | `int4` |  |
| `kategori_id` | `int4` |  Nullable |
| `deskripsi` | `text` |  |
| `jumlah` | `numeric` |  |
| `bukti_tf` | `varchar` |  Nullable |
| `created_at` | `timestamptz` |  Nullable |
| `updated_at` | `timestamptz` |  Nullable |

## RLS Policies

### `customers`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `products`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `sales_persons`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `invoice_items`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `invoices`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `coa`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `kategori_pengeluaran`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

### `pengeluaran`

| Policy | Command | Roles | Action | USING | WITH CHECK |
|--------|---------|-------|--------|-------|------------|
| `Allow full access` | ALL | public | PERMISSIVE | `true` | `true` |

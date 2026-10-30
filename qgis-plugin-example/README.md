# Plugin QGIS: Geoportal IGT-PR (Mockup V2)

Implementasi native Qt dari **Mockup V2 (Feature-Based Card UI & Hierarchical Tree Table)** sebagai plugin QGIS terpadu yang siap dijalankan langsung di QGIS 3.x (Qt5/Qt6).

```text
igtpr_login_example/
├── __init__.py           # classFactory QGIS
├── metadata.txt          # Metadata plugin v2.0
├── plugin.py             # Controller utama, IgtprDockWidget, integrasi layer QGIS (WMS/WFS)
├── topbar.py             # Header topbar persisten (breadcrumb, status QGIS, role chip, logout)
├── role_dialog.py        # Dialog modal pemilihan peran (Superadmin, Admin, Operator, Umum)
├── login_page.py         # Halaman login dengan hero card, SSO, dan Fitur Utama
├── dashboard_page.py     # Dashboard / Beranda V2 (Hero card, stat cards, katalog hub, alur kerja)
├── catalog_page.py       # Katalog Data V2 (Opsi 2 Accordion tree table, multi-layer chip, WMS/WFS)
├── management_page.py    # Manajemen Data V2 (Tab status, kompilasi, verifikasi topologi, persetujuan)
├── upload_dialog.py      # Formulir unggah data geospasial (file picker, kategori, satker)
├── model_builder_page.py # Model Builder spasial V2 (katalog model analisis & eksekusi di QGIS)
├── data.py               # Dataset referensi IGT ATR/BPN, sub-layer multi-year/skala, & pengajuan
├── assets.py             # SVG Tiny 1.2 vector icons & contour
└── illustration.png      # Ilustrasi antarmuka QGIS untuk halaman login
```

## Fitur Mockup V2

1. **Halaman Login & Autentikasi Peran**:
   - Header logo ganda (BPN & IGT-PR), bilah aksen 90×4 px, kartu hero 2 kolom, dan 5 ikon fitur melingkar.
   - Dialog pemilihan peran interaktif: **Superadmin (SA)**, **Admin (AD)**, **Operator Pusat (JH)**, dan **Pengguna Umum (UM)**.
2. **Topbar Persisten**:
   - Breadcrumb navigation (`Geoportal IGT-PR / Katalog IGT / IGT Pertanahan`) dengan tautan kembali.
   - Status koneksi QGIS aktif (`● QGIS Aktif`).
   - Chip profil peran dengan menu ganti peran dan tombol keluar (logout).
3. **Dashboard / Beranda (Card UI)**:
   - Kartu hero gradien biru tua ATR/BPN dengan filter tahun dinamis (`Semua tahun`, `2026`, `2025`, `2024`, `2023`).
   - Kartu statistik berstatus: *Terkompilasi* (Amber) dan *Terintegrasi* (Emerald).
   - Kartu Hub Katalog IGT (Pertanahan, Tata Ruang, Derivatif Multiguna, Lainnya).
   - Kartu Hub Alur Kerja (Unggah Data, Manajemen Data, Model Builder).
4. **Katalog Data (Opsi 2 - Hierarchical Tree Table & Multi-Layer Chip)**:
   - Navigasi subnav 4 kategori IGT.
   - Kolom tabel disesuaikan: `Nama IGT`, `Direktorat` (atau `Instansi` untuk IGT Lainnya), `Tanggal Pembaruan`, `WMS`, `WFS`. Kolom status, ID, dan ruang lingkup disederhanakan sesuai kebutuhan.
   - **Chip Multi-Layer**:
     - *Multi-Year* (Mint `#ecfdf5` / `#047857`): Lahan Baku Sawah, ZNT, Tanah Terindikasi Telantar.
     - *Multi-Skala* (Blue `#eff6ff` / `#1d4ed8`): RDTR Kab/Kota, RTRW Kabupaten.
   - Klik chip atau tombol toggle untuk membuka/menutup sub-layer berjenjang dengan indentasi `└─` dan tombol WMS/WFS mandiri.
   - **Integrasi Kanvas QGIS**: Klik WMS atau WFS memuat layer memory geospasial nyata ke dalam proyek QGIS (`QgsProject.instance().addMapLayer`) dan menampilkan notifikasi sukses di `iface.messageBar()`.
5. **Manajemen Data**:
   - Tab status: `Revisi`, `Diajukan`, `Terkompilasi`, `Terintegrasi`, `Semua`.
   - Tombol alur persetujuan: *Kompilasi*, *Verifikasi Topologi*, *Setujui Integrasi* (Superadmin), *Perbaiki Revisi*, dan *Tampilkan di QGIS*.
6. **Formulir Unggah Data**:
   - Dropzone berkas (.gpkg, .zip, .csv), pemilihan kategori, dataset target, dan satker.
   - Data otomatis masuk ke antrean pengajuan Manajemen Data.
7. **Model Builder Spasial**:
   - Daftar model analisis spasial (Analisis Kesesuaian Lahan, Buffer Kawasan Lindung, Overlay RTRW vs Bidang, dsb.) yang dapat dieksekusi langsung ke kanvas peta.

## Memasang di QGIS

Salin atau symlink folder `igtpr_login_example` ke folder plugin profil QGIS Anda, atau pasang dari file ZIP `igtpr_login_example.zip` melalui menu *Plugins → Install from ZIP*:

```bash
# Linux
ln -s "$PWD/igtpr_login_example" ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Windows
# %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```

Aktifkan **Geoportal IGT-PR (Mockup V2)** di *Plugins → Manage and Install Plugins*. Klik tombol toolbar IGT-PR untuk membuka panel dock.

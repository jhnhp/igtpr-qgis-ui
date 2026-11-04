# Matriks Hak Akses Peran (Role Permission Matrix) - Plugin QGIS Geoportal IGT-PR

Dokumen ini merangkum seluruh pemetaan fungsi dan hak akses untuk 4 peran (*roles*) pada **Plugin QGIS Geoportal IGT-PR (Mockup V2)** Kementerian Agraria dan Tata Ruang / Badan Pertanahan Nasional (ATR/BPN).

Berkas spreadsheet Excel tersedia di:
- [`MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx`](MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx)

---

## 1. Ringkasan Profil Peran

| Kode Peran | Nama Peran | Avatar | Satker Penugasan | Warna Tema | Deskripsi & Tanggung Jawab Utama |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `superadmin` | **Superadmin** | `SA` | Semua Satker | `#1e40af` | Akses WFS seluruh wilayah Indonesia, unggah semua kategori (termasuk IGT K/L Lainnya), verifikasi topologi, persetujuan integrasi data spasial nasional, dan manajemen data penuh. |
| `admin` | **Admin** | `AD` | Kantah Kab. Sleman | `#6b21a8` | Verifikasi kelayakan spasial & persetujuan pengajuan IGT Utama & Derivatif, unggah IGT Utama & Derivatif, akses Model Builder, serta akses WFS terbatas sesuai satker penugasan (Sleman). |
| `operator` | **Operator Pusat** | `JH` | Kantah Kab. Sleman | `#166534` | Unggah data IGT Utama & Derivatif, perbaikan revisi geometri/atribut, pemantauan status kompilasi, eksekusi alur 6-langkah Derivatif Bidang, dan akses WFS sesuai satker penugasan (Sleman). |
| `umum` | **Pengguna Umum** | `UM` | Non-Satker (Publik) | `#334155` | Akses visualisasi seluruh katalog publikasi IGT via WMS, pengajuan layer IGT Derivatif Multiguna, dan eksekusi pemodelan spasial Model Builder (tidak memiliki akses WFS). |

---

## 2. Tabel Matriks Hak Akses Fungsi Plugin QGIS

Keterangan simbol:
- `☑` : **Memiliki Hak Akses**
- `☐` : **Tidak Memiliki Akses**

| Fungsi / Fitur Plugin | superadmin | admin | operator | umum | Kategori / Modul | Keterangan & Lingkup Akses |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **A. Autentikasi & Akun** | | | | | | |
| Login SSO Akun Geoportal IGT-PR | ☑ | ☑ | ☑ | ☑ | Autentikasi & Akun | Autentikasi akun pengguna ATR/BPN atau publik |
| Pemilihan / Pergantian Peran (Role Switcher) | ☑ | ☑ | ☑ | ☑ | Autentikasi & Akun | Dialog interaktif pemilihan peran aktif (SA, AD, JH, UM) |
| Logout / Keluar Sesi | ☑ | ☑ | ☑ | ☑ | Autentikasi & Akun | Keluar dari sesi plugin pada antarmuka QGIS |
| Navigasi Breadcrumbs Topbar | ☑ | ☑ | ☑ | ☑ | Autentikasi & Akun | Jejak rekam halaman dengan tautan kembali ke Dashboard |
| **B. Dashboard / Beranda** | | | | | | |
| Akses Halaman Dashboard (Beranda) | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Beranda utama plugin dengan Card UI dan ringkasan data |
| Filter Tahun Global (2026, 2025, 2024, 2023, Semua Tahun) | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Filter sinkronisasi data statistik dan katalog secara dinamis |
| Statistik Ringkasan Data Terkompilasi | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Indikator jumlah pengajuan berstatus Terkompilasi |
| Statistik Ringkasan Data Terintegrasi | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Indikator jumlah dataset resmi terintegrasi nasional |
| Pintasan Hub Katalog IGT (4 Kategori) | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Pintasan ke IGT Pertanahan, Tata Ruang, Derivatif, Lainnya |
| Pintasan Hub Unggah Data | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Pintasan membuka dialog unggah data geospasial |
| Pintasan Hub Manajemen Data | ☑ | ☑ | ☑ | ☐ | Dashboard / Beranda | Tersedia untuk Superadmin, Admin, dan Operator |
| Pintasan Hub Model Builder | ☑ | ☑ | ☑ | ☑ | Dashboard / Beranda | Pintasan ke katalog modul analisis pemodelan spasial |
| **C. Katalog Data IGT** | | | | | | |
| Akses Halaman Katalog IGT Terpadu | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Katalog pencarian dan visualisasi dataset terintegrasi |
| Katalog Tab IGT-PR (Terpadu) | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Katalog gabungan IGT Pertanahan dan IGT Tata Ruang |
| Katalog Tab IGT Pertanahan | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Dataset tematik berbasis bidang tanah terintegrasi |
| Katalog Tab IGT Tata Ruang | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Dataset rencana tata ruang berbasis kawasan terintegrasi |
| Katalog Tab IGT Derivatif Multiguna | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Layer tematik turunan analisis spasial yang telah disetujui |
| Katalog Tab IGT K/L Lainnya (Eksternal) | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Layer referensi kementerian dan lembaga eksternal |
| Pencarian Kata Kunci Dataset | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Cari berdasarkan nama IGT, ID, sublayer, atau wilayah |
| Filter Wilayah Hirarkis (Provinsi & Kab/Kota) | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Filter cakupan wilayah administrasi 38 provinsi di Indonesia |
| Paginasi Katalog (8 Dataset per Halaman) | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Navigasi halaman 1, 2, ..., nomor halaman, dan dropdown |
| Detail Informasi IGT & Metadata | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Dialog informasi lengkap: direktorat, satker, tanggal, CRS |
| Sub-Layer Hierarkis Multi-Year (Tahun Jamak) | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Accordion sublayer per tahun (LBS, ZNT, TTT) |
| Sub-Layer Hierarkis Multi-Skala | ☑ | ☑ | ☑ | ☑ | Katalog Data IGT | Accordion sublayer per skala peta (RDTR 5K/10K/25K, RTRW) |
| **D. Integrasi Kanvas QGIS (WMS & WFS)** | | | | | | |
| Muat Layer WMS (Gambar Peta) ke Kanvas QGIS | ☑ | ☑ | ☑ | ☑ | Integrasi Kanvas QGIS | Menambahkan layer WMS (gambar peta) ke kanvas QGIS |
| Muat Layer WFS (Vektor Fitur) - Seluruh Satker Nasional | ☑ | ☐ | ☐ | ☐ | Integrasi Kanvas QGIS | Khusus Superadmin dapat mengakses fitur WFS seluruh Indonesia |
| Muat Layer WFS (Vektor Fitur) - Sesuai Satker Penugasan | ☑ | ☑ | ☑ | ☐ | Integrasi Kanvas QGIS | Admin & Operator hanya untuk satker Sleman. Umum tidak diizinkan |
| **E. Unggah Data (Upload Data)** | | | | | | |
| Akses Formulir Dialog Unggah Data | ☑ | ☑ | ☑ | ☑ | Unggah Data (Upload) | Dialog upload berkas dan entri metadata geospasial |
| Unggah Data IGT Pertanahan | ☑ | ☑ | ☑ | ☐ | Unggah Data (Upload) | Hanya internal pengelola data (Operator, Admin, Superadmin) |
| Unggah Data IGT Tata Ruang | ☑ | ☑ | ☑ | ☐ | Unggah Data (Upload) | Hanya internal pengelola data (Operator, Admin, Superadmin) |
| Unggah Data IGT Derivatif Multiguna | ☑ | ☑ | ☑ | ☑ | Unggah Data (Upload) | Pengguna Umum dan internal dapat mengunggah derivatif |
| Unggah Data IGT K/L Lainnya (Eksternal) | ☑ | ☐ | ☐ | ☐ | Unggah Data (Upload) | Khusus Superadmin untuk integrasi dataset rujukan K/L |
| Pilih Berkas Geospasial (.gpkg, .zip, .shp, .geojson) | ☑ | ☑ | ☑ | ☑ | Unggah Data (Upload) | File picker lokal mendukung berbagai format spasial |
| Simpan & Kirim Pengajuan ke Antrean | ☑ | ☑ | ☑ | ☑ | Unggah Data (Upload) | Menyimpan berkas pengajuan baru ke sistem |
| **F. Manajemen Data (Pengajuan, Kompilasi & Verifikasi)** | | | | | | |
| Akses Halaman Manajemen Data | ☑ | ☑ | ☑ | ☐ | Manajemen Data | Pemantauan status pengajuan data internal |
| Manajemen Kategori IGT Utama | ☑ | ☑ | ☑ | ☐ | Manajemen Data | Pengawasan proses kompilasi dan verifikasi IGT Utama |
| Manajemen Kategori IGT Derivatif | ☑ | ☑ | ☑ | ☑ | Manajemen Data | Pengawasan persetujuan layer derivatif |
| Filter Tab Status (Revisi, Diajukan, Terkompilasi, Terintegrasi) | ☑ | ☑ | ☑ | ☐ | Manajemen Data | Navigasi tab status tahapan pengajuan data |
| Cek / Verifikasi Topologi Spasial | ☑ | ☑ | ☐ | ☐ | Manajemen Data | Superadmin & Admin verifikasi topologi pada status Terkompilasi |
| Persetujuan Integrasi Data Spasial | ☑ | ☑ | ☐ | ☐ | Manajemen Data | Superadmin & Admin menyetujui integrasi ke Geoportal |
| Perbaiki Revisi Pengajuan | ☐ | ☐ | ☑ | ☐ | Manajemen Data | Khusus Operator mengunggah perbaikan saat status Revisi |
| Hapus Layer / Pengajuan Eksternal | ☑ | ☐ | ☐ | ☐ | Manajemen Data | Khusus Superadmin pada data eksternal K/L |
| **G. Model Builder Spasial** | | | | | | |
| Akses Modul Model Builder | ☑ | ☑ | ☑ | ☑ | Model Builder Spasial | Katalog modul analisis geospasial otomatis |
| Eksekusi Model Analisis Kesesuaian Lahan | ☑ | ☑ | ☑ | ☑ | Model Builder Spasial | Analisis multi-kriteria kesesuaian lahan langsung di kanvas |
| Eksekusi Model Buffer Kawasan Lindung | ☑ | ☑ | ☑ | ☑ | Model Builder Spasial | Analisis zona penyangga radius sempadan/kawasan lindung |
| Eksekusi Model Overlay RTRW vs Bidang Tanah | ☑ | ☑ | ☑ | ☑ | Model Builder Spasial | Tumpang susun bidang tanah terhadap zonasi pola ruang |
| **H. Alur Derivatif Bidang (Workflow 6-Langkah)** | | | | | | |
| Akses Alur 6-Langkah Derivatif Bidang | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Alur tematik pembuatan derivatif berbasis bidang tanah |
| Langkah 1: Muat Baseline Bidang Tanah QGIS | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Memuat data persil dasar ke memori peta |
| Langkah 2: Atur Struktur Atribut Baru | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Definisi kolom dan tipe data atribut tematik |
| Langkah 3: Pilih Bidang Tanah pada Kanvas | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Interaksi klik persil bidang tanah di QGIS |
| Langkah 4: Isi & Validasi Nilai Atribut | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Input data atribut tematik per persil |
| Langkah 5: Simpan File GeoPackage / GeoJSON | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Ekspor layer tematik derivatif lokal |
| Langkah 6: Join Atribut & Tampilkan Hasil di QGIS | ☑ | ☑ | ☑ | ☐ | Alur Derivatif Bidang | Penggabungan otomatis dan render visual kanvas |

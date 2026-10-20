# Checklist Pengembangan UI IGT-PR menjadi Plugin QGIS

Dokumen ini melacak pekerjaan dari mockup HTML/CSS/JavaScript saat ini menuju plugin QGIS yang benar-benar berjalan. Checklist ini membedakan **UI mockup yang sudah tersedia** dari **implementasi plugin QGIS yang belum dilakukan**.

Status: `[x]` selesai · `[ ]` belum selesai · `[~]` sebagian / perlu diverifikasi.

## 1. UI dan alur yang sudah dimockup

- [x] Preview empat role: Superadmin, Admin, Operator, dan Umum.
- [x] Dashboard/beranda dengan ringkasan status dataset.
- [x] Filter tahun pada Dashboard dan halaman katalog; default 2026, tersedia 2023–2025 dan Semua Tahun.
- [x] Halaman katalog IGT Pertanahan, IGT Tata Ruang, IGT Derivatif, dan IGT Lainnya.
- [x] Pencarian dan pengurutan data pada katalog.
- [x] Tombol aksi WMS/WFS sebagai simulasi UI.
- [x] Halaman Upload Data dan tab kategori berdasarkan role.
- [x] Mockup status pengajuan dan aksi role-specific (mis. verifikasi topologi, revisi, setujui/tolak, hapus).
- [x] Alur enam langkah Upload Derivatif Bidang untuk Operator sebagai simulasi.
- [x] Model Builder tersedia sebagai modul UI bersama.
- [x] Styling responsif untuk panel preview QGIS.
- [x] Navigasi ant halaman dan pemeriksaan tautan lokal dasar.

## 2. Fondasi plugin QGIS — belum dikerjakan

- [ ] Tentukan dan dokumentasikan versi minimum QGIS serta versi Python yang didukung.
- [ ] Buat struktur plugin QGIS yang valid (`metadata.txt`, `__init__.py`, `classFactory`, modul utama).
- [ ] Buat aksi plugin di menu/toolbar QGIS dan lifecycle aktivasi/nonaktivasi.
- [ ] Implementasikan antarmuka sebagai `QDockWidget` atau `QDialog` menggunakan PyQGIS + Qt (PyQt yang sesuai dengan versi QGIS).
- [ ] Port komponen HTML/CSS/JavaScript ke widget Qt, atau tentukan komponen yang memang perlu memakai `QWebEngineView`.
- [ ] Integrasikan stylesheet, ikon, aset, dan navigasi ke struktur paket plugin.
- [ ] Pastikan semua halaman dan kontrol dapat digunakan dalam panel QGIS, termasuk ukuran panel yang berubah.

## 3. Integrasi fungsi QGIS — belum dikerjakan

- [ ] Muat layer nyata ke QGIS project dan tangani layer yang gagal dimuat.
- [ ] Implementasikan Tampilkan di Canvas / zoom ke layer / pengaturan visibilitas.
- [ ] Hubungkan WMS ke URL layanan nyata dan buat layer WMS.
- [ ] Hubungkan WFS ke URL layanan nyata dan buat layer WFS.
- [ ] Implementasikan Load Baseline dari sumber data yang disepakati.
- [ ] Implementasikan validasi geometri dan pemeriksaan topologi menggunakan API QGIS.
- [ ] Implementasikan pemilihan fitur/bidang melalui QGIS map canvas.
- [ ] Implementasikan pembacaan, penulisan, dan ekspor data nyata (mis. GeoPackage), bukan simulasi.
- [ ] Implementasikan join atribut dengan kunci yang tervalidasi dan laporan ID cocok/tidak cocok.
- [ ] Pastikan operasi berat berjalan aman dan UI tidak membeku; gunakan task/background processing bila diperlukan.

## 4. Data, API, dan alur persetujuan — belum dikerjakan

- [ ] Tetapkan sumber data resmi, skema, identifier, dan aturan validasi tiap kategori IGT.
- [ ] Ganti `shared/igt-data.js` dan data dummy dengan sumber data persisten.
- [ ] Tentukan arsitektur penyimpanan dan API/backend jika diperlukan.
- [ ] Implementasikan autentikasi dan otorisasi role di sisi yang tepercaya; UI hiding saja tidak cukup.
- [ ] Implementasikan upload, penyimpanan file, metadata, serta penanganan kegagalan.
- [ ] Implementasikan status pengajuan dan transisi status yang persisten.
- [ ] Implementasikan persetujuan/penolakan, revisi, audit trail, dan siapa yang melakukan perubahan.
- [ ] Terapkan validasi ukuran/tipe file, sanitasi input, dan perlindungan data.
- [ ] Tentukan perilaku offline, koneksi terputus, retry, dan konflik perubahan.

## 5. Hak akses dan konsistensi UI — perlu diverifikasi saat porting

- [ ] Verifikasi setiap role pada plugin QGIS terhadap matriks izin di README.
- [ ] Pastikan Superadmin, Admin, Operator, dan Umum hanya dapat menjalankan aksi yang diizinkan.
- [ ] Pastikan katalog hanya menampilkan dataset sesuai status katalog yang ditetapkan.
- [ ] Pastikan filter tahun tetap default ke 2026, pilihan Semua Tahun berfungsi, dan tahun 2023–2025 tetap tersedia saat datanya belum ada.
- [ ] Pastikan state loading, kosong, sukses, error, dan konfirmasi aksi tersedia.
- [ ] Pastikan aksesibilitas kontrol: label, fokus keyboard, navigasi, dan pesan error.
- [ ] Hapus semua pesan `Simulasi` setelah fungsi terkait benar-benar diimplementasikan dan diuji.

## 6. Pengujian dan distribusi plugin — belum dikerjakan

- [ ] Tambahkan unit test untuk logika status, filter, validasi, dan izin.
- [ ] Uji di QGIS versi minimum dan versi target pada OS yang didukung.
- [ ] Uji alur end-to-end untuk setiap role dan kategori.
- [ ] Uji data besar, file rusak, layanan WMS/WFS gagal, serta koneksi terputus.
- [ ] Tambahkan logging dan pesan error yang bisa ditindaklanjuti.
- [ ] Siapkan dokumentasi instalasi, konfigurasi, penggunaan, dan troubleshooting.
- [ ] Paketkan plugin dan validasi struktur paket.
- [ ] Tentukan mekanisme distribusi/update plugin (internal atau repositori resmi).
- [ ] Lakukan uji penerimaan pengguna sebelum rilis.

## Catatan penting

Checklist ini tidak berarti fungsi yang dicentang pada bagian pertama sudah menjadi plugin QGIS. Bagian tersebut hanya menandai bahwa **alur UI sudah dimockup dalam HTML**. Semua integrasi PyQGIS, data nyata, backend, autentikasi, dan aksi QGIS harus diimplementasikan serta diuji sebelum dapat disebut selesai.

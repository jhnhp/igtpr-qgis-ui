# -*- coding: utf-8 -*-
"""Model data dan konfigurasi untuk plugin Geoportal IGT-PR (Mockup V2)."""

ROLES = {
    'superadmin': {
        'id': 'superadmin',
        'label': 'Superadmin',
        'avatar': 'SA',
        'satker': 'Semua Satker',
        'color': '#1e40af',
        'bg': '#dbeafe',
        'desc': 'Akses penuh seluruh katalog, verifikasi, manajemen pengajuan, dan konfigurasi data.',
    },
    'admin': {
        'id': 'admin',
        'label': 'Admin',
        'avatar': 'AD',
        'satker': 'Kantah Kab. Sleman',
        'color': '#6b21a8',
        'bg': '#ede9fe',
        'desc': 'Verifikasi & persetujuan pengajuan IGT Utama & Derivatif, serta Model Builder.',
    },
    'operator': {
        'id': 'operator',
        'label': 'Operator Pusat',
        'avatar': 'JH',
        'satker': 'Kantah Kab. Sleman',
        'color': '#166534',
        'bg': '#dcfce7',
        'desc': 'Unggah data IGT Utama & Derivatif, perbaikan revisi, dan pemantauan proses kompilasi.',
    },
    'umum': {
        'id': 'umum',
        'label': 'Pengguna Umum',
        'avatar': 'UM',
        'satker': None,
        'color': '#334155',
        'bg': '#f1f5f9',
        'desc': 'Akses katalog terintegrasi, unggah derivatif multiguna, dan pemodelan spasial.',
    },
}


def can_access_wfs(role_id, dataset):
    """Cek apakah role yang aktif memiliki izin untuk mengakses layer fitur WFS:
    - Superadmin: Bisa akses semua WFS.
    - Admin: Bisa akses WFS sesuai satkernya (Kantah Kab. Sleman).
    - Operator: Bisa akses WFS sesuai satkernya (Kantah Kab. Sleman).
    - Umum: Hanya WMS (tidak dapat mengakses WFS).
    """
    if not role_id:
        return False
    r = str(role_id).replace('2', '').lower()
    if r == 'superadmin':
        return True
    if r == 'umum':
        return False
    role_cfg = ROLES.get(r, {})
    user_satker = role_cfg.get('satker') or 'Kantah Kab. Sleman'
    ds_satker = str(dataset.get('satker') or dataset.get('direktorat') or '').strip().lower()
    return 'sleman' in ds_satker or ds_satker == user_satker.lower()


CATEGORIES = {
    'igt-pr': {
        'id': 'igt-pr',
        'label': 'IGT-PR',
        'shortLabel': 'IGT-PR',
        'basis': 'terpadu',
        'color': '#0f294d',
        'bg': '#e0f2fe',
        'desc': 'Katalog terpadu IGT Pertanahan dan IGT Tata Ruang Kementerian ATR/BPN.',
    },
    'pertanahan': {
        'id': 'pertanahan',
        'label': 'IGT Pertanahan',
        'shortLabel': 'Pertanahan',
        'basis': 'bidang',
        'color': '#1f6fd6',
        'bg': '#eff6ff',
        'desc': 'Dataset tematik pertanahan berbasis bidang tanah terintegrasi.',
    },
    'tata-ruang': {
        'id': 'tata-ruang',
        'label': 'IGT Tata Ruang',
        'shortLabel': 'Tata Ruang',
        'basis': 'kawasan',
        'color': '#047857',
        'bg': '#ecfdf5',
        'desc': 'Dataset rencana tata ruang dan pemanfaatan ruang berbasis kawasan.',
    },
    'derivatif': {
        'id': 'derivatif',
        'label': 'IGT Derivatif',
        'shortLabel': 'IGT Derivatif',
        'basis': 'kawasan',
        'color': '#7c3aed',
        'bg': '#f5f3ff',
        'desc': 'Layer tematik turunan hasil analisis spasial multiguna yang telah disetujui.',
    },
    'lainnya': {
        'id': 'lainnya',
        'label': 'IGT K/L Lainnya',
        'shortLabel': 'IGT K/L Lainnya',
        'basis': 'kawasan',
        'color': '#0284c7',
        'bg': '#f0f9ff',
        'desc': 'Layer geospasial rujukan dari kementerian dan lembaga eksternal.',
    },
}

DATASETS = [
    # IGT Pertanahan
    {
        'category': 'pertanahan', 'id': 'IGT-PR-001', 'name': 'IGT Bidang Tanah',
        'direktorat': 'Direktorat Pengukuran dan Pemetaan Kadastral', 'satker': 'Kantah Kab. Sleman',
        'scope': 'Kab. Sleman (Multi-Desa)', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-002', 'name': 'IGT Penguasaan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kab. Bantul',
        'scope': 'Kab. Bantul', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Bantul',
        'date': '12 Nov 2025', 'updated': '12 Nov 2025', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-003', 'name': 'IGT Pemilikan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kota Yogyakarta',
        'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '05 Agu 2025', 'updated': '05 Agu 2025', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-004', 'name': 'IGT Penggunaan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kab. Kulon Progo',
        'scope': 'Kab. Kulon Progo', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Kulon Progo',
        'date': '20 Sep 2024', 'updated': '20 Sep 2024', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-005', 'name': 'IGT Pemanfaatan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kab. Gunungkidul',
        'scope': 'Kab. Gunungkidul', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Gunungkidul',
        'date': '14 Jun 2024', 'updated': '14 Jun 2024', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-006', 'name': 'IGT Sebaran Lokasi Pemberdayaan Tanah Masyarakat',
        'direktorat': 'Direktorat Pemberdayaan Tanah Masyarakat', 'satker': 'Kanwil BPN D.I. Yogyakarta',
        'scope': 'Multi-Area (Kab. Gunungkidul & Kulon Progo)', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2023', 'updated': '18 Okt 2023', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-007', 'name': 'IGT Pertimbangan Teknis Pertanahan',
        'direktorat': 'Direktorat Penatagunaan Tanah', 'satker': 'Kantah Kab. Sleman',
        'scope': 'Kab. Sleman', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-009', 'name': 'IGT Tanah Terindikasi Telantar',
        'direktorat': 'Direktur Penertiban Penguasaan, Pemilikan dan Penggunaan Tanah',
        'satker': 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang',
        'scope': 'Multi-Area (Kab. Sleman, Bantul, Kulon Progo)', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-year', 'multiLabel': 'Multi-Layer',
        'subLayers': [
            {'id': 'TTT-2026', 'name': 'Tanah Terindikasi Telantar 2026', 'label': 'Tahun 2026', 'year': '2026', 'updated': '18 Okt 2026', 'scope': 'Multi-Area (Sleman, Bantul)'},
            {'id': 'TTT-2024', 'name': 'Tanah Terindikasi Telantar 2024', 'label': 'Tahun 2024', 'year': '2024', 'updated': '15 Okt 2024', 'scope': 'Multi-Area (Kulon Progo)'},
        ]
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-010', 'name': 'IGT Indikasi Pelanggaran Pemanfaatan Ruang',
        'direktorat': 'Direktorat Penertiban Pemanfaatan Ruang',
        'satker': 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang',
        'scope': 'Multi-Area (Kawasan Perkotaan Yogyakarta)', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-011', 'name': 'IGT Hak Atas Tanah',
        'direktorat': 'Sekretariat Direktorat Jenderal Penetapan Hak dan Pendaftaran Tanah',
        'satker': 'Kantah Kab. Sleman', 'scope': 'Kab. Sleman', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-012', 'name': 'IGT Informasi Mengenai Sengketa, Konflik, dan Perkara Pertanahan',
        'direktorat': 'Sekretariat Direktorat Jenderal Penanganan Sengketa dan Konflik Pertanahan',
        'satker': 'Kanwil BPN D.I. Yogyakarta', 'scope': 'Lintas Kabupaten/Kota', 'prov': 'D.I. Yogyakarta', 'kab': 'Lintas Kabupaten/Kota',
        'date': '14 Mei 2021', 'updated': '14 Mei 2021', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-013', 'name': 'IGT Potensi Subjek Konsolidasi Tanah',
        'direktorat': 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan',
        'satker': 'Kantah Kab. Kulon Progo', 'scope': 'Kab. Kulon Progo', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Kulon Progo',
        'date': '09 Des 2025', 'updated': '09 Des 2025', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-014', 'name': 'IGT Nilai Bidang Tanah',
        'direktorat': 'Direktorat Penilaian Tanah dan Ekonomi Pertanahan',
        'satker': 'Kantah Kota Yogyakarta', 'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '22 Agu 2024', 'updated': '22 Agu 2024', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-015', 'name': 'IGT Desain Konsolidasi Tanah',
        'direktorat': 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan',
        'satker': 'Kantah Kab. Sleman', 'scope': 'Kab. Sleman', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-016', 'name': 'IGT Hasil Penerapan Desain Konsolidasi Tanah',
        'direktorat': 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan',
        'satker': 'Kantah Kab. Sleman', 'scope': 'Kab. Sleman', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },

    # IGT Tata Ruang
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-017', 'name': 'IGT RTRW Nasional',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'Nasional (Seluruh Wilayah RI)', 'prov': 'Nasional', 'kab': 'Seluruh Indonesia',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-018', 'name': 'IGT RTRW Provinsi',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Kanwil BPN D.I. Yogyakarta', 'scope': 'Provinsi D.I. Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Lintas Kabupaten/Kota',
        'date': '10 Nov 2025', 'updated': '10 Nov 2025', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-019', 'name': 'IGT RTRW Kabupaten',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Ditjen Tata Ruang', 'scope': 'Multi-Kabupaten', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-scale', 'multiLabel': 'Multi-Layer',
        'subLayers': [
            {'id': 'RTRW-50K', 'name': 'RTRW Kab Skala 1:50.000', 'label': 'Skala 1:50.000', 'skala': '1:50.000', 'updated': '18 Okt 2026', 'scope': 'Pola Ruang Wilayah Kabupaten'},
            {'id': 'RTRW-25K', 'name': 'RTRW Kab Skala 1:25.000', 'label': 'Skala 1:25.000', 'skala': '1:25.000', 'updated': '15 Jul 2026', 'scope': 'Kawasan Strategis Kabupaten'},
        ]
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-020', 'name': 'IGT RTRW Kota',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Ditjen Tata Ruang', 'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '16 Jul 2024', 'updated': '16 Jul 2024', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-021', 'name': 'IGT RDTR Kawasan Perbatasan Negara',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'Kawasan Perbatasan PLBN', 'prov': 'Kalimantan Barat', 'kab': 'Multi-Kabupaten',
        'date': '24 Okt 2023', 'updated': '24 Okt 2023', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-022', 'name': 'IGT RTR Pulau/Kepulauan',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'Pulau Jawa - Bali', 'prov': 'Lintas Wilayah', 'kab': 'Lintas Wilayah',
        'date': '15 Des 2019', 'updated': '15 Des 2019', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-023', 'name': 'IGT RTR Kawasan Strategis Nasional',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'KSN Borobudur & Sekitarnya', 'prov': 'D.I. Yogyakarta & Jawa Tengah', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-024', 'name': 'IGT RDTR Kabupaten/Kota',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Kantah Kab. Sleman', 'scope': 'Kab. Sleman (Kawasan Depok)', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-scale', 'multiLabel': 'Multi-Layer',
        'subLayers': [
            {'id': 'RDTR-5K', 'name': 'RDTR Kab/Kota Skala 1:5.000', 'label': 'Skala 1:5.000', 'skala': '1:5.000', 'updated': '18 Okt 2026', 'scope': 'Kawasan Perkotaan Depok (Blok Rinci)'},
            {'id': 'RDTR-10K', 'name': 'RDTR Kab/Kota Skala 1:10.000', 'label': 'Skala 1:10.000', 'skala': '1:10.000', 'updated': '12 Agt 2026', 'scope': 'Aglomerasi Perkotaan Sleman'},
            {'id': 'RDTR-25K', 'name': 'RDTR Kab/Kota Skala 1:25.000', 'label': 'Skala 1:25.000', 'skala': '1:25.000', 'updated': '10 Jun 2026', 'scope': 'Kawasan Penyangga Wilayah'},
        ]
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-025', 'name': 'IGT KKPR',
        'direktorat': 'Direktorat Sinkronisasi Pemanfaatan Ruang', 'satker': 'Kanwil BPN D.I. Yogyakarta',
        'scope': 'Provinsi D.I. Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Lintas Kabupaten/Kota',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-026', 'name': 'IGT Lahan Baku Sawah',
        'direktorat': 'Direktorat Penatagunaan Tanah', 'satker': 'Kantah Kab. Bantul',
        'scope': 'Kab. Bantul', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Bantul',
        'date': '18 Okt 2024', 'updated': '18 Okt 2024', 'status': 'Terintegrasi',
        'multiType': 'multi-year', 'multiLabel': 'Multi-Layer',
        'subLayers': [
            {'id': 'LBS-2024', 'name': 'Lahan Baku Sawah 2024', 'label': 'Tahun 2024', 'year': '2024', 'updated': '18 Okt 2024', 'scope': 'Kab. Bantul'},
            {'id': 'LBS-2023', 'name': 'Lahan Baku Sawah 2023', 'label': 'Tahun 2023', 'year': '2023', 'updated': '15 Des 2023', 'scope': 'Kab. Bantul'},
            {'id': 'LBS-2021', 'name': 'Lahan Baku Sawah 2021', 'label': 'Tahun 2021', 'year': '2021', 'updated': '20 Nov 2021', 'scope': 'Kab. Bantul'},
            {'id': 'LBS-2019', 'name': 'Lahan Baku Sawah 2019', 'label': 'Tahun 2019', 'year': '2019', 'updated': '10 Sep 2019', 'scope': 'Kab. Bantul'},
        ]
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-038', 'name': 'IGT Zona Nilai Tanah',
        'direktorat': 'Direktorat Penilaian Tanah dan Ekonomi Pertanahan', 'satker': 'Kantah Kab. Sleman',
        'scope': 'Kab. Sleman', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Sleman',
        'date': '17 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-year', 'multiLabel': 'Multi-Layer',
        'subLayers': [
            {'id': 'ZNT-2026', 'name': 'Zona Nilai Tanah 2026', 'label': 'Tahun 2026', 'year': '2026', 'updated': '18 Okt 2026', 'scope': 'Kab. Sleman (Pembaruan Terkini)'},
            {'id': 'ZNT-2025', 'name': 'Zona Nilai Tanah 2025', 'label': 'Tahun 2025', 'year': '2025', 'updated': '10 Des 2025', 'scope': 'Kab. Sleman'},
            {'id': 'ZNT-2024', 'name': 'Zona Nilai Tanah 2024', 'label': 'Tahun 2024', 'year': '2024', 'updated': '14 Nov 2024', 'scope': 'Kab. Sleman'},
        ]
    },

    # IGT Derivatif Multiguna
    {
        'category': 'derivatif', 'id': 'DRV-2026-008', 'name': 'Derivatif Kawasan Hutan',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kanwil BPN D.I. Yogyakarta',
        'scope': 'Kab. Gunungkidul & Bantul', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '16 Okt 2026', 'updated': '17 Okt 2026', 'status': 'Disetujui',
    },
    {
        'category': 'derivatif', 'id': 'DRV-2026-005', 'name': 'Derivatif Bidang Wilayah B',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kota Yogyakarta',
        'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '12 Okt 2026', 'updated': '13 Okt 2026', 'status': 'Disetujui',
    },

    # IGT Lainnya (Eksternal)
    {
        'category': 'lainnya', 'id': 'IGT-EXT-004', 'name': 'Rencana Tata Ruang Wilayah',
        'instansi': 'Dinas Pertanahan dan Tata Ruang DIY', 'direktorat': 'Dinas Pertanahan dan Tata Ruang DIY',
        'satker': 'Dinas Pertanahan dan Tata Ruang DIY', 'scope': 'Provinsi D.I. Yogyakarta',
        'prov': 'D.I. Yogyakarta', 'kab': 'Lintas Kabupaten/Kota',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Tersedia',
    },
    {
        'category': 'lainnya', 'id': 'IGT-EXT-003', 'name': 'Tutupan Lahan Nasional',
        'instansi': 'Kementerian Lingkungan Hidup', 'direktorat': 'Kementerian Lingkungan Hidup',
        'satker': 'Kementerian Lingkungan Hidup', 'scope': 'Nasional',
        'prov': 'Nasional', 'kab': 'Seluruh Indonesia',
        'date': '15 Okt 2026', 'updated': '15 Okt 2026', 'status': 'Tersedia',
    },
    {
        'category': 'lainnya', 'id': 'IGT-EXT-002', 'name': 'Batas Wilayah Administrasi',
        'instansi': 'Badan Informasi Geospasial', 'direktorat': 'Badan Informasi Geospasial',
        'satker': 'Badan Informasi Geospasial', 'scope': 'Nasional',
        'prov': 'Nasional', 'kab': 'Seluruh Indonesia',
        'date': '12 Okt 2026', 'updated': '12 Okt 2026', 'status': 'Tersedia',
    },
    {
        'category': 'lainnya', 'id': 'IGT-EXT-001', 'name': 'Peta Risiko Bencana',
        'instansi': 'Badan Nasional Penanggulangan Bencana', 'direktorat': 'Badan Nasional Penanggulangan Bencana',
        'satker': 'Badan Nasional Penanggulangan Bencana', 'scope': 'D.I. Yogyakarta & Jawa Tengah',
        'prov': 'D.I. Yogyakarta & Jawa Tengah', 'kab': 'Multi-Kabupaten',
        'date': '10 Okt 2026', 'updated': '10 Okt 2026', 'status': 'Tersedia',
    },
]

# Pengajuan untuk halaman Manajemen Data
SUBMISSIONS = [
    {
        'id': 'PGJ-2026-001', 'layer': 'IGT Kemampuan Tanah', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Kulon Progo', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '17 Okt 2026', 'status': 'Revisi',
        'note': 'Periksa geometri bertampalan dan lengkapi atribut kesesuaian lahan.',
    },
    {
        'id': 'PGJ-2026-002', 'layer': 'IGT Inventarisasi Tanah Kritis', 'category': 'pertanahan',
        'satker': 'Kanwil BPN D.I. Yogyakarta', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '18 Okt 2026', 'status': 'Revisi',
        'note': 'Perbaiki kelengkapan atribut dan pastikan kode wilayah konsisten.',
    },
    {
        'id': 'PGJ-2026-003', 'layer': 'IGT Sebaran Tanah Objek Reforma Agraria', 'category': 'tata-ruang',
        'satker': 'Kanwil BPN D.I. Yogyakarta', 'direktorat': 'Direktorat Landreform',
        'date': '17 Okt 2026', 'status': 'Diajukan',
        'note': 'Menunggu telaah kelayakan spasial dan kompilasi.',
    },
    {
        'id': 'PGJ-2026-004', 'layer': 'IGT Unsur Dasar Pertanahan', 'category': 'tata-ruang',
        'satker': 'Kantah Kota Yogyakarta', 'direktorat': 'Direktorat Pengukuran Dan Pemetaan Dasar Pertanahan Ruang',
        'date': '17 Okt 2026', 'status': 'Diajukan',
        'note': 'Menunggu proses validasi batas administrasi.',
    },
    {
        'id': 'PGJ-2026-005', 'layer': 'Derivatif Bidang Wilayah A', 'category': 'derivatif',
        'satker': 'Kantah Kab. Sleman', 'direktorat': 'Direktorat Survei Dan Pemetaan Tematik',
        'date': '15 Okt 2026', 'status': 'Diajukan',
        'note': 'Pengajuan derivatif baru menanti persetujuan verifikator.',
    },
    {
        'id': 'PGJ-2026-006', 'layer': 'IGT Lahan Baku Sawah', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Bantul', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '17 Okt 2026', 'status': 'Terkompilasi',
        'note': 'Kompilasi selesai. Siap untuk verifikasi topologi dan persetujuan integrasi.',
    },
    {
        'id': 'PGJ-2026-007', 'layer': 'IGT Neraca Penatagunaan Tanah', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Sleman', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '15 Des 2025', 'status': 'Terkompilasi',
        'note': 'Kompilasi data kabupaten selesai.',
    },
    {
        'id': 'PGJ-2026-008', 'layer': 'IGT Analisa Tanah Objek Reforma Agraria', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Gunungkidul', 'direktorat': 'Direktorat Landreform',
        'date': '20 Nov 2024', 'status': 'Terkompilasi',
        'note': 'Data spasial siap diajukan untuk integrasi nasional.',
    },
    {
        'id': 'PGJ-2023-011', 'layer': 'IGT Potensi WP3WT', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Gunungkidul', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '18 Okt 2023', 'status': 'Terkompilasi',
        'note': 'Kompilasi potensi tanah selesai.',
    },
    {
        'id': 'PGJ-2021-012', 'layer': 'IGT Persebaran Pulau-Pulau Kecil Terluar', 'category': 'tata-ruang',
        'satker': 'Ditjen Penataan Agraria', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '12 Nov 2021', 'status': 'Terkompilasi',
        'note': 'Kompilasi batas pulau terluar selesai.',
    },
    {
        'id': 'PGJ-2019-013', 'layer': 'IGT Tanah Timbul', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Kulon Progo', 'direktorat': 'Direktorat Penatagunaan Tanah',
        'date': '15 Sep 2019', 'status': 'Terkompilasi',
        'note': 'Kompilasi data pesisir selesai.',
    },
    {
        'id': 'PGJ-2026-009', 'layer': 'IGT Bidang Tanah', 'category': 'pertanahan',
        'satker': 'Kantah Kab. Sleman', 'direktorat': 'Direktorat Pengukuran dan Pemetaan Kadastral',
        'date': '18 Okt 2026', 'status': 'Terintegrasi',
        'note': 'Dataset telah terintegrasi di geoportal pusat.',
    },
    {
        'id': 'PGJ-2026-010', 'layer': 'IGT RDTR Kabupaten/Kota', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Sleman', 'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'date': '18 Okt 2026', 'status': 'Terintegrasi',
        'note': 'Dataset multi-skala resmi telah dipublikasikan.',
    },
]


INDONESIA_REGIONS = {
    'Aceh': ['Aceh Barat', 'Aceh Barat Daya', 'Aceh Besar', 'Aceh Jaya', 'Aceh Selatan', 'Aceh Singkil', 'Aceh Tamiang', 'Aceh Tengah', 'Aceh Tenggara', 'Aceh Timur', 'Aceh Utara', 'Bener Meriah', 'Bireuen', 'Gayo Lues', 'Kota Banda Aceh', 'Kota Langsa', 'Kota Lhokseumawe', 'Kota Sabang', 'Kota Subulussalam', 'Nagan Raya', 'Pidie', 'Pidie Jaya', 'Simeulue'],
    'Bali': ['Badung', 'Bangli', 'Buleleng', 'Gianyar', 'Jembrana', 'Karangasem', 'Klungkung', 'Kota Denpasar', 'Tabanan'],
    'Banten': ['Kota Cilegon', 'Kota Serang', 'Kota Tangerang', 'Kota Tangerang Selatan', 'Lebak', 'Pandeglang', 'Serang', 'Tangerang'],
    'Bengkulu': ['Bengkulu Selatan', 'Bengkulu Tengah', 'Bengkulu Utara', 'Kaur', 'Kepahiang', 'Kota Bengkulu', 'Lebong', 'Mukomuko', 'Rejang Lebong', 'Seluma'],
    'Daerah Istimewa Yogyakarta': ['Bantul', 'Gunungkidul', 'Kota Yogyakarta', 'Kulon Progo', 'Sleman'],
    'Daerah Khusus Ibukota Jakarta': ['Administrasi Kepulauan Seribu', 'Kota Administrasi Jakarta Barat', 'Kota Administrasi Jakarta Pusat', 'Kota Administrasi Jakarta Selatan', 'Kota Administrasi Jakarta Timur', 'Kota Administrasi Jakarta Utara'],
    'Gorontalo': ['Boalemo', 'Bone Bolango', 'Gorontalo', 'Gorontalo Utara', 'Kota Gorontalo', 'Pohuwato'],
    'Jambi': ['Batanghari', 'Bungo', 'Kerinci', 'Kota Jambi', 'Kota Sungai Penuh', 'Merangin', 'Muaro Jambi', 'Sarolangun', 'Tanjung Jabung Barat', 'Tanjung Jabung Timur', 'Tebo'],
    'Jawa Barat': ['Bandung', 'Bandung Barat', 'Bekasi', 'Bogor', 'Ciamis', 'Cianjur', 'Cirebon', 'Garut', 'Indramayu', 'Karawang', 'Kota Bandung', 'Kota Banjar', 'Kota Bekasi', 'Kota Bogor', 'Kota Cimahi', 'Kota Cirebon', 'Kota Depok', 'Kota Sukabumi', 'Kota Tasikmalaya', 'Kuningan', 'Majalengka', 'Pangandaran', 'Purwakarta', 'Subang', 'Sukabumi', 'Sumedang', 'Tasikmalaya'],
    'Jawa Tengah': ['Banjarnegara', 'Banyumas', 'Batang', 'Blora', 'Boyolali', 'Brebes', 'Cilacap', 'Demak', 'Grobogan', 'Jepara', 'Karanganyar', 'Kebumen', 'Kendal', 'Klaten', 'Kota Magelang', 'Kota Pekalongan', 'Kota Salatiga', 'Kota Semarang', 'Kota Surakarta', 'Kota Tegal', 'Kudus', 'Magelang', 'Pati', 'Pekalongan', 'Pemalang', 'Purbalingga', 'Purworejo', 'Rembang', 'Semarang', 'Sragen', 'Sukoharjo', 'Tegal', 'Temanggung', 'Wonogiri', 'Wonosobo'],
    'Jawa Timur': ['Bangkalan', 'Banyuwangi', 'Blitar', 'Bojonegoro', 'Bondowoso', 'Gresik', 'Jember', 'Jombang', 'Kediri', 'Kota Batu', 'Kota Blitar', 'Kota Kediri', 'Kota Madiun', 'Kota Malang', 'Kota Mojokerto', 'Kota Pasuruan', 'Kota Probolinggo', 'Kota Surabaya', 'Lamongan', 'Lumajang', 'Madiun', 'Magetan', 'Malang', 'Mojokerto', 'Nganjuk', 'Ngawi', 'Pacitan', 'Pamekasan', 'Pasuruan', 'Ponorogo', 'Probolinggo', 'Sampang', 'Sidoarjo', 'Situbondo', 'Sumenep', 'Trenggalek', 'Tuban', 'Tulungagung'],
    'Kalimantan Barat': ['Bengkayang', 'Kapuas Hulu', 'Kayong Utara', 'Ketapang', 'Kota Pontianak', 'Kota Singkawang', 'Kubu Raya', 'Landak', 'Melawi', 'Mempawah', 'Sambas', 'Sanggau', 'Sekadau', 'Sintang'],
    'Kalimantan Selatan': ['Balangan', 'Banjar', 'Barito Kuala', 'Hulu Sungai Selatan', 'Hulu Sungai Tengah', 'Hulu Sungai Utara', 'Kota Banjarbaru', 'Kota Banjarmasin', 'Kotabaru', 'Tabalong', 'Tanah Bumbu', 'Tanah Laut', 'Tapin'],
    'Kalimantan Tengah': ['Barito Selatan', 'Barito Timur', 'Barito Utara', 'Gunung Mas', 'Kapuas', 'Katingan', 'Kota Palangkaraya', 'Kotawaringin Barat', 'Kotawaringin Timur', 'Lamandau', 'Murung Raya', 'Pulang Pisau', 'Seruyan', 'Sukamara'],
    'Kalimantan Timur': ['Berau', 'Kota Balikpapan', 'Kota Bontang', 'Kota Samarinda', 'Kutai Barat', 'Kutai Kartanegara', 'Kutai Timur', 'Mahakam Ulu', 'Paser', 'Penajam Paser Utara'],
    'Kalimantan Utara': ['Bulungan', 'Kota Tarakan', 'Malinau', 'Nunukan', 'Tana Tidung'],
    'Kepulauan Bangka Belitung': ['Bangka', 'Bangka Barat', 'Bangka Selatan', 'Bangka Tengah', 'Belitung', 'Belitung Timur', 'Kota Pangkal Pinang'],
    'Kepulauan Riau': ['Bintan', 'Karimun', 'Kepulauan Anambas', 'Kota Batam', 'Kota Tanjung Pinang', 'Lingga', 'Natuna'],
    'Lampung': ['Kota Bandar Lampung', 'Kota Metro', 'Lampung Barat', 'Lampung Selatan', 'Lampung Tengah', 'Lampung Timur', 'Lampung Utara', 'Mesuji', 'Pesawaran', 'Pesisir Barat', 'Pringsewu', 'Tanggamus', 'Tulang Bawang', 'Tulang Bawang Barat', 'Way Kanan'],
    'Maluku': ['Buru', 'Buru Selatan', 'Kepulauan Aru', 'Kepulauan Tanimbar', 'Kota Ambon', 'Kota Tual', 'Maluku Barat Daya', 'Maluku Tengah', 'Maluku Tenggara', 'Seram Bagian Barat', 'Seram Bagian Timur'],
    'Maluku Utara': ['Halmahera Barat', 'Halmahera Selatan', 'Halmahera Tengah', 'Halmahera Timur', 'Halmahera Utara', 'Kepulauan Sula', 'Kota Ternate', 'Kota Tidore Kepulauan', 'Pulau Morotai', 'Pulau Taliabu'],
    'Nusa Tenggara Barat': ['Bima', 'Dompu', 'Kota Bima', 'Kota Mataram', 'Lombok Barat', 'Lombok Tengah', 'Lombok Timur', 'Lombok Utara', 'Sumbawa', 'Sumbawa Barat'],
    'Nusa Tenggara Timur': ['Alor', 'Belu', 'Ende', 'Flores Timur', 'Kota Kupang', 'Kupang', 'Lembata', 'Malaka', 'Manggarai', 'Manggarai Barat', 'Manggarai Timur', 'Nagekeo', 'Ngada', 'Rote Ndao', 'Sabu Raijua', 'Sikka', 'Sumba Barat', 'Sumba Barat Daya', 'Sumba Tengah', 'Sumba Timur', 'Timor Tengah Selatan', 'Timor Tengah Utara'],
    'Papua': ['Biak Numfor', 'Jayapura', 'Keerom', 'Kepulauan Yapen', 'Kota Jayapura', 'Mamberamo Raya', 'Sarmi', 'Supiori', 'Waropen'],
    'Papua Barat': ['Fak Fak', 'Kaimana', 'Manokwari', 'Manokwari Selatan', 'Pegunungan Arfak', 'Teluk Bintuni', 'Teluk Wondama'],
    'Papua Barat Daya': ['Kota Sorong', 'Maybrat', 'Raja Ampat', 'Sorong', 'Sorong Selatan', 'Tambrauw'],
    'Papua Pegunungan': ['Jayawijaya', 'Lanny Jaya', 'Mamberamo Tengah', 'Nduga', 'Pegunungan Bintang', 'Tolikara', 'Yahukimo', 'Yalimo'],
    'Papua Selatan': ['Asmat', 'Boven Digoel', 'Mappi', 'Merauke'],
    'Papua Tengah': ['Deiyai', 'Dogiyai', 'Intan Jaya', 'Mimika', 'Nabire', 'Paniai', 'Puncak', 'Puncak Jaya'],
    'Riau': ['Bengkalis', 'Indragiri Hilir', 'Indragiri Hulu', 'Kampar', 'Kepulauan Meranti', 'Kota Dumai', 'Kota Pekanbaru', 'Kuantan Singingi', 'Pelalawan', 'Rokan Hilir', 'Rokan Hulu', 'Siak'],
    'Sulawesi Barat': ['Majene', 'Mamasa', 'Mamuju', 'Mamuju Tengah', 'Pasangkayu', 'Polewali Mandar'],
    'Sulawesi Selatan': ['Bantaeng', 'Barru', 'Bone', 'Bulukumba', 'Enrekang', 'Gowa', 'Jeneponto', 'Kepulauan Selayar', 'Kota Makassar', 'Kota Palopo', 'Kota Parepare', 'Luwu', 'Luwu Timur', 'Luwu Utara', 'Maros', 'Pangkajene Dan Kepulauan', 'Pinrang', 'Sidenreng Rappang', 'Sinjai', 'Soppeng', 'Takalar', 'Tana Toraja', 'Toraja Utara', 'Wajo'],
    'Sulawesi Tengah': ['Banggai', 'Banggai Kepulauan', 'Banggai Laut', 'Buol', 'Donggala', 'Kota Palu', 'Morowali', 'Morowali Utara', 'Parigi Moutong', 'Poso', 'Sigi', 'Tojo Una Una', 'Toli-Toli'],
    'Sulawesi Tenggara': ['Bombana', 'Buton', 'Buton Selatan', 'Buton Tengah', 'Buton Utara', 'Kolaka', 'Kolaka Timur', 'Kolaka Utara', 'Konawe', 'Konawe Kepulauan', 'Konawe Selatan', 'Konawe Utara', 'Kota Bau Bau', 'Kota Kendari', 'Muna', 'Muna Barat', 'Wakatobi'],
    'Sulawesi Utara': ['Bolaang Mongondow', 'Bolaang Mongondow Selatan', 'Bolaang Mongondow Timur', 'Bolaang Mongondow Utara', 'Kep. Siau Tagulandang Biaro', 'Kepulauan Sangihe', 'Kepulauan Talaud', 'Kota Bitung', 'Kota Kotamobagu', 'Kota Manado', 'Kota Tomohon', 'Minahasa', 'Minahasa Selatan', 'Minahasa Tenggara', 'Minahasa Utara'],
    'Sumatera Barat': ['Agam', 'Dharmasraya', 'Kepulauan Mentawai', 'Kota Bukittinggi', 'Kota Padang', 'Kota Padang Panjang', 'Kota Pariaman', 'Kota Payakumbuh', 'Kota Sawahlunto', 'Kota Solok', 'Lima Puluh Kota', 'Padang Pariaman', 'Pasaman', 'Pasaman Barat', 'Pesisir Selatan', 'Sijunjung', 'Solok', 'Solok Selatan', 'Tanah Datar'],
    'Sumatera Selatan': ['Banyuasin', 'Empat Lawang', 'Kota Lubuk Linggau', 'Kota Pagar Alam', 'Kota Palembang', 'Kota Prabumulih', 'Lahat', 'Muara Enim', 'Musi Banyuasin', 'Musi Rawas', 'Musi Rawas Utara', 'Ogan Ilir', 'Ogan Komering Ilir', 'Ogan Komering Ulu', 'Ogan Komering Ulu Selatan', 'Ogan Komering Ulu Timur', 'Penukal Abab Lematang Ilir'],
    'Sumatera Utara': ['Asahan', 'Batu Bara', 'Dairi', 'Deli Serdang', 'Humbang Hasundutan', 'Karo', 'Kota Binjai', 'Kota Gunungsitoli', 'Kota Medan', 'Kota Padangsidimpuan', 'Kota Pematangsiantar', 'Kota Sibolga', 'Kota Tanjungbalai', 'Kota Tebing Tinggi', 'Labuhanbatu', 'Labuhanbatu Selatan', 'Labuhanbatu Utara', 'Langkat', 'Mandailing Natal', 'Nias', 'Nias Barat', 'Nias Selatan', 'Nias Utara', 'Padang Lawas', 'Padang Lawas Utara', 'Pakpak Bharat', 'Samosir', 'Serdang Bedagai', 'Simalungun', 'Tapanuli Selatan', 'Tapanuli Tengah', 'Tapanuli Utara', 'Toba'],
}


# -*- coding: utf-8 -*-
"""Model data dan konfigurasi untuk plugin Geoportal IGT-PR (Mockup V2)."""

ROLES = {
    'superadmin': {
        'id': 'superadmin',
        'label': 'Superadmin',
        'avatar': 'SA',
        'color': '#1e40af',
        'bg': '#dbeafe',
        'desc': 'Akses penuh seluruh katalog, verifikasi, manajemen pengajuan, dan konfigurasi data.',
    },
    'admin': {
        'id': 'admin',
        'label': 'Admin',
        'avatar': 'AD',
        'color': '#6b21a8',
        'bg': '#ede9fe',
        'desc': 'Verifikasi & persetujuan pengajuan IGT Utama & Derivatif, serta Model Builder.',
    },
    'operator': {
        'id': 'operator',
        'label': 'Operator Pusat',
        'avatar': 'JH',
        'color': '#166534',
        'bg': '#dcfce7',
        'desc': 'Unggah data IGT Utama & Derivatif, perbaikan revisi, dan pemantauan proses kompilasi.',
    },
    'umum': {
        'id': 'umum',
        'label': 'Pengguna Umum',
        'avatar': 'UM',
        'color': '#334155',
        'bg': '#f1f5f9',
        'desc': 'Akses katalog terintegrasi, unggah derivatif multiguna, dan pemodelan spasial.',
    },
}

CATEGORIES = {
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
        'label': 'IGT Derivatif Multiguna',
        'shortLabel': 'IGT Derivatif',
        'basis': 'kawasan',
        'color': '#7c3aed',
        'bg': '#f5f3ff',
        'desc': 'Layer tematik turunan hasil analisis spasial multiguna yang telah disetujui.',
    },
    'lainnya': {
        'id': 'lainnya',
        'label': 'IGT Lainnya',
        'shortLabel': 'Lainnya',
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
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-003', 'name': 'IGT Pemilikan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kota Yogyakarta',
        'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-004', 'name': 'IGT Penggunaan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kab. Kulon Progo',
        'scope': 'Kab. Kulon Progo', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Kulon Progo',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-005', 'name': 'IGT Pemanfaatan Tanah',
        'direktorat': 'Direktorat Survei Dan Pemetaan Tematik', 'satker': 'Kantah Kab. Gunungkidul',
        'scope': 'Kab. Gunungkidul', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Gunungkidul',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-006', 'name': 'IGT Sebaran Lokasi Pemberdayaan Tanah Masyarakat',
        'direktorat': 'Direktorat Pemberdayaan Tanah Masyarakat', 'satker': 'Kanwil BPN D.I. Yogyakarta',
        'scope': 'Multi-Area (Kab. Gunungkidul & Kulon Progo)', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
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
        'multiType': 'multi-year', 'multiLabel': 'Multi-Year',
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
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-013', 'name': 'IGT Potensi Subjek Konsolidasi Tanah',
        'direktorat': 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan',
        'satker': 'Kantah Kab. Kulon Progo', 'scope': 'Kab. Kulon Progo', 'prov': 'D.I. Yogyakarta', 'kab': 'Kab. Kulon Progo',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'pertanahan', 'id': 'IGT-PR-014', 'name': 'IGT Nilai Bidang Tanah',
        'direktorat': 'Direktorat Penilaian Tanah dan Ekonomi Pertanahan',
        'satker': 'Kantah Kota Yogyakarta', 'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
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
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-019', 'name': 'IGT RTRW Kabupaten',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Ditjen Tata Ruang', 'scope': 'Multi-Kabupaten', 'prov': 'D.I. Yogyakarta', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-scale', 'multiLabel': 'Multi-Skala',
        'subLayers': [
            {'id': 'RTRW-50K', 'name': 'RTRW Kab Skala 1:50.000', 'label': 'Skala 1:50.000', 'skala': '1:50.000', 'updated': '18 Okt 2026', 'scope': 'Pola Ruang Wilayah Kabupaten'},
            {'id': 'RTRW-25K', 'name': 'RTRW Kab Skala 1:25.000', 'label': 'Skala 1:25.000', 'skala': '1:25.000', 'updated': '15 Jul 2026', 'scope': 'Kawasan Strategis Kabupaten'},
        ]
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-020', 'name': 'IGT RTRW Kota',
        'direktorat': 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I',
        'satker': 'Ditjen Tata Ruang', 'scope': 'Kota Yogyakarta', 'prov': 'D.I. Yogyakarta', 'kab': 'Kota Yogyakarta',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-021', 'name': 'IGT RDTR Kawasan Perbatasan Negara',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'Kawasan Perbatasan PLBN', 'prov': 'Kalimantan Barat', 'kab': 'Multi-Kabupaten',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
    },
    {
        'category': 'tata-ruang', 'id': 'IGT-PR-022', 'name': 'IGT RTR Pulau/Kepulauan',
        'direktorat': 'Direktorat Perencanaan Tata Ruang', 'satker': 'Ditjen Tata Ruang',
        'scope': 'Pulau Jawa - Bali', 'prov': 'Lintas Wilayah', 'kab': 'Lintas Wilayah',
        'date': '18 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
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
        'multiType': 'multi-scale', 'multiLabel': 'Multi-Skala',
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
        'date': '17 Okt 2026', 'updated': '18 Okt 2026', 'status': 'Terintegrasi',
        'multiType': 'multi-year', 'multiLabel': 'Multi-Year',
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
        'multiType': 'multi-year', 'multiLabel': 'Multi-Year',
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
        'date': '17 Okt 2026', 'status': 'Terkompilasi',
        'note': 'Kompilasi data kabupaten selesai.',
    },
    {
        'id': 'PGJ-2026-008', 'layer': 'IGT Analisa Tanah Objek Reforma Agraria', 'category': 'tata-ruang',
        'satker': 'Kantah Kab. Gunungkidul', 'direktorat': 'Direktorat Landreform',
        'date': '17 Okt 2026', 'status': 'Terkompilasi',
        'note': 'Data spasial siap diajukan untuk integrasi nasional.',
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

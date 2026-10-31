// Sample data and role permissions for the IGT-PR mockup. Static: nothing is fetched or persisted.
//
// Data model
// - One record = one IGT dataset together with its latest submission. Re-submissions of an
//   already integrated dataset are not modelled, so counting records equals counting datasets.
// - The catalog pages show only records with status `Terintegrasi`.
// - The Upload Data page shows every record of a category (the submission lifecycle).
//
// Lifecycle (statuses differ per category)
// - IGT Pertanahan / IGT Tata Ruang: Terkompilasi (proses integrasi) -> Terintegrasi (Revisi = returned to Operator).
//   Only these two categories use Terkompilasi / Terintegrasi.
// - IGT Derivatif: Diajukan -> Disetujui or Ditolak; an approved layer later becomes Kadaluwarsa when its
//   validity period ends. Admin uploads start as Disetujui, Operator/Umum uploads start as Diajukan.
// - IGT Lainnya: everything uploaded (Superadmin only) is available immediately, status Tersedia.
// A record enters its catalog when its status equals the category's `catalogStatus`.
const IgtData = (() => {
  const CATEGORY_ORDER = ['igt-pr', 'pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];

  const CATEGORIES = {
    'igt-pr': {
      label: 'IGT-PR', shortLabel: 'IGT-PR', slug: 'igt-pr', kind: 'terpadu', detail: 'utama', integration: true,
      catalogStatus: 'Terintegrasi', noun: 'dataset terpadu', rule: 'Menampilkan dataset IGT Pertanahan dan IGT Tata Ruang terpadu.',
    },
    pertanahan: {
      label: 'IGT Pertanahan', shortLabel: 'IGT Pertanahan', slug: 'igt-pertanahan', kind: 'bidang', detail: 'utama', integration: true,
      catalogStatus: 'Terintegrasi', noun: 'dataset terintegrasi', rule: 'Menampilkan dataset yang sudah terintegrasi dan siap dimanfaatkan di QGIS.',
    },
    'tata-ruang': {
      label: 'IGT Tata Ruang', shortLabel: 'IGT Tata Ruang', slug: 'igt-tata-ruang', kind: 'kawasan', detail: 'utama', integration: true,
      catalogStatus: 'Terintegrasi', noun: 'dataset terintegrasi', rule: 'Menampilkan dataset yang sudah terintegrasi dan siap dimanfaatkan di QGIS.',
    },
    derivatif: {
      label: 'IGT Derivatif Multiguna', shortLabel: 'IGT Derivatif', slug: 'igt-derivatif', detail: 'derivatif',
      catalogStatus: 'Disetujui', noun: 'layer disetujui',
      rule: 'Hanya layer berstatus Disetujui yang tampil; layer Diajukan, Ditolak, dan Kadaluwarsa tidak ditampilkan.',
    },
    lainnya: {
      label: 'IGT K/L Lainnya', shortLabel: 'IGT K/L Lainnya', slug: 'igt-lainnya',
      catalogStatus: 'Tersedia', noun: 'layer tersedia', rule: 'Semua layer eksternal yang diunggah langsung masuk katalog.',
    },
  };

  // Permissions. Every role may browse all four catalogs (`view`). Uploading and managing submissions
  // (`upload`) is narrower: IGT Lainnya (Eksternal) can only be managed by Superadmin, and Umum (public users) can only upload IGT Derivatif.
  // Umum sees only its own submissions (records with `owner: 'umum'`).
  // `derivatifWorkflow` marks the role that gets the Derivatif Bidang workflow page (Operator only).
  const ALL = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];
  const ROLES = {
    superadmin: { label: 'Superadmin', avatar: 'SA', satker: 'Semua Satker', view: ALL, upload: ['lainnya'] },
    superadmin2: { label: 'Superadmin', avatar: 'SA', satker: 'Semua Satker', view: ALL, upload: ALL, derivatifWorkflow: true, v2: true, baseRole: 'superadmin' },
    admin: { label: 'Admin', avatar: 'AD', satker: 'Kantah Kab. Sleman', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'] },
    admin2: { label: 'Admin', avatar: 'AD', satker: 'Kantah Kab. Sleman', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'], derivatifWorkflow: true, v2: true, baseRole: 'admin' },
    operator: { label: 'Operator Pusat', avatar: 'JH', satker: 'Kantah Kab. Sleman', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'], derivatifWorkflow: true },
    operator2: { label: 'Operator Pusat', avatar: 'JH', satker: 'Kantah Kab. Sleman', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'], derivatifWorkflow: true, v2: true, baseRole: 'operator' },
    umum: { label: 'Umum', avatar: 'UM', satker: null, view: ALL, upload: ['derivatif'], ownSubmissionsOnly: true },
    umum2: { label: 'Umum', avatar: 'UM', satker: null, view: ALL, upload: ['derivatif'], ownSubmissionsOnly: true, derivatifWorkflow: true, v2: true, baseRole: 'umum' },
  };

  // `n` is the record index understood by the shared detail pages (igt-utama-detail, layer-derivatif-detail).
  // `updated` is the date the dataset was last updated once integrated (catalog "Tanggal Update").
  // `scope` is Ruang Lingkup Data (e.g. Multi-Area, Kabupaten, Kota, Nasional) to identify multi-area datasets.
  // `satker` / `instansi` is Satuan Kerja (Ditjen, Kanwil, Kantah) for IGT Utama & Derivatif, or Instansi for IGT Lainnya.
  const RECORDS = [
    // IGT Pertanahan dan Tata Ruang: 39 dataset dari daftar resmi yang diberikan.
    { category: 'pertanahan', n: 0, id: 'IGT-PR-001', name: 'IGT Bidang Tanah', direktorat: 'Direktorat Pengukuran dan Pemetaan Kadastral', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman (Multi-Desa)', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 1, id: 'IGT-PR-002', name: 'IGT Penguasaan Tanah', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Bantul', scope: 'Kab. Bantul', prov: 'D.I. Yogyakarta', kab: 'Kab. Bantul', date: '12 Nov 2025', updated: '12 Nov 2025', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 2, id: 'IGT-PR-003', name: 'IGT Pemilikan Tanah', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kota Yogyakarta', scope: 'Kota Yogyakarta', prov: 'D.I. Yogyakarta', kab: 'Kota Yogyakarta', date: '05 Agu 2025', updated: '05 Agu 2025', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 3, id: 'IGT-PR-004', name: 'IGT Penggunaan Tanah', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '20 Sep 2024', updated: '20 Sep 2024', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 4, id: 'IGT-PR-005', name: 'IGT Pemanfaatan Tanah', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Gunungkidul', scope: 'Kab. Gunungkidul', prov: 'D.I. Yogyakarta', kab: 'Kab. Gunungkidul', date: '14 Jun 2024', updated: '14 Jun 2024', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 5, id: 'IGT-PR-006', name: 'IGT Sebaran Lokasi Pemberdayaan Tanah Masyarakat', direktorat: 'Direktorat Pemberdayaan Tanah Masyarakat', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Kab. Gunungkidul & Kulon Progo)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Gunungkidul, Kulon Progo)', date: '18 Okt 2023', updated: '18 Okt 2023', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 6, id: 'IGT-PR-007', name: 'IGT Pertimbangan Teknis Pertanahan', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 7, id: 'IGT-PR-008', name: 'IGT Inventarisasi Tanah Kritis', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Kab. Bantul & Gunungkidul)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Bantul, Gunungkidul)', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Revisi', revisionNote: 'Perbaiki kelengkapan atribut dan pastikan kode wilayah konsisten.' },
    { category: 'pertanahan', n: 8, id: 'IGT-PR-009', name: 'IGT Tanah Terindikasi Telantar', direktorat: 'Direktur Penertiban Penguasaan, Pemilikan dan Penggunaan Tanah', satker: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', scope: 'Multi-Area (Kab. Sleman, Bantul, Kulon Progo)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Sleman, Bantul, Kulon Progo)', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi',
      multiType: 'multi-year', multiLabel: 'Multi-Layer',
      subLayers: [
        { id: 'TTT-2026', name: 'Tanah Terindikasi Telantar 2026', label: 'Tahun 2026', year: '2026', updated: '18 Okt 2026', scope: 'Multi-Area (Sleman, Bantul, Kulon Progo)' },
        { id: 'TTT-2024', name: 'Tanah Terindikasi Telantar 2024', label: 'Tahun 2024', year: '2024', updated: '15 Okt 2024', scope: 'Multi-Area (Sleman, Bantul, Kulon Progo)' }
      ]
    },
    { category: 'pertanahan', n: 9, id: 'IGT-PR-010', name: 'IGT Indikasi Pelanggaran Pemanfaatan Ruang', direktorat: 'Direktorat Penertiban Pemanfaatan Ruang', satker: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', scope: 'Multi-Area (Kawasan Perkotaan Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Kota Yogyakarta, Sleman, Bantul)', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 10, id: 'IGT-PR-011', name: 'IGT Hak Atas Tanah', direktorat: 'Sekretariat Direktorat Jenderal Penetapan Hak dan Pendaftaran Tanah', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 11, id: 'IGT-PR-012', name: 'IGT Informasi Mengenai Sengketa, Konflik, dan Perkara Pertanahan', direktorat: 'Sekretariat Direktorat Jenderal Penanganan Sengketa dan Konflik Pertanahan', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Prov. D.I. Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Lintas Kabupaten/Kota', date: '14 Mei 2021', updated: '14 Mei 2021', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 12, id: 'IGT-PR-013', name: 'IGT Potensi Subjek Konsolidasi Tanah', direktorat: 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '09 Des 2025', updated: '09 Des 2025', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 13, id: 'IGT-PR-014', name: 'IGT Nilai Bidang Tanah', direktorat: 'Direktorat Penilaian Tanah dan Ekonomi Pertanahan', satker: 'Kantah Kota Yogyakarta', scope: 'Kota Yogyakarta', prov: 'D.I. Yogyakarta', kab: 'Kota Yogyakarta', date: '22 Agu 2024', updated: '22 Agu 2024', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 14, id: 'IGT-PR-015', name: 'IGT Desain Konsolidasi Tanah', direktorat: 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 15, id: 'IGT-PR-016', name: 'IGT Hasil Penerapan Desain Konsolidasi Tanah', direktorat: 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 16, id: 'IGT-PR-017', name: 'IGT RTRW Nasional', direktorat: 'Direktorat Perencanaan Tata Ruang', satker: 'Ditjen Tata Ruang', scope: 'Nasional (Seluruh Wilayah RI)', prov: 'Nasional', kab: 'Seluruh Indonesia', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 17, id: 'IGT-PR-018', name: 'IGT RTRW Provinsi', direktorat: 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Provinsi (D.I. Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Lintas Kabupaten/Kota', date: '10 Nov 2025', updated: '10 Nov 2025', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 18, id: 'IGT-PR-019', name: 'IGT RTRW Kabupaten', direktorat: 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I', satker: 'Ditjen Tata Ruang', scope: 'Multi-Kabupaten (Sleman, Bantul, Kulon Progo)', prov: 'D.I. Yogyakarta', kab: 'Multi-Kabupaten', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi',
      multiType: 'multi-scale', multiLabel: 'Multi-Layer',
      subLayers: [
        { id: 'RTRW-50K', name: 'RTRW Kab Skala 1:50.000', label: 'Skala 1:50.000', skala: '1:50.000', updated: '18 Okt 2026', scope: 'Rencana Pola Ruang Kabupaten' },
        { id: 'RTRW-25K', name: 'RTRW Kab Skala 1:25.000', label: 'Skala 1:25.000', skala: '1:25.000', updated: '15 Jul 2026', scope: 'Kawasan Strategis Kabupaten' }
      ]
    },
    { category: 'tata-ruang', n: 19, id: 'IGT-PR-020', name: 'IGT RTRW Kota', direktorat: 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I', satker: 'Ditjen Tata Ruang', scope: 'Kota (Kota Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Kota Yogyakarta', date: '16 Jul 2024', updated: '16 Jul 2024', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 20, id: 'IGT-PR-021', name: 'IGT RDTR Kawasan Perbatasan Negara', direktorat: 'Direktorat Perencanaan Tata Ruang', satker: 'Ditjen Tata Ruang', scope: 'Multi-Area (Kawasan Perbatasan PLBN)', prov: 'Kalimantan Barat', kab: 'Multi-Area (Sambas, Bengkayang)', date: '24 Okt 2023', updated: '24 Okt 2023', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 21, id: 'IGT-PR-022', name: 'IGT RTR Pulau/Kepulauan', direktorat: 'Direktorat Perencanaan Tata Ruang', satker: 'Ditjen Tata Ruang', scope: 'Multi-Area (Pulau Jawa - Bali)', prov: 'Lintas Provinsi (Jawa-Bali)', kab: 'Lintas Wilayah', date: '15 Des 2019', updated: '15 Des 2019', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 22, id: 'IGT-PR-023', name: 'IGT RTR Kawasan Strategis Nasional', direktorat: 'Direktorat Perencanaan Tata Ruang', satker: 'Ditjen Tata Ruang', scope: 'Multi-Area (KSN Borobudur & Sekitarnya)', prov: 'D.I. Yogyakarta & Jawa Tengah', kab: 'Multi-Area (Magelang, Sleman, Kulon Progo)', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 23, id: 'IGT-PR-024', name: 'IGT RDTR Kabupaten/Kota', direktorat: 'Direktorat Bina Perencanaan Tata Ruang Daerah Wilayah I', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman (Kawasan Perkotaan Depok)', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi',
      multiType: 'multi-scale', multiLabel: 'Multi-Layer',
      subLayers: [
        { id: 'RDTR-5K', name: 'RDTR Kab/Kota Skala 1:5.000', label: 'Skala 1:5.000', skala: '1:5.000', updated: '18 Okt 2026', scope: 'Kawasan Perkotaan Depok (Blok Rinci)' },
        { id: 'RDTR-10K', name: 'RDTR Kab/Kota Skala 1:10.000', label: 'Skala 1:10.000', skala: '1:10.000', updated: '12 Agt 2026', scope: 'Kawasan Aglomerasi Sleman' },
        { id: 'RDTR-25K', name: 'RDTR Kab/Kota Skala 1:25.000', label: 'Skala 1:25.000', skala: '1:25.000', updated: '10 Jun 2026', scope: 'Kawasan Penyangga Wilayah' }
      ]
    },
    { category: 'tata-ruang', n: 24, id: 'IGT-PR-025', name: 'IGT KKPR', direktorat: 'Direktorat Sinkronisasi Pemanfaatan Ruang', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Prov. D.I. Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Lintas Kabupaten/Kota', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 25, id: 'IGT-PR-026', name: 'IGT Lahan Baku Sawah', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Bantul', scope: 'Kab. Bantul', prov: 'D.I. Yogyakarta', kab: 'Kab. Bantul', date: '18 Okt 2024', updated: '18 Okt 2024', status: 'Terintegrasi',
      multiType: 'multi-year', multiLabel: 'Multi-Layer',
      subLayers: [
        { id: 'LBS-2024', name: 'Lahan Baku Sawah 2024', label: 'Tahun 2024', year: '2024', updated: '18 Okt 2024', scope: 'Kab. Bantul' },
        { id: 'LBS-2023', name: 'Lahan Baku Sawah 2023', label: 'Tahun 2023', year: '2023', updated: '15 Des 2023', scope: 'Kab. Bantul' },
        { id: 'LBS-2021', name: 'Lahan Baku Sawah 2021', label: 'Tahun 2021', year: '2021', updated: '20 Nov 2021', scope: 'Kab. Bantul' },
        { id: 'LBS-2019', name: 'Lahan Baku Sawah 2019', label: 'Tahun 2019', year: '2019', updated: '10 Sep 2019', scope: 'Kab. Bantul' }
      ]
    },
    { category: 'tata-ruang', n: 26, id: 'IGT-PR-027', name: 'IGT Kemampuan Tanah', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '17 Okt 2026', status: 'Revisi', revisionNote: 'Periksa geometri yang bertampalan dan lengkapi metadata sumber data.' },
    { category: 'tata-ruang', n: 27, id: 'IGT-PR-028', name: 'IGT Neraca Penatagunaan Tanah', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '15 Des 2025', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 28, id: 'IGT-PR-029', name: 'IGT Persebaran Pulau-Pulau Kecil Terluar di Indonesia', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Ditjen Penataan Agraria', scope: 'Nasional (Kawasan Terluar)', prov: 'Nasional', kab: 'Lintas Wilayah Pesisir', date: '12 Nov 2021', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 29, id: 'IGT-PR-030', name: 'IGT Sebaran Tanah Objek Reforma Agraria', direktorat: 'Direktorat Landreform', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Kab. Gunungkidul & Bantul)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Gunungkidul, Bantul)', date: '17 Okt 2026', status: 'Diajukan' },
    { category: 'tata-ruang', n: 30, id: 'IGT-PR-031', name: 'IGT Analisa Tanah Objek Reforma Agraria', direktorat: 'Direktorat Landreform', satker: 'Kantah Kab. Gunungkidul', scope: 'Kab. Gunungkidul', prov: 'D.I. Yogyakarta', kab: 'Kab. Gunungkidul', date: '20 Nov 2024', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 31, id: 'IGT-PR-032', name: 'IGT Potensi Objek Redistribusi Tanah', direktorat: 'Direktorat Landreform', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 32, id: 'IGT-PR-033', name: 'IGT Potensi WP3WT', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Gunungkidul', scope: 'Kab. Gunungkidul', prov: 'D.I. Yogyakarta', kab: 'Kab. Gunungkidul', date: '18 Okt 2023', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 33, id: 'IGT-PR-034', name: 'IGT Tanah Timbul', direktorat: 'Direktorat Penatagunaan Tanah', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo (Pesisir Selatan)', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '15 Sep 2019', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 34, id: 'IGT-PR-035', name: 'IGT Unsur Dasar Pertanahan', direktorat: 'Direktorat Pengukuran Dan Pemetaan Dasar Pertanahan Ruang', satker: 'Kantah Kota Yogyakarta', scope: 'Kota Yogyakarta', prov: 'D.I. Yogyakarta', kab: 'Kota Yogyakarta', date: '17 Okt 2026', status: 'Diajukan' },
    { category: 'tata-ruang', n: 35, id: 'IGT-PR-036', name: 'IGT Lahan Sawah Dilindungi', direktorat: 'Direktorat Pengendalian Hak Tanah, Alih Fungsi Lahan, Kepulauan dan Wilayah Tertentu', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Kab. Sleman & Bantul)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Sleman, Bantul)', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 36, id: 'IGT-PR-037', name: 'IGT Kawasan Terindikasi Telantar', direktorat: 'Direktur Penertiban Penguasaan, Pemilikan dan Penggunaan Tanah', satker: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', scope: 'Multi-Area (Kab. Kulon Progo & Gunungkidul)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Kulon Progo, Gunungkidul)', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 37, id: 'IGT-PR-038', name: 'IGT Zona Nilai Tanah', direktorat: 'Direktorat Penilaian Tanah dan Ekonomi Pertanahan', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '17 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi',
      multiType: 'multi-year', multiLabel: 'Multi-Layer',
      subLayers: [
        { id: 'ZNT-2026', name: 'Zona Nilai Tanah 2026', label: 'Tahun 2026', year: '2026', updated: '18 Okt 2026', scope: 'Kab. Sleman (Pembaruan Terkini)' },
        { id: 'ZNT-2025', name: 'Zona Nilai Tanah 2025', label: 'Tahun 2025', year: '2025', updated: '10 Des 2025', scope: 'Kab. Sleman' },
        { id: 'ZNT-2024', name: 'Zona Nilai Tanah 2024', label: 'Tahun 2024', year: '2024', updated: '14 Nov 2024', scope: 'Kab. Sleman' }
      ]
    },
    { category: 'tata-ruang', n: 38, id: 'IGT-PR-039', name: 'IGT Sebaran Potensi Pengembangan Pertanahan', direktorat: 'Direktorat Konsolidasi Tanah Dan Pengembangan Pertanahan', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Prov. D.I. Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Lintas Kabupaten/Kota', date: '17 Okt 2026', status: 'Terkompilasi' },
    // IGT Derivatif
    { category: 'derivatif', n: 0, id: 'DRV-2026-008', name: 'Derivatif Kawasan Hutan', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kanwil BPN D.I. Yogyakarta', scope: 'Multi-Area (Kab. Gunungkidul & Bantul)', prov: 'D.I. Yogyakarta', kab: 'Multi-Area (Gunungkidul, Bantul)', date: '16 Okt 2026', updated: '17 Okt 2026', status: 'Disetujui' },
    { category: 'derivatif', n: 1, id: 'DRV-2026-007', name: 'Derivatif Bidang Wilayah A', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Sleman', scope: 'Kab. Sleman', prov: 'D.I. Yogyakarta', kab: 'Kab. Sleman', date: '15 Okt 2026', status: 'Diajukan' },
    { category: 'derivatif', n: 2, id: 'DRV-2026-006', name: 'Derivatif Kawasan Lindung', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Kulon Progo', scope: 'Kab. Kulon Progo', prov: 'D.I. Yogyakarta', kab: 'Kab. Kulon Progo', date: '14 Okt 2026', status: 'Ditolak' },
    { category: 'derivatif', n: 3, id: 'DRV-2026-005', name: 'Derivatif Bidang Wilayah B', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kota Yogyakarta', scope: 'Kota Yogyakarta', prov: 'D.I. Yogyakarta', kab: 'Kota Yogyakarta', date: '12 Okt 2026', updated: '13 Okt 2026', status: 'Disetujui' },
    { category: 'derivatif', n: 4, id: 'DRV-2026-004', name: 'Derivatif Kawasan Permukiman', direktorat: 'Direktorat Survei Dan Pemetaan Tematik', satker: 'Kantah Kab. Bantul', scope: 'Kab. Bantul', prov: 'D.I. Yogyakarta', kab: 'Kab. Bantul', date: '2 Okt 2026', status: 'Kadaluwarsa' },
    // IGT Lainnya (eksternal): no detail page, everything uploaded is available immediately
    { category: 'lainnya', id: 'IGT-EXT-004', name: 'Rencana Tata Ruang Wilayah', instansi: 'Dinas Pertanahan dan Tata Ruang DIY', source: 'Dinas Pertanahan dan Tata Ruang DIY', scope: 'Provinsi (D.I. Yogyakarta)', prov: 'D.I. Yogyakarta', kab: 'Lintas Kabupaten/Kota', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-003', name: 'Tutupan Lahan Nasional', instansi: 'Kementerian Lingkungan Hidup', source: 'Kementerian Lingkungan Hidup', scope: 'Nasional', prov: 'Nasional', kab: 'Seluruh Indonesia', date: '15 Okt 2026', updated: '15 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-002', name: 'Batas Wilayah Administrasi', instansi: 'Badan Informasi Geospasial', source: 'Badan Informasi Geospasial', scope: 'Nasional', prov: 'Nasional', kab: 'Seluruh Indonesia', date: '12 Okt 2026', updated: '12 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-001', name: 'Peta Risiko Bencana', instansi: 'Badan Nasional Penanggulangan Bencana', source: 'Badan Nasional Penanggulangan Bencana', scope: 'Multi-Area (D.I. Yogyakarta & Jawa Tengah)', prov: 'D.I. Yogyakarta & Jawa Tengah', kab: 'Multi-Area (Sleman, Magelang, Klaten)', date: '10 Okt 2026', updated: '10 Okt 2026', status: 'Tersedia' },
  ];

  const REGIONS = {
    "Aceh": ["Aceh Barat", "Aceh Barat Daya", "Aceh Besar", "Aceh Jaya", "Aceh Selatan", "Aceh Singkil", "Aceh Tamiang", "Aceh Tengah", "Aceh Tenggara", "Aceh Timur", "Aceh Utara", "Bener Meriah", "Bireuen", "Gayo Lues", "Kota Banda Aceh", "Kota Langsa", "Kota Lhokseumawe", "Kota Sabang", "Kota Subulussalam", "Nagan Raya", "Pidie", "Pidie Jaya", "Simeulue"],
    "Bali": ["Badung", "Bangli", "Buleleng", "Gianyar", "Jembrana", "Karangasem", "Klungkung", "Kota Denpasar", "Tabanan"],
    "Banten": ["Kota Cilegon", "Kota Serang", "Kota Tangerang", "Kota Tangerang Selatan", "Lebak", "Pandeglang", "Serang", "Tangerang"],
    "Bengkulu": ["Bengkulu Selatan", "Bengkulu Tengah", "Bengkulu Utara", "Kaur", "Kepahiang", "Kota Bengkulu", "Lebong", "Mukomuko", "Rejang Lebong", "Seluma"],
    "Daerah Istimewa Yogyakarta": ["Bantul", "Gunungkidul", "Kota Yogyakarta", "Kulon Progo", "Sleman"],
    "Daerah Khusus Ibukota Jakarta": ["Administrasi Kepulauan Seribu", "Kota Administrasi Jakarta Barat", "Kota Administrasi Jakarta Pusat", "Kota Administrasi Jakarta Selatan", "Kota Administrasi Jakarta Timur", "Kota Administrasi Jakarta Utara"],
    "Gorontalo": ["Boalemo", "Bone Bolango", "Gorontalo", "Gorontalo Utara", "Kota Gorontalo", "Pohuwato"],
    "Jambi": ["Batanghari", "Bungo", "Kerinci", "Kota Jambi", "Kota Sungai Penuh", "Merangin", "Muaro Jambi", "Sarolangun", "Tanjung Jabung Barat", "Tanjung Jabung Timur", "Tebo"],
    "Jawa Barat": ["Bandung", "Bandung Barat", "Bekasi", "Bogor", "Ciamis", "Cianjur", "Cirebon", "Garut", "Indramayu", "Karawang", "Kota Bandung", "Kota Banjar", "Kota Bekasi", "Kota Bogor", "Kota Cimahi", "Kota Cirebon", "Kota Depok", "Kota Sukabumi", "Kota Tasikmalaya", "Kuningan", "Majalengka", "Pangandaran", "Purwakarta", "Subang", "Sukabumi", "Sumedang", "Tasikmalaya"],
    "Jawa Tengah": ["Banjarnegara", "Banyumas", "Batang", "Blora", "Boyolali", "Brebes", "Cilacap", "Demak", "Grobogan", "Jepara", "Karanganyar", "Kebumen", "Kendal", "Klaten", "Kota Magelang", "Kota Pekalongan", "Kota Salatiga", "Kota Semarang", "Kota Surakarta", "Kota Tegal", "Kudus", "Magelang", "Pati", "Pekalongan", "Pemalang", "Purbalingga", "Purworejo", "Rembang", "Semarang", "Sragen", "Sukoharjo", "Tegal", "Temanggung", "Wonogiri", "Wonosobo"],
    "Jawa Timur": ["Bangkalan", "Banyuwangi", "Blitar", "Bojonegoro", "Bondowoso", "Gresik", "Jember", "Jombang", "Kediri", "Kota Batu", "Kota Blitar", "Kota Kediri", "Kota Madiun", "Kota Malang", "Kota Mojokerto", "Kota Pasuruan", "Kota Probolinggo", "Kota Surabaya", "Lamongan", "Lumajang", "Madiun", "Magetan", "Malang", "Mojokerto", "Nganjuk", "Ngawi", "Pacitan", "Pamekasan", "Pasuruan", "Ponorogo", "Probolinggo", "Sampang", "Sidoarjo", "Situbondo", "Sumenep", "Trenggalek", "Tuban", "Tulungagung"],
    "Kalimantan Barat": ["Bengkayang", "Kapuas Hulu", "Kayong Utara", "Ketapang", "Kota Pontianak", "Kota Singkawang", "Kubu Raya", "Landak", "Melawi", "Mempawah", "Sambas", "Sanggau", "Sekadau", "Sintang"],
    "Kalimantan Selatan": ["Balangan", "Banjar", "Barito Kuala", "Hulu Sungai Selatan", "Hulu Sungai Tengah", "Hulu Sungai Utara", "Kota Banjarbaru", "Kota Banjarmasin", "Kotabaru", "Tabalong", "Tanah Bumbu", "Tanah Laut", "Tapin"],
    "Kalimantan Tengah": ["Barito Selatan", "Barito Timur", "Barito Utara", "Gunung Mas", "Kapuas", "Katingan", "Kota Palangkaraya", "Kotawaringin Barat", "Kotawaringin Timur", "Lamandau", "Murung Raya", "Pulang Pisau", "Seruyan", "Sukamara"],
    "Kalimantan Timur": ["Berau", "Kota Balikpapan", "Kota Bontang", "Kota Samarinda", "Kutai Barat", "Kutai Kartanegara", "Kutai Timur", "Mahakam Ulu", "Paser", "Penajam Paser Utara"],
    "Kalimantan Utara": ["Bulungan", "Kota Tarakan", "Malinau", "Nunukan", "Tana Tidung"],
    "Kepulauan Bangka Belitung": ["Bangka", "Bangka Barat", "Bangka Selatan", "Bangka Tengah", "Belitung", "Belitung Timur", "Kota Pangkal Pinang"],
    "Kepulauan Riau": ["Bintan", "Karimun", "Kepulauan Anambas", "Kota Batam", "Kota Tanjung Pinang", "Lingga", "Natuna"],
    "Lampung": ["Kota Bandar Lampung", "Kota Metro", "Lampung Barat", "Lampung Selatan", "Lampung Tengah", "Lampung Timur", "Lampung Utara", "Mesuji", "Pesawaran", "Pesisir Barat", "Pringsewu", "Tanggamus", "Tulang Bawang", "Tulang Bawang Barat", "Way Kanan"],
    "Maluku": ["Buru", "Buru Selatan", "Kepulauan Aru", "Kepulauan Tanimbar", "Kota Ambon", "Kota Tual", "Maluku Barat Daya", "Maluku Tengah", "Maluku Tenggara", "Seram Bagian Barat", "Seram Bagian Timur"],
    "Maluku Utara": ["Halmahera Barat", "Halmahera Selatan", "Halmahera Tengah", "Halmahera Timur", "Halmahera Utara", "Kepulauan Sula", "Kota Ternate", "Kota Tidore Kepulauan", "Pulau Morotai", "Pulau Taliabu"],
    "Nusa Tenggara Barat": ["Bima", "Dompu", "Kota Bima", "Kota Mataram", "Lombok Barat", "Lombok Tengah", "Lombok Timur", "Lombok Utara", "Sumbawa", "Sumbawa Barat"],
    "Nusa Tenggara Timur": ["Alor", "Belu", "Ende", "Flores Timur", "Kota Kupang", "Kupang", "Lembata", "Malaka", "Manggarai", "Manggarai Barat", "Manggarai Timur", "Nagekeo", "Ngada", "Rote Ndao", "Sabu Raijua", "Sikka", "Sumba Barat", "Sumba Barat Daya", "Sumba Tengah", "Sumba Timur", "Timor Tengah Selatan", "Timor Tengah Utara"],
    "Papua": ["Biak Numfor", "Jayapura", "Keerom", "Kepulauan Yapen", "Kota Jayapura", "Mamberamo Raya", "Sarmi", "Supiori", "Waropen"],
    "Papua Barat": ["Fak Fak", "Kaimana", "Manokwari", "Manokwari Selatan", "Pegunungan Arfak", "Teluk Bintuni", "Teluk Wondama"],
    "Papua Barat Daya": ["Kota Sorong", "Maybrat", "Raja Ampat", "Sorong", "Sorong Selatan", "Tambrauw"],
    "Papua Pegunungan": ["Jayawijaya", "Lanny Jaya", "Mamberamo Tengah", "Nduga", "Pegunungan Bintang", "Tolikara", "Yahukimo", "Yalimo"],
    "Papua Selatan": ["Asmat", "Boven Digoel", "Mappi", "Merauke"],
    "Papua Tengah": ["Deiyai", "Dogiyai", "Intan Jaya", "Mimika", "Nabire", "Paniai", "Puncak", "Puncak Jaya"],
    "Riau": ["Bengkalis", "Indragiri Hilir", "Indragiri Hulu", "Kampar", "Kepulauan Meranti", "Kota Dumai", "Kota Pekanbaru", "Kuantan Singingi", "Pelalawan", "Rokan Hilir", "Rokan Hulu", "Siak"],
    "Sulawesi Barat": ["Majene", "Mamasa", "Mamuju", "Mamuju Tengah", "Pasangkayu", "Polewali Mandar"],
    "Sulawesi Selatan": ["Bantaeng", "Barru", "Bone", "Bulukumba", "Enrekang", "Gowa", "Jeneponto", "Kepulauan Selayar", "Kota Makassar", "Kota Palopo", "Kota Parepare", "Luwu", "Luwu Timur", "Luwu Utara", "Maros", "Pangkajene Dan Kepulauan", "Pinrang", "Sidenreng Rappang", "Sinjai", "Soppeng", "Takalar", "Tana Toraja", "Toraja Utara", "Wajo"],
    "Sulawesi Tengah": ["Banggai", "Banggai Kepulauan", "Banggai Laut", "Buol", "Donggala", "Kota Palu", "Morowali", "Morowali Utara", "Parigi Moutong", "Poso", "Sigi", "Tojo Una Una", "Toli-Toli"],
    "Sulawesi Tenggara": ["Bombana", "Buton", "Buton Selatan", "Buton Tengah", "Buton Utara", "Kolaka", "Kolaka Timur", "Kolaka Utara", "Konawe", "Konawe Kepulauan", "Konawe Selatan", "Konawe Utara", "Kota Bau Bau", "Kota Kendari", "Muna", "Muna Barat", "Wakatobi"],
    "Sulawesi Utara": ["Bolaang Mongondow", "Bolaang Mongondow Selatan", "Bolaang Mongondow Timur", "Bolaang Mongondow Utara", "Kep. Siau Tagulandang Biaro", "Kepulauan Sangihe", "Kepulauan Talaud", "Kota Bitung", "Kota Kotamobagu", "Kota Manado", "Kota Tomohon", "Minahasa", "Minahasa Selatan", "Minahasa Tenggara", "Minahasa Utara"],
    "Sumatera Barat": ["Agam", "Dharmasraya", "Kepulauan Mentawai", "Kota Bukittinggi", "Kota Padang", "Kota Padang Panjang", "Kota Pariaman", "Kota Payakumbuh", "Kota Sawahlunto", "Kota Solok", "Lima Puluh Kota", "Padang Pariaman", "Pasaman", "Pasaman Barat", "Pesisir Selatan", "Sijunjung", "Solok", "Solok Selatan", "Tanah Datar"],
    "Sumatera Selatan": ["Banyuasin", "Empat Lawang", "Kota Lubuk Linggau", "Kota Pagar Alam", "Kota Palembang", "Kota Prabumulih", "Lahat", "Muara Enim", "Musi Banyuasin", "Musi Rawas", "Musi Rawas Utara", "Ogan Ilir", "Ogan Komering Ilir", "Ogan Komering Ulu", "Ogan Komering Ulu Selatan", "Ogan Komering Ulu Timur", "Penukal Abab Lematang Ilir"],
    "Sumatera Utara": ["Asahan", "Batu Bara", "Dairi", "Deli Serdang", "Humbang Hasundutan", "Karo", "Kota Binjai", "Kota Gunungsitoli", "Kota Medan", "Kota Padangsidimpuan", "Kota Pematangsiantar", "Kota Sibolga", "Kota Tanjungbalai", "Kota Tebing Tinggi", "Labuhanbatu", "Labuhanbatu Selatan", "Labuhanbatu Utara", "Langkat", "Mandailing Natal", "Nias", "Nias Barat", "Nias Selatan", "Nias Utara", "Padang Lawas", "Padang Lawas Utara", "Pakpak Bharat", "Samosir", "Serdang Bedagai", "Simalungun", "Tapanuli Selatan", "Tapanuli Tengah", "Tapanuli Utara", "Toba"],
  };

  const canView = (role, category) => {
    if (category === 'igt-pr') return Boolean(ROLES[role] && ROLES[role].view.includes('pertanahan') && ROLES[role].view.includes('tata-ruang'));
    return Boolean(ROLES[role] && ROLES[role].view.includes(category));
  };
  const canUpload = (role, category) => Boolean(ROLES[role] && ROLES[role].upload.includes(category));
  // Submissions a role may see in Upload Data: its upload categories, and only its own records for Umum.
  const submissionsFor = (role, records) => {
    const ownerKey = (ROLES[role] && ROLES[role].baseRole) || role;
    return records.filter((r) => canUpload(role, r.category) && (!ROLES[role].ownSubmissionsOnly || r.owner === ownerKey || r.owner === role));
  };
  const inCatalog = (record) => {
    return record.status === CATEGORIES[record.category].catalogStatus;
  };
  // Terkompilasi / Terintegrasi exist only for categories with an integration step.
  const integrationRecords = (records) => records.filter((r) => CATEGORIES[r.category].integration);
  const loadRecords = () => RECORDS.map((record) => ({
    ...record,
    ditjen: record.satker || record.ditjen,
    satker: record.satker || record.ditjen,
    instansi: record.instansi || record.source,
  }));
  const countByStatus = (records, status) => records.filter((record) => record.status === status).length;

  return { CATEGORY_ORDER, CATEGORIES, ROLES, REGIONS, canView, canUpload, submissionsFor, inCatalog, integrationRecords, loadRecords, countByStatus };
})();

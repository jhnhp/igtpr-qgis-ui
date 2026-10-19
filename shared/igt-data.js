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
  const CATEGORY_ORDER = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];

  const CATEGORIES = {
    pertanahan: {
      label: 'IGT Pertanahan', slug: 'igt-pertanahan', kind: 'bidang', detail: 'utama', integration: true,
      catalogStatus: 'Terintegrasi', noun: 'dataset terintegrasi', rule: 'Hanya dataset berstatus Terintegrasi yang tampil.',
    },
    'tata-ruang': {
      label: 'IGT Tata Ruang', slug: 'igt-tata-ruang', kind: 'kawasan', detail: 'utama', integration: true,
      catalogStatus: 'Terintegrasi', noun: 'dataset terintegrasi', rule: 'Hanya dataset berstatus Terintegrasi yang tampil.',
    },
    derivatif: {
      label: 'IGT Derivatif', slug: 'igt-derivatif', detail: 'derivatif',
      catalogStatus: 'Disetujui', noun: 'layer disetujui',
      rule: 'Hanya layer berstatus Disetujui yang tampil; layer Diajukan, Ditolak, dan Kadaluwarsa tidak ditampilkan.',
    },
    lainnya: {
      label: 'IGT Lainnya', slug: 'igt-lainnya',
      catalogStatus: 'Tersedia', noun: 'layer tersedia', rule: 'Semua layer eksternal yang diunggah langsung masuk katalog.',
    },
  };

  // Permissions. Every role may browse all four catalogs (`view`). Uploading and managing submissions
  // (`upload`) is narrower: IGT Lainnya (Eksternal) can only be managed by Superadmin, and Umum (public users) can only upload IGT Derivatif.
  // Umum sees only its own submissions (records with `owner: 'umum'`).
// `derivatifWorkflow` enables the shared Derivatif Bidang workflow for every role.
  const ALL = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];
  const ROLES = {
    superadmin: { label: 'Superadmin', avatar: 'SA', view: ALL, upload: ['pertanahan', 'tata-ruang', 'lainnya'] },
    admin: { label: 'Admin', avatar: 'AD', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'], derivatifWorkflow: true },
    operator: { label: 'Operator Pusat', avatar: 'JH', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'], derivatifWorkflow: true },
    umum: { label: 'Umum', avatar: 'UM', view: ALL, upload: ['derivatif'], ownSubmissionsOnly: true, derivatifWorkflow: true },
  };

  // `n` is the record index understood by the shared detail pages (igt-utama-detail, layer-derivatif-detail).
  // `updated` is the date the dataset was last updated once integrated (catalog "Tanggal Update").
  const RECORDS = [
    // IGT Pertanahan dan Tata Ruang: 39 dataset dari daftar resmi yang diberikan.
    { category: 'pertanahan', n: 0, id: 'IGT-PR-001', name: 'IGT Bidang Tanah', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 1, id: 'IGT-PR-002', name: 'IGT Penguasaan Tanah', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 2, id: 'IGT-PR-003', name: 'IGT Pemilikan Tanah', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 3, id: 'IGT-PR-004', name: 'IGT Penggunaan Tanah', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 4, id: 'IGT-PR-005', name: 'IGT Pemanfaatan Tanah', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 5, id: 'IGT-PR-006', name: 'IGT Sebaran Lokasi Pemberdayaan Tanah Masyarakat', ditjen: 'Ditjen Penataan Agraria', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 6, id: 'IGT-PR-007', name: 'IGT Pertimbangan Teknis Pertanahan', ditjen: 'Ditjen Penataan Agraria', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 7, id: 'IGT-PR-008', name: 'IGT Inventarisasi Tanah Kritis', ditjen: 'Ditjen Penataan Agraria', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Revisi', revisionNote: 'Perbaiki kelengkapan atribut dan pastikan kode wilayah konsisten.' },
    { category: 'pertanahan', n: 8, id: 'IGT-PR-009', name: 'IGT Tanah Terindikasi Telantar', ditjen: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 9, id: 'IGT-PR-010', name: 'IGT Indikasi Pelanggaran Pemanfaatan Ruang', ditjen: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 10, id: 'IGT-PR-011', name: 'IGT Hak Atas Tanah', ditjen: 'Ditjen Penetapan Hak dan Pendaftaran Tanah', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 11, id: 'IGT-PR-012', name: 'IGT Informasi Mengenai Sengketa, Konflik, dan Perkara Pertanahan', ditjen: 'Ditjen Penanganan Sengketa dan Konflik Pertanahan', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 12, id: 'IGT-PR-013', name: 'IGT Potensi Subjek Konsolidasi Tanah', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 13, id: 'IGT-PR-014', name: 'IGT Nilai Bidang Tanah', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 14, id: 'IGT-PR-015', name: 'IGT Desain Konsolidasi Tanah', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 15, id: 'IGT-PR-016', name: 'IGT Hasil Penerapan Desain Konsolidasi Tanah', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 16, id: 'IGT-PR-017', name: 'IGT RTRW Nasional', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 17, id: 'IGT-PR-018', name: 'IGT RTRW Provinsi', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 18, id: 'IGT-PR-019', name: 'IGT RTRW Kabupaten', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 19, id: 'IGT-PR-020', name: 'IGT RTRW Kota', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 20, id: 'IGT-PR-021', name: 'IGT RDTR Kawasan Perbatasan Negara', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 21, id: 'IGT-PR-022', name: 'IGT RTR Pulau/Kepulauan', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 22, id: 'IGT-PR-023', name: 'IGT RTR Kawasan Strategis Nasional', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 23, id: 'IGT-PR-024', name: 'IGT RDTR Kabupaten/Kota', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 24, id: 'IGT-PR-025', name: 'IGT KKPR', ditjen: 'Ditjen Tata Ruang', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 25, id: 'IGT-PR-026', name: 'IGT Lahan Baku Sawah', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 26, id: 'IGT-PR-027', name: 'IGT Kemampuan Tanah', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Revisi', revisionNote: 'Periksa geometri yang bertampalan dan lengkapi metadata sumber data.' },
    { category: 'tata-ruang', n: 27, id: 'IGT-PR-028', name: 'IGT Neraca Penatagunaan Tanah', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 28, id: 'IGT-PR-029', name: 'IGT Persebaran Pulau-Pulau Kecil Terluar di Indonesia', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 29, id: 'IGT-PR-030', name: 'IGT Sebaran Tanah Objek Reforma Agraria', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 30, id: 'IGT-PR-031', name: 'IGT Analisa Tanah Objek Reforma Agraria', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 31, id: 'IGT-PR-032', name: 'IGT Potensi Objek Redistribusi Tanah', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 32, id: 'IGT-PR-033', name: 'IGT Potensi WP3WT', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 33, id: 'IGT-PR-034', name: 'IGT Tanah Timbul', ditjen: 'Ditjen Penataan Agraria', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 34, id: 'IGT-PR-035', name: 'IGT Unsur Dasar Pertanahan', ditjen: 'Ditjen Survei dan Pemetaan Pertanahan dan Ruang', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 35, id: 'IGT-PR-036', name: 'IGT Lahan Sawah Dilindungi', ditjen: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 36, id: 'IGT-PR-037', name: 'IGT Kawasan Terindikasi Telantar', ditjen: 'Ditjen Pengendalian dan Penertiban Tanah dan Ruang', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 37, id: 'IGT-PR-038', name: 'IGT Zona Nilai Tanah', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '17 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 38, id: 'IGT-PR-039', name: 'IGT Sebaran Potensi Pengembangan Pertanahan', ditjen: 'Ditjen Pengadaan Tanah dan Pengembangan Pertanahan', date: '17 Okt 2026', status: 'Terkompilasi' },
    // IGT Derivatif
    { category: 'derivatif', n: 0, id: 'DRV-2026-008', name: 'Derivatif Kawasan Hutan', date: '16 Okt 2026', updated: '17 Okt 2026', status: 'Disetujui' },
    { category: 'derivatif', n: 1, id: 'DRV-2026-007', name: 'Derivatif Bidang Wilayah A', date: '15 Okt 2026', status: 'Diajukan' },
    { category: 'derivatif', n: 2, id: 'DRV-2026-006', name: 'Derivatif Kawasan Lindung', date: '14 Okt 2026', status: 'Ditolak' },
    { category: 'derivatif', n: 3, id: 'DRV-2026-005', name: 'Derivatif Bidang Wilayah B', date: '12 Okt 2026', updated: '13 Okt 2026', status: 'Disetujui' },
    { category: 'derivatif', n: 4, id: 'DRV-2026-004', name: 'Derivatif Kawasan Permukiman', date: '2 Okt 2026', status: 'Kadaluwarsa' },
    // IGT Lainnya (eksternal): no detail page, everything uploaded is available immediately
    { category: 'lainnya', id: 'IGT-EXT-004', name: 'Rencana Tata Ruang Wilayah', source: 'Dinas Pertanahan dan Tata Ruang DIY', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-003', name: 'Tutupan Lahan Nasional', source: 'Kementerian Lingkungan Hidup', date: '15 Okt 2026', updated: '15 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-002', name: 'Batas Wilayah Administrasi', source: 'Badan Informasi Geospasial', date: '12 Okt 2026', updated: '12 Okt 2026', status: 'Tersedia' },
    { category: 'lainnya', id: 'IGT-EXT-001', name: 'Peta Risiko Bencana', source: 'Badan Nasional Penanggulangan Bencana', date: '10 Okt 2026', updated: '10 Okt 2026', status: 'Tersedia' },
  ];

  const canView = (role, category) => Boolean(ROLES[role] && ROLES[role].view.includes(category));
  const canUpload = (role, category) => Boolean(ROLES[role] && ROLES[role].upload.includes(category));
  // Submissions a role may see in Upload Data: its upload categories, and only its own records for Umum.
  const submissionsFor = (role, records) =>
    records.filter((r) => canUpload(role, r.category) && (!ROLES[role].ownSubmissionsOnly || r.owner === role));
  const inCatalog = (record) => record.status === CATEGORIES[record.category].catalogStatus;
  // Terkompilasi / Terintegrasi exist only for categories with an integration step.
  const integrationRecords = (records) => records.filter((r) => CATEGORIES[r.category].integration);
  const loadRecords = () => RECORDS.map((record) => ({ ...record }));
  const countByStatus = (records, status) => records.filter((record) => record.status === status).length;

  return { CATEGORY_ORDER, CATEGORIES, ROLES, canView, canUpload, submissionsFor, inCatalog, integrationRecords, loadRecords, countByStatus };
})();

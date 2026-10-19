// Sample data and role permissions for the IGT-PR mockup. Static: nothing is fetched or persisted.
//
// Data model
// - One record = one IGT dataset together with its latest submission. Re-submissions of an
//   already integrated dataset are not modelled, so counting records equals counting datasets.
// - The catalog pages show only records with status `Terintegrasi`.
// - The Upload Data page shows every record of a category (the submission lifecycle).
//
// Lifecycle
// - IGT Pertanahan / IGT Tata Ruang: Proses -> Terkompilasi -> Terintegrasi (Revisi = returned to Operator).
// - IGT Derivatif: Proses -> Disetujui -> Terintegrasi (Ditolak = rejected). Admin uploads start as Disetujui.
// - IGT Lainnya: external layers added by Superadmin are available immediately (Terintegrasi).
const IgtData = (() => {
  const CATEGORY_ORDER = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];

  const CATEGORIES = {
    pertanahan: { label: 'IGT Pertanahan', slug: 'igt-pertanahan', kind: 'bidang', detail: 'utama' },
    'tata-ruang': { label: 'IGT Tata Ruang', slug: 'igt-tata-ruang', kind: 'kawasan', detail: 'utama' },
    derivatif: { label: 'IGT Derivatif', slug: 'igt-derivatif', detail: 'derivatif' },
    lainnya: { label: 'IGT Lainnya', slug: 'igt-lainnya' },
  };

  // Permissions. Every role may browse all four catalogs (`view`). Uploading and managing submissions
  // (`upload`) is narrower: IGT Lainnya (Eksternal) can only be managed by Superadmin, and Umum (public users) can only upload IGT Derivatif.
  // Umum sees only its own submissions (records with `owner: 'umum'`) and has no Model Builder.
  const ALL = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'];
  const ROLES = {
    superadmin: { label: 'Superadmin', avatar: 'SA', view: ALL, upload: ALL },
    admin: { label: 'Admin', avatar: 'AD', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'] },
    operator: { label: 'Operator Pusat', avatar: 'JH', view: ALL, upload: ['pertanahan', 'tata-ruang', 'derivatif'] },
    umum: { label: 'Umum', avatar: 'UM', view: ALL, upload: ['derivatif'], ownSubmissionsOnly: true, modelBuilder: false },
  };

  // `n` is the record index understood by the shared detail pages (igt-utama-detail, layer-derivatif-detail).
  // `updated` is the date the dataset was last updated once integrated (catalog "Tanggal Update").
  const RECORDS = [
    // IGT Pertanahan (berbasis bidang)
    { category: 'pertanahan', n: 0, id: 'IGT-2026-012', name: 'IGT Bidang Wilayah A', date: '18 Okt 2026', status: 'Proses' },
    { category: 'pertanahan', n: 2, id: 'IGT-2026-010', name: 'IGT Bidang Wilayah B', date: '15 Okt 2026', status: 'Revisi' },
    { category: 'pertanahan', n: 4, id: 'IGT-2026-008', name: 'IGT Bidang Infrastruktur', date: '12 Okt 2026', status: 'Proses' },
    { category: 'pertanahan', n: 5, id: 'IGT-2026-007', name: 'IGT Bidang Kota Yogyakarta', date: '10 Okt 2026', updated: '12 Okt 2026', status: 'Terintegrasi' },
    { category: 'pertanahan', n: 7, id: 'IGT-2026-005', name: 'IGT Bidang Kecamatan Depok', date: '6 Okt 2026', updated: '8 Okt 2026', status: 'Terintegrasi' },
    // IGT Tata Ruang (berbasis kawasan)
    { category: 'tata-ruang', n: 1, id: 'IGT-2026-011', name: 'IGT Kawasan Hutan', date: '16 Okt 2026', updated: '17 Okt 2026', status: 'Terintegrasi' },
    { category: 'tata-ruang', n: 3, id: 'IGT-2026-009', name: 'IGT Kawasan Lindung', date: '14 Okt 2026', status: 'Terkompilasi' },
    { category: 'tata-ruang', n: 6, id: 'IGT-2026-006', name: 'IGT Kawasan Rawan Bencana', date: '9 Okt 2026', updated: '11 Okt 2026', status: 'Terintegrasi' },
    // IGT Derivatif
    { category: 'derivatif', n: 0, id: 'DRV-2026-008', name: 'Derivatif Kawasan Hutan', date: '16 Okt 2026', updated: '17 Okt 2026', status: 'Terintegrasi' },
    { category: 'derivatif', n: 1, id: 'DRV-2026-007', name: 'Derivatif Bidang Wilayah A', date: '15 Okt 2026', status: 'Proses' },
    { category: 'derivatif', n: 2, id: 'DRV-2026-006', name: 'Derivatif Kawasan Lindung', date: '14 Okt 2026', status: 'Ditolak' },
    { category: 'derivatif', n: 3, id: 'DRV-2026-005', name: 'Derivatif Bidang Wilayah B', date: '12 Okt 2026', status: 'Disetujui' },
    // IGT Lainnya (eksternal): no detail page, available immediately
    { category: 'lainnya', id: 'IGT-EXT-004', name: 'Rencana Tata Ruang Wilayah', source: 'Dinas Pertanahan dan Tata Ruang DIY', date: '18 Okt 2026', updated: '18 Okt 2026', status: 'Terintegrasi' },
    { category: 'lainnya', id: 'IGT-EXT-003', name: 'Tutupan Lahan Nasional', source: 'Kementerian Lingkungan Hidup', date: '15 Okt 2026', updated: '15 Okt 2026', status: 'Terintegrasi' },
    { category: 'lainnya', id: 'IGT-EXT-002', name: 'Batas Wilayah Administrasi', source: 'Badan Informasi Geospasial', date: '12 Okt 2026', updated: '12 Okt 2026', status: 'Terintegrasi' },
    { category: 'lainnya', id: 'IGT-EXT-001', name: 'Peta Risiko Bencana', source: 'Badan Nasional Penanggulangan Bencana', date: '10 Okt 2026', updated: '10 Okt 2026', status: 'Terintegrasi' },
  ];

  const canView = (role, category) => Boolean(ROLES[role] && ROLES[role].view.includes(category));
  const canUpload = (role, category) => Boolean(ROLES[role] && ROLES[role].upload.includes(category));
  // Submissions a role may see in Upload Data: its upload categories, and only its own records for Umum.
  const submissionsFor = (role, records) =>
    records.filter((r) => canUpload(role, r.category) && (!ROLES[role].ownSubmissionsOnly || r.owner === role));
  const loadRecords = () => RECORDS.map((record) => ({ ...record }));
  const countByStatus = (records, status) => records.filter((record) => record.status === status).length;

  return { CATEGORY_ORDER, CATEGORIES, ROLES, canView, canUpload, submissionsFor, loadRecords, countByStatus };
})();

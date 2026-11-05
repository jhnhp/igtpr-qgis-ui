// Page logic for the role pages: navigation, dashboard, IGT catalogs and Upload Data.
// Needs shared/igt-data.js. Every QGIS-related action is a simulation (alert/confirm), nothing is sent anywhere.
const IgtApp = (() => {
  const { CATEGORIES, CATEGORY_ORDER, ROLES } = IgtData;
  const $ = (selector) => document.querySelector(selector);
  // Use the official ATR/BPN website favicon in the browser tab.
  const favicon = document.createElement('link');
  favicon.rel = 'icon';
  favicon.type = 'image/x-icon';
  favicon.href = 'https://www.atrbpn.go.id/favicon.ico';
  document.head.appendChild(favicon);

  // RemixIcon paths used in IGTPR-UI-mockup (assets/lib/remixicon & assets/js/core/layout.js)
  const RI_PATHS = {
    'map-pin-line': 'M12 20.9l4.95-4.95a7 7 0 1 0-9.9 0L12 20.9zm0 2.828l-6.364-6.364a9 9 0 1 1 12.728 0L12 23.728zM12 13a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm0 2a4 4 0 1 1 0-8 4 4 0 0 1 0 8z',
    'building-line': 'M21 19h2v2H1v-2h2V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v15h4v-8h-2V9h3a1 1 0 0 1 1 1v9zM5 5v14h8V5H5zm2 6h4v2H7v-2zm0-4h4v2H7V7z',
    'building-2-line': 'M3 19V5.7a1 1 0 0 1 .658-.94l9.671-3.516a.5.5 0 0 1 .671.47v4.953l6.316 2.105a1 1 0 0 1 .684.949V19h2v2H1v-2h2zm2 0h7V3.855L5 6.401V19zm14 0v-8.558l-5-1.667V19h5z',
    'map-2-line': 'M2 5l7-3 6 3 6.303-2.701a.5.5 0 0 1 .697.46V19l-7 3-6-3-6.303 2.701a.5.5 0 0 1-.697-.46V5zm14 14.395l4-1.714V5.033l-4 1.714v12.648zm-2-.131V6.736l-4-2v12.528l4 2zm-6-2.011V4.605L4 6.319v12.648l4-1.714z',
    'stack-line': 'M20.083 15.2l1.202.721a.5.5 0 0 1 0 .858l-8.77 5.262a1 1 0 0 1-1.03 0l-8.77-5.262a.5.5 0 0 1 0-.858l1.202-.721L12 20.05l8.083-4.85zm0-4.7l1.202.721a.5.5 0 0 1 0 .858L12 17.65l-9.285-5.571a.5.5 0 0 1 0-.858l1.202-.721L12 15.35l8.083-4.85zm-7.569-9.191l8.771 5.262a.5.5 0 0 1 0 .858L12 13 2.715 7.429a.5.5 0 0 1 0-.858l8.77-5.262a1 1 0 0 1 1.03 0zM12 3.332L5.887 7 12 10.668 18.113 7 12 3.332z',
    'global-line': 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-2.29-2.333A17.9 17.9 0 0 1 8.027 13H4.062a8.008 8.008 0 0 0 5.648 6.667zM10.03 13c.151 2.439.848 4.73 1.97 6.752A15.905 15.905 0 0 0 13.97 13h-3.94zm9.908 0h-3.965a17.9 17.9 0 0 1-1.683 6.667A8.008 8.008 0 0 0 19.938 13zM4.062 11h3.965A17.9 17.9 0 0 1 9.71 4.333 8.008 8.008 0 0 0 4.062 11zm5.969 0h3.938A15.905 15.905 0 0 0 12 4.248 15.905 15.905 0 0 0 10.03 11zm4.259-6.667A17.9 17.9 0 0 1 15.973 11h3.965a8.008 8.008 0 0 0-5.648-6.667z',
    'database-2-line': 'M5 12.5c0 .313.461.858 1.53 1.393C7.914 14.585 9.877 15 12 15c2.123 0 4.086-.415 5.47-1.107 1.069-.535 1.53-1.08 1.53-1.393v-2.171C17.35 11.349 14.827 12 12 12s-5.35-.652-7-1.671V12.5zm14 2.829C17.35 16.349 14.827 17 12 17s-5.35-.652-7-1.671V17.5c0 .313.461.858 1.53 1.393C7.914 19.585 9.877 20 12 20c2.123 0 4.086-.415 5.47-1.107 1.069-.535 1.53-1.08 1.53-1.393v-2.171zM3 17.5v-10C3 5.015 7.03 3 12 3s9 2.015 9 4.5v10c0 2.485-4.03 4.5-9 4.5s-9-2.015-9-4.5zm9-7.5c2.123 0 4.086-.415 5.47-1.107C18.539 8.358 19 7.813 19 7.5c0-.313-.461-.858-1.53-1.393C16.086 5.415 14.123 5 12 5c-2.123 0-4.086.415-5.47 1.107C5.461 6.642 5 7.187 5 7.5c0 .313.461.858 1.53 1.393C7.914 9.585 9.877 10 12 10z',
    'upload-cloud-2-line': 'M12 12.586l4.243 4.242-1.415 1.415L13 16.415V22h-2v-5.587l-1.828 1.83-1.415-1.415L12 12.586zM12 2a7.001 7.001 0 0 1 6.954 6.194 5.5 5.5 0 0 1-.953 10.784v-2.014a3.5 3.5 0 1 0-1.112-6.91 5 5 0 1 0-9.777 0 3.5 3.5 0 0 0-1.292 6.88l.18.03v2.014a5.5 5.5 0 0 1-.954-10.784A7 7 0 0 1 12 2z',
    'file-text-line': 'M21 8v12.993A1 1 0 0 1 20.007 22H3.993A.993.993 0 0 1 3 21.008V2.992C3 2.455 3.449 2 4.002 2h10.995L21 8zm-2 1h-5V4H5v16h14V9zM8 7h3v2H8V7zm0 4h8v2H8v-2zm0 4h8v2H8v-2z',
    'node-tree': 'M10 2c.552 0 1 .448 1 1v4c0 .552-.448 1-1 1H8v2h5V9c0-.552.448-1 1-1h6c.552 0 1 .448 1 1v4c0 .552-.448 1-1 1h-6c-.552 0-1-.448-1-1v-1H8v6h5v-1c0-.552.448-1 1-1h6c.552 0 1 .448 1 1v4c0 .552-.448 1-1 1h-6c-.552 0-1-.448-1-1v-1H7c-.552 0-1-.448-1-1V8H4c-.552 0-1-.448-1-1V3c0-.552.448-1 1-1h6zm9 16h-4v2h4v-2zm0-8h-4v2h4v-2zM9 4H5v2h4V4z',
    'folder-line': 'M4 5v14h16V7h-8.414l-2-2H4zm8.414 0H21a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h7.414l2 2z',
    'checkbox-circle-line': 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-.997-4L6.76 11.757l1.414-1.414 2.829 2.829 5.656-5.657 1.415 1.414L11.003 16z',
    'time-line': 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm1-8h4v2h-6V7h2v5z',
    'error-warning-line': 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5h2v2h-2v-2zm0-8h2v6h-2V7z',
    'eye-line': 'M12 3c5.392 0 9.878 3.88 10.819 9-.94 5.12-5.427 9-10.819 9-5.392 0-9.878-3.88-10.819-9C2.121 6.88 6.608 3 12 3zm0 16a9.005 9.005 0 0 0 8.777-7 9.005 9.005 0 0 0-17.554 0A9.005 9.005 0 0 0 12 19zm0-2.5a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9zm0-2a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z',
    'focus-3-line': 'M13 1l.001 3.062A8.004 8.004 0 0 1 19.938 11H23v2l-3.062.001a8.004 8.004 0 0 1-6.937 6.937L13 23h-2v-3.062a8.004 8.004 0 0 1-6.938-6.937L1 13v-2h3.062A8.004 8.004 0 0 1 11 4.062V1h2zm-1 5a6 6 0 1 0 0 12 6 6 0 0 0 0-12zm0 4a2 2 0 1 1 0 4 2 2 0 0 1 0-4z',
    'check-line': 'M10 15.172l9.192-9.193 1.415 1.414L10 18l-6.364-6.364 1.414-1.414z',
    'close-line': 'M12 10.586l4.95-4.95 1.414 1.414-4.95 4.95 4.95 4.95-1.414 1.414-4.95-4.95-4.95 4.95-1.414-1.414 4.95-4.95-4.95-4.95L7.05 5.636z',
    'edit-line': 'M6.414 16L16.556 5.858l-1.414-1.414L5 14.586V16h1.414zm.829 2H3v-4.243L14.435 2.322a1 1 0 0 1 1.414 0l2.829 2.829a1 1 0 0 1 0 1.414L7.243 18zM3 20h18v2H3v-2z',
    'delete-bin-line': 'M17 6h5v2h-2v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V8H2V6h5V3a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v3zm1 2H6v12h12V8zm-9 3h2v6H9v-6zm4 0h2v6h-2v-6zM9 4v2h6V4H9z',
    'notification-3-line': 'M20 17h2v2H2v-2h2v-7a8 8 0 1 1 16 0v7zm-2 0v-7a6 6 0 1 0-12 0v7h12zm-9 4h6v2H9v-2z',
    'information-line': 'M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM11 7h2v2h-2V7zm0 4h2v6h-2v-6z',
    'external-link-line': 'M10 6v2H5v11h11v-5h2v6a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6zm11-3v8h-2V6.413l-7.793 7.794-1.414-1.414L17.585 5H13V3h8z',
    'shape-line': 'M2 3.993A1 1 0 0 1 2.992 3h18.016c.548 0 .992.445.992.993v16.014a1 1 0 0 1-.992.993H2.992A.993.993 0 0 1 2 20.007V3.993zM4 5v14h16V5H4z',
  };

  const ri = (name) => `<svg class="ri-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="${RI_PATHS[name] || RI_PATHS['map-pin-line']}"/></svg>`;

  const notifBtn = document.querySelector('.icon-btn[aria-label="Notifikasi"]');
  if (notifBtn) notifBtn.innerHTML = ri('notification-3-line');

  const STATUS_CLASS = {
    Proses: 'info',
    Terkompilasi: 'info',
    Terintegrasi: 'ok',
    Revisi: 'warn',
    Disetujui: 'ok',
    Ditolak: 'fix',
    Diajukan: 'info',
    Kadaluwarsa: 'warn',
    Tersedia: 'ok',
  };

  const badge = (status) => `<span class="status ${STATUS_CLASS[status] || ''}">${status}</span>`;
  const button = (cls, action, id, label, extra = '') =>
    `<button class="btn ${cls} qgis-action" data-action="${action}" data-id="${id}"${extra}>${label}</button>`;
  const link = (href, label) => `<a class="btn btn-soft qgis-action" href="${href}">${label}</a>`;
  const toolbar = (...items) => `<div class="toolbar">${items.filter(Boolean).join('')}</div>`;
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };

  const yearOf = (record) => {
    const match = String(record.updated || record.date || '').match(/(20[0-9]{2})/);
    return match ? match[1] : 'Tidak diketahui';
  };
  // Keep future catalog years selectable even before datasets for those years are added.
  const yearOptions = (records) => {
    const fromSubs = records.flatMap((r) => (r.subLayers ? r.subLayers.map((s) => s.year || yearOf(s)) : []));
    return [...new Set([...records.map(yearOf), ...fromSubs, '2026', '2025', '2024', '2023', '2021', '2019'])].filter((year) => year && year !== 'Tidak diketahui').sort().reverse();
  };
  const yearFilterOptions = (records) => '<option value="all" selected>Semua tahun</option>' + yearOptions(records).map((year) => '<option value="' + year + '">' + year + '</option>').join('');
  const provOptions = (records) => {
    if (typeof IgtData !== 'undefined' && IgtData.REGIONS) {
      return Object.keys(IgtData.REGIONS).sort();
    }
    const fromData = records.map((r) => r.prov).filter(Boolean);
    const defaults = ['D.I. Yogyakarta', 'Jawa Tengah', 'Kalimantan Barat', 'Nasional'];
    return [...new Set([...fromData, ...defaults])].sort();
  };
  const provFilterOptions = (records) =>
    '<option value="all" selected>Semua Provinsi</option>' +
    provOptions(records).map((p) => '<option value="' + p + '">' + p + '</option>').join('');
  const kabOptions = (records, selectedProv = 'all') => {
    if (typeof IgtData !== 'undefined' && IgtData.REGIONS) {
      if (selectedProv && selectedProv !== 'all' && IgtData.REGIONS[selectedProv]) {
        return IgtData.REGIONS[selectedProv];
      }
      return [];
    }
    const fromData = records.map((r) => r.kab).filter(Boolean);
    const defaults = ['Kab. Sleman', 'Kab. Bantul', 'Kab. Kulon Progo', 'Kab. Gunungkidul', 'Kota Yogyakarta', 'Multi-Kabupaten', 'Seluruh Indonesia'];
    return [...new Set([...fromData, ...defaults])].sort();
  };
  const kabFilterOptions = (records, selectedProv = 'all') =>
    '<option value="all" selected>Semua Kab / Kota</option>' +
    kabOptions(records, selectedProv).map((k) => '<option value="' + k + '">' + k + '</option>').join('');
  const statCard = (label, num, hint, icon, cls, id) =>
    `<div class="card stat"><div><div class="label">${label}</div><div class="num" id="${id}">${num}</div>` +
    `<div class="hint">${hint}</div></div><div class="stat-icon${cls ? ' ' + cls : ''}">${icon}</div></div>`;

  const DETAIL_URL = {
    utama: '../../operator/igt-utama-detail/index.html',
    derivatif: '../../operator/layer-derivatif-detail/index.html',
  };
  const BIDANG_WORKFLOW_URL = '../derivatif-bidang/index.html';

  const isV2Role = (role) => Boolean(ROLES[role] && ROLES[role].v2);
  const baseRoleOf = (role) => (ROLES[role] && ROLES[role].baseRole) || role;

  function managementCategories(role) {
    const base = baseRoleOf(role);
    if (base === 'umum') return ['derivatif'];
    return ['igt-utama', 'derivatif'];
  }

  const managementLabel = (key) => (key === 'semua' ? 'Semua Kategori' : key === 'igt-utama' ? 'IGT Utama' : CATEGORIES[key].label);
  const managementShortLabel = (key) => (key === 'semua' ? 'Semua Kategori' : key === 'igt-utama' ? 'IGT Utama' : (CATEGORIES[key].shortLabel || CATEGORIES[key].label));
  const CATALOG_ICON = {
    'igt-pr': ri('database-2-line'),
    pertanahan: ri('map-pin-line'),
    'tata-ruang': ri('map-2-line'),
    derivatif: ri('stack-line'),
    lainnya: ri('global-line'),
  };

  const categoryIcon = (cat) => {
    if (cat === 'tata-ruang') return ri('map-2-line');
    if (cat === 'derivatif') return ri('stack-line');
    if (cat === 'lainnya') return ri('global-line');
    if (cat === 'igt-pr') return ri('database-2-line');
    return ri('map-pin-line');
  };

  const MANAGEMENT_ICON = {
    'igt-utama': ri('database-2-line'),
    derivatif: ri('upload-cloud-2-line'),
    lainnya: ri('file-text-line'),
  };

  // ----------------------------------------------------------------- dashboard

  // Repository overview: how many datasets are compiled and integrated. No upload controls here.
  function dashboard(role) {
    const records = IgtData.loadRecords().filter((r) => IgtData.canView(role, r.category));
    const manageButtons = managementCategories(role)
      .map((key) => '<a class="btn btn-primary menu-btn" id="upload-button-' + key + '" href="../upload-data/index.html?tab=' + key + '">' + (MANAGEMENT_ICON[key] || ri('database-2-line')) + '<span>' + managementShortLabel(key) + '</span></a>')
      .join('');
    $('#view').innerHTML =
      '<div class="field year-filter-wrap"><label for="dashboard-year-filter">FILTER TAHUN</label><select id="dashboard-year-filter">' + yearFilterOptions(records) + '</select></div>' +
      '<div class="grid stats">' +
      statCard('Terkompilasi', '0', 'Menunggu integrasi', ri('folder-line'), 'amber', 'count-compiled') +
      statCard('Terintegrasi', '0', 'Pertanahan dan Tata Ruang', ri('checkbox-circle-line'), 'green', 'count-integrated') +
      '</div>' +
      '<section class="card" style="margin-bottom:16px;">' +
      '<div class="card-head"><div><h2>Katalog IGT</h2><p>Katalog terpadu data IGT Pertanahan dan Tata Ruang Kementerian ATR/BPN.</p></div></div>' +
      '<div class="dash-cat-widget" id="dashboard-catalog-widget"></div>' +
      '</section>' +
      '<section class="card">' +
      '<div class="card-head menu-upload-head"><div><h2>Kelola data</h2><p>Unggah data baru dan pantau status pengajuan.</p></div></div>' +
      '<div class="menu-buttons' + (role === 'superadmin' ? ' menu-buttons-superadmin' : '') + '" id="upload-buttons">' + manageButtons + '</div>' +
      '<div class="menu-buttons model-builder-buttons"><a class="btn btn-primary menu-btn" id="model-builder-button" href="../../../shared/model-builder/index.html?role=' + role + '">' + ri('node-tree') + '<span>Model Builder</span></a></div>' +
      '</section>';
    const catWidget = dashboardCatalog('#dashboard-catalog-widget', role);
    const updateDashboard = () => {
      const year = $('#dashboard-year-filter').value;
      const visible = records.filter((record) => year === 'all' || yearOf(record) === year || (record.subLayers && record.subLayers.some((s) => (s.year || s.updated || '').includes(year))));
      const staged = IgtData.integrationRecords(visible);
      setText('count-compiled', IgtData.countByStatus(staged, 'Terkompilasi'));
      setText('count-integrated', IgtData.countByStatus(staged, 'Terintegrasi'));
      if (catWidget && catWidget.setYear) {
        catWidget.setYear(year);
      }
    };
    $('#dashboard-year-filter').addEventListener('change', updateDashboard);
    updateDashboard();
  }

  // ------------------------------------------------------------------- catalog

  const WMS_MESSAGE = (name) =>
    `Simulasi WMS: layanan peta "${name}" akan ditambahkan sebagai layer WMS (gambar peta) di QGIS. ` +
    'Belum terhubung ke layanan nyata.';
  const WFS_MESSAGE = (name) =>
    `Simulasi WFS: layanan fitur "${name}" akan dimuat sebagai layer vektor WFS di QGIS. ` +
    'Belum terhubung ke layanan nyata.';

  // Verifikasi izin akses WFS berdasarkan role dan satker:
  // - Superadmin: Bisa akses semua WFS
  // - Admin & Operator: Bisa akses WFS sesuai satkernya (Kantah Kab. Sleman pada akun demo)
  // - Umum: Hanya WMS (tidak dapat mengakses WFS)
  function canAccessWfs(role, dataset) {
    const r = (role || '').replace('2', '').toLowerCase();
    if (r === 'superadmin') return true;
    if (r === 'umum') return false;
    const roleCfg = (typeof IgtData !== 'undefined' && IgtData.ROLES && IgtData.ROLES[role]) ? IgtData.ROLES[role] : null;
    const userSatker = (roleCfg && roleCfg.satker) || 'Kantah Kab. Sleman';
    const dsSatker = (dataset && (dataset.satker || dataset.direktorat || '')) ? String(dataset.satker || dataset.direktorat).trim() : '';
    return dsSatker.toLowerCase().includes('sleman') || dsSatker.toLowerCase() === userSatker.toLowerCase();
  }

  // Referensi Hirarki Wilayah Administrasi untuk Filter WFS
  const WFS_ADMIN_DATA = {
    'D.I. Yogyakarta': {
      'Kab. Sleman': {
        'Kec. Depok': ['Kel. Caturtunggal', 'Kel. Maguwoharjo', 'Kel. Condongcatur'],
        'Kec. Mlati': ['Kel. Sendangadi', 'Kel. Sinduadi', 'Kel. Tirtoadi', 'Kel. Tlogoadi', 'Kel. Sumberadi'],
        'Kec. Gamping': ['Kel. Ambarketawang', 'Kel. Balecatur', 'Kel. Banyuraden', 'Kel. Nogotirto', 'Kel. Trihanggo'],
        'Kec. Ngaglik': ['Kel. Donoharjo', 'Kel. Minomartani', 'Kel. Sardonoharjo', 'Kel. Sariharjo', 'Kel. Sinduharjo'],
        'Kec. Kalasan': ['Kel. Purwomartani', 'Kel. Selomartani', 'Kel. Tamanmartani', 'Kel. Tirtomartani'],
        'Kec. Berbah': ['Kel. Jogotirto', 'Kel. Kalitirto', 'Kel. Sendangtirto', 'Kel. Tegaltirto'],
      },
      'Kab. Bantul': {
        'Kec. Sewon': ['Kel. Bangunharjo', 'Kel. Panggungharjo', 'Kel. Pendowoharjo', 'Kel. Timbulharjo'],
        'Kec. Banguntapan': ['Kel. Banguntapan', 'Kel. Baturetno', 'Kel. Jagalan', 'Kel. Potorono', 'Kel. Singosaren'],
        'Kec. Kasihan': ['Kel. Bangunjiwo', 'Kel. Ngestiharjo', 'Kel. Tamantirto', 'Kel. Tirtonirmolo'],
      },
      'Kota Yogyakarta': {
        'Kec. Danurejan': ['Kel. Bausasran', 'Kel. Suryatmajan', 'Kel. Tegalpanggung'],
        'Kec. Gondomanan': ['Kel. Ngupasan', 'Kel. Prawirodirjan'],
        'Kec. Umbulharjo': ['Kel. Giwangan', 'Kel. Muja Muju', 'Kel. Pandeyan', 'Kel. Semaki', 'Kel. Sorosutan'],
      },
      'Kab. Kulon Progo': {
        'Kec. Wates': ['Kel. Bendungan', 'Kel. Giripeni', 'Kel. Karangwuni', 'Kel. Wates'],
        'Kec. Temon': ['Kel. Glagah', 'Kel. Jangkaran', 'Kel. Palihan', 'Kel. Temon Kulon'],
      },
      'Kab. Gunungkidul': {
        'Kec. Wonosari': ['Kel. Baleharjo', 'Kel. Duwet', 'Kel. Kepek', 'Kel. Wonosari'],
        'Kec. Playen': ['Kel. Playen', 'Kel. Logandeng', 'Kel. Plembutan'],
      },
    },
    'Jawa Barat': {
      'Kota Bandung': {
        'Kec. Coblong': ['Kel. Dago', 'Kel. Lebakgede', 'Kel. Sadangserang'],
        'Kec. Sukasari': ['Kel. Gegerkalong', 'Kel. Sarijadi', 'Kel. Isola'],
      },
      'Kab. Bogor': {
        'Kec. Cibinong': ['Kel. Cirimekar', 'Kel. Pakansari', 'Kel. Tengah'],
      },
    },
    'DKI Jakarta': {
      'Kota Jakarta Selatan': {
        'Kec. Kebayoran Baru': ['Kel. Selong', 'Kel. Senayan', 'Kel. Melawai'],
        'Kec. Cilandak': ['Kel. Cilandak Barat', 'Kel. Cipete Selatan'],
      },
      'Kota Jakarta Pusat': {
        'Kec. Gambir': ['Kel. Gambir', 'Kel. Kebon Kelapa', 'Kel. Petojo Selatan'],
      },
    },
    'Jawa Tengah': {
      'Kota Semarang': {
        'Kec. Semarang Tengah': ['Kel. Miroto', 'Kel. Pandansari', 'Kel. Sekayu'],
      },
      'Kota Surakarta': {
        'Kec. Banjarsari': ['Kel. Manahan', 'Kel. Nusukan', 'Kel. Kadipiro'],
      },
    },
    'Jawa Timur': {
      'Kota Surabaya': {
        'Kec. Gubeng': ['Kel. Airlangga', 'Kel. Barata Jaya', 'Kel. Gubeng'],
      },
    },
    'Bali': {
      'Kota Denpasar': {
        'Kec. Denpasar Selatan': ['Kel. Sanur', 'Kel. Sidakarya', 'Kel. Panjer'],
      },
    },
  };

  function showWfsFilterModal(dataset, role) {
    const dsName = (dataset && (dataset.name || dataset.layer || dataset.id)) || 'Layer WFS';
    let modal = document.getElementById('wfs-filter-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'wfs-filter-modal';
      modal.className = 'modal-backdrop v2-modal-backdrop';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.style.cssText = 'position:fixed;inset:0;z-index:1001;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto;';
      document.body.appendChild(modal);

      modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.closest('[data-close-wfs-modal]')) {
          modal.style.display = 'none';
          modal.hidden = true;
        }
      });
    }

    const modalHtml = `
      <div class="wfs-modal-card">
        <div class="wfs-modal-head">
          <div>
            <div style="font-size:10px;font-weight:800;color:#bfdbfe;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:3px;">
              Sistem Informasi Geospasial ATR/BPN · Layanan Fitur WFS
            </div>
            <h3 style="margin:0 0 3px;font-size:16px;font-weight:800;color:#fff;">Opsi Pemuatan Layer WFS</h3>
            <p style="margin:0;font-size:11.5px;color:#bfdbfe;">Layer: <strong>${dsName}</strong></p>
          </div>
          <button type="button" class="btn btn-soft" data-close-wfs-modal style="background:rgba(255,255,255,0.15);color:#fff;border:none;border-radius:8px;font-weight:700;">✕</button>
        </div>

        <div class="wfs-modal-body">
          <div style="padding:10px 12px;background:#fef3c7;border:1px solid #fde68a;border-radius:9px;color:#92400e;font-size:11.5px;line-height:1.5;display:flex;align-items:flex-start;gap:8px;">
            <span style="font-size:15px;line-height:1;">⚠️</span>
            <div><strong>Perhatian:</strong> Data WFS nasional berukuran sangat besar. Disarankan menggunakan batasan wilayah (Batas Admin atau AOI) agar proses unduh dan visualisasi lebih cepat.</div>
          </div>

          <!-- Opsi 1: Load Semua -->
          <div class="wfs-opt-card" id="wfs-card-all">
            <div class="wfs-opt-header">
              <input type="radio" name="wfs-mode-radio" value="all" id="wfs-radio-all">
              <label for="wfs-radio-all" style="flex:1;cursor:pointer;">
                <div class="wfs-opt-title">1. Load Semua (Seluruh Indonesia)</div>
                <p class="wfs-opt-desc">Memuat seluruh data fitur spasial cakupan nasional tanpa batasan wilayah.</p>
              </label>
            </div>
          </div>

          <!-- Opsi 2: Batas Admin (Default) -->
          <div class="wfs-opt-card active" id="wfs-card-admin">
            <div class="wfs-opt-header">
              <input type="radio" name="wfs-mode-radio" value="admin" id="wfs-radio-admin" checked>
              <label for="wfs-radio-admin" style="flex:1;cursor:pointer;">
                <div class="wfs-opt-title">2. Load Berdasarkan Batas Admin</div>
                <p class="wfs-opt-desc">Filter fitur WFS berdasarkan hirarki wilayah administratif pemerintahan.</p>
              </label>
            </div>
            <div class="wfs-opt-subpanel" id="wfs-admin-panel">
              <div class="wfs-grid-2x2">
                <div class="wfs-field">
                  <label for="wfs-sel-prov">Provinsi (Ketik / Pilih)</label>
                  <input list="wfs-prov-datalist" id="wfs-sel-prov" value="" placeholder="Pilih atau ketik provinsi..." autocomplete="off">
                  <datalist id="wfs-prov-datalist"></datalist>
                </div>
                <div class="wfs-field">
                  <label for="wfs-sel-kab">Kabupaten / Kota</label>
                  <select id="wfs-sel-kab"></select>
                </div>
                <div class="wfs-field">
                  <label for="wfs-sel-kec">Kecamatan</label>
                  <select id="wfs-sel-kec"></select>
                </div>
                <div class="wfs-field">
                  <label for="wfs-sel-desa">Desa / Kelurahan</label>
                  <select id="wfs-sel-desa"></select>
                </div>
              </div>
            </div>
          </div>

          <!-- Opsi 3: AOI -->
          <div class="wfs-opt-card" id="wfs-card-aoi">
            <div class="wfs-opt-header">
              <input type="radio" name="wfs-mode-radio" value="aoi" id="wfs-radio-aoi">
              <label for="wfs-radio-aoi" style="flex:1;cursor:pointer;">
                <div class="wfs-opt-title">3. Load Berdasarkan AOI (Area of Interest)</div>
                <p class="wfs-opt-desc">Batasi fitur spasial dengan poligon delineasi atau penggambaran area di kanvas.</p>
              </label>
            </div>
            <div class="wfs-opt-subpanel" id="wfs-aoi-panel" style="display:none;">
              <div class="wfs-aoi-choice">
                <label class="wfs-aoi-subrow">
                  <input type="radio" name="wfs-aoi-sub-radio" value="layer" checked id="wfs-aoi-sub-layer">
                  <span>Pilih AOI yang ada di QGIS:</span>
                </label>
                <div style="margin-left:22px;margin-bottom:8px;">
                  <select id="wfs-sel-aoi-layer" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:7px;font-size:11.5px;color:#0f294d;">
                    <option value="Batas Kawasan Perencanaan DIY">Layer: Batas Kawasan Perencanaan DIY (Poligon)</option>
                    <option value="Delineasi Area Prioritas RDTR">Layer: Delineasi Area Prioritas RDTR</option>
                    <option value="Fitur Terpilih di Kanvas QGIS (Selected Features)">Fitur Terpilih di Kanvas QGIS (Selected Features)</option>
                    <option value="Buffer Koridor 500m Infrastruktur">Layer: Buffer Koridor 500m Infrastruktur</option>
                  </select>
                </div>

                <label class="wfs-aoi-subrow">
                  <input type="radio" name="wfs-aoi-sub-radio" value="draw" id="wfs-aoi-sub-draw">
                  <span>Gambar AOI-nya:</span>
                </label>
                <div style="margin-left:22px;">
                  <button type="button" class="wfs-draw-btn" id="wfs-btn-draw-action">
                    <span>🖌 Gambar Kotak Pembatas (BBOX) di Kanvas</span>
                  </button>
                  <div style="font-size:10.5px;color:#64748b;margin-top:4px;">Klik untuk mengaktifkan kursor gambar poligon/kotak pada kanvas peta QGIS.</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Action buttons -->
          <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px;padding-top:12px;border-top:1px solid #e2e8f0;">
            <button type="button" class="btn btn-soft" data-close-wfs-modal>Batal</button>
            <button type="button" class="btn btn-primary" id="wfs-btn-submit" style="background:#7c3aed;border-color:#7c3aed;">
              <span>Muat WFS ke Kanvas →</span>
            </button>
          </div>
        </div>
      </div>
    `;

    modal.innerHTML = modalHtml;
    modal.hidden = false;
    modal.style.display = 'flex';

    // Wiring
    const cardAll = modal.querySelector('#wfs-card-all');
    const cardAdmin = modal.querySelector('#wfs-card-admin');
    const cardAoi = modal.querySelector('#wfs-card-aoi');
    const radioAll = modal.querySelector('#wfs-radio-all');
    const radioAdmin = modal.querySelector('#wfs-radio-admin');
    const radioAoi = modal.querySelector('#wfs-radio-aoi');
    const adminPanel = modal.querySelector('#wfs-admin-panel');
    const aoiPanel = modal.querySelector('#wfs-aoi-panel');

    function updateActiveMode(mode) {
      cardAll.classList.toggle('active', mode === 'all');
      cardAdmin.classList.toggle('active', mode === 'admin');
      cardAoi.classList.toggle('active', mode === 'aoi');
      adminPanel.style.display = mode === 'admin' ? 'block' : 'none';
      aoiPanel.style.display = mode === 'aoi' ? 'block' : 'none';
    }

    radioAll.addEventListener('change', () => updateActiveMode('all'));
    radioAdmin.addEventListener('change', () => updateActiveMode('admin'));
    radioAoi.addEventListener('change', () => updateActiveMode('aoi'));

    cardAll.addEventListener('click', (e) => {
      radioAll.checked = true;
      updateActiveMode('all');
    });
    cardAdmin.addEventListener('click', (e) => {
      if (!e.target.closest('#wfs-admin-panel')) {
        radioAdmin.checked = true;
        updateActiveMode('admin');
      }
    });
    cardAoi.addEventListener('click', (e) => {
      if (!e.target.closest('#wfs-aoi-panel')) {
        radioAoi.checked = true;
        updateActiveMode('aoi');
      }
    });

    // Mencegah klik di dalam panel filter administratif dan AOI memicu event kartu
    adminPanel.addEventListener('click', (e) => e.stopPropagation());
    adminPanel.addEventListener('mousedown', (e) => e.stopPropagation());
    aoiPanel.addEventListener('click', (e) => e.stopPropagation());
    aoiPanel.addEventListener('mousedown', (e) => e.stopPropagation());

    // Populate Cascading Dropdowns
    const selProv = modal.querySelector('#wfs-sel-prov');
    const selKab = modal.querySelector('#wfs-sel-kab');
    const selKec = modal.querySelector('#wfs-sel-kec');
    const selDesa = modal.querySelector('#wfs-sel-desa');

    const provList = Object.keys(WFS_ADMIN_DATA);
    const provDatalist = modal.querySelector('#wfs-prov-datalist');
    if (provDatalist) {
      provDatalist.innerHTML = provList.map((p) => `<option value="${p}">${p}</option>`).join('');
    }

    function resolveProv(raw) {
      const q = (raw || '').trim().toLowerCase();
      if (!q) return null;
      for (const p of provList) {
        if (p.toLowerCase() === q) return p;
      }
      for (const p of provList) {
        if (p.toLowerCase().includes(q)) return p;
      }
      return null;
    }

    function syncKab() {
      const p = resolveProv(selProv.value);
      if (!p) {
        selKab.innerHTML = '<option value="">-- Pilih Provinsi Terlebih Dahulu --</option>';
        selKab.disabled = true;
        selKec.innerHTML = '<option value="">-- Pilih Provinsi Terlebih Dahulu --</option>';
        selKec.disabled = true;
        selDesa.innerHTML = '<option value="">-- Pilih Provinsi Terlebih Dahulu --</option>';
        selDesa.disabled = true;
        return;
      }
      selKab.disabled = false;
      const rawKabs = (WFS_ADMIN_DATA[p] && Object.keys(WFS_ADMIN_DATA[p])) || ['Kab. Sleman', 'Kota Yogyakarta'];
      const kabs = ['Semua Kabupaten / Kota', ...rawKabs.filter((x) => x !== 'Semua Kabupaten / Kota')];
      selKab.innerHTML = kabs.map((k) => `<option value="${k}">${k}</option>`).join('');
      selKab.value = 'Semua Kabupaten / Kota';
      syncKec();
    }

    function syncKec() {
      const p = resolveProv(selProv.value);
      if (!p) {
        selKec.innerHTML = '<option value="">-- Pilih Provinsi Terlebih Dahulu --</option>';
        selKec.disabled = true;
        syncDesa();
        return;
      }
      const k = selKab.value;
      const isAllKab = k === 'Semua Kabupaten / Kota' || k === 'Semua Kabupaten' || !k;
      if (isAllKab) {
        selKec.innerHTML = '<option value="Semua Kecamatan">Semua Kecamatan</option>';
        selKec.value = 'Semua Kecamatan';
        selKec.disabled = true;
      } else {
        selKec.disabled = false;
        const kecs = (WFS_ADMIN_DATA[p] && WFS_ADMIN_DATA[p][k] && Object.keys(WFS_ADMIN_DATA[p][k])) || ['Semua Kecamatan', 'Kec. Depok', 'Kec. Mlati', 'Kec. Gamping', 'Kec. Sentral'];
        selKec.innerHTML = ['Semua Kecamatan', ...kecs.filter((x) => x !== 'Semua Kecamatan')].map((kc) => `<option value="${kc}">${kc}</option>`).join('');
        selKec.value = 'Semua Kecamatan';
      }
      syncDesa();
    }

    function syncDesa() {
      const p = resolveProv(selProv.value);
      if (!p) {
        selDesa.innerHTML = '<option value="">-- Pilih Provinsi Terlebih Dahulu --</option>';
        selDesa.disabled = true;
        return;
      }
      const k = selKab.value;
      const kc = selKec.value;
      const isAllKab = k === 'Semua Kabupaten / Kota' || k === 'Semua Kabupaten' || !k;
      const isAllKec = kc === 'Semua Kecamatan' || !kc;
      if (isAllKab || isAllKec) {
        selDesa.innerHTML = '<option value="Semua Desa / Kelurahan">Semua Desa / Kelurahan</option>';
        selDesa.value = 'Semua Desa / Kelurahan';
        selDesa.disabled = true;
      } else {
        selDesa.disabled = false;
        let desas = ['Semua Desa / Kelurahan'];
        if (WFS_ADMIN_DATA[p] && WFS_ADMIN_DATA[p][k] && WFS_ADMIN_DATA[p][k][kc]) {
          desas = ['Semua Desa / Kelurahan', ...WFS_ADMIN_DATA[p][k][kc]];
        } else {
          desas = ['Semua Desa / Kelurahan', 'Kel. 01 Sentra', 'Kel. 02 Utama', 'Kel. 03 Terpadu'];
        }
        selDesa.innerHTML = desas.map((d) => `<option value="${d}">${d}</option>`).join('');
        selDesa.value = 'Semua Desa / Kelurahan';
      }
    }

    selProv.addEventListener('input', syncKab);
    selProv.addEventListener('change', syncKab);
    selKab.addEventListener('change', syncKec);
    selKec.addEventListener('change', syncDesa);

    // Cek apakah ada filter wilayah aktif dari Katalog IGT
    let activeProv = '';
    let activeKab = '';
    const dashProvEl = document.getElementById('dash-cat-prov-select');
    const dashKabEl = document.getElementById('dash-cat-kab-select');
    const catProvEl = document.getElementById('catalog-prov-filter');
    const catKabEl = document.getElementById('catalog-kab-filter');

    if (dashProvEl && dashProvEl.value && dashProvEl.value !== 'all') {
      activeProv = dashProvEl.value;
      if (dashKabEl && dashKabEl.value && dashKabEl.value !== 'all') {
        activeKab = dashKabEl.value;
      }
    } else if (catProvEl && catProvEl.value && catProvEl.value !== 'all') {
      activeProv = catProvEl.value;
      if (catKabEl && catKabEl.value && catKabEl.value !== 'all') {
        activeKab = catKabEl.value;
      }
    }

    if (activeProv) {
      const resolved = resolveProv(activeProv) || activeProv;
      selProv.value = resolved;
      syncKab();
      if (activeKab) {
        for (let i = 0; i < selKab.options.length; i++) {
          const optVal = selKab.options[i].value.toLowerCase();
          const target = activeKab.toLowerCase().replace('kabupaten', '').replace('kab. ', '').replace('kota ', '').trim();
          if (optVal.includes(target) || target.includes(optVal.replace('kabupaten', '').replace('kab. ', '').replace('kota ', '').trim())) {
            selKab.selectedIndex = i;
            break;
          }
        }
        syncKec();
      }
      radioAdmin.checked = true;
      updateActiveMode('admin');
    } else {
      radioAll.checked = true;
      updateActiveMode('all');
      syncKab();
    }

    // Submit handler
    const btnSubmit = modal.querySelector('#wfs-btn-submit');
    btnSubmit.addEventListener('click', () => {
      const mode = modal.querySelector('input[name="wfs-mode-radio"]:checked').value;
      if (mode === 'admin') {
        const p = resolveProv(selProv.value);
        if (!p) {
          alert('Silakan pilih atau ketik nama provinsi terlebih dahulu.');
          selProv.focus();
          return;
        }
      }

      modal.style.display = 'none';
      modal.hidden = true;

      if (mode === 'all') {
        const msg = `Simulasi QGIS: Memuat seluruh data fitur WFS '${dsName}' (cakupan Nasional / Seluruh Indonesia).`;
        if (typeof toast === 'function') toast(msg); else alert(msg);
      } else if (mode === 'admin') {
        const p = resolveProv(selProv.value);
        const k = selKab.value;
        const kc = selKec.value;
        const d = selDesa.value;

        // Sinkronisasi pilihan filter WFS kembali ke Katalog agar tersambung dua arah
        if (dashProvEl) {
          dashProvEl.value = p;
          dashProvEl.dispatchEvent(new Event('change'));
          if (dashKabEl && k && k !== 'Semua Kabupaten / Kota') {
            setTimeout(() => {
              dashKabEl.value = k;
              dashKabEl.dispatchEvent(new Event('change'));
            }, 60);
          }
        }
        if (catProvEl) {
          catProvEl.value = p;
          catProvEl.dispatchEvent(new Event('change'));
          if (catKabEl && k && k !== 'Semua Kabupaten / Kota') {
            setTimeout(() => {
              catKabEl.value = k;
              catKabEl.dispatchEvent(new Event('change'));
            }, 60);
          }
        }

        let adminLabel = p;
        if (k && k !== 'Semua Kabupaten / Kota' && k !== 'Semua Kabupaten') {
          adminLabel += ` > ${k}`;
          if (kc && kc !== 'Semua Kecamatan') adminLabel += ` > ${kc}`;
          if (d && d !== 'Semua Desa / Kelurahan') adminLabel += ` > ${d}`;
        } else {
          adminLabel += ' (Semua Kabupaten)';
        }
        const msg = `Simulasi QGIS: Memuat fitur WFS '${dsName}' terfilter Batas Admin [${adminLabel}].`;
        if (typeof toast === 'function') toast(msg); else alert(msg);
      } else if (mode === 'aoi') {
        const aoiSub = modal.querySelector('input[name="wfs-aoi-sub-radio"]:checked').value;
        if (aoiSub === 'draw') {
          const msg = `Simulasi QGIS: Mengaktifkan alat gambar AOI pada kanvas peta untuk memfilter fitur WFS '${dsName}'.`;
          if (typeof toast === 'function') toast(msg); else alert(msg);
        } else {
          const aoiLayer = modal.querySelector('#wfs-sel-aoi-layer').value;
          const msg = `Simulasi QGIS: Memuat fitur WFS '${dsName}' terfilter berdasarkan layer AOI: '${aoiLayer}'.`;
          if (typeof toast === 'function') toast(msg); else alert(msg);
        }
      }
    });

    const drawBtn = modal.querySelector('#wfs-btn-draw-action');
    if (drawBtn) {
      drawBtn.addEventListener('click', () => {
        modal.querySelector('#wfs-aoi-sub-draw').checked = true;
        btnSubmit.click();
      });
    }
  }

  function showIgtDetailModal(dataset, role) {
    if (!dataset) return;
    let modal = document.getElementById('igt-detail-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'igt-detail-modal';
      modal.className = 'modal-backdrop';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.style.cssText = 'position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto;';
      document.body.appendChild(modal);

      modal.addEventListener('click', (e) => {
        if (e.target === modal || e.target.closest('[data-close-detail-modal]')) {
          modal.style.display = 'none';
          modal.hidden = true;
        }
      });
    }

    const cat = dataset.category || 'pertanahan';
    let jenisIgt = 'IGT Pertanahan (Berbasis Bidang Tanah)';
    if (cat === 'tata-ruang') jenisIgt = 'IGT Tata Ruang (Berbasis Rencana & Pola Kawasan)';
    else if (cat === 'derivatif') jenisIgt = 'IGT Derivatif Multiguna (Analisis Tematik Lanjutan)';
    else if (cat === 'lainnya') jenisIgt = 'IGT K/L Lainnya (Data Tematik Eksternal)';

    const direktoratVal = dataset.direktorat || dataset.satker || dataset.instansi || 'Direktorat Pengukuran dan Pemetaan Kadastral';
    const satkerVal = dataset.satker || dataset.direktorat || dataset.instansi || 'Kantah Kab. Sleman';
    const tglVal = dataset.updated || dataset.date || '18 Okt 2026';
    const lingkupVal = dataset.scope || `${dataset.kab || 'Kab. Sleman'}, ${dataset.prov || 'D.I. Yogyakarta'}`;
    const metaUrl = `https://geoportal.atrbpn.go.id/metadata/${dataset.id.toLowerCase()}`;
    const hasSubs = Boolean(dataset.subLayers && dataset.subLayers.length > 0);
    const allowWfs = canAccessWfs(role, dataset);

    const keteranganVal = dataset.keterangan || dataset.description || dataset.desc || dataset.catatan || dataset.note || (
      hasSubs
        ? `Dataset terpadu multi-layer memuat ${dataset.subLayers.length} sub-layer tematik terintegrasi siap pakai.`
        : cat === 'pertanahan'
        ? 'Data geospasial tematik pertanahan terverifikasi berbasis bidang tanah (baseline kadastral).'
        : cat === 'tata-ruang'
        ? 'Data geospasial tematik tata ruang berstatus terintegrasi dan tervalidasi topologi.'
        : cat === 'derivatif'
        ? 'Layer tematik hasil analisis dan pemodelan spasial derivatif multiguna.'
        : 'Data geospasial tematik resmi terintegrasi pada Geoportal Kementerian ATR/BPN.'
    );

    const subLayersHtml = hasSubs ? `
      <div class="igt-detail-box" style="border-color:#bbf7d0;background:#f0fdf4;">
        <div class="igt-detail-box-title" style="color:#047857;">Daftar Sub-Layer (${dataset.subLayers.length} Sub-IGT Terintegrasi)</div>
        ${dataset.subLayers.map((s) => `
          <div class="igt-detail-sub-item">
            <div>
              <div class="igt-detail-sub-title">• ${s.name}</div>
              <div class="igt-detail-sub-meta">ID: ${s.id || '—'} · Update: ${s.updated || s.year || '—'} · Cakupan: ${s.scope || lingkupVal}</div>
            </div>
            <div style="display:flex;gap:6px;">
              <button type="button" class="btn btn-soft btn-sm" data-action="wms" data-name="${s.name.replace(/"/g, '&quot;')}">WMS</button>
              ${allowWfs ? `<button type="button" class="btn btn-soft btn-sm" data-action="wfs" data-name="${s.name.replace(/"/g, '&quot;')}">WFS</button>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    ` : '';

    const modalInner = `
      <section class="card" style="width:min(640px,100%);max-height:92vh;overflow:auto;margin:auto;box-shadow:0 20px 48px rgba(15,23,42,.25);border-radius:12px;">
        <div class="card-head" style="background:linear-gradient(135deg, #102b59 0%, #1858b8 100%);color:#fff;border-bottom:none;padding:16px 20px;border-radius:12px 12px 0 0;">
          <div>
            <div style="font-size:10px;font-weight:800;color:#bfdbfe;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:4px;">
              Sistem Informasi Geospasial ATR/BPN · Detail IGT
            </div>
            <h2 id="igt-detail-modal-title" style="font-size:16px;color:#fff;margin:0 0 4px 0;line-height:1.3;">${dataset.name}</h2>
            <div style="font-size:11.5px;color:#cbd5e1;">ID Dataset: <strong>${dataset.id}</strong> · Status: <span class="status integrated">${dataset.status || 'Terintegrasi'}</span></div>
          </div>
          <button type="button" class="btn btn-soft" data-close-detail-modal style="background:rgba(255,255,255,0.15);color:#fff;border:none;border-radius:8px;font-weight:700;">✕ Tutup</button>
        </div>

        <div style="padding:18px 20px;">
          <!-- Detail Grid -->
          <div class="igt-detail-box">
            <div class="igt-detail-box-title">Metadata Pokok Dataset</div>
            <div class="igt-detail-grid">
              <div class="igt-detail-item">
                <span class="igt-detail-label">Direktorat Pembina</span>
                <span class="igt-detail-val">${direktoratVal}</span>
              </div>
              <div class="igt-detail-item">
                <span class="igt-detail-label">Satuan Kerja (Satker)</span>
                <span class="igt-detail-val">${satkerVal}</span>
              </div>
              <div class="igt-detail-item">
                <span class="igt-detail-label">Tanggal Integrasi</span>
                <span class="igt-detail-val">${tglVal}</span>
              </div>
              <div class="igt-detail-item">
                <span class="igt-detail-label">Jenis IGT</span>
                <span class="igt-detail-val">${jenisIgt}</span>
              </div>
              <div class="igt-detail-item">
                <span class="igt-detail-label">Ruang Lingkup / Wilayah</span>
                <span class="igt-detail-val">${lingkupVal}</span>
              </div>
              <div class="igt-detail-item">
                <span class="igt-detail-label">Sistem Koordinat (CRS)</span>
                <span class="igt-detail-val">EPSG:4326 (WGS 84) / EPSG:3857 (Web Mercator)</span>
              </div>
              <div class="igt-detail-item" style="grid-column: 1 / -1;">
                <span class="igt-detail-label">Keterangan</span>
                <span class="igt-detail-val" style="line-height:1.5;">${keteranganVal}</span>
              </div>
            </div>
          </div>

          <!-- Link Dokumen Metadata Resmi -->
          <div class="igt-detail-box" style="border-color:#bfdbfe;background:#eff6ff;">
            <div class="igt-detail-box-title" style="color:#1d4ed8;">Dokumen & Spesifikasi Metadata (ISO 19115)</div>
            <p style="font-size:11.5px;color:#334155;margin:0 0 10px 0;line-height:1.4;">
              Metadata geospasial resmi berstandar ISO 19115 / SNI ISO 19115 lengkap dengan informasi riwayat pengolahan (lineage), batas spasial (bounding box), dan kamus data tersedia pada Geoportal ATR/BPN:
            </p>
            <a href="${metaUrl}" target="_blank" rel="noopener noreferrer" class="igt-metadata-link" onclick="event.preventDefault(); alert('Simulasi membuka dokumen metadata ISO 19115:\\n' + this.href);">
              ${ri('external-link-line')} <span>Lihat Metadata Geospasial (${metaUrl})</span>
            </a>
          </div>

          <!-- Sub-layer bila multi-layer -->
          ${subLayersHtml}

          <!-- Toolbar Muat Layer -->
          <div class="toolbar" style="margin-top:16px;justify-content:space-between;padding-top:12px;border-top:1px solid #e2e8f0;">
            <button type="button" class="btn btn-soft" data-close-detail-modal>Tutup</button>
            <div style="display:flex;gap:8px;">
              <button type="button" class="btn btn-primary" data-action="wms" data-name="${dataset.name.replace(/"/g, '&quot;')}" ${hasSubs ? 'data-is-parent-multi="true"' : ''}>
                ${ri('map-2-line')}<span>Muat WMS ke Kanvas</span>
              </button>
              ${allowWfs ? `
                <button type="button" class="btn btn-primary" style="background:#7c3aed;border-color:#7c3aed;" data-action="wfs" data-name="${dataset.name.replace(/"/g, '&quot;')}" ${hasSubs ? 'data-is-parent-multi="true"' : ''}>
                  ${ri('shape-line')}<span>Muat WFS ke Kanvas</span>
                </button>
              ` : ''}
            </div>
          </div>
        </div>
      </section>
    `;

    modal.innerHTML = modalInner;
    modal.hidden = false;
    modal.style.display = 'flex';

    // Hook load actions inside modal
    modal.querySelectorAll('[data-action]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const act = btn.dataset.action;
        const name = btn.dataset.name;
        if (act === 'wfs') {
          showWfsFilterModal(dataset || { name }, role);
          return;
        }
        if (btn.dataset.isParentMulti === 'true' && dataset && dataset.subLayers) {
          const count = dataset.subLayers.length;
          const subNames = dataset.subLayers.map((s) => s.name).join(', ');
          const typeLabel = 'layer citra WMS';
          const msg = "Simulasi QGIS: Memuat " + (count === 2 ? "kedua" : "seluruh " + count) + " sub-IGT untuk '" + dataset.name + "' (" + subNames + ") sebagai " + typeLabel + " ke dalam kanvas peta QGIS.";
          if (typeof toast === 'function') toast(msg);
          else alert(msg);
          return;
        }
        const msg = act === 'wms' ? WMS_MESSAGE(name) : WFS_MESSAGE(name);
        if (typeof toast === 'function') toast(msg);
        else alert(msg);
      });
    });
  }

  // Datasets of one category that are in its catalog (see CATEGORIES[...].catalogStatus); nothing can be edited here.
  function catalog(role, category) {
    // Karena Katalog IGT sudah ditampilkan di depan (dashboard), page khusus dialihkan ke dashboard utama
    if (typeof window !== 'undefined' && window.location) {
      window.location.replace('../beranda/index.html#dashboard-catalog-widget');
      return;
    }
    const view = $('#view');
    const isV2 = isV2Role(role);
    if (isV2) {
      document.body.classList.add('v2-page', 'v2-theme-catalog');
    }
    if (!IgtData.canView(role, category)) {
      view.innerHTML = '<div class="notice"><strong>Akses ditolak</strong>' + CATEGORIES[category].label + ' tidak tersedia untuk role ini.</div>';
      return;
    }
    const config = CATEGORIES[category];
    if (isV2) {
      const crumb = document.querySelector('.topbar .crumb');
      if (crumb) {
        crumb.innerHTML = 'Geoportal IGT-PR　/　<a href="../beranda/index.html">Dashboard</a>　/　<strong>' + config.label + '</strong>';
      }
      const eyebrow = document.querySelector('.page-head .eyebrow');
      if (eyebrow) eyebrow.textContent = 'Katalog IGT Geospasial';
      const headH1 = document.querySelector('.page-head h1');
      if (headH1) headH1.textContent = config.label;
      document.title = config.label + ' · IGT-PR';
    }
    const v2CatalogNav = isV2
      ? '<nav class="v2-subnav" aria-label="Kategori Katalog IGT">' +
        CATEGORY_ORDER.filter((key) => IgtData.canView(role, key))
          .map((key) =>
            '<a class="' + (key === category ? 'active' : '') + '" href="../beranda/index.html#dashboard-catalog-widget">' +
            (CATALOG_ICON[key] || categoryIcon(key)) + '<span>' + (CATEGORIES[key].shortLabel || CATEGORIES[key].label) + '</span></a>'
          ).join('') +
        '</nav>'
      : '';
    const datasets = IgtData.loadRecords().filter((r) =>
      (category === 'igt-pr' ? (r.category === 'pertanahan' || r.category === 'tata-ruang') : r.category === category) &&
      IgtData.inCatalog(r)
    );
    let query = '';
    let sortKey = '';
    let sortDirection = 1;
    const orgLabel = category === 'lainnya' ? 'Instansi' : 'Direktorat';
    view.innerHTML =
      v2CatalogNav +
      '<div class="notice"><strong>Isi katalog</strong>' + config.rule + ' Tombol WMS, WFS, dan Keduanya adalah simulasi integrasi QGIS.</div>' +
      '<div class="catalog-controls-v2">' +
      '<div class="catalog-search-row">' +
      '<div class="field catalog-search catalog-search-input-wrap"><input id="catalog-search" type="search" placeholder="Cari nama IGT, ID, atau kata kunci..."></div>' +
      '<button type="button" class="catalog-filter-toggle" id="catalog-filter-toggle" aria-expanded="false" title="Buka / tutup filter wilayah">' +
      ri('filter-3-line') + ' <span>Filter</span></button>' +
      '</div>' +
      '<div class="catalog-filter-drawer" id="catalog-filter-drawer" hidden>' +
      '<div class="field year-filter"><label for="catalog-year-filter">TAHUN</label><select id="catalog-year-filter">' + yearFilterOptions(datasets) + '</select></div>' +
      '<div class="field prov-filter"><label for="catalog-prov-filter">PROVINSI</label><select id="catalog-prov-filter">' + provFilterOptions(datasets) + '</select></div>' +
      '<div class="field kab-filter"><label for="catalog-kab-filter">KABUPATEN / KOTA</label><select id="catalog-kab-filter" disabled><option value="all">-- Pilih Provinsi Terlebih Dahulu --</option></select></div>' +
      '</div>' +
      '</div>' +
      '<section class="card"><div class="card-head"><div><h2>' + config.noun.charAt(0).toUpperCase() + config.noun.slice(1) + '</h2><p id="catalog-count"></p></div></div>' +
      '<div class="table-wrap"><table class="stack"><thead><tr>' +
      '<th class="igt-col-no">No.</th>' +
      '<th><button type="button" class="sort-header" data-sort="name">Nama IGT <span aria-hidden="true">↕</span></button></th>' +
      '<th><button type="button" class="sort-header" data-sort="direktorat">' + orgLabel + ' <span aria-hidden="true">↕</span></button></th>' +
      '<th><button type="button" class="sort-header" data-sort="updated">' +
      (config.integration ? 'Tanggal Pembaruan' : category === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Unggah') +
      ' <span aria-hidden="true">↕</span></button></th><th style="min-width:180px">Aksi Muat Layer</th></tr></thead><tbody id="catalog-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden></div></section>';
    function render() {
      const q = query.toLowerCase();
      const year = $('#catalog-year-filter').value;
      const prov = $('#catalog-prov-filter') ? $('#catalog-prov-filter').value : 'all';
      const kab = $('#catalog-kab-filter') ? $('#catalog-kab-filter').value : 'all';

      const filtered = datasets.filter((d) => {
        if (year !== 'all') {
          const matchParent = yearOf(d) === year;
          const matchSub = d.subLayers && d.subLayers.some((s) => (s.year || yearOf(s)) === year);
          if (!matchParent && !matchSub) return false;
        }
        if (prov !== 'all') {
          const provHaystack = ((d.prov || '') + ' ' + (d.scope || '')).toLowerCase();
          const pLower = prov.toLowerCase();
          const matchAlias = (pLower.includes('yogyakarta') && (provHaystack.includes('yogyakarta') || provHaystack.includes('d.i.'))) ||
                             (pLower.includes('jakarta') && (provHaystack.includes('jakarta') || provHaystack.includes('dki'))) ||
                             (pLower.includes('bangka belitung') && provHaystack.includes('bangka')) ||
                             provHaystack.includes(pLower);
          if (!matchAlias && !provHaystack.includes('nasional')) {
            return false;
          }
        }
        if (kab !== 'all') {
          const kabHaystack = ((d.kab || '') + ' ' + (d.scope || '')).toLowerCase();
          if (!kabHaystack.includes(kab.toLowerCase())) {
            return false;
          }
        }
        if (q) {
          const orgVal = d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '';
          const subText = d.subLayers ? d.subLayers.map((s) => s.name + ' ' + (s.label || '') + ' ' + (s.year || '') + ' ' + (s.skala || '')).join(' ') : '';
          const haystack = (d.name + ' ' + (d.scope || '') + ' ' + orgVal + ' ' + (d.prov || '') + ' ' + (d.kab || '') + ' ' + subText).toLowerCase();
          if (!haystack.includes(q)) return false;
        }
        return true;
      });
      const shown = [...filtered];
      if (sortKey) {
        const value = (d) =>
          sortKey === 'name' ? d.name :
          sortKey === 'direktorat' || sortKey === 'satker' || sortKey === 'ditjen' ? (d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '') :
          sortKey === 'updated' ? (d.updated || d.date || '') : d.name;
        shown.sort((a, b) => String(value(a)).localeCompare(String(value(b)), 'id', { numeric: true }) * sortDirection);
      }
      document.querySelectorAll('.sort-header').forEach((btn) => {
        const active = btn.dataset.sort === sortKey;
        btn.setAttribute('aria-sort', active ? (sortDirection === 1 ? 'ascending' : 'descending') : 'none');
        btn.querySelector('span').textContent = active ? (sortDirection === 1 ? '↑' : '↓') : '↕';
      });
      $('#catalog-rows').innerHTML = shown.map((d, idx) => {
        const hasSubs = Boolean(d.subLayers && d.subLayers.length > 0);
        const autoExpand = Boolean(q && d.subLayers && d.subLayers.some((s) => (s.name + ' ' + (s.label || '') + ' ' + (s.year || '') + ' ' + (s.skala || '')).toLowerCase().includes(q)));
        const isExp = autoExpand;
        const catIcon = categoryIcon(d.category);
        const parentRow = (
          '<tr class="' + (hasSubs ? 'has-sublayers' : '') + (isExp ? ' is-expanded' : '') + '" data-record-id="' + d.id + '">' +
          '<td class="igt-col-no" data-label="No."><span class="igt-catalog-num">' + (idx + 1) + '</span></td>' +
          '<td data-label="Nama IGT">' +
          '<div class="igt-catalog-item">' +
          '<div class="igt-catalog-header">' +
          (hasSubs
            ? '<button type="button" class="igt-tree-toggle" data-toggle-sub="' + d.id + '" aria-expanded="' + (isExp ? 'true' : 'false') + '" title="Buka/tutup sub-layer">' +
              '<span class="igt-tree-icon" aria-hidden="true">' + (isExp ? '▼' : '▶') + '</span>' +
              '</button>'
            : '') +
          '<span class="igt-cat-inline-icon is-' + d.category + '" title="' + d.category + '">' + catIcon + '</span>' +
          '<button type="button" class="igt-catalog-name igt-card-link-title" data-open-detail="' + d.id + '" title="Klik untuk melihat detail lengkap dataset IGT">' + d.name + '</button>' +
          '<button type="button" class="igt-info-btn" data-open-detail="' + d.id + '" title="Detail Informasi & Metadata IGT" aria-label="Detail Informasi IGT">' + ri('information-line') + '</button>' +
          (hasSubs
            ? '<button type="button" class="igt-chip igt-chip--multi-layer igt-chip--compact" data-toggle-sub="' + d.id + '" aria-expanded="' + (isExp ? 'true' : 'false') + '" title="Klik untuk membuka/menutup sub-layer">' +
              '<span class="igt-chip__text">Multi-layer (' + d.subLayers.length + ')</span>' +
              '<span class="igt-chip__caret" aria-hidden="true">' + (isExp ? '▴' : '▾') + '</span>' +
              '</button>'
            : '') +
          '</div></div></td>' +
          '<td data-label="' + orgLabel + '">' + (d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '—') + '</td>' +
          '<td data-label="Tanggal">' + (d.updated || d.date || '—') + '</td>' +
          '<td data-label="Aksi Muat Layer"><div class="toolbar-inline">' +
          button('btn-soft btn-sm', hasSubs ? 'wms-all' : 'wms', d.id, ri('map-2-line') + '<span>WMS</span>') +
          (canAccessWfs(role, d) ? button('btn-soft btn-sm', hasSubs ? 'wfs-all' : 'wfs', d.id, ri('stack-line') + '<span>WFS</span>') : '') +
          '</div></td>' +
          '</tr>'
        );

        if (!hasSubs) return parentRow;

        const subRows = d.subLayers.map((sub) => {
          return (
            '<tr class="igt-sublayer-row igt-sublayer-for-' + d.id + '" data-parent-id="' + d.id + '" style="' + (isExp ? '' : 'display:none;') + '"' + (isExp ? '' : ' hidden') + '>' +
            '<td class="igt-col-no" data-label="No."></td>' +
            '<td class="igt-sublayer-cell" data-label="Nama Sub-layer">' +
            '<div class="igt-sublayer-branch">' +
            '<span class="igt-tree-branch-line" aria-hidden="true">└─</span>' +
            '<div class="igt-sublayer-content">' +
            '<span class="igt-sublayer-title">' + sub.name + '</span>' +
            '</div></div></td>' +
            '<td data-label="' + orgLabel + '"><span class="igt-sublayer-meta">' + (sub.scope || d.direktorat || '—') + '</span></td>' +
            '<td data-label="Tanggal"><span class="igt-sublayer-date">' + (sub.updated || sub.date || d.updated || '—') + '</span></td>' +
            '<td data-label="Aksi Muat Layer"><div class="toolbar-inline">' +
            '<button type="button" class="btn btn-soft btn-sm igt-sub-btn" data-action="wms-sub" data-sub-id="' + sub.id + '" data-sub-name="' + sub.name + '" data-parent-name="' + d.name + '">' + ri('map-2-line') + '<span>WMS</span></button>' +
            (canAccessWfs(role, d) ? '<button type="button" class="btn btn-soft btn-sm igt-sub-btn" data-action="wfs-sub" data-sub-id="' + sub.id + '" data-sub-name="' + sub.name + '" data-parent-name="' + d.name + '">' + ri('stack-line') + '<span>WFS</span></button>' : '') +
            '</div></td>' +
            '</tr>'
          );
        }).join('');

        return parentRow + subRows;
      }).join('');
      const yearText = year === 'all' ? 'semua tahun' : 'tahun ' + year;
      setText('catalog-count', shown.length + ' dari ' + datasets.length + ' dataset · ' + yearText);
      const empty = $('#empty-state');
      empty.hidden = shown.length > 0;
      empty.textContent = datasets.length === 0 ? 'Belum ada ' + config.noun + ' pada ' + config.label + '.' : 'Tidak ada dataset yang cocok dengan kriteria filter atau pencarian.';
    }
    $('#catalog-search').addEventListener('input', (event) => { query = event.target.value; render(); });
    const catFilterToggle = $('#catalog-filter-toggle');
    const catFilterDrawer = $('#catalog-filter-drawer');
    if (catFilterToggle && catFilterDrawer) {
      catFilterToggle.addEventListener('click', () => {
        const isHidden = catFilterDrawer.hidden;
        catFilterDrawer.hidden = !isHidden;
        catFilterToggle.classList.toggle('active', isHidden);
        catFilterToggle.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
      });
    }
    $('#catalog-year-filter').addEventListener('change', render);
    if ($('#catalog-prov-filter')) {
      $('#catalog-prov-filter').addEventListener('change', (e) => {
        const selP = e.target.value;
        const kabEl = $('#catalog-kab-filter');
        if (kabEl) {
          if (!selP || selP === 'all') {
            kabEl.disabled = true;
            kabEl.innerHTML = '<option value="all">-- Pilih Provinsi Terlebih Dahulu --</option>';
            kabEl.value = 'all';
          } else {
            kabEl.disabled = false;
            kabEl.innerHTML = kabFilterOptions(datasets, selP);
            kabEl.value = 'all';
          }
        }
        render();
      });
    }
    if ($('#catalog-kab-filter')) $('#catalog-kab-filter').addEventListener('change', render);
    document.querySelectorAll('.sort-header').forEach((btn) => btn.addEventListener('click', () => {
      if (sortKey === btn.dataset.sort) sortDirection *= -1;
      else { sortKey = btn.dataset.sort; sortDirection = 1; }
      render();
    }));
    document.addEventListener('click', (event) => {
      const openDetailBtn = event.target.closest('[data-open-detail]');
      if (openDetailBtn) {
        event.stopPropagation();
        const dsId = openDetailBtn.dataset.openDetail;
        const ds = datasets.find((x) => x.id === dsId);
        if (ds) {
          showIgtDetailModal(ds, role);
        }
        return;
      }

      const toggleSub = event.target.closest('[data-toggle-sub]');
      if (toggleSub) {
        const parentId = toggleSub.dataset.toggleSub;
        const subRows = document.querySelectorAll('.igt-sublayer-for-' + parentId);
        const toggles = document.querySelectorAll('[data-toggle-sub="' + parentId + '"]');
        const parentTr = document.querySelector('tr[data-record-id="' + parentId + '"]');
        if (subRows.length > 0) {
          const isCurrentlyHidden = subRows[0].style.display === 'none' || subRows[0].hidden;
          subRows.forEach((r) => {
            r.style.display = isCurrentlyHidden ? 'table-row' : 'none';
            r.hidden = !isCurrentlyHidden;
          });
          toggles.forEach((t) => {
            t.setAttribute('aria-expanded', isCurrentlyHidden ? 'true' : 'false');
            const caret = t.querySelector('.igt-chip__caret');
            if (caret) caret.textContent = isCurrentlyHidden ? '▴' : '▾';
            const icon = t.querySelector('.igt-tree-icon');
            if (icon) icon.textContent = isCurrentlyHidden ? '▼' : '▶';
          });
          if (parentTr) {
            parentTr.classList.toggle('is-expanded', isCurrentlyHidden);
          }
        }
        return;
      }

      const target = event.target.closest('[data-action]');
      if (!target) return;
      const { action, id, subId, subName, parentName } = target.dataset;

      if (action === 'wms-sub') {
        alert("Simulasi QGIS: Memuat layer WMS untuk '" + subName + "' (sub-layer dari " + parentName + ") ke dalam kanvas peta.");
        return;
      }
      if (action === 'wfs-sub') {
        const parentRecord = datasets.find((d) => d.name === parentName || (d.subLayers && d.subLayers.some((s) => s.id === subId)));
        if (parentRecord && !canAccessWfs(role, parentRecord)) {
          alert("Akses WFS dibatasi: Akun Anda tidak memiliki izin untuk mengakses layanan fitur WFS dataset ini.");
          return;
        }
        showWfsFilterModal({ name: subName, parent: parentName }, role);
        return;
      }
      if (action === 'wms-all') {
        const d = datasets.find((x) => x.id === id);
        if (d && d.subLayers) {
          const count = d.subLayers.length;
          const subNames = d.subLayers.map((s) => s.name).join(', ');
          alert("Simulasi QGIS: Memuat " + (count === 2 ? "kedua" : "seluruh " + count) + " sub-IGT untuk '" + d.name + "' (" + subNames + ") sebagai layer citra WMS sekaligus ke dalam kanvas peta QGIS.");
        }
        return;
      }
      if (action === 'wfs-all') {
        const d = datasets.find((x) => x.id === id);
        if (d && d.subLayers) {
          if (!canAccessWfs(role, d)) {
            alert("Akses WFS dibatasi: Akun Anda tidak memiliki izin untuk mengakses layanan fitur WFS dataset ini.");
            return;
          }
          showWfsFilterModal(d, role);
        }
        return;
      }

      const dataset = datasets.find((d) => d.id === id);
      if (!dataset) return;
      if (action === 'wms') {
        if (dataset.subLayers && dataset.subLayers.length > 0) {
          alert("Simulasi QGIS: Memuat seluruh sub-layer tematik untuk '" + dataset.name + "' (" + dataset.subLayers.length + " layer) ke dalam kanvas peta.");
        } else {
          alert(WMS_MESSAGE(dataset.name));
        }
      } else if (action === 'wfs') {
        if (!canAccessWfs(role, dataset)) {
          alert("Akses WFS dibatasi: Akun Anda tidak memiliki izin untuk mengakses layanan fitur WFS dataset ini.");
          return;
        }
        showWfsFilterModal(dataset, role);
        return;
      } else if (action === 'both') {
        if (dataset.subLayers && dataset.subLayers.length > 0) {
          alert("Simulasi QGIS: Memuat sekaligus layer WMS dan WFS untuk seluruh sub-layer '" + dataset.name + "' (" + dataset.subLayers.length + " layer) ke dalam kanvas peta QGIS.");
        } else {
          alert("Simulasi QGIS: Memuat sekaligus layer WMS dan WFS untuk '" + dataset.name + "' ke dalam kanvas peta QGIS.");
        }
      }
    });
    render();
  }

  // --------------------------------------------------------------- upload data

  const UPLOAD_TEXT = {
    pertanahan: 'Unggah atribut bidang baru, lalu pantau status pengajuan.',
    'tata-ruang': 'Unggah geometri dan atribut kawasan, lalu pantau status verifikasinya.',
    derivatif: 'Ajukan layer derivatif dan pantau keputusan persetujuannya.',
    lainnya: 'Kelola layer IGT dari sumber eksternal. Data yang diunggah Superadmin langsung tersedia tanpa proses persetujuan.',
  };

  const LEGACY = '../../../legacy/';

  function uploadIgtUtamaPanel(role, category, recordToRevise = null) {
    const isRev = Boolean(recordToRevise);
    const catLabel = category === 'tata-ruang' ? 'IGT Tata Ruang' : 'IGT Pertanahan';
    const initName = isRev ? recordToRevise.name : (category === 'tata-ruang' ? 'Kawasan RTRW Sleman 2026' : 'Bidang Tanah Sleman 2026');
    const initSatker = isRev ? (recordToRevise.satker || recordToRevise.direktorat || 'Kantah Kab. Sleman') : 'Kantah Kab. Sleman';

    return (
      `<div class="upload-modal-v2">` +
      (isRev ? `<div class="notice" style="background:#fff7ed;border-color:#fdba74;color:#9a3412;margin-bottom:12px"><strong>Mode Perbaikan Revisi</strong>Silakan perbarui berkas spasial dan catatan tindak lanjut untuk pengajuan <strong>${recordToRevise.id}</strong>.</div>` : '') +
      `<div class="form-section">` +
      `<h3>1. Informasi Dasar Layer</h3>` +
      `<div class="form-grid">` +
      `<div class="field"><label for="u-nama">NAMA LAYER IGT</label><input id="u-nama" type="text" value="${initName}" placeholder="Masukkan nama layer IGT"></div>` +
      `<div class="field"><label for="u-kategori">KATEGORI / SUB-ELEMEN</label><select id="u-kategori">` +
      (category === 'tata-ruang'
        ? `<option selected>Rencana Pola Ruang (RTRW/RDTR)</option><option>Rencana Struktur Ruang</option><option>Kesesuaian Kegiatan Pemanfaatan Ruang (KKPR)</option><option>Lahan Pertanian Pangan Berkelanjutan (LP2B)</option>`
        : `<option selected>Bidang Tanah (Baseline Hak Atas Tanah)</option><option>Penguasaan Tanah</option><option>Pemanfaatan Tanah</option><option>Zona Nilai Tanah</option>`) +
      `</select></div>` +
      `<div class="field"><label for="u-satker">SATKER / INSTANSI PENGUNGGAH</label><select id="u-satker">` +
      `<option ${initSatker.includes('Sleman') ? 'selected' : ''}>Kantah Kab. Sleman</option><option>Kantah Kab. Bantul</option><option>Ditjen Survei dan Pemetaan Pertanahan dan Ruang</option><option>Ditjen Tata Ruang</option>` +
      `</select></div>` +
      `<div class="field"><label for="u-tahun">TAHUN PEMBUATAN</label><select id="u-tahun"><option selected>2026</option><option>2025</option><option>2024</option></select></div>` +
      `</div></div>` +
      `<div class="form-section">` +
      `<h3>2. Pilih Berkas Geospasial</h3>` +
      `<div class="dropzone" style="padding:16px 12px;margin:0">` +
      `<div class="big" style="font-size:24px;margin-bottom:4px">📁</div>` +
      `<strong>${isRev ? 'Unggah Berkas Geospasial Hasil Revisi' : 'Tarik & Letakkan Berkas di Sini'}</strong>` +
      `<p style="margin:2px 0 8px 0;font-size:12px">Mendukung GeoPackage (.gpkg), Shapefile (.zip), atau GeoJSON (.geojson)</p>` +
      `<input type="file" id="u-file-input" style="display:none" accept=".gpkg,.zip,.shp,.geojson">` +
      `<button type="button" class="btn btn-soft btn-sm" id="u-file-browse-btn" onclick="document.getElementById('u-file-input').click()">Pilih Berkas Komputer</button>` +
      `<div id="u-file-name" style="font-size:12px;color:#047857;margin-top:6px;font-weight:600">${isRev ? 'berkas_revisi_' + recordToRevise.id.toLowerCase() + '.gpkg' : 'peta_geospasial_sleman_2026.gpkg (14.2 MB)'}</div>` +
      `</div></div>` +
      `<div class="form-section">` +
      `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px"><h3 style="margin:0">3. Pengecekan Atribut Standar</h3><span class="badge-valid">✓ 5 Kolom Sesuai Standar</span></div>` +
      `<p style="font-size:11.5px;color:#64748b;margin:0 0 8px 0">Struktur skema atribut telah divalidasi terhadap standar data geospasial ATR/BPN.</p>` +
      `<div style="max-height:110px;overflow:auto;border:1px solid #e2e8f0;border-radius:6px"><table class="stack" style="font-size:11px;margin:0;width:100%">` +
      `<thead><tr style="background:#f8fafc"><th style="padding:4px 8px">Kolom</th><th style="padding:4px 8px">Tipe Data</th><th style="padding:4px 8px">Keterangan</th><th style="padding:4px 8px">Status</th></tr></thead>` +
      `<tbody>` +
      `<tr><td style="padding:4px 8px"><code>KODE_UNIK</code></td><td style="padding:4px 8px">String (32)</td><td style="padding:4px 8px">NIB / ID Objek</td><td style="padding:4px 8px;color:#047857;font-weight:700">Valid</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>NAMA_OBJEK</code></td><td style="padding:4px 8px">String (100)</td><td style="padding:4px 8px">Penggunaan / Zonasi</td><td style="padding:4px 8px;color:#047857;font-weight:700">Valid</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>LUAS_HA</code></td><td style="padding:4px 8px">Float (10,2)</td><td style="padding:4px 8px">Luas Hektar</td><td style="padding:4px 8px;color:#047857;font-weight:700">Valid</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>TAHUN</code></td><td style="padding:4px 8px">Integer (4)</td><td style="padding:4px 8px">Tahun Penetapan</td><td style="padding:4px 8px;color:#047857;font-weight:700">Valid</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>TEMA</code></td><td style="padding:4px 8px">String (50)</td><td style="padding:4px 8px">Tema IGT</td><td style="padding:4px 8px;color:#047857;font-weight:700">Valid</td></tr>` +
      `</tbody></table></div></div>` +
      `<div class="form-section">` +
      `<h3>4. Simbologi &amp; Visualisasi (SLD / QML)</h3>` +
      `<div style="display:flex;align-items:center;gap:12px"><span style="display:inline-block;width:24px;height:24px;border-radius:4px;background:#3b82f6;border:2px solid #1d4ed8" title="Warna Standar ATR/BPN"></span><div style="flex:1;font-size:12px;color:#475569">Gaya visual bawaan: <strong>ATR/BPN Standard Thematic Style (.sld)</strong></div><button type="button" class="btn btn-soft btn-sm" onclick="alert('Simulasi: Berkas SLD khusus berhasil dipilih.')">Ganti SLD</button></div>` +
      `</div>` +
      `<div class="form-section">` +
      `<h3>5. Metadata Standar (ISO 19115)</h3>` +
      `<div style="font-size:11.5px;color:#475569;background:#f8fafc;padding:8px;border-radius:6px;border:1px solid #e2e8f0;line-height:1.5"><div><strong>Sistem Proyeksi (CRS):</strong> EPSG:3857 (WGS 84 / Pseudo-Mercator)</div><div><strong>Cakupan Spasial:</strong> Kab. Sleman, D.I. Yogyakarta</div><div><strong>Status Metadata:</strong> Lengkap (Pratinjau XML Valid)</div></div>` +
      `</div>` +
      `<div class="toolbar" style="margin-top:16px;justify-content:flex-end;gap:8px">` +
      `<button type="button" class="btn btn-soft" data-close-upload-modal>Batal</button>` +
      `<button type="button" class="btn btn-soft" onclick="alert('Draf pengajuan disimpan.'); document.getElementById('igt-upload-modal').hidden = true; document.getElementById('igt-upload-modal').style.display = 'none';">Simpan Draf</button>` +
      `<button type="button" class="btn btn-primary" id="u-submit-btn" data-modal-submit="${isRev ? 'revision' : 'new'}" data-record-id="${isRev ? recordToRevise.id : ''}">${ri('upload-cloud-2-line')}<span>${isRev ? 'Kirim Ulang Pengajuan Revisi' : 'Kirim Pengajuan'}</span></button>` +
      `</div></div>`
    );
  }

  // Upload controls differ per category and role. Baseline exists only for IGT Pertanahan.
  function uploadPanel(role, category) {
    if (category === 'pertanahan' || category === 'tata-ruang') {
      return uploadIgtUtamaPanel(role, category);
    }
    if (category === 'derivatif') {
      if (role === 'admin') {
        return (
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">${ri('upload-cloud-2-line')}<span>Unggah Derivatif</span></button></div>` +
          `<div class="notice"><strong>Catatan</strong>Unggahan Admin langsung berstatus Disetujui. Pengajuan Operator dan Umum berstatus Diajukan sampai diputuskan.</div>`
        );
      }
      if (role === 'umum') {
        return (
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">${ri('upload-cloud-2-line')}<span>Unggah Derivatif</span></button></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan Umum berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin. Anda hanya melihat pengajuan Anda sendiri.</div>`
        );
      }
      if (role === 'operator') {
        return (
          `<div class="toolbar"><a class="btn btn-primary" href="${LEGACY}06-derivative-kawasan.html">${ri('upload-cloud-2-line')}<span>Unggah Derivatif Kawasan</span></a>` +
          `<a class="btn btn-primary" href="${BIDANG_WORKFLOW_URL}">${ri('upload-cloud-2-line')}<span>Unggah Derivatif Bidang</span></a></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin.</div>`
        );
      }
      return (
        `<div class="notice"><strong>Catatan</strong>Superadmin tidak mengunggah derivatif. Gunakan panel ini untuk menyetujui atau menolak pengajuan.</div>`
      );
    }
    return (
      `<div class="toolbar"><button class="btn btn-primary" data-action="upload-lainnya">${ri('upload-cloud-2-line')}<span>Unggah layer</span></button></div>` +
      `<div class="notice"><strong>Catatan</strong>Penambahan dan pengaturan layer dilakukan langsung melalui QGIS. Layer eksternal tidak memakai status persetujuan.</div>`
    );
  }

  // Row actions depend on category, status and role. Catalog actions (WMS/WFS) never appear here.
  function rowActions(role, r) {
    const base = baseRoleOf(role);
    const isSuper = base === 'superadmin';
    const reviewer = base === 'admin' || isSuper;
    const kind = CATEGORIES[r.category].detail;
    const extras = [button('btn-soft', 'show-qgis', r.id, ri('eye-line') + '<span>Tampilkan</span>')];
    if (r.category === 'lainnya') {
      if (isSuper) extras.push(button('btn-danger', 'delete', r.id, ri('delete-bin-line') + '<span>Hapus</span>'));
      return toolbar(...extras);
    }
    if (kind === 'utama') {
      if (reviewer && r.status === 'Terkompilasi') {
        extras.push(button('btn-primary', 'topology', r.id, ri('focus-3-line') + '<span>Cek Topologi</span>'));
      }
      if (base === 'operator' && r.status === 'Revisi') {
        extras.push(button('btn-soft', 'revision', r.id, ri('edit-line') + '<span>Revisi</span>'));
      }
    }
    return toolbar(...extras);
  }

  // Submission management: summary, upload controls and submission table for the selected category.
  function upload(role) {
    const noUploadMenu = isV2Role(role);
    const base = baseRoleOf(role);
    const categories = managementCategories(role);
    const allRecords = IgtData.loadRecords();
    const records = (base === 'superadmin')
      ? allRecords.filter((r) => ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'].includes(r.category))
      : role === 'umum2'
        ? allRecords.filter((r) => r.category === 'derivatif')
        : IgtData.submissionsFor(role, allRecords);
    const params = new URLSearchParams(location.search);
    const requested = params.get('tab');
    const normalizedRequested = (requested === 'pertanahan' || requested === 'tata-ruang') ? 'igt-utama' : requested;
    if (normalizedRequested && !categories.includes(normalizedRequested)) {
      const deniedLabel = normalizedRequested === 'igt-utama' ? 'IGT Utama' : (CATEGORIES[normalizedRequested] ? CATEGORIES[normalizedRequested].label : normalizedRequested);
      $('#view').innerHTML = '<div class="notice"><strong>Akses ditolak</strong>' + deniedLabel + ' tidak tersedia untuk role ini.</div>';
      return;
    }
    let tab = normalizedRequested && categories.includes(normalizedRequested) ? normalizedRequested : categories[0];
    // Default to the leftmost status tab for the initially selected category.
    let statusTab = params.get('status') || (tab === 'igt-utama' ? (base === 'operator' ? 'Revisi' : 'Cek Topologi') : tab === 'derivatif' && (base === 'operator' || base === 'umum') ? 'Semua' : tab === 'derivatif' ? 'Diproses' : 'Semua');
    let nextDerivative = 9;

    const isMainInit = tab === 'igt-utama';
    const pageTitle = managementLabel(tab);
    const v2DescFor = (cat) =>
      cat === 'igt-utama'
        ? 'Pantau status kompilasi, revisi, dan persetujuan integrasi IGT Pertanahan & IGT Tata Ruang.'
        : cat === 'derivatif'
          ? 'Pantau pengajuan dan persetujuan layer IGT Derivatif Multiguna.'
          : 'Kelola layer IGT Lainnya dari sumber eksternal yang tersedia di katalog.';
    const pageDesc = noUploadMenu
      ? v2DescFor(tab)
      : (isMainInit ? 'Kelola pengajuan IGT Pertanahan dan IGT Tata Ruang dari satu halaman.' : UPLOAD_TEXT[tab]);
    document.title = pageTitle + ' · IGT-PR';
    if (noUploadMenu) {
      document.body.classList.add('v2-page', 'v2-theme-manage');
      const crumb = document.querySelector('.topbar .crumb');
      if (crumb) {
        crumb.innerHTML = 'Geoportal IGT-PR　/　<a href="../beranda/index.html">Dashboard</a>　/　<strong>' + pageTitle + '</strong>';
      }
      const eyebrow = document.querySelector('.page-head .eyebrow');
      if (eyebrow) eyebrow.textContent = 'Manajemen Data Geospasial';
    }
    const crumbStrong = document.querySelector('.crumb strong');
    if (crumbStrong) crumbStrong.textContent = pageTitle;
    const headH1 = document.querySelector('.page-head h1');
    if (headH1) headH1.textContent = pageTitle;
    const headP = document.querySelector('.page-head p');
    if (headP) headP.textContent = pageDesc;

    $('#view').innerHTML =
      `<div class="grid stats">` +
      statCard('Total pengajuan', '', pageTitle, MANAGEMENT_ICON[tab] || ri('database-2-line'), '', 'count-total') +
      statCard('Dalam proses', '', 'Proses atau Diajukan', ri('time-line'), 'amber', 'count-process') +
      statCard('Menunggu integrasi', '', 'Terkompilasi', ri('folder-line'), '', 'count-waiting') +
      `</div><section class="card">` +
      `<div class="card-head"><div><h2 id="tab-heading"></h2><p id="tab-description"></p></div></div>` +
      `<div id="upload-panel"></div>` +
      `<div id="igt-upload-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="igt-upload-modal-title" style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto">` +
      `<section class="card" style="width:min(760px,100%);max-height:90vh;overflow:auto;margin:auto"><div class="card-head"><div><h2 id="igt-upload-modal-title">Unggah IGT</h2><p id="igt-upload-modal-description"></p></div><button type="button" class="btn btn-soft" data-close-upload-modal>✕ Tutup</button></div><div id="igt-upload-modal-content" style="padding:16px 20px"></div></section></div>` +
      `<div id="topology-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="topol-modal-title" style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto">` +
      `<section class="card" style="width:min(640px,100%);max-height:90vh;overflow:auto;margin:auto"><div class="card-head"><div><h2 id="topol-modal-title">Cek Topologi Geospasial</h2><p id="topol-modal-subtitle">Hasil verifikasi aturan topologi dataset IGT Utama</p></div><button type="button" class="btn btn-soft" data-close-topol-modal>✕ Tutup</button></div>` +
      `<div style="padding:16px 20px"><div id="topol-dataset-info" style="margin-bottom:14px;padding:10px 14px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;font-size:12.5px;color:#334155"></div>` +
      `<div class="topol-rules-container">` +
      `<div class="rule-card-web"><strong>1. Must Not Have Gaps (Tidak Ada Celah Antar Poligon)</strong><p>Memastikan seluruh bidang poligon berhimpit rapi tanpa celah tak beraturan.</p><span class="badge-valid">✓ Valid · 0 Celah</span></div>` +
      `<div class="rule-card-web"><strong>2. Must Not Overlap (Tidak Ada Tumpang Tindih Poligon)</strong><p>Mencegah poligon ganda atau tumpang tindih kepemilikan spasial.</p><span class="badge-valid">✓ Valid · 0 Tumpang Tindih</span></div>` +
      `<div class="rule-card-web"><strong>3. Must Not Have Dangles (Tidak Ada Garis Menggantung)</strong><p>Memastikan seluruh segmen batas tertutup dan membentuk poligon utuh.</p><span class="badge-valid">✓ Valid · 0 Dangle</span></div>` +
      `<div class="rule-card-web"><strong>4. Must Be Inside Administrative Boundary (Batas Administrasi)</strong><p>Memastikan seluruh objek spasial berada di dalam yurisdiksi Satker.</p><span class="badge-valid">✓ Valid · 100% Di Dalam Batas</span></div>` +
      `<div class="rule-card-web"><strong>5. No Duplicate Geometries (Tidak Ada Geometri Duplikat)</strong><p>Memeriksa ketiadaan data redundant pada tingkat geometri.</p><span class="badge-valid">✓ Valid · 0 Duplikasi</span></div>` +
      `</div><div class="notice" style="margin-top:14px"><strong>Pemeriksaan Topologi Selesai</strong>Semua aturan topologi memenuhi standar ketetapan ATR/BPN. Data siap untuk proses integrasi data geospasial.</div>` +
      `<div class="toolbar" style="margin-top:16px;justify-content:flex-end;gap:8px"><button type="button" class="btn btn-soft" data-close-topol-modal>Tutup</button>` +
      `<button type="button" class="btn btn-primary" id="btn-confirm-topol">${ri('checkbox-circle-line')}<span>Konfirmasi Hasil Topologi</span></button></div></div></section></div>` +
      `<div id="submission-status-tabs" class="tabs" data-status-tabs></div>` +
      `<div class="card-head submissions-head"><div><h2>Daftar Pengajuan</h2><p id="submission-count"></p></div></div>` +
      `<div class="table-wrap"><table class="stack"><thead id="submission-thead"><tr><th>ID Pengajuan</th><th>Layer Target</th><th id="submission-org-heading">Satker</th><th id="submission-date-heading">Tanggal Unggah</th><th>Status</th><th>Aksi</th></tr></thead>` +
      `<tbody id="submission-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden>Belum ada pengajuan pada kategori ini.</div></section>`;

    function renderCounts(ownRecords) {
      const count = (...statuses) => ownRecords.filter((r) => statuses.includes(r.status)).length;
      setText('count-total', ownRecords.length);
      setText('count-process', count('Proses', 'Diajukan'));
      setText('count-waiting', count('Terkompilasi'));
    }

    function render() {
      const isMain = tab === 'igt-utama';
      const label = managementLabel(tab);
      const isIntegratedTab = statusTab === 'Terintegrasi';
      const orgLabel = tab === 'lainnya'
        ? 'Instansi'
        : isIntegratedTab
          ? 'Direktorat'
          : tab === 'semua'
            ? 'Satker / Direktorat / Instansi'
            : 'Satker';
      const isReviewerMain = isMain && (base === 'admin' || base === 'superadmin');
      const dateLabel = (isMain && isIntegratedTab)
        ? 'Tanggal Terintegrasi'
        : tab === 'derivatif'
          ? 'Tanggal Disetujui'
          : 'Tanggal Unggah';

      const theadEl = $('#submission-thead');
      if (theadEl) {
        theadEl.innerHTML = `<tr>` +
          `<th>ID Pengajuan</th>` +
          `<th>Layer Target</th>` +
          `<th id="submission-org-heading">${orgLabel}</th>` +
          (isReviewerMain ? '' : `<th id="submission-date-heading">${dateLabel}</th>`) +
          `<th>Status</th>` +
          `<th>Aksi</th>` +
          `</tr>`;
      } else {
        setText('submission-org-heading', orgLabel);
        if (!isReviewerMain) {
          setText('submission-date-heading', dateLabel);
        }
      }
      if (noUploadMenu) {
        document.title = label + ' · Manajemen Data · IGT-PR';
        if (crumbStrong) crumbStrong.textContent = label;
        if (headH1) headH1.textContent = label;
        if (headP) headP.textContent = v2DescFor(tab);
        const firstStatHint = document.querySelector('.stats .card.stat:first-child .hint');
        if (firstStatHint) firstStatHint.textContent = label;
        setText('tab-heading', 'Manajemen ' + label);
        setText('tab-description', v2DescFor(tab));
        $('#upload-panel').innerHTML = isMain
          ? (base === 'superadmin'
            ? `<div class="notice"><strong>Catatan</strong>Superadmin berfokus pada pemeriksaan topologi dan persetujuan integrasi IGT Utama. Unggah data dilakukan oleh Satker/Operator terkait.</div>`
            : `<div class="toolbar"><button class="btn btn-primary" data-open-upload-modal="pertanahan">${ri('upload-cloud-2-line')}<span>Unggah Data Pertanahan</span></button><button class="btn btn-primary" data-open-upload-modal="tata-ruang">${ri('upload-cloud-2-line')}<span>Unggah Data Tata Ruang</span></button></div>`)
          : uploadPanel(role, tab);
      } else {
        setText('tab-heading', isMain ? 'IGT Utama' : CATEGORIES[tab].label);
        setText('tab-description', isMain ? 'Kelola pengajuan IGT Pertanahan dan IGT Tata Ruang dari satu halaman.' : UPLOAD_TEXT[tab]);
        $('#upload-panel').innerHTML = isMain
          ? (role === 'superadmin'
            ? `<div class="notice"><strong>Catatan</strong>Superadmin hanya memeriksa topologi dan menyetujui integrasi IGT Utama. Unggah data IGT Utama dilakukan oleh role yang berwenang.</div>`
            : `<div class="toolbar"><button class="btn btn-primary" data-open-upload-modal="pertanahan">${ri('upload-cloud-2-line')}<span>Unggah Data Pertanahan</span></button><button class="btn btn-primary" data-open-upload-modal="tata-ruang">${ri('upload-cloud-2-line')}<span>Unggah Data Tata Ruang</span></button></div>`)
          : uploadPanel(role, tab);
      }
      const own = records.filter((r) => isMain ? (r.category === 'pertanahan' || r.category === 'tata-ruang') : r.category === tab);
      const statusOptions = isMain
        ? (base === 'operator'
            ? ['Revisi', 'Diajukan', 'Terkompilasi', 'Terintegrasi', 'Semua']
            : ['Cek Topologi', 'Diajukan', 'Revisi'])
        : tab === 'derivatif'
          ? (base === 'operator' || base === 'umum'
            ? ['Semua', 'Diproses', 'Disetujui']
            : ['Diproses', 'Disetujui', 'Semua'])
          : [];
      const showStatusTabs = statusOptions.length > 0;
      const statusEl = $('#submission-status-tabs');
      statusEl.innerHTML = showStatusTabs
        ? statusOptions.map((s) => `<button class="tab" data-status-tab="${s}">${s}</button>`).join('')
        : '';
      statusEl.hidden = !showStatusTabs;
      if (showStatusTabs && !statusOptions.includes(statusTab)) statusTab = statusOptions[0];
      statusEl.querySelectorAll('[data-status-tab]').forEach((t) => {
        t.classList.toggle('active', t.dataset.statusTab === statusTab);
        t.setAttribute('aria-selected', t.dataset.statusTab === statusTab);
      });
      const statusMatches = (r) => {
        if (!showStatusTabs || statusTab === 'Semua') return true;
        if (isMain) {
          if (statusTab === 'Cek Topologi') return r.status === 'Terkompilasi';
          if (statusTab === 'Revisi') return r.status === 'Revisi';
          if (statusTab === 'Diajukan') return r.status === 'Diajukan' || r.status === 'Proses';
          if (statusTab === 'Terkompilasi') return r.status === 'Terkompilasi';
          if (statusTab === 'Terintegrasi') return ['Terintegrasi', 'Disetujui', 'Tersedia'].includes(r.status);
          return true;
        }
        if (statusTab === 'Revisi') return r.status === 'Revisi';
        if (statusTab === 'Diproses') return ['Proses', 'Diajukan', 'Terkompilasi'].includes(r.status);
        if (statusTab === 'Disetujui') return ['Disetujui', 'Terintegrasi', 'Tersedia'].includes(r.status);
        return true;
      };
      const displayed = own.filter(statusMatches);
      $('#submission-rows').innerHTML = displayed
        .map((r) => {
          const id = r.n === undefined || r.category === 'lainnya'
            ? r.id
            : `<a class="text-link" href="${DETAIL_URL[CATEGORIES[r.category].detail]}?id=${r.n}&role=${role}">${r.id}</a>`;
          const orgVal = (r.status === 'Terintegrasi' && r.direktorat)
            ? r.direktorat
            : (r.satker || r.direktorat || r.ditjen || r.instansi || r.source || '—');
          const dateVal = (isMain && isIntegratedTab) || tab === 'derivatif' ? (r.updated || "—") : r.date;
          return (
            `<tr data-category="${r.category}"><td data-label="ID Pengajuan">${id}</td><td data-label="Layer Target">${r.name}</td>` +
            `<td data-label="${orgLabel}">${orgVal}</td>` +
            (isReviewerMain ? '' : `<td data-label="${dateLabel}">${dateVal}</td>`) +
            `<td data-label="Status">${badge(r.status)}</td>` +
            `<td data-label="Aksi" class="action-cell">${rowActions(role, r)}</td></tr>`
          );
        })
        .join('');
      setText('submission-count', `${displayed.length} dari ${own.length} pengajuan pada ${label}.`);
      $('#empty-state').hidden = displayed.length > 0;
      renderCounts(own);
    }

    const catTabsEl = $('#submission-category-tabs');
    if (catTabsEl) {
      catTabsEl.addEventListener('click', (event) => {
        const target = event.target.closest('[data-category-tab]');
        if (!target) return;
        tab = target.dataset.categoryTab;
        render();
      });
    }

    $('#submission-status-tabs').addEventListener('click', (event) => {
      const target = event.target.closest('[data-status-tab]');
      if (!target) return;
      statusTab = target.dataset.statusTab;
      render();
    });

    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action], [data-open-upload-modal], [data-close-upload-modal], [data-close-topol-modal], [data-modal-submit], #btn-confirm-topol, #igt-upload-modal, #topology-modal');
      if (!target) return;
      const { action, id } = target.dataset || {};
      const record = records.find((r) => r.id === id);

      if (target.dataset && target.dataset.modalSubmit) {
        const isRev = target.dataset.modalSubmit === 'revision';
        if (isRev) {
          const recId = target.dataset.recordId;
          const targetRec = records.find((r) => r.id === recId);
          if (targetRec) {
            targetRec.status = 'Diajukan';
            targetRec.updated = '20 Okt 2026';
            alert('Pengajuan revisi untuk ' + recId + ' berhasil dikirim ulang. Status kini kembali menjadi Diajukan untuk diverifikasi.');
          }
        } else {
          const inputName = $('#u-nama') ? $('#u-nama').value : 'Dataset Baru 2026';
          const inputSatker = $('#u-satker') ? $('#u-satker').value : 'Kantah Kab. Sleman';
          records.unshift({
            id: 'PRT-2026-' + String(Math.floor(Math.random() * 899 + 100)),
            name: inputName,
            category: tab === 'igt-utama' ? 'pertanahan' : tab,
            satker: inputSatker,
            date: '20 Okt 2026',
            status: 'Diajukan',
          });
          alert('Pengajuan baru "' + inputName + '" berhasil dikirim dengan status Diajukan.');
        }
        const m = $('#igt-upload-modal');
        if (m) { m.hidden = true; m.style.display = 'none'; }
        render();
        return;
      }

      if (target.hasAttribute('data-close-topol-modal') || (target.id === 'topology-modal' && event.target === target)) {
        const modal = $('#topology-modal');
        if (modal) { modal.hidden = true; modal.style.display = 'none'; }
        return;
      }

      if (target.id === 'btn-confirm-topol') {
        alert('Hasil Cek Topologi telah diverifikasi valid. Semua aturan topologi terpenuhi.');
        const modal = $('#topology-modal');
        if (modal) { modal.hidden = true; modal.style.display = 'none'; }
        return;
      }

      if (target.dataset && target.dataset.openUploadModal) {
        const category = target.dataset.openUploadModal;
        if (role === 'superadmin' && (category === 'pertanahan' || category === 'tata-ruang')) {
          alert('Superadmin tidak memiliki akses untuk mengunggah IGT Utama.');
          return;
        }
        const modal = $('#igt-upload-modal');
        $('#igt-upload-modal-title').textContent = category === 'pertanahan' ? 'Unggah IGT Pertanahan' : 'Unggah IGT Tata Ruang';
        $('#igt-upload-modal-description').textContent = category === 'pertanahan' ? 'Unggah atribut bidang.' : 'Unggah geometri dan atribut kawasan.';
        $('#igt-upload-modal-content').innerHTML = uploadPanel(role, category);
        modal.hidden = false;
        modal.style.display = 'flex';
        return;
      }
      if (target.hasAttribute('data-close-upload-modal') || (target.id === 'igt-upload-modal' && event.target === target)) {
        const modal = $('#igt-upload-modal');
        modal.hidden = true;
        modal.style.display = 'none';
        return;
      }
      if (action === 'upload') {
        if (role === 'superadmin') {
          alert('Superadmin tidak memiliki akses untuk mengunggah IGT Utama.');
          return;
        }
        alert('Simulasi: pilih berkas data untuk diunggah (' + (tab === 'igt-utama' ? ($('#igt-upload-modal-title').textContent || 'IGT Utama') : CATEGORIES[tab].label) + ').');
      }
      else if (action === 'validate') {
        if (role === 'superadmin') {
          alert('Superadmin tidak memiliki akses untuk mengunggah IGT Utama.');
          return;
        }
        alert('Parameter valid. Proses ini masih berupa prototipe UI.');
      }
      else if (action === 'upload-lainnya') alert('Unggah layer dan konfigurasi data dilakukan langsung melalui QGIS.');
      else if (action === 'revision') {
        const modal = $('#igt-upload-modal');
        if (modal && record) {
          $('#igt-upload-modal-title').textContent = 'Perbaikan Revisi — ' + record.name;
          $('#igt-upload-modal-description').textContent = 'Perbarui berkas spasial dan kirim ulang pengajuan.';
          $('#igt-upload-modal-content').innerHTML = uploadIgtUtamaPanel(role, record.category || 'pertanahan', record);
          modal.hidden = false;
          modal.style.display = 'flex';
        } else {
          alert('Simulasi: buka formulir revisi untuk pengajuan ' + id + '.');
        }
      }
      else if (action === 'show-qgis') alert('Simulasi: layer ' + (record ? record.name : id) + ' akan ditampilkan di QGIS. Integrasi QGIS belum aktif pada prototipe ini.');
      else if (action === 'compile') {
        alert('Simulasi: proses kompilasi IGT Utama ' + id + ' berhasil. Status diperbarui menjadi Terkompilasi.');
        record.status = 'Terkompilasi';
        render();
      }
      else if (action === 'topology') {
        const topolModal = $('#topology-modal');
        if (topolModal) {
          const recName = record ? record.name : id;
          const recSatker = record ? (record.satker || record.direktorat || 'Kantah Kab. Sleman') : 'Kantah Kab. Sleman';
          $('#topol-dataset-info').innerHTML = '<strong>ID Pengajuan:</strong> ' + id + ' &nbsp;·&nbsp; <strong>Layer:</strong> ' + recName + ' &nbsp;·&nbsp; <strong>Satker:</strong> ' + recSatker;
          topolModal.hidden = false;
          topolModal.style.display = 'flex';
        } else {
          alert('Membuka layer ' + (record ? record.name : id) + ' di QGIS Plugin untuk Cek Topologi.');
        }
        record.status = 'Terkompilasi';
        render();
      } else if (action === 'approve-integration') {
        if ((role !== 'superadmin' && role !== 'superadmin2') || !record || !['pertanahan', 'tata-ruang'].includes(record.category) || record.status !== 'Terkompilasi') {
          alert('Aksi persetujuan integrasi hanya tersedia bagi Superadmin untuk IGT Utama berstatus Terkompilasi.');
          return;
        }
        if (!confirm('Setujui integrasi IGT Utama ' + id + '?')) return;
        record.status = 'Terintegrasi';
        record.updated = '20 Okt 2026';
        render();
      } else if (action === 'approve' || action === 'reject') {
        if (!confirm((action === 'approve' ? 'Setujui' : 'Tolak') + ' pengajuan ' + id + '?')) return;
        record.status = action === 'approve' ? 'Disetujui' : 'Ditolak';
        render();
      } else if (action === 'upload-derivatif') {
        // Admin uploads skip review and are approved immediately; Umum uploads wait for a decision.
        const direct = role !== 'umum';
        const message = direct
          ? 'Simulasi: pilih berkas layer derivatif. Unggahan Admin langsung berstatus Disetujui. Lanjutkan?'
          : 'Simulasi: pilih berkas layer derivatif. Pengajuan Umum berstatus Diajukan dan menunggu keputusan Admin atau Superadmin. Lanjutkan?';
        if (!confirm(message)) return;
        records.unshift({
          category: 'derivatif',
          id: 'DRV-2026-' + String(nextDerivative).padStart(3, '0'),
          name: (direct ? 'Derivatif Unggahan Admin ' : 'Derivatif Unggahan Umum ') + nextDerivative,
          date: '19 Okt 2026',
          status: direct ? 'Disetujui' : 'Diajukan',
          owner: role === 'umum' ? 'umum' : undefined,
        });
        nextDerivative += 1;
        render();
      } else if (action === 'delete') {
        if (!confirm('Hapus layer ' + id + ' dari katalog IGT Lainnya? Tindakan ini tidak dapat dibatalkan.')) return;
        records.splice(records.indexOf(record), 1);
        render();
        alert('Layer ' + id + ' dihapus dari daftar mockup.');
      }
    });

    render();
  }

  // ----------------------------------------------------------------- dashboardCatalog (V2 Live Embedded)
  function dashboardCatalog(target, role = 'superadmin2') {
    const rootEl = typeof target === 'string' ? document.querySelector(target) : target;
    if (!rootEl) return;

    let currentCategory = 'igt-pr';
    let currentPage = 1;
    let pageSize = 8;
    let query = '';
    let selectedProv = 'all';
    let selectedKab = 'all';
    let filterExpanded = false;
    const expandedIds = new Set();

    // Sinkronisasi dengan filter tahun kanan atas (Dashboard)
    const topYearSelect = document.getElementById('dashboard-year-filter');
    let selectedYear = topYearSelect ? topYearSelect.value : 'all';

    // Memuat daftar tab kategori secara dinamis dari CATEGORIES
    const TABS = Object.keys(CATEGORIES).map((k) => ({
      key: k,
      label: CATEGORIES[k].label,
      shortLabel: CATEGORIES[k].shortLabel || CATEGORIES[k].label,
      icon: CATEGORIES[k].icon || 'database-2-line',
    }));

    function getCategoryRecords(cat) {
      const allRecords = IgtData.loadRecords();
      if (cat === 'igt-pr') {
        return allRecords.filter((r) => (r.category === 'pertanahan' || r.category === 'tata-ruang') && IgtData.inCatalog(r));
      }
      return allRecords.filter((r) => r.category === cat && IgtData.inCatalog(r));
    }

    function getProvOptions() {
      if (typeof IgtData !== 'undefined' && IgtData.REGIONS) {
        return Object.keys(IgtData.REGIONS).sort();
      }
      const records = getCategoryRecords(currentCategory);
      const provs = records.map((r) => r.prov).filter(Boolean);
      return [...new Set(provs)].sort();
    }

    function getKabOptions(provOrCat, maybeProv) {
      const prov = maybeProv !== undefined ? maybeProv : provOrCat;
      if (typeof IgtData !== 'undefined' && IgtData.REGIONS) {
        if (prov && prov !== 'all' && IgtData.REGIONS[prov]) {
          return IgtData.REGIONS[prov];
        }
        return [];
      }
      let records = getCategoryRecords(currentCategory);
      if (prov && prov !== 'all') {
        records = records.filter((r) => ((r.prov || '') + ' ' + (r.scope || '')).toLowerCase().includes(prov.toLowerCase()));
      }
      const kabs = records.map((r) => r.kab).filter(Boolean);
      return [...new Set(kabs)].sort();
    }

    function getFiltered() {
      const records = getCategoryRecords(currentCategory);
      const q = query.trim().toLowerCase();

      return records.filter((d) => {
        // 1. Filter Tahun dari filter kanan atas
        if (selectedYear !== 'all') {
          const matchParent = (d.updated || d.date || '').includes(selectedYear);
          const matchSub = d.subLayers && d.subLayers.some((s) => (s.year || s.updated || '').includes(selectedYear));
          if (!matchParent && !matchSub) return false;
        }
        // 2. Filter Provinsi
        if (selectedProv !== 'all') {
          const provHaystack = ((d.prov || '') + ' ' + (d.scope || '')).toLowerCase();
          const pLower = selectedProv.toLowerCase();
          const matchAlias = (pLower.includes('yogyakarta') && (provHaystack.includes('yogyakarta') || provHaystack.includes('d.i.'))) ||
                             (pLower.includes('jakarta') && (provHaystack.includes('jakarta') || provHaystack.includes('dki'))) ||
                             (pLower.includes('bangka belitung') && provHaystack.includes('bangka')) ||
                             provHaystack.includes(pLower);
          if (!matchAlias && !provHaystack.includes('nasional')) {
            return false;
          }
        }
        // 3. Filter Kabupaten (mengikuti provinsi)
        if (selectedKab !== 'all') {
          const kabHaystack = ((d.kab || '') + ' ' + (d.scope || '')).toLowerCase();
          const cleanK = selectedKab.toLowerCase().replace('kabupaten', '').replace('kab. ', '').replace('kota ', '').trim();
          if (!kabHaystack.includes(selectedKab.toLowerCase()) && !kabHaystack.includes(cleanK)) {
            return false;
          }
        }
        // 4. Pencarian
        if (q) {
          const orgVal = d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '';
          const subText = d.subLayers ? d.subLayers.map((s) => s.name + ' ' + (s.label || '')).join(' ') : '';
          const haystack = (d.name + ' ' + (d.scope || '') + ' ' + orgVal + ' ' + (d.prov || '') + ' ' + (d.kab || '') + ' ' + subText).toLowerCase();
          if (!haystack.includes(q)) return false;
        }
        return true;
      });
    }

    function renderPageNumbers(curr, total) {
      const maxBtns = 5;
      let startP = Math.max(1, curr - 2);
      let endP = Math.min(total, startP + maxBtns - 1);
      if (endP - startP < maxBtns - 1) {
        startP = Math.max(1, endP - maxBtns + 1);
      }
      let html = '';
      for (let p = startP; p <= endP; p++) {
        html += `<button type="button" class="dash-pag-num ${p === curr ? 'active' : ''}" data-dash-page="${p}" aria-label="Halaman ${p}">${p}</button>`;
      }
      return html;
    }

    function render() {
      const filtered = getFiltered();
      const totalItems = filtered.length;
      const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
      if (currentPage > totalPages) currentPage = totalPages;
      if (currentPage < 1) currentPage = 1;

      const startIdx = (currentPage - 1) * pageSize;
      const endIdx = Math.min(startIdx + pageSize, totalItems);
      const pageItems = filtered.slice(startIdx, endIdx);

      const catInfo = CATEGORIES[currentCategory] || CATEGORIES['igt-pr'];
      const provOptions = getProvOptions();
      const kabOptions = getKabOptions(selectedProv);

      let html = '';

      // 1. Subnav 5 Tabs (Dinamis, Stretch sampai ujung, Responsif)
      html += `
        <div class="dash-cat-tabs" role="tablist" aria-label="Pilih Kategori IGT">
          ${TABS.map((t) => `
            <button type="button" class="dash-cat-tab ${t.key === currentCategory ? 'active' : ''}" data-dash-cat="${t.key}" role="tab" aria-selected="${t.key === currentCategory}" title="${t.label}">
              <span class="tab-icon">${ri(t.icon)}</span>
              <span class="tab-label">${t.label}</span>
            </button>
          `).join('')}
        </div>
      `;

      // 2. Filter Box (Pencarian, Provinsi, Kabupaten)
      html += `
        <div class="dash-cat-filter-box catalog-controls-v2">
          <div class="catalog-search-row">
            <div class="dash-cat-search-wrap catalog-search-input-wrap">
              <input type="search" class="dash-cat-search-input" id="dash-cat-search-field" placeholder="Cari nama IGT, sublayer, wilayah..." value="${query.replace(/"/g, '&quot;')}">
            </div>
            <button type="button" class="catalog-filter-toggle ${filterExpanded ? 'active' : ''}" id="dash-cat-filter-btn" aria-expanded="${filterExpanded}">
              ${ri('filter-3-line')}<span>Filter</span>
            </button>
          </div>
          <div class="catalog-filter-drawer dash-cat-dropdowns" id="dash-cat-drawer" ${filterExpanded ? '' : 'hidden'}>
            <div class="field prov-filter">
              <label for="dash-cat-prov-select">PROVINSI</label>
              <select class="dash-cat-select" id="dash-cat-prov-select" aria-label="Filter Provinsi">
                <option value="all" ${selectedProv === 'all' ? 'selected' : ''}>Semua Provinsi</option>
                ${provOptions.map((p) => `
                  <option value="${p.replace(/"/g, '&quot;')}" ${selectedProv === p ? 'selected' : ''}>${p}</option>
                `).join('')}
              </select>
            </div>
            <div class="field kab-filter">
              <label for="dash-cat-kab-select">KABUPATEN / KOTA</label>
              <select class="dash-cat-select" id="dash-cat-kab-select" aria-label="Filter Kabupaten" ${selectedProv === 'all' ? 'disabled' : ''}>
                <option value="all" ${selectedKab === 'all' ? 'selected' : ''}>${selectedProv === 'all' ? '-- Pilih Provinsi Terlebih Dahulu --' : 'Semua Kabupaten / Kota'}</option>
                ${selectedProv !== 'all' ? kabOptions.map((k) => `
                  <option value="${k.replace(/"/g, '&quot;')}" ${selectedKab === k ? 'selected' : ''}>${k}</option>
                `).join('') : ''}
              </select>
            </div>
          </div>
        </div>
      `;

      // 3. Summary Count Label
      html += `
        <div class="dash-cat-summary">
          ${totalItems > 0
            ? `Menampilkan ${startIdx + 1}–${endIdx} dari ${totalItems} dataset · Halaman ${currentPage} dari ${totalPages} · Kategori ${catInfo.label}${selectedYear !== 'all' ? ' · Tahun ' + selectedYear : ''}`
            : `Tidak ada dataset yang cocok dengan kriteria filter atau pencarian · Kategori ${catInfo.label}${selectedYear !== 'all' ? ' · Tahun ' + selectedYear : ''}`
          }
        </div>
      `;

      // 4. Cards List (8 Data Teratas)
      html += '<div class="dash-cat-cards">';
      if (pageItems.length === 0) {
        html += `
          <div class="dash-cat-empty">
            <p>Tidak ada dataset yang cocok dengan kriteria filter atau pencarian.</p>
          </div>
        `;
      } else {
        pageItems.forEach((d, idx) => {
          const hasSubs = Boolean(d.subLayers && d.subLayers.length > 0);
          const isExp = expandedIds.has(d.id) || Boolean(query && hasSubs && d.subLayers.some((s) => s.name.toLowerCase().includes(query.toLowerCase())));
          const allowWfs = canAccessWfs(role, d);
          const cat = d.category;
          const iconHtml = categoryIcon(cat);

          html += `
            <div class="dash-card" data-id="${d.id}">
              <div class="dash-card-row">
                <div class="dash-card-left">
                  <div class="dash-card-header">
                    <div class="dash-card-title-wrap">
                      <span class="igt-catalog-num">${startIdx + idx + 1}</span>
                      <span class="igt-cat-inline-icon is-${cat}" title="${cat}">${iconHtml}</span>
                      <button type="button" class="dash-card-title igt-catalog-name igt-card-link-title" data-open-detail="${d.id}" title="Klik untuk melihat detail lengkap dataset IGT">${d.name}</button>
                      <button type="button" class="igt-info-btn" data-open-detail="${d.id}" title="Detail Informasi & Metadata IGT" aria-label="Detail Informasi IGT">
                        ${ri('information-line')}
                      </button>
                      ${hasSubs ? `
                        <button type="button" class="igt-chip igt-chip--multi-layer igt-chip--compact dash-chip-toggle" data-dash-toggle="${d.id}" aria-expanded="${isExp}" title="Klik untuk membuka/menutup sub-layer">
                          <span class="igt-chip__text">Multi-layer (${d.subLayers.length})</span>
                          <span class="igt-chip__caret" aria-hidden="true">${isExp ? '▴' : '▾'}</span>
                        </button>
                      ` : ''}
                    </div>
                  </div>
                </div>
                <div class="dash-card-actions">
                  <button type="button" class="dash-btn-wms" data-action="wms" data-name="${d.name.replace(/"/g, '&quot;')}" ${hasSubs ? 'data-is-parent-multi="true"' : ''} title="${hasSubs ? 'Muat seluruh (' + d.subLayers.length + ') sub-IGT sekaligus sebagai layer WMS ke kanvas peta QGIS' : 'Muat layer WMS ke kanvas peta QGIS'}">WMS</button>
                  ${allowWfs ? `<button type="button" class="dash-btn-wfs" data-action="wfs" data-name="${d.name.replace(/"/g, '&quot;')}" ${hasSubs ? 'data-is-parent-multi="true"' : ''} title="${hasSubs ? 'Muat seluruh (' + d.subLayers.length + ') sub-IGT sekaligus sebagai layer WFS ke kanvas peta QGIS' : 'Muat layer WFS ke kanvas peta QGIS'}">WFS</button>` : ''}
                </div>
              </div>
              ${hasSubs ? `
                <div class="dash-sub-container" style="${isExp ? '' : 'display:none;'}">
                  ${d.subLayers.map((sub) => `
                    <div class="dash-sub-item">
                      <div class="dash-sub-left">
                        <span class="dash-sub-branch">└─</span>
                        <span class="dash-sub-title">${sub.name}</span>
                      </div>
                      <div class="dash-sub-actions">
                        <button type="button" class="dash-sub-btn dash-sub-btn--wms" data-action="wms" data-name="${sub.name.replace(/"/g, '&quot;')}">WMS</button>
                        ${allowWfs ? `<button type="button" class="dash-sub-btn dash-sub-btn--wfs" data-action="wfs" data-name="${sub.name.replace(/"/g, '&quot;')}">WFS</button>` : ''}
                      </div>
                    </div>
                  `).join('')}
                </div>
              ` : ''}
            </div>
          `;
        });
      }
      html += '</div>';

      // 5. Pagination Bar (tampil jika dataset > pageSize atau totalPages > 1)
      if (totalItems > pageSize || totalPages > 1) {
        html += `
          <div class="dash-cat-pag-box">
            <div class="dash-cat-pagesize-wrap">
              <label for="dash-cat-pagesize-select" class="dash-cat-pagesize-label">Tampilkan:</label>
              <select class="dash-cat-pagesize-select" id="dash-cat-pagesize-select" aria-label="Jumlah card per halaman">
                <option value="4" ${pageSize === 4 ? 'selected' : ''}>4 card</option>
                <option value="8" ${pageSize === 8 ? 'selected' : ''}>8 card</option>
                <option value="12" ${pageSize === 12 ? 'selected' : ''}>12 card</option>
                <option value="16" ${pageSize === 16 ? 'selected' : ''}>16 card</option>
                <option value="24" ${pageSize === 24 ? 'selected' : ''}>24 card</option>
              </select>
            </div>
            <div class="dash-pag-nav-group">
              <button type="button" class="dash-pag-nav-btn dash-pag-prev" ${currentPage <= 1 ? 'disabled' : ''} aria-label="Sebelumnya" title="Halaman sebelumnya">
                ←
              </button>
              <div class="dash-pag-numbers">
                ${renderPageNumbers(currentPage, totalPages)}
              </div>
              <button type="button" class="dash-pag-nav-btn dash-pag-next" ${currentPage >= totalPages ? 'disabled' : ''} aria-label="Berikutnya" title="Halaman berikutnya">
                →
              </button>
            </div>
          </div>
        `;
      }

      rootEl.innerHTML = html;

      // Attach Event Listeners
      const pageSizeSelect = rootEl.querySelector('#dash-cat-pagesize-select');
      if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', (e) => {
          pageSize = parseInt(e.target.value, 10) || 8;
          currentPage = 1;
          render();
        });
      }

      rootEl.querySelectorAll('[data-dash-cat]').forEach((btn) => {
        btn.addEventListener('click', () => {
          currentCategory = btn.dataset.dashCat;
          currentPage = 1;
          selectedProv = 'all';
          selectedKab = 'all';
          render();
        });
      });

      const searchInput = rootEl.querySelector('#dash-cat-search-field');
      if (searchInput) {
        searchInput.addEventListener('input', (e) => {
          query = e.target.value;
          currentPage = 1;
          render();
          const nextInput = rootEl.querySelector('#dash-cat-search-field');
          if (nextInput) {
            nextInput.focus();
            nextInput.setSelectionRange(nextInput.value.length, nextInput.value.length);
          }
        });
      }

      const provSelect = rootEl.querySelector('#dash-cat-prov-select');
      if (provSelect) {
        provSelect.addEventListener('change', (e) => {
          selectedProv = e.target.value;
          if (selectedProv === 'all') {
            selectedKab = 'all';
          } else {
            const validKabs = getKabOptions(selectedProv);
            if (!validKabs.includes(selectedKab)) {
              selectedKab = 'all';
            }
          }
          currentPage = 1;
          render();
        });
      }

      const kabSelect = rootEl.querySelector('#dash-cat-kab-select');
      if (kabSelect) {
        kabSelect.addEventListener('change', (e) => {
          selectedKab = e.target.value;
          currentPage = 1;
          render();
        });
      }

      const prevBtn = rootEl.querySelector('.dash-pag-prev');
      if (prevBtn) {
        prevBtn.addEventListener('click', () => {
          if (currentPage > 1) {
            currentPage -= 1;
            render();
          }
        });
      }

      const nextBtn = rootEl.querySelector('.dash-pag-next');
      if (nextBtn) {
        nextBtn.addEventListener('click', () => {
          if (currentPage < totalPages) {
            currentPage += 1;
            render();
          }
        });
      }

      rootEl.querySelectorAll('[data-dash-page]').forEach((btn) => {
        btn.addEventListener('click', () => {
          const val = parseInt(btn.dataset.dashPage, 10);
          if (val && val !== currentPage) {
            currentPage = val;
            render();
          }
        });
      });

      rootEl.querySelectorAll('[data-dash-toggle]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const id = btn.dataset.dashToggle;
          if (expandedIds.has(id)) expandedIds.delete(id);
          else expandedIds.add(id);
          render();
        });
      });

      const dashFilterBtn = rootEl.querySelector('#dash-cat-filter-btn');
      const dashDrawer = rootEl.querySelector('#dash-cat-drawer');
      if (dashFilterBtn && dashDrawer) {
        dashFilterBtn.addEventListener('click', () => {
          filterExpanded = !filterExpanded;
          dashDrawer.hidden = !filterExpanded;
          dashFilterBtn.classList.toggle('active', filterExpanded);
          dashFilterBtn.setAttribute('aria-expanded', filterExpanded ? 'true' : 'false');
        });
      }

      rootEl.querySelectorAll('[data-open-detail]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const id = btn.dataset.openDetail;
          const ds = IgtData.loadRecords().find((r) => r.id === id);
          if (ds) {
            showIgtDetailModal(ds, role);
          }
        });
      });

      rootEl.querySelectorAll('[data-action]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const act = btn.dataset.action;
          const name = btn.dataset.name;
          const cardEl = btn.closest('.dash-card');
          const cardId = cardEl ? cardEl.dataset.id : null;
          const ds = cardId ? IgtData.loadRecords().find((r) => r.id === cardId) : null;
          if (act === 'wfs') {
            if (ds && !canAccessWfs(role, ds)) {
              const warn = 'Akses WFS dibatasi untuk satker terkait.';
              if (typeof toast === 'function') toast(warn);
              else alert(warn);
              return;
            }
            showWfsFilterModal(ds || { name }, role);
            return;
          }
          if (btn.dataset.isParentMulti === 'true' && ds && ds.subLayers) {
            const count = ds.subLayers.length;
            const subNames = ds.subLayers.map((s) => s.name).join(', ');
            const typeLabel = 'layer citra WMS';
            const msg = "Simulasi QGIS: Memuat " + (count === 2 ? "kedua" : "seluruh " + count) + " sub-IGT untuk '" + ds.name + "' (" + subNames + ") sebagai " + typeLabel + " ke dalam kanvas peta QGIS.";
            if (typeof toast === 'function') toast(msg);
            else alert(msg);
            return;
          }
          if (act === 'both') {
            const bothMsg = "Simulasi QGIS: Memuat sekaligus WMS dan WFS untuk layer '" + name + "' ke dalam kanvas peta QGIS.";
            if (typeof toast === 'function') toast(bothMsg);
            else alert(bothMsg);
            return;
          }
          const msg = act === 'wms' ? WMS_MESSAGE(name) : WFS_MESSAGE(name);
          if (typeof toast === 'function') {
            toast(msg);
          } else {
            alert(msg);
          }
        });
      });
    }

    render();

    return {
      setYear: (y) => {
        selectedYear = y;
        currentPage = 1;
        render();
      },
      render,
    };
  }

  return { dashboard, catalog, upload, dashboardCatalog, showWfsFilterModal };
})();

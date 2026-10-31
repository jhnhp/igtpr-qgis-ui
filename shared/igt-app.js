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
  };

  const ri = (name) => `<svg class="ri-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="${RI_PATHS[name] || RI_PATHS['stack-line']}"/></svg>`;

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
    const fromData = records.map((r) => r.prov).filter(Boolean);
    const defaults = ['D.I. Yogyakarta', 'Jawa Tengah', 'Kalimantan Barat', 'Nasional'];
    return [...new Set([...fromData, ...defaults])].sort();
  };
  const provFilterOptions = (records) =>
    '<option value="all" selected>Semua Provinsi</option>' +
    provOptions(records).map((p) => '<option value="' + p + '">' + p + '</option>').join('');
  const kabOptions = (records) => {
    const fromData = records.map((r) => r.kab).filter(Boolean);
    const defaults = ['Kab. Sleman', 'Kab. Bantul', 'Kab. Kulon Progo', 'Kab. Gunungkidul', 'Kota Yogyakarta', 'Multi-Kabupaten', 'Seluruh Indonesia'];
    return [...new Set([...fromData, ...defaults])].sort();
  };
  const kabFilterOptions = (records) =>
    '<option value="all" selected>Semua Kab / Kota</option>' +
    kabOptions(records).map((k) => '<option value="' + k + '">' + k + '</option>').join('');
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
    const availableCategories = CATEGORY_ORDER.filter((key) => IgtData.canUpload(base, key));
    // Superadmin can review IGT Utama and derivatif, but may only upload IGT Lainnya.
    if (base === 'superadmin') return ['igt-utama', 'derivatif', ...availableCategories.filter((key) => key === 'lainnya')];
    return [
      ...(availableCategories.some((key) => key === 'pertanahan' || key === 'tata-ruang') ? ['igt-utama'] : []),
      ...availableCategories.filter((key) => key !== 'pertanahan' && key !== 'tata-ruang'),
    ];
  }

  const managementLabel = (key) => (key === 'semua' ? 'Semua Kategori' : key === 'igt-utama' ? 'IGT Utama' : CATEGORIES[key].label);
  const managementShortLabel = (key) => (key === 'semua' ? 'Semua Kategori' : key === 'igt-utama' ? 'IGT Utama' : (CATEGORIES[key].shortLabel || CATEGORIES[key].label));
  const CATALOG_ICON = {
    pertanahan: ri('map-pin-line'),
    'tata-ruang': ri('map-2-line'),
    derivatif: ri('stack-line'),
    lainnya: ri('global-line'),
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
    const categories = CATEGORY_ORDER.filter((key) => IgtData.canView(role, key));
    const catalogButtons = categories.map((key) => '<a class="btn btn-soft menu-btn" href="../' + CATEGORIES[key].slug + '/index.html">' + (CATALOG_ICON[key] || ri('stack-line')) + '<span>' + (CATEGORIES[key].shortLabel || CATEGORIES[key].label) + '</span></a>').join('');
    const manageButtons = managementCategories(role)
      .map((key) => '<a class="btn btn-primary menu-btn" id="upload-button-' + key + '" href="../upload-data/index.html?tab=' + key + '">' + (MANAGEMENT_ICON[key] || ri('database-2-line')) + '<span>' + managementShortLabel(key) + '</span></a>')
      .join('');
    $('#view').innerHTML =
      '<div class="field year-filter-wrap"><label for="dashboard-year-filter">FILTER TAHUN</label><select id="dashboard-year-filter">' + yearFilterOptions(records) + '</select></div>' +
      '<div class="grid stats">' +
      statCard('Terkompilasi', '0', 'Menunggu integrasi', ri('folder-line'), 'amber', 'count-compiled') +
      statCard('Terintegrasi', '0', 'Pertanahan dan Tata Ruang', ri('checkbox-circle-line'), 'green', 'count-integrated') +
      '</div>' +
      '<section class="card"><div class="card-head"><div><h2>Katalog IGT</h2><p>Pilih kategori untuk melihat dataset.</p></div></div>' +
      '<div class="menu-buttons" id="catalog-buttons">' + catalogButtons + '</div>' +
      '<div class="card-head menu-upload-head"><div><h2>Kelola data</h2><p>Unggah data baru dan pantau status pengajuan.</p></div></div>' +
      '<div class="menu-buttons' + (role === 'superadmin' ? ' menu-buttons-superadmin' : '') + '" id="upload-buttons">' + manageButtons + '</div>' +
      '<div class="menu-buttons model-builder-buttons"><a class="btn btn-primary menu-btn" id="model-builder-button" href="../../../shared/model-builder/index.html?role=' + role + '">' + ri('node-tree') + '<span>Model Builder</span></a></div>' +
      '</section>';
    const updateDashboard = () => {
      const year = $('#dashboard-year-filter').value;
      const visible = records.filter((record) => year === 'all' || yearOf(record) === year);
      const staged = IgtData.integrationRecords(visible);
      setText('count-compiled', IgtData.countByStatus(staged, 'Terkompilasi'));
      setText('count-integrated', IgtData.countByStatus(staged, 'Terintegrasi'));
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

  // Datasets of one category that are in its catalog (see CATEGORIES[...].catalogStatus); nothing can be edited here.
  function catalog(role, category) {
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
        crumb.innerHTML = 'Geoportal IGT-PR　/　<a href="../beranda/index.html">Katalog IGT</a>　/　<strong>' + config.label + '</strong>';
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
            '<a class="' + (key === category ? 'active' : '') + '" href="../' + CATEGORIES[key].slug + '/index.html">' +
            (CATALOG_ICON[key] || ri('stack-line')) + '<span>' + (CATEGORIES[key].shortLabel || CATEGORIES[key].label) + '</span></a>'
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
      '<div class="notice"><strong>Isi katalog</strong>' + config.rule + ' Tombol WMS dan WFS adalah simulasi; belum ada layanan nyata yang terhubung.</div>' +
      '<div class="catalog-controls">' +
      '<div class="field catalog-search"><label for="catalog-search">PENCARIAN</label><input id="catalog-search" type="search" placeholder="Cari nama IGT, ID..."></div>' +
      '<div class="field year-filter"><label for="catalog-year-filter">TAHUN</label><select id="catalog-year-filter">' + yearFilterOptions(datasets) + '</select></div>' +
      '<div class="field prov-filter"><label for="catalog-prov-filter">PROVINSI</label><select id="catalog-prov-filter">' + provFilterOptions(datasets) + '</select></div>' +
      '<div class="field kab-filter"><label for="catalog-kab-filter">KABUPATEN / KOTA</label><select id="catalog-kab-filter">' + kabFilterOptions(datasets) + '</select></div>' +
      '</div>' +
      '<section class="card"><div class="card-head"><div><h2>' + config.noun.charAt(0).toUpperCase() + config.noun.slice(1) + '</h2><p id="catalog-count"></p></div></div>' +
      '<div class="table-wrap"><table class="stack"><thead><tr>' +
      '<th><button type="button" class="sort-header" data-sort="name">Nama IGT <span aria-hidden="true">↕</span></button></th>' +
      '<th><button type="button" class="sort-header" data-sort="direktorat">' + orgLabel + ' <span aria-hidden="true">↕</span></button></th>' +
      '<th><button type="button" class="sort-header" data-sort="updated">' +
      (config.integration ? 'Tanggal Pembaruan' : category === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Unggah') +
      ' <span aria-hidden="true">↕</span></button></th><th>Tampilkan WMS</th><th>Tampilkan WFS</th></tr></thead><tbody id="catalog-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden></div></section>';
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
          if (prov !== 'Nasional' && d.prov === 'Nasional') {
            // Data lingkup nasional mencakup semua provinsi
          } else if (!provHaystack.includes(prov.toLowerCase())) {
            return false;
          }
        }
        if (kab !== 'all') {
          const kabHaystack = ((d.kab || '') + ' ' + (d.scope || '')).toLowerCase();
          if (d.kab === 'Seluruh Indonesia' || d.prov === 'Nasional') {
            // Data nasional mencakup seluruh kabupaten
          } else if (!kabHaystack.includes(kab.toLowerCase())) {
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
      $('#catalog-rows').innerHTML = shown.map((d) => {
        const hasSubs = Boolean(d.subLayers && d.subLayers.length > 0);
        const autoExpand = Boolean(q && d.subLayers && d.subLayers.some((s) => (s.name + ' ' + (s.label || '') + ' ' + (s.year || '') + ' ' + (s.skala || '')).toLowerCase().includes(q)));
        const isExp = autoExpand;
        const parentRow = (
          '<tr class="' + (hasSubs ? 'has-sublayers' : '') + (isExp ? ' is-expanded' : '') + '" data-record-id="' + d.id + '">' +
          '<td data-label="Nama IGT">' +
          '<div class="igt-catalog-item">' +
          '<div class="igt-catalog-header">' +
          (hasSubs
            ? '<button type="button" class="igt-tree-toggle" data-toggle-sub="' + d.id + '" aria-expanded="' + (isExp ? 'true' : 'false') + '" title="Buka/tutup sub-layer">' +
              '<span class="igt-tree-icon" aria-hidden="true">' + (isExp ? '▼' : '▶') + '</span>' +
              '</button>'
            : '') +
          '<strong class="igt-catalog-name">' + d.name + '</strong>' +
          '</div></div></td>' +
          '<td data-label="' + orgLabel + '">' + (d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '—') + '</td>' +
          '<td data-label="Tanggal">' + (d.updated || d.date || '—') + '</td>' +
          (hasSubs
            ? '<td colspan="2" class="igt-action-cell-multilayer" data-label="Sub-layer">' +
              '<button type="button" class="igt-chip igt-chip--multi-layer" data-toggle-sub="' + d.id + '" aria-expanded="' + (isExp ? 'true' : 'false') + '" title="Dataset Multi-Layer. Klik untuk membuka/menutup sub-layer">' +
              '<span class="igt-chip__text">Multi-Layer</span>' +
              '<span class="igt-chip__count">' + d.subLayers.length + ' Layer</span>' +
              '<span class="igt-chip__caret" aria-hidden="true">' + (isExp ? '▴' : '▾') + '</span>' +
              '</button>' +
              '</td>'
            : '<td data-label="Tampilkan WMS">' + button('btn-soft', 'wms', d.id, ri('map-2-line') + '<span>WMS</span>') + '</td>' +
              '<td data-label="Tampilkan WFS">' + button('btn-soft', 'wfs', d.id, ri('stack-line') + '<span>WFS</span>') + '</td>'
          ) +
          '</tr>'
        );

        if (!hasSubs) return parentRow;

        const subRows = d.subLayers.map((sub) => {
          return (
            '<tr class="igt-sublayer-row igt-sublayer-for-' + d.id + '" data-parent-id="' + d.id + '" style="' + (isExp ? '' : 'display:none;') + '"' + (isExp ? '' : ' hidden') + '>' +
            '<td class="igt-sublayer-cell" data-label="Nama Sub-layer">' +
            '<div class="igt-sublayer-branch">' +
            '<span class="igt-tree-branch-line" aria-hidden="true">└─</span>' +
            '<div class="igt-sublayer-content">' +
            '<span class="igt-sublayer-title">' + sub.name + '</span>' +
            '</div></div></td>' +
            '<td data-label="' + orgLabel + '"><span class="igt-sublayer-meta">' + (sub.scope || d.direktorat || '—') + '</span></td>' +
            '<td data-label="Tanggal"><span class="igt-sublayer-date">' + (sub.updated || sub.date || d.updated || '—') + '</span></td>' +
            '<td data-label="Tampilkan WMS"><button type="button" class="btn btn-soft btn-sm igt-sub-btn" data-action="wms-sub" data-sub-id="' + sub.id + '" data-sub-name="' + sub.name + '" data-parent-name="' + d.name + '">' + ri('map-2-line') + '<span>WMS</span></button></td>' +
            '<td data-label="Tampilkan WFS"><button type="button" class="btn btn-soft btn-sm igt-sub-btn" data-action="wfs-sub" data-sub-id="' + sub.id + '" data-sub-name="' + sub.name + '" data-parent-name="' + d.name + '">' + ri('stack-line') + '<span>WFS</span></button></td>' +
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
    $('#catalog-year-filter').addEventListener('change', render);
    if ($('#catalog-prov-filter')) $('#catalog-prov-filter').addEventListener('change', render);
    if ($('#catalog-kab-filter')) $('#catalog-kab-filter').addEventListener('change', render);
    document.querySelectorAll('.sort-header').forEach((btn) => btn.addEventListener('click', () => {
      if (sortKey === btn.dataset.sort) sortDirection *= -1;
      else { sortKey = btn.dataset.sort; sortDirection = 1; }
      render();
    }));
    document.addEventListener('click', (event) => {
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
        alert("Simulasi QGIS: Mengambil data fitur WFS untuk '" + subName + "' (sub-layer dari " + parentName + ").");
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
        if (dataset.subLayers && dataset.subLayers.length > 0) {
          alert("Simulasi QGIS: Mengambil fitur WFS seluruh sub-layer untuk '" + dataset.name + "' (" + dataset.subLayers.length + " layer).");
        } else {
          alert(WFS_MESSAGE(dataset.name));
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

  // Upload controls differ per category and role. Baseline exists only for IGT Pertanahan.
  function uploadPanel(role, category) {
    if (category === 'pertanahan') {
      return (
        `<div class="dropzone"><div class="big">⇧</div><strong>Unggah data atribut bidang</strong>` +
        `<p>Unggah tabel atribut yang terhubung dengan ID bidang.</p><button class="btn btn-primary" data-action="upload">Pilih berkas</button></div>` +
        `<div class="notice"><strong>Catatan</strong>Geometri bidang berasal dari baseline. Pastikan ID bidang cocok sebelum mengirim atribut.</div>`
      );
    }
    if (category === 'tata-ruang') {
      return (
        `<div class="dropzone"><div class="big">⇧</div><strong>Tarik dan letakkan berkas di sini</strong>` +
        `<p>Shapefile (.zip) atau GeoPackage (.gpkg), maksimal 500 MB</p><button class="btn btn-primary" data-action="upload">Pilih berkas</button></div>` +
        `<div class="form-grid" style="margin-top:18px"><div class="field"><label for="f-tema">TEMA IGT</label><select id="f-tema"><option>Pilih tema...</option>` +
        `<option>Lingkungan</option><option>Infrastruktur</option><option>Administrasi</option></select></div>` +
        `<div class="field"><label for="f-nama">NAMA LAYER</label><input id="f-nama" placeholder="Masukkan nama layer"></div>` +
        `<div class="field"><label for="f-wilayah">WILAYAH</label><input id="f-wilayah" placeholder="Provinsi / Kabupaten / Kota"></div>` +
        `<div class="field"><label for="f-deskripsi">DESKRIPSI</label><input id="f-deskripsi" placeholder="Deskripsi singkat"></div></div>` +
        `<div class="toolbar"><button class="btn btn-primary" data-action="validate">Validasi dan lanjutkan</button></div>`
      );
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
      if (reviewer && r.status === 'Diajukan') {
        extras.push(button('btn-primary', 'compile', r.id, ri('check-line') + '<span>Kompilasi</span>'));
      }
      if (reviewer && r.status === 'Terkompilasi') {
        extras.push(button('btn-primary', 'topology', r.id, ri('focus-3-line') + '<span>Verifikasi Topologi</span>'));
        if (isSuper) extras.push(button('btn-primary', 'approve-integration', r.id, ri('check-line') + '<span>Setujui Integrasi</span>'));
      }
      if ((base === 'operator' || isV2Role(role)) && r.status === 'Revisi') extras.push(button('btn-soft', 'revision', r.id, ri('edit-line') + '<span>Revisi</span>'));
    } else if (reviewer && r.status === 'Diajukan') {
      extras.push(button('btn-primary', 'approve', r.id, ri('check-line') + '<span>Setujui</span>'), button('btn-soft', 'reject', r.id, ri('close-line') + '<span>Tolak</span>'));
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
    let statusTab = params.get('status') || (tab === 'igt-utama' ? (base === 'operator' ? 'Revisi' : 'Diajukan') : tab === 'derivatif' && (base === 'operator' || base === 'umum') ? 'Semua' : tab === 'derivatif' ? 'Diproses' : 'Semua');
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
        crumb.innerHTML = 'Geoportal IGT-PR　/　<a href="../beranda/index.html">Manajemen Data</a>　/　<strong>' + pageTitle + '</strong>';
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
      statCard('Perlu perhatian', '', 'Revisi, Ditolak, atau Kadaluwarsa', ri('error-warning-line'), 'red', 'count-attention') +
      `</div><section class="card">` +
      (noUploadMenu
        ? `<div class="card-head"><div><h2 id="tab-heading"></h2><p id="tab-description"></p></div></div>`
        : `<div class="card-head"><div><h2 id="tab-heading"></h2><p id="tab-description"></p></div></div>` +
          `<div id="upload-panel"></div>` +
          `<div id="igt-upload-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="igt-upload-modal-title" style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto">` +
          `<section class="card" style="width:min(760px,100%);max-height:90vh;overflow:auto;margin:auto"><div class="card-head"><div><h2 id="igt-upload-modal-title">Unggah IGT</h2><p id="igt-upload-modal-description"></p></div><button type="button" class="btn btn-soft" data-close-upload-modal>✕ Tutup</button></div><div id="igt-upload-modal-content"></div></section></div>`) +
      `<div id="submission-status-tabs" class="tabs" data-status-tabs></div>` +
      `<div class="card-head submissions-head"><div><h2>Daftar Pengajuan</h2><p id="submission-count"></p></div></div>` +
      `<div class="table-wrap"><table class="stack"><thead><tr><th>ID Pengajuan</th><th>Layer Target</th><th id="submission-org-heading">Satker</th><th id="submission-date-heading">Tanggal Unggah</th><th>Status</th><th>Aksi</th></tr></thead>` +
      `<tbody id="submission-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden>Belum ada pengajuan pada kategori ini.</div></section>`;

    function renderCounts(ownRecords) {
      const count = (...statuses) => ownRecords.filter((r) => statuses.includes(r.status)).length;
      setText('count-total', ownRecords.length);
      setText('count-process', count('Proses', 'Diajukan'));
      setText('count-waiting', count('Terkompilasi'));
      setText('count-attention', count('Revisi', 'Ditolak', 'Kadaluwarsa'));
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
      setText('submission-org-heading', orgLabel);
      setText('submission-date-heading', isMain ? 'Tanggal Terintegrasi' : tab === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Unggah');
      if (noUploadMenu) {
        document.title = label + ' · Manajemen Data · IGT-PR';
        if (crumbStrong) crumbStrong.textContent = label;
        if (headH1) headH1.textContent = label;
        if (headP) headP.textContent = v2DescFor(tab);
        const firstStatHint = document.querySelector('.stats .card.stat:first-child .hint');
        if (firstStatHint) firstStatHint.textContent = label;
        setText('tab-heading', 'Manajemen ' + label);
        setText('tab-description', v2DescFor(tab));
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
        ? ['Revisi', 'Diajukan', 'Terkompilasi', 'Terintegrasi', 'Semua']
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
          const dateLabel = isMain ? 'Tanggal Terintegrasi' : tab === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Unggah';
          const dateVal = isMain || tab === 'derivatif' ? (r.updated || "—") : r.date;
          return (
            `<tr data-category="${r.category}"><td data-label="ID Pengajuan">${id}</td><td data-label="Layer Target">${r.name}</td>` +
            `<td data-label="${orgLabel}">${orgVal}</td>` +
            `<td data-label="${dateLabel}">${dateVal}</td><td data-label="Status">${badge(r.status)}</td>` +
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
      const target = event.target.closest('[data-action], [data-open-upload-modal], [data-close-upload-modal], #igt-upload-modal');
      if (!target) return;
      const { action, id } = target.dataset;
      const record = records.find((r) => r.id === id);
      if (target.dataset.openUploadModal) {
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
      else if (action === 'revision') alert('Simulasi: buka formulir revisi untuk pengajuan ' + id + '.');
      else if (action === 'show-qgis') alert('Simulasi: layer ' + (record ? record.name : id) + ' akan ditampilkan di QGIS. Integrasi QGIS belum aktif pada prototipe ini.');
      else if (action === 'compile') {
        alert('Simulasi: proses kompilasi IGT Utama ' + id + ' berhasil. Status diperbarui menjadi Terkompilasi.');
        record.status = 'Terkompilasi';
        render();
      }
      else if (action === 'topology') {
        alert('Simulasi verifikasi topologi untuk ' + id + '. Pada implementasi QGIS, aksi ini menjalankan pemeriksaan topologi pada layer terkait.');
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
    let selectedYear = 'all';
    let selectedReg = 'all';
    const expandedIds = new Set();

    const TABS = [
      { key: 'igt-pr', label: 'IGT-PR' },
      { key: 'pertanahan', label: 'IGT Pertanahan' },
      { key: 'tata-ruang', label: 'IGT Tata Ruang' },
      { key: 'derivatif', label: 'IGT Derivatif' },
      { key: 'lainnya', label: 'IGT K/L Lainnya' },
    ];

    function getFiltered() {
      const allRecords = IgtData.loadRecords();
      let records = [];
      if (currentCategory === 'igt-pr') {
        records = allRecords.filter((r) => (r.category === 'pertanahan' || r.category === 'tata-ruang') && IgtData.inCatalog(r));
      } else {
        records = allRecords.filter((r) => r.category === currentCategory && IgtData.inCatalog(r));
      }

      const q = query.trim().toLowerCase();
      return records.filter((d) => {
        if (selectedYear !== 'all') {
          const matchParent = (d.updated || d.date || '').includes(selectedYear);
          const matchSub = d.subLayers && d.subLayers.some((s) => (s.year || s.updated || '').includes(selectedYear));
          if (!matchParent && !matchSub) return false;
        }
        if (selectedReg !== 'all') {
          const haystack = ((d.prov || '') + ' ' + (d.kab || '') + ' ' + (d.scope || '')).toLowerCase();
          if (!haystack.includes(selectedReg.toLowerCase()) && !(d.prov && d.prov.toLowerCase().includes('nasional'))) {
            return false;
          }
        }
        if (q) {
          const orgVal = d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '';
          const subText = d.subLayers ? d.subLayers.map((s) => s.name + ' ' + (s.label || '')).join(' ') : '';
          const haystack = (d.name + ' ' + (d.scope || '') + ' ' + orgVal + ' ' + subText).toLowerCase();
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

      let html = '';

      // 1. Subnav 5 Tabs
      html += `
        <div class="dash-cat-tabs" role="tablist" aria-label="Pilih Kategori IGT">
          ${TABS.map((t) => `
            <button type="button" class="dash-cat-tab ${t.key === currentCategory ? 'active' : ''}" data-dash-cat="${t.key}" role="tab" aria-selected="${t.key === currentCategory}">
              ${t.label}
            </button>
          `).join('')}
        </div>
      `;

      // 2. Filter Box (Pencarian, Tahun, Wilayah)
      html += `
        <div class="dash-cat-filter-box">
          <div class="dash-cat-search-wrap">
            <input type="search" class="dash-cat-search-input" id="dash-cat-search-field" placeholder="Cari nama IGT, sublayer, direktorat, wilayah..." value="${query.replace(/"/g, '&quot;')}">
          </div>
          <div class="dash-cat-dropdowns">
            <select class="dash-cat-select" id="dash-cat-year-select" aria-label="Filter Tahun">
              <option value="all" ${selectedYear === 'all' ? 'selected' : ''}>Semua tahun</option>
              <option value="2026" ${selectedYear === '2026' ? 'selected' : ''}>2026</option>
              <option value="2025" ${selectedYear === '2025' ? 'selected' : ''}>2025</option>
              <option value="2024" ${selectedYear === '2024' ? 'selected' : ''}>2024</option>
              <option value="2023" ${selectedYear === '2023' ? 'selected' : ''}>2023</option>
              <option value="2021" ${selectedYear === '2021' ? 'selected' : ''}>2021</option>
              <option value="2019" ${selectedYear === '2019' ? 'selected' : ''}>2019</option>
            </select>
            <select class="dash-cat-select" id="dash-cat-reg-select" aria-label="Filter Wilayah">
              <option value="all" ${selectedReg === 'all' ? 'selected' : ''}>Semua Wilayah</option>
              <option value="Kab. Sleman" ${selectedReg === 'Kab. Sleman' ? 'selected' : ''}>Kab. Sleman</option>
              <option value="Kab. Bantul" ${selectedReg === 'Kab. Bantul' ? 'selected' : ''}>Kab. Bantul</option>
              <option value="Kab. Kulon Progo" ${selectedReg === 'Kab. Kulon Progo' ? 'selected' : ''}>Kab. Kulon Progo</option>
              <option value="Kab. Gunungkidul" ${selectedReg === 'Kab. Gunungkidul' ? 'selected' : ''}>Kab. Gunungkidul</option>
              <option value="Kota Yogyakarta" ${selectedReg === 'Kota Yogyakarta' ? 'selected' : ''}>Kota Yogyakarta</option>
              <option value="Nasional" ${selectedReg === 'Nasional' ? 'selected' : ''}>Nasional</option>
            </select>
          </div>
        </div>
      `;

      // 3. Summary Count Label
      html += `
        <div class="dash-cat-summary">
          ${totalItems > 0
            ? `Menampilkan ${startIdx + 1}–${endIdx} dari ${totalItems} dataset · Halaman ${currentPage} dari ${totalPages} · Kategori ${catInfo.label}`
            : `Tidak ada dataset yang cocok dengan kriteria filter atau pencarian · Kategori ${catInfo.label}`
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
        pageItems.forEach((d) => {
          const hasSubs = Boolean(d.subLayers && d.subLayers.length > 0);
          const isExp = expandedIds.has(d.id) || Boolean(query && hasSubs && d.subLayers.some((s) => s.name.toLowerCase().includes(query.toLowerCase())));
          const cat = d.category;
          const badgeClass = cat === 'pertanahan' ? 'dash-cat-badge--pertanahan' :
                             cat === 'tata-ruang' ? 'dash-cat-badge--tataruang' :
                             cat === 'derivatif' ? 'dash-cat-badge--derivatif' :
                             'dash-cat-badge--lainnya';
          const badgeLabel = cat === 'pertanahan' ? 'Pertanahan' :
                             cat === 'tata-ruang' ? 'Tata Ruang' :
                             cat === 'derivatif' ? 'Derivatif' :
                             'K/L Lainnya';
          const org = d.direktorat || d.satker || d.ditjen || d.instansi || d.source || '—';
          const date = d.updated || d.date || '—';
          const iconHtml = cat === 'tata-ruang' ? ri('map-2-line') :
                           cat === 'derivatif' ? ri('stack-line') :
                           cat === 'lainnya' ? ri('global-line') :
                           ri('map-pin-line');

          html += `
            <div class="dash-card" data-id="${d.id}">
              <div class="dash-card-row">
                <div class="dash-card-left">
                  <div class="dash-card-header">
                    <div class="dash-card-title-wrap">
                      <span class="dash-card-icon dash-card-icon--${cat}">${iconHtml}</span>
                      <span class="dash-card-title">${d.name}</span>
                      <span class="dash-cat-badge ${badgeClass}">${badgeLabel}</span>
                    </div>
                  </div>
                </div>
                <div class="dash-card-actions">
                  ${hasSubs ? `
                    <button type="button" class="igt-chip igt-chip--multi-layer dash-chip-toggle" data-dash-toggle="${d.id}" aria-expanded="${isExp}">
                      <span class="igt-chip__text">Multi-Layer</span>
                      <span class="igt-chip__count">${d.subLayers.length} Layer</span>
                      <span class="igt-chip__caret" aria-hidden="true">${isExp ? '▴' : '▾'}</span>
                    </button>
                  ` : `
                    <button type="button" class="dash-btn-wms" data-action="wms" data-name="${d.name.replace(/"/g, '&quot;')}">WMS</button>
                    <button type="button" class="dash-btn-wfs" data-action="wfs" data-name="${d.name.replace(/"/g, '&quot;')}">WFS</button>
                  `}
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
                        <button type="button" class="dash-sub-btn dash-sub-btn--wfs" data-action="wfs" data-name="${sub.name.replace(/"/g, '&quot;')}">WFS</button>
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

      const yearSelect = rootEl.querySelector('#dash-cat-year-select');
      if (yearSelect) {
        yearSelect.addEventListener('change', (e) => {
          selectedYear = e.target.value;
          currentPage = 1;
          render();
        });
      }

      const regSelect = rootEl.querySelector('#dash-cat-reg-select');
      if (regSelect) {
        regSelect.addEventListener('change', (e) => {
          selectedReg = e.target.value;
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

      rootEl.querySelectorAll('[data-action]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          const act = btn.dataset.action;
          const name = btn.dataset.name;
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
  }

  return { dashboard, catalog, upload, dashboardCatalog };
})();

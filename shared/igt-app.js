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
  const yearOptions = (records) => [...new Set([...records.map(yearOf).filter((year) => year !== 'Tidak diketahui'), '2026', '2025', '2024', '2023'])].sort().reverse();
  const yearFilterOptions = (records) => '<option value="all" selected>Semua tahun</option>' + yearOptions(records).map((year) => '<option value="' + year + '">' + year + '</option>').join('');
  const statCard = (label, num, hint, icon, cls, id) =>
    `<div class="card stat"><div><div class="label">${label}</div><div class="num" id="${id}">${num}</div>` +
    `<div class="hint">${hint}</div></div><div class="stat-icon${cls ? ' ' + cls : ''}">${icon}</div></div>`;

  const DETAIL_URL = {
    utama: '../../operator/igt-utama-detail/index.html',
    derivatif: '../../operator/layer-derivatif-detail/index.html',
  };
  const BIDANG_WORKFLOW_URL = '../derivatif-bidang/index.html';

  function managementCategories(role) {
    const availableCategories = CATEGORY_ORDER.filter((key) => IgtData.canUpload(role, key));
    // Superadmin can review IGT Utama and derivatif, but may only upload IGT Lainnya.
    if (role === 'superadmin') return ['igt-utama', 'derivatif', ...availableCategories.filter((key) => key === 'lainnya')];
    if (role === 'superadmin2') return ['semua', 'igt-utama', 'derivatif', 'lainnya'];
    return [
      ...(availableCategories.some((key) => key === 'pertanahan' || key === 'tata-ruang') ? ['igt-utama'] : []),
      ...availableCategories.filter((key) => key !== 'pertanahan' && key !== 'tata-ruang'),
    ];
  }

  const managementLabel = (key) => (key === 'semua' ? 'Semua Kategori' : key === 'igt-utama' ? 'IGT Utama' : CATEGORIES[key].label);
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
    const catalogButtons = categories.map((key) => '<a class="btn btn-soft menu-btn" href="../' + CATEGORIES[key].slug + '/index.html">' + (CATALOG_ICON[key] || ri('stack-line')) + '<span>' + CATEGORIES[key].label + '</span></a>').join('');
    const manageButtons = managementCategories(role)
      .map((key) => '<a class="btn btn-primary menu-btn" id="upload-button-' + key + '" href="../upload-data/index.html?tab=' + key + '">' + (MANAGEMENT_ICON[key] || ri('database-2-line')) + '<span>' + managementLabel(key) + '</span></a>')
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
    if (!IgtData.canView(role, category)) {
      view.innerHTML = '<div class="notice"><strong>Akses ditolak</strong>' + CATEGORIES[category].label + ' tidak tersedia untuk role ini.</div>';
      return;
    }
    const config = CATEGORIES[category];
    const datasets = IgtData.loadRecords().filter((r) => r.category === category && IgtData.inCatalog(r));
    let query = '';
    let sortKey = '';
    let sortDirection = 1;
    view.innerHTML =
      '<div class="notice"><strong>Isi katalog</strong>' + config.rule + ' Tombol WMS dan WFS adalah simulasi; belum ada layanan nyata yang terhubung.</div>' +
      '<div class="catalog-controls"><div class="field catalog-search"><label for="catalog-search">PENCARIAN</label><input id="catalog-search" type="search" placeholder="Cari nama IGT..."></div>' +
      '<div class="field year-filter"><label for="catalog-year-filter">TAHUN</label><select id="catalog-year-filter">' + yearFilterOptions(datasets) + '</select></div></div>' +
      '<section class="card"><div class="card-head"><div><h2>' + config.noun.charAt(0).toUpperCase() + config.noun.slice(1) + '</h2><p id="catalog-count"></p></div></div>' +
      '<div class="table-wrap"><table class="stack"><thead><tr><th><button type="button" class="sort-header" data-sort="name">Nama IGT <span aria-hidden="true">↕</span></button></th><th><button type="button" class="sort-header" data-sort="ditjen">Ditjen <span aria-hidden="true">↕</span></button></th><th><button type="button" class="sort-header" data-sort="updated">' +
      (config.integration ? 'Tanggal Terintegrasi' : category === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Upload') +
      ' <span aria-hidden="true">↕</span></button></th><th>Tampilkan WMS</th><th>Tampilkan WFS</th></tr></thead><tbody id="catalog-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden></div></section>';
    function render() {
      const q = query.toLowerCase();
      const year = $('#catalog-year-filter').value;
      const filtered = datasets.filter((d) => (year === 'all' || yearOf(d) === year) && (d.name + ' ' + (d.ditjen || d.source || '') + ' ' + d.id).toLowerCase().includes(q));
      const shown = [...filtered];
      if (sortKey) {
        const value = (d) => sortKey === 'name' ? d.name : sortKey === 'ditjen' ? (d.ditjen || d.source || '') : sortKey === 'updated' ? (d.updated || d.date || '') : d.name;
        shown.sort((a, b) => String(value(a)).localeCompare(String(value(b)), 'id', { numeric: true }) * sortDirection);
      }
      document.querySelectorAll('.sort-header').forEach((btn) => {
        const active = btn.dataset.sort === sortKey;
        btn.setAttribute('aria-sort', active ? (sortDirection === 1 ? 'ascending' : 'descending') : 'none');
        btn.querySelector('span').textContent = active ? (sortDirection === 1 ? '↑' : '↓') : '↕';
      });
      $('#catalog-rows').innerHTML = shown.map((d) =>
        '<tr><td data-label="Nama IGT">' + d.name + '</td><td data-label="Ditjen">' + (d.ditjen || d.source || '—') + '</td><td data-label="Tanggal">' + (d.updated || d.date || '—') + '</td>' +
        '<td data-label="Tampilkan WMS">' + button('btn-soft', 'wms', d.id, ri('map-2-line') + '<span>WMS</span>') + '</td><td data-label="Tampilkan WFS">' + button('btn-soft', 'wfs', d.id, ri('stack-line') + '<span>WFS</span>') + '</td></tr>'
      ).join('');
      setText('catalog-count', shown.length + ' dari ' + datasets.length + ' dataset · ' + (year === 'all' ? 'semua tahun' : 'tahun ' + year));
      const empty = $('#empty-state');
      empty.hidden = shown.length > 0;
      empty.textContent = datasets.length === 0 ? 'Belum ada ' + config.noun + ' pada ' + config.label + '.' : 'Tidak ada dataset yang cocok dengan filter tahun atau pencarian.';
    }
    $('#catalog-search').addEventListener('input', (event) => { query = event.target.value; render(); });
    $('#catalog-year-filter').addEventListener('change', render);
    document.querySelectorAll('.sort-header').forEach((btn) => btn.addEventListener('click', () => {
      if (sortKey === btn.dataset.sort) sortDirection *= -1;
      else { sortKey = btn.dataset.sort; sortDirection = 1; }
      render();
    }));
    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const dataset = datasets.find((d) => d.id === target.dataset.id);
      if (!dataset) return;
      if (target.dataset.action === 'wms') alert(WMS_MESSAGE(dataset.name));
      else if (target.dataset.action === 'wfs') alert(WFS_MESSAGE(dataset.name));
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
        `<div class="dropzone"><div class="big">⇧</div><strong>Upload data atribut bidang</strong>` +
        `<p>Unggah tabel atribut yang terhubung dengan ID bidang.</p><button class="btn btn-primary" data-action="upload">Pilih file</button></div>` +
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
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">${ri('upload-cloud-2-line')}<span>Upload Derivatif</span></button></div>` +
          `<div class="notice"><strong>Catatan</strong>Unggahan Admin langsung berstatus Disetujui. Pengajuan Operator dan Umum berstatus Diajukan sampai diputuskan.</div>`
        );
      }
      if (role === 'umum') {
        return (
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">${ri('upload-cloud-2-line')}<span>Upload Derivatif</span></button></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan Umum berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin. Anda hanya melihat pengajuan Anda sendiri.</div>`
        );
      }
      if (role === 'operator') {
        return (
          `<div class="toolbar"><a class="btn btn-primary" href="${LEGACY}06-derivative-kawasan.html">${ri('upload-cloud-2-line')}<span>Upload Derivatif Kawasan</span></a>` +
          `<a class="btn btn-primary" href="${BIDANG_WORKFLOW_URL}">${ri('upload-cloud-2-line')}<span>Upload Derivatif Bidang</span></a></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin.</div>`
        );
      }
      return (
        `<div class="notice"><strong>Catatan</strong>Superadmin tidak mengunggah derivatif. Gunakan panel ini untuk menyetujui atau menolak pengajuan.</div>`
      );
    }
    return (
      `<div class="toolbar"><button class="btn btn-primary" data-action="upload-lainnya">${ri('upload-cloud-2-line')}<span>Upload layer</span></button></div>` +
      `<div class="notice"><strong>Catatan</strong>Penambahan dan pengaturan layer dilakukan langsung melalui QGIS. Layer eksternal tidak memakai status persetujuan.</div>`
    );
  }

  // Row actions depend on category, status and role. Catalog actions (WMS/WFS) never appear here.
  function rowActions(role, r) {
    const isSuper = role === 'superadmin' || role === 'superadmin2';
    const reviewer = role === 'admin' || isSuper;
    const kind = CATEGORIES[r.category].detail;
    const extras = [button('btn-soft', 'show-qgis', r.id, ri('eye-line') + '<span>Tampilkan</span>')];
    if (r.category === 'lainnya') {
      if (isSuper) extras.push(button('btn-danger', 'delete', r.id, ri('delete-bin-line') + '<span>Hapus</span>'));
      return toolbar(...extras);
    }
    if (kind === 'utama') {
      if (reviewer && r.status === 'Terkompilasi') {
        extras.push(button('btn-primary', 'topology', r.id, ri('focus-3-line') + '<span>Verifikasi Topologi</span>'));
        if (isSuper) extras.push(button('btn-primary', 'approve-integration', r.id, ri('check-line') + '<span>Setujui Integrasi</span>'));
      }
      if ((role === 'operator' || role === 'superadmin2') && r.status === 'Revisi') extras.push(button('btn-soft', 'revision', r.id, ri('edit-line') + '<span>Revisi</span>'));
    } else if (reviewer && r.status === 'Diajukan') {
      extras.push(button('btn-primary', 'approve', r.id, ri('check-line') + '<span>Setujui</span>'), button('btn-soft', 'reject', r.id, ri('close-line') + '<span>Tolak</span>'));
    }
    return toolbar(...extras);
  }

  // Submission management: summary, upload controls and submission table for the selected category.
  function upload(role) {
    const noUploadMenu = role === 'superadmin2';
    const categories = managementCategories(role);
    const allRecords = IgtData.loadRecords();
    const records = (role === 'superadmin' || role === 'superadmin2')
      ? allRecords.filter((r) => ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya'].includes(r.category))
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
    let statusTab = params.get('status') || (noUploadMenu ? 'Diproses' : tab === 'igt-utama' && role === 'operator' ? 'Revisi' : tab === 'igt-utama' ? 'Diproses' : tab === 'derivatif' && (role === 'operator' || role === 'umum') ? 'Semua' : tab === 'derivatif' ? 'Diproses' : 'Semua');
    let nextDerivative = 9;

    const isMainInit = tab === 'igt-utama';
    const pageTitle = noUploadMenu ? 'Manajemen Data' : managementLabel(tab);
    const pageDesc = noUploadMenu
      ? 'Kelola proses, revisi perbaikan, dan status persetujuan data geospasial tanpa menu upload (menu Upload Data tersedia di Dashboard).'
      : isMainInit ? 'Kelola pengajuan IGT Pertanahan dan IGT Tata Ruang dari satu halaman.' : UPLOAD_TEXT[tab];
    document.title = pageTitle + ' · IGT-PR';
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
        ? `<div class="card-head"><div><h2 id="tab-heading">Daftar Pengajuan & Status Data</h2><p id="tab-description">Filter berdasarkan kategori IGT dan status pemrosesan data.</p></div></div>` +
          `<div id="submission-category-tabs" class="tabs" style="margin-bottom:8px">` +
          categories.map((c) => `<button class="tab" data-category-tab="${c}">${managementLabel(c)}</button>`).join('') +
          `</div>`
        : `<div class="card-head"><div><h2 id="tab-heading"></h2><p id="tab-description"></p></div></div>` +
          `<div id="upload-panel"></div>` +
          `<div id="igt-upload-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="igt-upload-modal-title" style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto">` +
          `<section class="card" style="width:min(760px,100%);max-height:90vh;overflow:auto;margin:auto"><div class="card-head"><div><h2 id="igt-upload-modal-title">Upload IGT</h2><p id="igt-upload-modal-description"></p></div><button type="button" class="btn btn-soft" data-close-upload-modal>✕ Tutup</button></div><div id="igt-upload-modal-content"></div></section></div>`) +
      `<div id="submission-status-tabs" class="tabs" data-status-tabs></div>` +
      `<div class="card-head submissions-head"><div><h2>Pengajuan</h2><p id="submission-count"></p></div></div>` +
      `<div class="table-wrap"><table class="stack"><thead><tr><th>ID Pengajuan</th><th>Layer Target</th><th id="submission-date-heading">Tanggal Upload</th><th>Status</th><th>Aksi</th></tr></thead>` +
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
      const isAll = tab === 'semua';
      setText('submission-date-heading', isMain ? 'Tanggal Terintegrasi' : tab === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Upload');
      if (noUploadMenu) {
        setText('tab-heading', isAll ? 'Semua Kategori IGT' : managementLabel(tab));
        setText('tab-description', 'Pantau proses verifikasi, revisi perbaikan, dan persetujuan integrasi data geospasial.');
        const catEl = $('#submission-category-tabs');
        if (catEl) {
          catEl.querySelectorAll('[data-category-tab]').forEach((t) => {
            t.classList.toggle('active', t.dataset.categoryTab === tab);
            t.setAttribute('aria-selected', t.dataset.categoryTab === tab);
          });
        }
      } else {
        setText('tab-heading', isMain ? 'IGT Utama' : CATEGORIES[tab].label);
        setText('tab-description', isMain ? 'Kelola pengajuan IGT Pertanahan dan IGT Tata Ruang dari satu halaman.' : UPLOAD_TEXT[tab]);
        $('#upload-panel').innerHTML = isMain
          ? (role === 'superadmin'
            ? `<div class="notice"><strong>Catatan</strong>Superadmin hanya memeriksa topologi dan menyetujui integrasi IGT Utama. Unggah data IGT Utama dilakukan oleh role yang berwenang.</div>`
            : `<div class="toolbar"><button class="btn btn-primary" data-open-upload-modal="pertanahan">${ri('upload-cloud-2-line')}<span>Upload Data Pertanahan</span></button><button class="btn btn-primary" data-open-upload-modal="tata-ruang">${ri('upload-cloud-2-line')}<span>Upload Data Tata Ruang</span></button></div>`)
          : uploadPanel(role, tab);
      }
      const own = records.filter((r) => isAll ? true : isMain ? (r.category === 'pertanahan' || r.category === 'tata-ruang') : r.category === tab);
      const statusOptions = noUploadMenu
        ? ['Diproses', 'Revisi', 'Disetujui', 'Semua']
        : isMain
          ? (role === 'operator'
            ? ['Revisi', 'Diproses', 'Disetujui', 'Semua']
            : ['Diproses', 'Disetujui', 'Revisi', 'Semua'])
          : tab === 'derivatif'
            ? (role === 'operator' || role === 'umum'
              ? ['Semua', 'Diproses', 'Disetujui']
              : ['Diproses', 'Disetujui', 'Semua'])
            : [];
      const showStatusTabs = statusOptions.length > 0;
      const statusEl = $('#submission-status-tabs');
      const statusLabel = (s) => (noUploadMenu && s === 'Diproses' ? 'Proses' : noUploadMenu && s === 'Revisi' ? 'Revisi Perbaikan' : s);
      statusEl.innerHTML = showStatusTabs
        ? statusOptions.map((s) => `<button class="tab" data-status-tab="${s}">${statusLabel(s)}</button>`).join('')
        : '';
      statusEl.hidden = !showStatusTabs;
      if (showStatusTabs && !statusOptions.includes(statusTab)) statusTab = statusOptions[0];
      statusEl.querySelectorAll('[data-status-tab]').forEach((t) => {
        t.classList.toggle('active', t.dataset.statusTab === statusTab);
        t.setAttribute('aria-selected', t.dataset.statusTab === statusTab);
      });
      const statusMatches = (r) => {
        if (!showStatusTabs || statusTab === 'Semua') return true;
        if (statusTab === 'Revisi') return noUploadMenu ? ['Revisi', 'Ditolak'].includes(r.status) : r.status === 'Revisi';
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
          return (
            `<tr data-category="${r.category}"><td data-label="ID Pengajuan">${id}</td><td data-label="Layer Target">${r.name}</td>` +
            `<td data-label="${tab === 'igt-utama' ? 'Tanggal Terintegrasi' : tab === 'derivatif' ? 'Tanggal Disetujui' : 'Tanggal Upload'}">${tab === 'igt-utama' || tab === 'derivatif' || isAll ? (r.updated || r.date || "—") : r.date}</td><td data-label="Status">${badge(r.status)}</td>` +
            `<td data-label="Aksi" class="action-cell">${rowActions(role, r)}</td></tr>`
          );
        })
        .join('');
      setText('submission-count', `${displayed.length} dari ${own.length} pengajuan pada ${managementLabel(tab)}.`);
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
        $('#igt-upload-modal-title').textContent = category === 'pertanahan' ? 'Upload IGT Pertanahan' : 'Upload IGT Tata Ruang';
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
        alert('Simulasi: pilih file data untuk diunggah (' + (tab === 'igt-utama' ? ($('#igt-upload-modal-title').textContent || 'IGT Utama') : CATEGORIES[tab].label) + ').');
      }
      else if (action === 'validate') {
        if (role === 'superadmin') {
          alert('Superadmin tidak memiliki akses untuk mengunggah IGT Utama.');
          return;
        }
        alert('Parameter valid. Proses ini masih berupa prototipe UI.');
      }
      else if (action === 'upload-lainnya') alert('Upload layer dan konfigurasi data dilakukan langsung melalui QGIS.');
      else if (action === 'revision') alert('Simulasi: buka formulir revisi untuk pengajuan ' + id + '.');
      else if (action === 'show-qgis') alert('Simulasi: layer ' + (record ? record.name : id) + ' akan ditampilkan di QGIS. Integrasi QGIS belum aktif pada prototipe ini.');
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

  return { dashboard, catalog, upload };
})();

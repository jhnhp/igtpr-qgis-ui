// Page logic for the role pages: navigation, dashboard, IGT catalogs and Upload Data.
// Needs shared/igt-data.js. Every QGIS-related action is a simulation (alert/confirm), nothing is sent anywhere.
const IgtApp = (() => {
  const { CATEGORIES, CATEGORY_ORDER, ROLES } = IgtData;
  const $ = (selector) => document.querySelector(selector);

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
  const statCard = (label, num, hint, icon, cls, id) =>
    `<div class="card stat"><div><div class="label">${label}</div><div class="num" id="${id}">${num}</div>` +
    `<div class="hint">${hint}</div></div><div class="stat-icon${cls ? ' ' + cls : ''}">${icon}</div></div>`;

  const DETAIL_URL = {
    utama: '../../operator/igt-utama-detail/index.html',
    derivatif: '../../operator/layer-derivatif-detail/index.html',
  };

  // ----------------------------------------------------------------- dashboard

  // Repository overview: how many datasets are compiled and integrated. No upload controls here.
  function dashboard(role) {
    // The Dashboard has no menu bar: navigation is the buttons below the overview.
    // Terkompilasi / Terintegrasi only exist for IGT Pertanahan and IGT Tata Ruang.
    const records = IgtData.loadRecords().filter((r) => IgtData.canView(role, r.category));
    const staged = IgtData.integrationRecords(records);
    const compiled = IgtData.countByStatus(staged, 'Terkompilasi');
    const integrated = IgtData.countByStatus(staged, 'Terintegrasi');
    const categories = CATEGORY_ORDER.filter((key) => IgtData.canView(role, key));

    const rows = categories
      .filter((key) => CATEGORIES[key].integration)
      .map((key) => {
        const own = records.filter((r) => r.category === key);
        return (
          `<tr><td data-label="Kategori">${CATEGORIES[key].label}</td>` +
          `<td data-label="Terkompilasi">${IgtData.countByStatus(own, 'Terkompilasi')}</td>` +
          `<td data-label="Terintegrasi">${IgtData.countByStatus(own, 'Terintegrasi')}</td></tr>`
        );
      })
      .join('');

    // One button per catalog the role may open, then a single button for Upload Data.
    const catalogButtons = categories
      .map((key) => `<a class="btn btn-soft menu-btn" href="../${CATEGORIES[key].slug}/index.html">▧ ${CATEGORIES[key].label}</a>`)
      .join('');

    $('#view').innerHTML =
      `<div class="grid stats">` +
      statCard('Terkompilasi', compiled, 'Menunggu integrasi', '▤', 'amber', 'count-compiled') +
      statCard('Terintegrasi', integrated, 'Pertanahan dan Tata Ruang', '✓', 'green', 'count-integrated') +
      `</div>` +
      `<section class="card"><div class="card-head"><div><h2>Ringkasan status</h2>` +
      `<p>Dihitung dari data contoh. Satu catatan mewakili satu dataset.</p></div></div>` +
      `<div class="table-wrap"><table class="compact"><thead><tr><th>Kategori</th><th>Terkompilasi</th><th>Terintegrasi</th></tr></thead>` +
      `<tbody id="category-rows">${rows}</tbody></table></div>` +
      `<p class="summary-note">Hanya IGT Pertanahan dan IGT Tata Ruang melewati tahap Terkompilasi dan Terintegrasi. ` +
      `IGT Derivatif tersedia setelah Disetujui, dan semua layer IGT Lainnya yang diunggah langsung tersedia.</p></section>` +
      `<section class="card"><div class="card-head"><div><h2>Lihat peta IGT</h2><p>Buka katalog dataset yang sudah tersedia.</p></div></div>` +
      `<div class="menu-buttons" id="catalog-buttons">${catalogButtons}</div>` +
      `<div class="card-head menu-upload-head"><div><h2>Kelola data</h2><p>Unggah data baru dan pantau status pengajuan.</p></div></div>` +
      `<div class="menu-buttons"><a class="btn btn-primary menu-btn" id="upload-button" href="../upload-data/index.html">↑ Upload Data</a></div>` +
      (ROLES[role].modelBuilder === false
        ? ''
        : `<div class="menu-buttons model-builder-buttons"><a class="btn btn-primary menu-btn" id="model-builder-button" href="../../../shared/model-builder/index.html?role=${role}">⚙ Model Builder</a></div>`) +
      `</section>`;
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
      view.innerHTML = `<div class="notice"><strong>Akses ditolak</strong>${CATEGORIES[category].label} tidak tersedia untuk role ini.</div>`;
      return;
    }
    const config = CATEGORIES[category];
    const datasets = IgtData.loadRecords().filter((r) => r.category === category && IgtData.inCatalog(r));
    let query = '';
    let sortKey = '';
    let sortDirection = 1;

    view.innerHTML =
      `<div class="notice"><strong>Isi katalog</strong>${config.rule} ` +
      `Tombol WMS dan WFS adalah simulasi; belum ada layanan nyata yang terhubung.</div>` +
      `<section class="card"><div class="card-head"><div><h2>${config.noun.charAt(0).toUpperCase() + config.noun.slice(1)}</h2><p id="catalog-count"></p></div></div>` +
      `<div class="field catalog-search"><label for="catalog-search">PENCARIAN</label><input id="catalog-search" type="search" placeholder="Cari nama IGT..."></div>` +
      `<div class="table-wrap"><table class="stack"><thead><tr><th><button type="button" class="sort-header" data-sort="name">Nama IGT <span aria-hidden="true">↕</span></button></th><th><button type="button" class="sort-header" data-sort="ditjen">Ditjen <span aria-hidden="true">↕</span></button></th><th><button type="button" class="sort-header" data-sort="updated">Tanggal Update <span aria-hidden="true">↕</span></button></th><th>Tampilkan WMS</th><th>Tampilkan WFS</th></tr></thead>` +
      `<tbody id="catalog-rows"></tbody></table></div>` +
      `<div class="empty-state" id="empty-state" hidden></div></section>`;

    function render() {
      const q = query.toLowerCase();
      const shown = datasets.filter((d) => (d.name + ' ' + (d.ditjen || '') + ' ' + d.id).toLowerCase().includes(q));
      if (sortKey) {
        const value = (d) => sortKey === 'name' ? d.name
          : sortKey === 'ditjen' ? (d.ditjen || d.source || '')
          : sortKey === 'updated' ? (d.updated || '')
          : d.name;
        shown.sort((a, b) => String(value(a)).localeCompare(String(value(b)), 'id', { numeric: true }) * sortDirection);
      }
      document.querySelectorAll('.sort-header').forEach((btn) => {
        const active = btn.dataset.sort === sortKey;
        btn.setAttribute('aria-sort', active ? (sortDirection === 1 ? 'ascending' : 'descending') : 'none');
        btn.querySelector('span').textContent = active ? (sortDirection === 1 ? '↑' : '↓') : '↕';
      });
      $('#catalog-rows').innerHTML = shown
        .map((d) => {
          return (
            `<tr><td data-label="Nama IGT"><div class="primary-cell">${d.name}</div></td>` +
            `<td data-label="Ditjen">${d.ditjen || "—"}</td>` +
            `<td data-label="Tanggal Update">${d.updated || "—"}</td>` +
            `<td data-label="Tampilkan WMS">${button('btn-soft', 'wms', d.id, '▧ WMS', ` aria-label="Tampilkan WMS untuk ${d.name}"`)}</td>` +
            `<td data-label="Tampilkan WFS">${button('btn-soft', 'wfs', d.id, '▤ WFS', ` aria-label="Tampilkan WFS untuk ${d.name}"`)}</td></tr>`
          );
        })
        .join('');
      setText('catalog-count', `${datasets.length} ${config.noun} di ${config.label}.`);
      const empty = $('#empty-state');
      empty.hidden = shown.length > 0;
      empty.textContent = datasets.length === 0
        ? `Belum ada ${config.noun} pada ${config.label}.`
        : 'Tidak ada dataset yang cocok dengan pencarian.';
    }

    $('#catalog-search').addEventListener('input', (event) => {
      query = event.target.value;
      render();
    });
    document.querySelectorAll('.sort-header').forEach((btn) => {
      btn.addEventListener('click', () => {
        if (sortKey === btn.dataset.sort) sortDirection *= -1;
        else { sortKey = btn.dataset.sort; sortDirection = 1; }
        render();
      });
    });
    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const dataset = datasets.find((d) => d.id === target.dataset.id);
      if (target.dataset.action === 'wms') alert(WMS_MESSAGE(dataset.name));
      else if (target.dataset.action === 'wfs') alert(WFS_MESSAGE(dataset.name));
    });
    render();
  }

  // --------------------------------------------------------------- upload data

  const UPLOAD_TEXT = {
    pertanahan: 'Muat baseline bidang atau unggah atribut baru, lalu pantau status pengajuan.',
    'tata-ruang': 'Unggah geometri dan atribut kawasan, lalu pantau status verifikasinya.',
    derivatif: 'Ajukan layer derivatif dan pantau keputusan persetujuannya.',
    lainnya: 'Kelola layer IGT dari sumber eksternal. Data yang diunggah Superadmin langsung tersedia tanpa proses persetujuan.',
  };

  const LEGACY = '../../../legacy/';

  // Upload controls differ per category and role. Baseline exists only for IGT Pertanahan.
  function uploadPanel(role, category) {
    if (category === 'pertanahan') {
      return (
        `<div class="grid quick-grid"><div class="quick"><div class="q-icon">▦</div><b>Load Baseline</b><p>Muat layer bidang acuan dari layanan yang tersedia.</p>` +
        `<button class="btn btn-primary" style="margin-top:12px" data-action="load-baseline">Muat baseline</button></div>` +
        `<div class="quick"><div class="q-icon">↑</div><b>Upload Data</b><p>Unggah tabel atribut yang terhubung dengan ID bidang.</p>` +
        `<button class="btn btn-primary" style="margin-top:12px" data-action="upload">Pilih file</button></div></div>` +
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
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">↑ Upload Derivatif</button></div>` +
          `<div class="notice"><strong>Catatan</strong>Unggahan Admin langsung berstatus Disetujui. Pengajuan Operator berstatus Diajukan sampai diputuskan.</div>`
        );
      }
      if (role === 'umum') {
        return (
          `<div class="toolbar"><button class="btn btn-primary" data-action="upload-derivatif">↑ Upload Derivatif</button></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan Umum berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin. Anda hanya melihat pengajuan Anda sendiri.</div>`
        );
      }
      if (role === 'operator') {
        return (
          `<div class="toolbar"><a class="btn btn-primary" href="${LEGACY}06-derivative-kawasan.html">＋ Derivative Kawasan</a>` +
          `<a class="btn btn-soft" href="${LEGACY}07-derivative-bidang.html">＋ Derivative Bidang</a></div>` +
          `<div class="notice"><strong>Catatan</strong>Pengajuan berstatus Diajukan sampai disetujui atau ditolak oleh Admin atau Superadmin.</div>`
        );
      }
      return `<div class="notice"><strong>Panel verifikasi</strong>Setujui atau tolak pengajuan yang berstatus Diajukan.</div>`;
    }
    return (
      `<div class="toolbar"><button class="btn btn-primary" data-action="upload-lainnya">＋ Upload layer</button></div>` +
      `<div class="notice"><strong>Catatan</strong>Penambahan dan pengaturan layer dilakukan langsung melalui QGIS. Layer eksternal tidak memakai status persetujuan.</div>`
    );
  }

  // Row actions depend on category, status and role. Catalog actions (WMS/WFS) never appear here.
  function rowActions(role, r) {
    const reviewer = role === 'admin' || role === 'superadmin';
    const kind = CATEGORIES[r.category].detail;
    if (r.category === 'lainnya') {
      return role === 'superadmin' ? toolbar(button('btn-danger', 'delete', r.id, 'Hapus')) : '';
    }
    const detail = r.n === undefined
      ? button('btn-soft', 'detail-sim', r.id, 'Detail')
      : link(`${DETAIL_URL[kind]}?id=${r.n}&role=${role}`, 'Detail');
    const extras = [];
    if (kind === 'utama') {
      if (reviewer && r.status === 'Terkompilasi') extras.push(button('btn-primary', 'topology', r.id, '⌁ Verifikasi Topologi'));
      if (role === 'operator' && r.status === 'Revisi') extras.push(button('btn-soft', 'revision', r.id, '✎ Revisi'));
    } else if (reviewer && r.status === 'Diajukan') {
      extras.push(button('btn-primary', 'approve', r.id, '✓ Setujui'), button('btn-soft', 'reject', r.id, '✕ Tolak'));
    }
    return toolbar(...extras, detail);
  }

  // Submission management: summary, one tab per authorized category, upload controls and submission table.
  function upload(role) {
    const availableCategories = CATEGORY_ORDER.filter((key) => IgtData.canUpload(role, key));
    const categories = [
      ...(availableCategories.some((key) => key === 'pertanahan' || key === 'tata-ruang') ? ['igt-utama'] : []),
      ...availableCategories.filter((key) => key !== 'pertanahan' && key !== 'tata-ruang'),
    ];
    const records = IgtData.submissionsFor(role, IgtData.loadRecords());
    const params = new URLSearchParams(location.search);
    const requested = params.get('tab');
    let tab = categories.includes(requested) ? requested : (requested === 'pertanahan' || requested === 'tata-ruang') && categories.includes('igt-utama') ? 'igt-utama' : categories[0];
    let statusTab = params.get('status') || 'Semua';
    let nextDerivative = 9;

    $('#view').innerHTML =
      `<div class="grid stats">` +
      statCard('Total pengajuan', '', 'Semua kategori', '▦', '', 'count-total') +
      statCard('Dalam proses', '', 'Proses atau Diajukan', '◷', 'amber', 'count-process') +
      statCard('Menunggu integrasi', '', 'Terkompilasi', '▤', '', 'count-waiting') +
      statCard('Perlu perhatian', '', 'Revisi, Ditolak, atau Kadaluwarsa', '!', 'red', 'count-attention') +
      `</div><section class="card"><div class="tabs" data-tabs>` +
      categories.map((key) => `<button class="tab" data-tab="${key}">${key === 'igt-utama' ? 'IGT Utama' : CATEGORIES[key].label}</button>`).join('') +
      `</div><div class="card-head"><div><h2 id="tab-heading"></h2><p id="tab-description"></p></div></div>` +
      `<div id="upload-panel"></div>` +
      `<div id="igt-upload-modal" class="modal-backdrop" hidden role="dialog" aria-modal="true" aria-labelledby="igt-upload-modal-title" style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:none;align-items:center;justify-content:center;padding:20px;overflow:auto">` +
      `<section class="card" style="width:min(760px,100%);max-height:90vh;overflow:auto;margin:auto"><div class="card-head"><div><h2 id="igt-upload-modal-title">Upload IGT</h2><p id="igt-upload-modal-description"></p></div><button type="button" class="btn btn-soft" data-close-upload-modal>✕ Tutup</button></div><div id="igt-upload-modal-content"></div></section></div>` +
      `<div id="submission-status-tabs" class="tabs" data-status-tabs></div>`
      `<div class="card-head submissions-head"><div><h2>Pengajuan</h2><p id="submission-count"></p></div></div>` +
      `<div class="table-wrap"><table class="stack"><thead><tr><th>ID Pengajuan</th><th>Layer Target</th><th>Tanggal Upload</th><th>Status</th><th>Aksi</th></tr></thead>` +
      `<tbody id="submission-rows"></tbody></table></div><div class="empty-state" id="empty-state" hidden>Belum ada pengajuan pada kategori ini.</div></section>`;

    function renderCounts() {
      const count = (...statuses) => records.filter((r) => statuses.includes(r.status)).length;
      setText('count-total', records.length);
      setText('count-process', count('Proses', 'Diajukan'));
      setText('count-waiting', count('Terkompilasi'));
      setText('count-attention', count('Revisi', 'Ditolak', 'Kadaluwarsa'));
    }

    function render() {
      document.querySelectorAll('[data-tab]').forEach((t) => {
        t.classList.toggle('active', t.dataset.tab === tab);
        t.setAttribute('aria-selected', t.dataset.tab === tab);
      });
      const isMain = tab === 'igt-utama';
      setText('tab-heading', isMain ? 'IGT Utama' : CATEGORIES[tab].label);
      setText('tab-description', isMain ? 'Kelola pengajuan IGT Pertanahan dan IGT Tata Ruang dari satu tab.' : UPLOAD_TEXT[tab]);
      $('#upload-panel').innerHTML = isMain
        ? `<div class="grid quick-grid"><div class="quick"><div class="q-icon">▦</div><b>IGT Pertanahan</b><p>Muat baseline bidang atau unggah atribut baru.</p><button class="btn btn-primary" data-open-upload-modal="pertanahan">Upload IGT Pertanahan</button></div><div class="quick"><div class="q-icon">▧</div><b>IGT Tata Ruang</b><p>Unggah geometri dan atribut kawasan.</p><button class="btn btn-primary" data-open-upload-modal="tata-ruang">Upload IGT Tata Ruang</button></div></div>`
        : uploadPanel(role, tab);
      const own = records.filter((r) => isMain ? (r.category === 'pertanahan' || r.category === 'tata-ruang') : r.category === tab);
      const statusOptions = isMain
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
          return (
            `<tr data-category="${r.category}"><td data-label="ID Pengajuan">${id}</td><td data-label="Layer Target">${r.name}</td>` +
            `<td data-label="Tanggal Upload">${r.date}</td><td data-label="Status">${badge(r.status)}</td>` +
            `<td data-label="Aksi" class="action-cell">${rowActions(role, r)}</td></tr>`
          );
        })
        .join('');
      setText('submission-count', `${displayed.length} dari ${own.length} pengajuan pada ${isMain ? 'IGT Utama' : CATEGORIES[tab].label}.`);
      $('#empty-state').hidden = displayed.length > 0;
      renderCounts();
    }

    document.querySelectorAll('[data-tab]').forEach((t) =>
      t.addEventListener('click', () => {
        tab = t.dataset.tab;
        statusTab = 'Semua';
        try {
          history.replaceState(null, '', '?tab=' + tab);
        } catch (e) {
          /* file:// previews may refuse; the tab still switches */
        }
        render();
      }),
    );
    $('#submission-status-tabs').addEventListener('click', (event) => {
      const target = event.target.closest('[data-status-tab]');
      if (!target) return;
      statusTab = target.dataset.statusTab;
      render();
    });

    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const { action, id } = target.dataset;
      const record = records.find((r) => r.id === id);
      if (target.dataset.openUploadModal) {
        const category = target.dataset.openUploadModal;
        const modal = $('#igt-upload-modal');
        $('#igt-upload-modal-title').textContent = category === 'pertanahan' ? 'Upload IGT Pertanahan' : 'Upload IGT Tata Ruang';
        $('#igt-upload-modal-description').textContent = category === 'pertanahan' ? 'Muat baseline atau unggah atribut bidang.' : 'Unggah geometri dan atribut kawasan.';
        $('#igt-upload-modal-content').innerHTML = uploadPanel(role, category);
        modal.hidden = false;
        modal.style.display = 'flex';
        return;
      }
      if (target.hasAttribute('data-close-upload-modal') || target.id === 'igt-upload-modal') {
        const modal = $('#igt-upload-modal');
        modal.hidden = true;
        modal.style.display = 'none';
        return;
      }
      if (action === 'load-baseline') alert('Simulasi: pilih layer baseline dari QGIS.');
      else if (action === 'upload') alert('Simulasi: pilih file data untuk diunggah (' + (tab === 'igt-utama' ? ($('#igt-upload-modal-title').textContent || 'IGT Utama') : CATEGORIES[tab].label) + ').');
      else if (action === 'validate') alert('Parameter valid. Proses ini masih berupa prototipe UI.');
      else if (action === 'upload-lainnya') alert('Upload layer dan konfigurasi data dilakukan langsung melalui QGIS.');
      else if (action === 'revision') alert('Simulasi: buka formulir revisi untuk pengajuan ' + id + '.');
      else if (action === 'detail-sim') alert('Simulasi: detail ' + id + ' tersedia setelah data tersambung.');
      else if (action === 'topology') {
        alert('Simulasi verifikasi topologi untuk ' + id + '. Pada implementasi QGIS, aksi ini menjalankan pemeriksaan topologi pada layer terkait.');
        record.status = 'Terkompilasi';
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

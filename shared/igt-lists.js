// Shared list logic for the IGT Utama and IGT Derivatif pages.
// Pages call IgtLists.utama(role) or IgtLists.derivatif(role); role is 'superadmin', 'admin' or 'operator'.
// Everything here is simulated: no data leaves the page and nothing is persisted.
const IgtLists = (() => {
  const $ = (selector) => document.querySelector(selector);

  const STATUS_CLASS = {
    Proses: 'info',
    Terkompilasi: 'info',
    Terintegrasi: 'ok',
    Revisi: 'warn',
    Disetujui: 'ok',
    Ditolak: 'fix',
  };

  const badge = (status) => `<span class="status ${STATUS_CLASS[status] || ''}">${status}</span>`;
  const button = (cls, action, id, label) =>
    `<button class="btn ${cls} qgis-action" data-action="${action}" data-id="${id}">${label}</button>`;
  const link = (href, label) => `<a class="btn btn-soft qgis-action" href="${href}">${label}</a>`;
  const actionCell = (...items) => `<div class="toolbar">${items.join('')}</div>`;
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  };

  // Query string that keeps the role on shared detail pages (Operator is the default and has none).
  const roleQuery = (role) => (role === 'operator' ? '' : `&role=${role}`);

  // ---------------------------------------------------------------- IGT Utama

  const UTAMA_DETAIL = '../../operator/igt-utama-detail/index.html';

  const UTAMA_ROWS = [
    { n: 0, id: 'IGT-2026-012', kind: 'bidang', name: 'IGT Bidang Wilayah A', date: '18 Okt 2026', status: 'Proses' },
    { n: 1, id: 'IGT-2026-011', kind: 'kawasan', name: 'IGT Kawasan Hutan', date: '16 Okt 2026', status: 'Terintegrasi' },
    { n: 2, id: 'IGT-2026-010', kind: 'bidang', name: 'IGT Bidang Wilayah B', date: '15 Okt 2026', status: 'Revisi' },
    { n: 3, id: 'IGT-2026-009', kind: 'kawasan', name: 'IGT Kawasan Lindung', date: '14 Okt 2026', status: 'Terkompilasi' },
    { n: 4, id: 'IGT-2026-008', kind: 'bidang', name: 'IGT Bidang Infrastruktur', date: '12 Okt 2026', status: 'Proses' },
  ];

  // Baseline only exists for Berbasis Bidang; upload is offered on every tab.
  const UTAMA_TABS = {
    semua: {
      heading: 'Semua data IGT Utama',
      description: 'Seluruh pengajuan, baik berbasis bidang maupun kawasan.',
      tools: ['upload'],
    },
    bidang: {
      heading: 'IGT Utama Berbasis Bidang',
      description: 'Muat baseline bidang atau unggah data baru.',
      tools: ['baseline', 'upload'],
    },
    kawasan: {
      heading: 'IGT Utama Berbasis Kawasan',
      description: 'Unggah data kawasan. Baseline tidak tersedia untuk jenis ini.',
      tools: ['upload'],
    },
  };

  const TOOL_BUTTONS = {
    baseline: '<button class="btn btn-soft" data-action="load-baseline">▦ Load Baseline</button>',
    upload: '<button class="btn btn-primary" data-action="upload">↑ Upload Data</button>',
  };

  // Superadmin and Admin verify topology on rows still in Proses; Operator revises returned rows.
  function utamaActions(role, row) {
    const qgis = button('btn-soft', 'show-qgis', row.id, '▧ Tampilkan di QGIS');
    if (role === 'operator') {
      return row.status === 'Revisi' ? button('btn-soft', 'revision', row.id, '✎ Revisi') : qgis;
    }
    return row.status === 'Proses'
      ? actionCell(button('btn-primary', 'topology', row.id, '⌁ Verifikasi Topologi'), qgis)
      : qgis;
  }

  function utama(role) {
    const rows = UTAMA_ROWS.map((row) => ({ ...row }));
    let tab = 'semua';

    function renderCounts() {
      const count = (status) => rows.filter((r) => r.status === status).length;
      setText('count-total', rows.length);
      setText('count-process', count('Proses'));
      setText('count-compiled', count('Terkompilasi'));
      setText('count-integrated', count('Terintegrasi'));
    }

    function render() {
      document.querySelectorAll('[data-tab]').forEach((t) => t.classList.toggle('active', t.dataset.tab === tab));
      const config = UTAMA_TABS[tab];
      setText('tab-heading', config.heading);
      setText('tab-description', config.description);
      $('#tab-actions').innerHTML = config.tools.map((tool) => TOOL_BUTTONS[tool]).join('');
      $('#submission-rows').innerHTML = rows
        .filter((row) => tab === 'semua' || row.kind === tab)
        .map(
          (row) =>
            `<tr data-kind="${row.kind}">` +
            `<td data-label="ID pengajuan"><a class="text-link" href="${UTAMA_DETAIL}?id=${row.n}${roleQuery(role)}">${row.id}</a></td>` +
            `<td data-label="Layer target">${row.name}</td>` +
            `<td data-label="Tanggal upload">${row.date}</td>` +
            `<td data-label="Status">${badge(row.status)}</td>` +
            `<td data-label="Aksi" class="action-cell">${utamaActions(role, row)}</td></tr>`,
        )
        .join('');
      renderCounts();
    }

    document.querySelectorAll('[data-tab]').forEach((t) =>
      t.addEventListener('click', () => {
        tab = t.dataset.tab;
        render();
      }),
    );

    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const { action, id } = target.dataset;
      if (action === 'load-baseline') alert('Simulasi: pilih layer baseline dari QGIS.');
      else if (action === 'upload') alert('Simulasi: pilih file data untuk diunggah (' + UTAMA_TABS[tab].heading + ').');
      else if (action === 'show-qgis') alert('Simulasi plugin QGIS: layer ' + id + ' akan ditampilkan pada kanvas peta QGIS.');
      else if (action === 'revision') alert('Simulasi: buka formulir revisi untuk pengajuan ' + id + '.');
      else if (action === 'topology') {
        alert('Simulasi verifikasi topologi untuk ' + id + '. Pada implementasi QGIS, aksi ini menjalankan pemeriksaan topologi pada layer terkait.');
        rows.find((row) => row.id === id).status = 'Terkompilasi';
        render();
      }
    });

    render();
  }

  // ------------------------------------------------------------- IGT Derivatif

  const DERIVATIF_DETAIL = '../../operator/layer-derivatif-detail/index.html';

  // `n` is the record index understood by the detail page; rows added in this session have none.
  const DERIVATIF_ROWS = [
    { n: 0, id: 'DRV-2026-008', name: 'Derivatif Kawasan Hutan', date: '16 Okt 2026', status: 'Disetujui' },
    { n: 1, id: 'DRV-2026-007', name: 'Derivatif Bidang Wilayah A', date: '15 Okt 2026', status: 'Proses' },
    { n: 2, id: 'DRV-2026-006', name: 'Derivatif Kawasan Lindung', date: '14 Okt 2026', status: 'Ditolak' },
    { n: 3, id: 'DRV-2026-005', name: 'Derivatif Bidang Wilayah B', date: '12 Okt 2026', status: 'Disetujui' },
  ];

  const DERIVATIF_TEXT = {
    superadmin: {
      proses: 'Periksa pengajuan yang menunggu keputusan Superadmin.',
      tools: '<span class="status info">Panel verifikasi Superadmin</span>',
    },
    admin: {
      proses: 'Pengajuan yang menunggu keputusan Admin.',
      tools: '<button class="btn btn-primary" data-action="upload">↑ Upload Derivatif</button>',
    },
  };

  const DERIVATIF_TABS = {
    proses: { heading: 'Pengajuan dalam proses', match: (row) => row.status !== 'Disetujui' },
    disetujui: {
      heading: 'Pengajuan disetujui',
      description: 'Daftar layer derivatif yang telah disetujui, termasuk data yang diunggah Admin.',
      match: (row) => row.status === 'Disetujui',
    },
  };

  // Rows in Proses can be approved or rejected; every row can open its detail page.
  function derivatifActions(role, row) {
    const detail = row.n === undefined
      ? button('btn-soft', 'detail-sim', row.id, 'Detail')
      : link(`${DERIVATIF_DETAIL}?id=${row.n}&role=${role}`, 'Detail');
    if (row.status === 'Proses') {
      return actionCell(
        button('btn-primary', 'approve', row.id, '✓ Setujui'),
        button('btn-soft', 'reject', row.id, '✕ Tolak'),
        detail,
      );
    }
    if (row.status === 'Disetujui') return actionCell(detail, button('btn-soft', 'show-qgis', row.id, '▧ Tampilkan di QGIS'));
    return actionCell(detail);
  }

  function derivatif(role) {
    const rows = DERIVATIF_ROWS.map((row) => ({ ...row }));
    const text = DERIVATIF_TEXT[role];
    let tab = 'proses';
    let nextNumber = 9;

    function renderCounts() {
      const count = (status) => rows.filter((r) => r.status === status).length;
      setText('count-total', rows.length);
      setText('count-pending', count('Proses'));
      setText('count-approved', count('Disetujui'));
      setText('count-rejected', count('Ditolak'));
    }

    function render() {
      document.querySelectorAll('[data-tab]').forEach((t) => t.classList.toggle('active', t.dataset.tab === tab));
      const config = DERIVATIF_TABS[tab];
      setText('tab-heading', config.heading);
      setText('tab-description', config.description || text.proses);
      $('#tab-actions').innerHTML = text.tools;
      $('#submission-rows').innerHTML = rows
        .filter(config.match)
        .map((row) => {
          const id = row.n === undefined ? row.id : `<a class="text-link" href="${DERIVATIF_DETAIL}?id=${row.n}&role=${role}">${row.id}</a>`;
          return (
            `<tr><td data-label="ID pengajuan">${id}</td>` +
            `<td data-label="Nama Layer">${row.name}</td>` +
            `<td data-label="Tanggal pengajuan">${row.date}</td>` +
            `<td data-label="Status">${badge(row.status)}</td>` +
            `<td data-label="Aksi" class="action-cell">${derivatifActions(role, row)}</td></tr>`
          );
        })
        .join('');
      renderCounts();
    }

    document.querySelectorAll('[data-tab]').forEach((t) =>
      t.addEventListener('click', () => {
        tab = t.dataset.tab;
        render();
      }),
    );

    document.addEventListener('click', (event) => {
      const target = event.target.closest('[data-action]');
      if (!target) return;
      const { action, id } = target.dataset;
      const row = rows.find((r) => r.id === id);
      if (action === 'show-qgis') alert('Simulasi plugin QGIS: layer ' + id + ' akan ditampilkan pada kanvas peta QGIS.');
      else if (action === 'detail-sim') alert('Simulasi: detail ' + id + ' tersedia setelah data tersambung.');
      else if (action === 'approve' || action === 'reject') {
        if (!confirm((action === 'approve' ? 'Setujui' : 'Tolak') + ' pengajuan ' + id + '?')) return;
        row.status = action === 'approve' ? 'Disetujui' : 'Ditolak';
        render();
      } else if (action === 'upload') {
        // Admin uploads skip review and are approved immediately.
        if (!confirm('Simulasi: pilih berkas layer derivatif. Unggahan Admin langsung berstatus Disetujui. Lanjutkan?')) return;
        const id = 'DRV-2026-' + String(nextNumber).padStart(3, '0');
        rows.unshift({ id, name: 'Derivatif Unggahan Admin ' + nextNumber, date: '19 Okt 2026', status: 'Disetujui' });
        nextNumber += 1;
        tab = 'disetujui';
        render();
      }
    });

    render();
  }

  return { utama, derivatif };
})();

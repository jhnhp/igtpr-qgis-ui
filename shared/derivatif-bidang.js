// Workflow page "Upload Derivatif Bidang" (IGT Derivatif, Operator): six steps on one page.
// Needs shared/igt-data.js. Everything that would touch QGIS, the baseline layer or files is a simulation:
// there is no WFS, no QGIS API and no file generation. Workflow state lives in this page; only the list of
// "saved" attribute files is mirrored to sessionStorage so step 6 can be revisited after leaving the page.
const DerivatifBidang = (() => {
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) =>
    String(value).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

  const STEPS = [
    { short: 'Sumber', title: 'Pilih Sumber Bidang Tanah', text: 'Muat layer baseline sebagai sumber geometri bidang.' },
    { short: 'Struktur', title: 'Atur Struktur Atribut', text: 'Gunakan template layer derivatif atau tambahkan kolom manual.' },
    { short: 'Bidang', title: 'Pilih Bidang Tanah', text: 'Pilih satu bidang pada QGIS Canvas.' },
    { short: 'Atribut', title: 'Isi Atribut', text: 'Lengkapi nilai atribut untuk bidang terpilih.' },
    { short: 'Simpan', title: 'Simpan Berkas', text: 'Simpan ID bidang dan atribut tambahan ke sebuah berkas.' },
    { short: 'Disetujui', title: 'Atribut Disetujui', text: 'Gabungkan atribut dari berkas yang disetujui ke bidang sumber berdasarkan ID Bidang.' },
  ];
  const APPROVED = STEPS.length;

  const FIELD_TYPES = { text: 'Teks', integer: 'Bilangan bulat', decimal: 'Desimal', date: 'Tanggal' };
  const FIELD_NAME = /^[A-Za-z][A-Za-z0-9_]{0,29}$/;
  const FILE_NAME = /^[A-Za-z0-9][A-Za-z0-9._-]{0,59}$/;
  const FORMATS = { gpkg: { ext: '.gpkg', label: 'GeoPackage (.gpkg)' }, json: { ext: '.json', label: 'JSON (.json)' } };
  const ID_FIELD = 'id_bidang';
  const STORAGE_KEY = 'igtpr.derivatifBidang.savedFiles';

  // Dummy data. None of this comes from a real baseline, Geoportal or template registry.
  const BASELINE = [
    { id: '123456789012345', desa: 'Caturtunggal', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '842', hak: 'Hak Milik' },
    { id: '123456789012346', desa: 'Condongcatur', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '1.215', hak: 'Hak Guna Bangunan' },
    { id: '123456789012347', desa: 'Maguwoharjo', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '530', hak: 'Hak Milik' },
    { id: '123456789012348', desa: 'Sinduadi', kecamatan: 'Mlati', kabupaten: 'Sleman', luas: '2.060', hak: 'Hak Pakai' },
    { id: '123456789012349', desa: 'Tirtomartani', kecamatan: 'Kalasan', kabupaten: 'Sleman', luas: '978', hak: 'Hak Milik' },
    { id: '123456789012350', desa: 'Purwomartani', kecamatan: 'Kalasan', kabupaten: 'Sleman', luas: '1.430', hak: 'Hak Milik' },
  ];
  const CANVAS_COUNT = 4; // the first parcels are inside the simulated canvas extent
  const CANVAS_SHAPES = [
    { points: '18,22 138,14 150,82 28,96', cx: 84, cy: 54 },
    { points: '150,14 282,24 270,92 160,84', cx: 216, cy: 54 },
    { points: '28,106 150,96 160,166 22,160', cx: 90, cy: 132 },
    { points: '160,96 270,104 282,162 170,166', cx: 220, cy: 132 },
  ];
  const TEMPLATES = [
    {
      id: 'penggunaan-lahan', name: 'Template Contoh A · Penggunaan Lahan',
      fields: [
        { name: 'kode_guna', type: 'text', required: true },
        { name: 'jenis_guna', type: 'text', required: true },
        { name: 'luas_ha', type: 'decimal', required: false },
        { name: 'jumlah_bangunan', type: 'integer', required: false },
        { name: 'tgl_survei', type: 'date', required: false },
      ],
    },
    {
      id: 'kondisi-bidang', name: 'Template Contoh B · Kondisi Bidang',
      fields: [
        { name: 'kondisi', type: 'text', required: true },
        { name: 'tahun_data', type: 'integer', required: true },
        { name: 'nilai_taksiran', type: 'decimal', required: false },
        { name: 'tgl_verifikasi', type: 'date', required: false },
      ],
    },
  ];
  const SAMPLE_FILES = [
    {
      fileName: 'atribut_penggunaan_lahan_contoh.gpkg', format: 'gpkg', origin: 'sample',
      fields: [{ name: 'kode_guna', type: 'text' }, { name: 'jenis_guna', type: 'text' }, { name: 'luas_ha', type: 'decimal' }],
      records: [
        { id: '123456789012345', values: { kode_guna: 'PMK-01', jenis_guna: 'Permukiman', luas_ha: '0.08' } },
        { id: '123456789012346', values: { kode_guna: 'PRD-02', jenis_guna: 'Perdagangan', luas_ha: '0.12' } },
        { id: '999999999999999', values: { kode_guna: 'PMK-01', jenis_guna: 'Permukiman', luas_ha: '0.05' } },
      ],
    },
    {
      fileName: 'atribut_kondisi_bidang_contoh.json', format: 'json', origin: 'sample',
      fields: [{ name: 'kondisi', type: 'text' }, { name: 'tahun_data', type: 'integer' }],
      records: [
        { id: '123456789012347', values: { kondisi: 'Terbangun', tahun_data: '2025' } },
        { id: '123456789012348', values: { kondisi: 'Kosong', tahun_data: '2024' } },
      ],
    },
    {
      fileName: 'atribut_tidak_valid_contoh.gpkg', format: 'gpkg', origin: 'sample',
      invalid: 'Kolom ID Bidang (id_bidang) tidak ditemukan pada berkas ini.',
      fields: [], records: [],
    },
  ];

  const today = () => new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
  const findParcel = (id) => BASELINE.find((p) => p.id === id);
  const typeLabel = (type) => FIELD_TYPES[type] || type;
  const badge = (cls, text) => `<span class="status ${cls}">${text}</span>`;

  function loadSavedFiles() {
    try {
      const parsed = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]');
      return Array.isArray(parsed)
        ? parsed.filter((f) => f && typeof f.fileName === 'string' && Array.isArray(f.fields) && Array.isArray(f.records))
        : [];
    } catch (e) {
      return [];
    }
  }
  function persistSavedFiles(files) {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(files));
    } catch (e) {
      /* storage can be blocked (file:// previews); the files stay available while the page is open */
    }
  }

  function init(role) {
    const view = $('#view');
    if (!IgtData.ROLES[role] || !IgtData.ROLES[role].derivatifWorkflow) {
      view.innerHTML = '<div class="notice"><strong>Akses ditolak</strong>Upload Derivatif Bidang tidak tersedia untuk role ini.</div>';
      return;
    }
    const isV2 = Boolean(IgtData.ROLES[role].v2);
    if (isV2) {
      document.body.classList.add('v2-page', 'v2-theme-upload');
    }
    const backUrl = isV2 ? '../beranda/index.html' : '../upload-data/index.html?tab=derivatif';
    const finishLabel = isV2 ? 'Selesai · Kembali ke Dashboard' : 'Selesai · Kembali ke IGT Derivatif';

    const state = {
      step: 1,
      resumeMode: false,
      sourceLoaded: false,
      selectionActive: false,
      parcelId: '',
      mode: 'template',
      templateId: '',
      manualFields: [],
      draft: { name: '', type: 'text', required: false },
      draftError: '',
      values: {},
      touched: {},
      filename: '',
      filenameEdited: false,
      format: 'gpkg',
      saveDone: false,
      savedFiles: loadSavedFiles(),
      fileKey: '',
      loadedFile: null,
      loadError: '',
      join: null,
      notice: '',
    };

    // ---------------------------------------------------------------- derived data

    const currentFields = () =>
      state.mode === 'template'
        ? (TEMPLATES.find((t) => t.id === state.templateId) || { fields: [] }).fields
        : state.manualFields;

    function fieldError(field, raw) {
      const value = String(raw === undefined ? '' : raw).trim();
      if (!value) return field.required ? 'Wajib diisi.' : '';
      if (field.type === 'integer' && !/^-?\d+$/.test(value)) return 'Isi dengan bilangan bulat.';
      if (field.type === 'decimal' && !(value !== '' && Number.isFinite(Number(value)))) return 'Isi dengan angka desimal, contoh 12.5.';
      if (field.type === 'date' && !/^\d{4}-\d{2}-\d{2}$/.test(value)) return 'Isi dengan tanggal yang valid.';
      return '';
    }
    const attributeErrors = () => currentFields().filter((f) => fieldError(f, state.values[f.name]));

    function filenameError() {
      const name = state.filename.trim();
      if (!name) return 'Nama berkas wajib diisi.';
      if (/\.(gpkg|json)$/i.test(name)) return 'Tulis nama tanpa ekstensi; ekstensi mengikuti format yang dipilih.';
      if (!FILE_NAME.test(name)) return 'Gunakan huruf, angka, titik, garis bawah atau tanda hubung (maks. 60 karakter).';
      return '';
    }

    // Messages explaining why a step cannot be left yet. Empty = the step is complete.
    function blockers(step) {
      if (step === 1) return state.sourceLoaded ? [] : ['Muat baseline bidang tanah terlebih dahulu.'];
      if (step === 2) {
        if (state.mode === 'template') return state.templateId ? [] : ['Pilih satu template layer derivatif.'];
        return state.manualFields.length ? [] : ['Tambahkan minimal satu kolom atribut.'];
      }
      if (step === 3) return state.parcelId ? [] : [state.selectionActive ? 'Pilih satu bidang tanah.' : 'Aktifkan alat pilih, lalu pilih satu bidang tanah.'];
      if (step === 4) {
        if (blockers(2).length || blockers(3).length) return ['Tentukan struktur atribut dan pilih bidang terlebih dahulu.'];
        const bad = attributeErrors().length;
        return bad ? [`Lengkapi atau perbaiki ${bad} kolom atribut.`] : [];
      }
      if (step === 5) return state.saveDone ? [] : ['Simpan file untuk melanjutkan (atau selesaikan dan kembali nanti).'];
      return [];
    }
    // A step can be opened when it is behind us, the last step (independent of 1-5), or all steps before it are complete.
    function canReach(target) {
      if (target <= state.step || target === APPROVED) return true;
      for (let s = state.step; s < target; s += 1) if (blockers(s).length) return false;
      return true;
    }

    const touch = () => { state.saveDone = false; };

    // ---------------------------------------------------------------- step renderers

    function renderSource() {
      const ready = state.sourceLoaded;
      return (
        `<div class="notice"><strong>Baseline bidang tanah</strong>Baseline menyediakan geometri bidang dan pengenal uniknya (ID Bidang). ` +
        `Geometri tidak diunggah ulang; atribut derivatif dihubungkan ke bidang melalui ID Bidang.</div>` +
        `<div class="detail-grid">` +
        `<div class="detail-item"><div class="detail-label">Layer sumber</div><div class="detail-value">Baseline Bidang Tanah (contoh)</div></div>` +
        `<div class="detail-item"><div class="detail-label">Status sumber</div><div class="detail-value" id="source-status">${ready ? badge('ok', 'Siap digunakan') : badge('', 'Belum dimuat')}</div></div>` +
        `<div class="detail-item"><div class="detail-label">Pengenal bidang</div><div class="detail-value">ID Bidang</div></div>` +
        `<div class="detail-item"><div class="detail-label">Koneksi</div><div class="detail-value">Simulasi · tanpa WFS</div></div></div>` +
        `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="load-baseline" id="load-baseline">▦ ${ready ? 'Muat Ulang Baseline' : 'Load Baseline'}</button></div>` +
        `<div class="card-head submissions-head"><div><h2>Lanjutkan data tersimpan</h2><p>Muat struktur dan nilai atribut dari berkas sebelumnya agar tidak perlu dibuat ulang.</p></div></div>` +
        `<div class="field"><label for="resume-file-select">BERKAS DERIVATIF TERSIMPAN</label><select id="resume-file-select">${fileOptions()}</select></div>` +
        `<div class="toolbar"><button type="button" class="btn btn-soft" data-act="load-saved-for-edit" id="load-saved-for-edit" ${state.fileKey ? '' : 'disabled'}>↻ Muat Data Tersimpan</button></div>` +
        (state.loadError ? `<div class="notice error" role="alert"><strong>Berkas tidak dapat dimuat</strong>${esc(state.loadError)}</div>` : '') +
        (state.notice ? `<div class="notice" role="status"><strong>Simulasi</strong>${esc(state.notice)}</div>` : '') +
        `<p class="summary-note">Sudah punya berkas atribut? <button type="button" class="text-link" data-act="goto-approved">Langsung ke Atribut Disetujui</button></p>`
      );
    }

    function parcelPanel(parcel) {
      if (!parcel) return `<div class="empty-state" id="parcel-panel">Belum ada bidang yang dipilih.</div>`;
      return (
        `<div class="detail-grid" id="parcel-panel">` +
        [['ID Bidang', parcel.id], ['Desa / Kelurahan', parcel.desa], ['Kecamatan', parcel.kecamatan], ['Kabupaten', parcel.kabupaten], ['Luas (m²)', parcel.luas], ['Jenis hak', parcel.hak]]
          .map(([l, v]) => `<div class="detail-item"><div class="detail-label">${l}</div><div class="detail-value">${esc(v)}</div></div>`)
          .join('') +
        `</div>`
      );
    }

    function renderParcel() {
      const active = state.selectionActive;
      const candidates = BASELINE.slice(0, CANVAS_COUNT);
      return (
        `<div class="notice"><strong>Simulasi pemilihan bidang</strong>Pada plugin QGIS, bidang dipilih dengan alat seleksi di QGIS Canvas. ` +
        `Di prototipe ini canvas di bawah hanya gambar skema; memilih bidang contoh di sini tidak memilih fitur QGIS yang sebenarnya.</div>` +
        `<p class="summary-note" style="margin:0 0 10px">Instruksi: aktifkan alat pilih, lalu pilih <strong>satu</strong> bidang tanah.</p>` +
        `<div class="toolbar"><button type="button" class="btn ${active ? 'btn-soft' : 'btn-primary'}" data-act="activate-selection" id="activate-selection">◎ ${active ? 'Alat pilih aktif (simulasi)' : 'Aktifkan alat pilih (simulasi)'}</button></div>` +
        `<div class="canvas-sim${active ? ' active' : ''}"><div class="canvas-tag">Simulasi QGIS Canvas</div>` +
        `<svg viewBox="0 0 300 180" role="img" aria-label="Skema canvas dengan empat bidang contoh" focusable="false">` +
        candidates.map((p, i) => `<polygon class="parcel-shape${p.id === state.parcelId ? ' selected' : ''}" data-act="pick-parcel" data-id="${p.id}" points="${CANVAS_SHAPES[i].points}"></polygon>` +
          `<text x="${CANVAS_SHAPES[i].cx}" y="${CANVAS_SHAPES[i].cy}" text-anchor="middle" class="parcel-label">…${p.id.slice(-3)}</text>`).join('') +
        `</svg></div>` +
        `<fieldset class="choice-list"><legend>Hasil seleksi (simulasi)</legend>` +
        candidates.map((p) =>
          `<label class="choice"><input type="radio" name="parcel" value="${p.id}" ${p.id === state.parcelId ? 'checked' : ''} ${active ? '' : 'disabled'}>` +
          `<span><strong>${p.id}</strong><small>${esc(p.desa)}, ${esc(p.kecamatan)}</small></span></label>`).join('') +
        `</fieldset>` +
        `<div class="card-head submissions-head"><div><h2>Bidang terpilih</h2><p>Informasi bidang dari baseline contoh.</p></div></div>` +
        parcelPanel(findParcel(state.parcelId))
      );
    }

    function fieldTable(fields, withRemove) {
      if (!fields.length) return `<div class="empty-state" id="field-empty">Belum ada kolom atribut.</div>`;
      return (
        `<div class="table-wrap"><table class="stack"><thead><tr><th>Nama Kolom</th><th>Tipe</th><th>Wajib</th>${withRemove ? '<th>Aksi</th>' : ''}</tr></thead><tbody>` +
        fields.map((f, i) =>
          `<tr><td data-label="Nama Kolom"><div class="primary-cell">${esc(f.name)}</div></td><td data-label="Tipe">${typeLabel(f.type)}</td>` +
          `<td data-label="Wajib">${f.required ? 'Ya' : 'Tidak'}</td>` +
          (withRemove ? `<td data-label="Aksi" class="action-cell"><button type="button" class="btn btn-danger qgis-action" data-act="remove-field" data-index="${i}" aria-label="Hapus kolom ${esc(f.name)}">Hapus</button></td>` : '') +
          `</tr>`).join('') +
        `</tbody></table></div>`
      );
    }

    function renderStructure() {
      const tpl = state.mode === 'template';
      const d = state.draft;
      if (state.resumeMode) {
        return (
          `<div class="notice"><strong>Struktur dipulihkan dari berkas</strong>Kolom dan nilai yang tersimpan telah dimuat. Kamu bisa menghapus kolom yang tidak diperlukan atau menambahkan kolom baru; struktur tidak perlu dibuat ulang.</div>` +
          `<div class="card-head submissions-head"><div><h2>Struktur atribut saat ini</h2><p>${esc(state.loadedFile ? state.loadedFile.fileName : '')} · ${currentFields().length} kolom dipulihkan.</p></div></div>` +
          fieldTable(currentFields(), true) +
          `<div class="form-grid" style="margin-top:14px"><div class="field"><label for="draft-name">NAMA KOLOM BARU</label><input id="draft-name" autocomplete="off" maxlength="30" placeholder="contoh: kode_guna" value="${esc(d.name)}" aria-describedby="draft-error"></div>` +
          `<div class="field"><label for="draft-type">TIPE DATA</label><select id="draft-type">${Object.entries(FIELD_TYPES).map(([k, v]) => `<option value="${k}" ${d.type === k ? 'selected' : ''}>${v}</option>`).join('')}</select></div></div>` +
          `<label class="check"><input type="checkbox" id="draft-required" ${d.required ? 'checked' : ''}> Wajib diisi pada langkah berikutnya</label>` +
          `<div class="field-error" id="draft-error" role="alert">${esc(state.draftError)}</div>` +
          `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="add-field">＋ Tambah Kolom</button></div>`
        );
      }
      return (
        `<div class="choice-list" role="radiogroup" aria-label="Pendekatan struktur atribut">` +
        `<label class="choice"><input type="radio" name="mode" value="template" ${tpl ? 'checked' : ''}><span><strong>Gunakan Template Layer Derivatif</strong><small>Pakai daftar kolom dari template yang sudah ada.</small></span></label>` +
        `<label class="choice"><input type="radio" name="mode" value="manual" ${tpl ? '' : 'checked'}><span><strong>Tambahkan Kolom Manual</strong><small>Susun sendiri nama dan tipe kolom atribut.</small></span></label></div>` +
        (tpl
          ? `<div class="notice"><strong>Template contoh</strong>Daftar di bawah adalah template dummy untuk prototipe; belum terhubung ke Geoportal.</div>` +
            `<div class="field"><label for="template-select">TEMPLATE LAYER DERIVATIF</label><select id="template-select"><option value="">Pilih template...</option>` +
            TEMPLATES.map((t) => `<option value="${t.id}" ${t.id === state.templateId ? 'selected' : ''}>${t.name}</option>`).join('') + `</select></div>` +
            `<div class="card-head submissions-head"><div><h2>Kolom template</h2><p>ID Bidang selalu disertakan sebagai penghubung ke bidang sumber.</p></div></div>` +
            fieldTable(currentFields(), false)
          : `<div class="form-grid" style="margin-top:14px">` +
            `<div class="field"><label for="draft-name">NAMA KOLOM</label><input id="draft-name" autocomplete="off" maxlength="30" placeholder="contoh: kode_guna" value="${esc(d.name)}" aria-describedby="draft-error"></div>` +
            `<div class="field"><label for="draft-type">TIPE DATA</label><select id="draft-type">${Object.entries(FIELD_TYPES).map(([k, v]) => `<option value="${k}" ${d.type === k ? 'selected' : ''}>${v}</option>`).join('')}</select></div></div>` +
            `<label class="check"><input type="checkbox" id="draft-required" ${d.required ? 'checked' : ''}> Wajib diisi pada langkah berikutnya</label>` +
            `<div class="field-error" id="draft-error" role="alert">${esc(state.draftError)}</div>` +
            `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="add-field">＋ Tambah Kolom</button></div>` +
            `<div class="card-head submissions-head"><div><h2>Kolom yang ditambahkan</h2><p>Hapus kolom sebelum melanjutkan jika tidak diperlukan.</p></div></div>` +
            fieldTable(currentFields(), true))
      );
    }

    function inputFor(f, i) {
      const value = esc(state.values[f.name] === undefined ? '' : state.values[f.name]);
      const attrs = `id="attr-${i}" data-attr="${esc(f.name)}" value="${value}" aria-describedby="attr-err-${i}"${f.required ? ' required' : ''}`;
      if (f.type === 'integer') return `<input type="number" step="1" inputmode="numeric" ${attrs}>`;
      if (f.type === 'decimal') return `<input type="number" step="any" inputmode="decimal" ${attrs}>`;
      if (f.type === 'date') return `<input type="date" ${attrs}>`;
      return `<input type="text" ${attrs}>`;
    }

    function renderAttributes() {
      const parcel = findParcel(state.parcelId);
      const fields = currentFields();
      return (
        `<div class="id-banner"><span>ID Bidang terpilih</span><strong id="active-parcel-id">${esc(state.parcelId)}</strong>` +
        `<small>${esc(parcel.desa)}, ${esc(parcel.kecamatan)}, ${esc(parcel.kabupaten)}</small></div>` +
        `<p class="summary-note" style="margin:0 0 12px">ID Bidang menghubungkan atribut di bawah dengan bidang sumber. Kolom bertanda * wajib diisi.</p>` +
        `<div class="form-grid">` +
        fields.map((f, i) =>
          `<div class="field"><label for="attr-${i}">${esc(f.name)}${f.required ? ' *' : ''} <small class="type-hint">${typeLabel(f.type)}</small></label>${inputFor(f, i)}` +
          `<div class="field-error" id="attr-err-${i}"></div></div>`).join('') +
        `</div>`
      );
    }

    function summaryTable() {
      const fields = currentFields();
      return (
        `<div class="table-wrap"><table class="stack"><thead><tr><th>Kolom</th><th>Tipe</th><th>Nilai</th></tr></thead><tbody>` +
        `<tr><td data-label="Kolom"><div class="primary-cell">${ID_FIELD}</div></td><td data-label="Tipe">Teks</td><td data-label="Nilai">${esc(state.parcelId)}</td></tr>` +
        fields.map((f) => `<tr><td data-label="Kolom"><div class="primary-cell">${esc(f.name)}</div></td><td data-label="Tipe">${typeLabel(f.type)}</td><td data-label="Nilai">${esc(state.values[f.name] || '—')}</td></tr>`).join('') +
        `</tbody></table></div>`
      );
    }

    function renderSave() {
      const err = filenameError();
      const ext = FORMATS[state.format].ext;
      const saved = state.saveDone;
      return (
        `<div class="notice"><strong>Simulasi penyimpanan</strong>Prototipe ini tidak membuat berkas sungguhan. Tombol simpan hanya mencatat berkas contoh agar dapat dipakai pada langkah Disetujui.</div>` +
        `<div class="field"><label for="filename">NAMA BERKAS OUTPUT</label><div class="filename-row"><input id="filename" autocomplete="off" value="${esc(state.filename)}" aria-describedby="filename-error"><span class="ext" id="filename-ext">${ext}</span></div>` +
        `<div class="field-error" id="filename-error">${state.filenameEdited ? esc(err) : ''}</div></div>` +
        `<fieldset class="choice-list"><legend>Format output</legend>` +
        `<label class="choice"><input type="radio" name="format" value="gpkg" ${state.format === 'gpkg' ? 'checked' : ''}><span><strong>GeoPackage (.gpkg)</strong><small>Format utama (disarankan).</small></span></label>` +
        `<label class="choice"><input type="radio" name="format" value="json" ${state.format === 'json' ? 'checked' : ''}><span><strong>JSON (.json)</strong><small>Hanya tabel atribut dan ID Bidang.</small></span></label></fieldset>` +
        `<div class="card-head submissions-head"><div><h2>Ringkasan</h2><p>Bidang ${esc(state.parcelId)} · ${currentFields().length} kolom atribut tambahan.</p></div></div>` +
        summaryTable() +
        `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="save-file" id="save-file" ${err ? 'disabled' : ''}>💾 Simpan File (simulasi)</button></div>` +
        (saved
          ? `<div class="notice ok" role="status" id="save-success"><strong>Berkas tercatat (simulasi)</strong>${esc(state.filename.trim() + ext)} dicatat sebagai berkas contoh berisi ID Bidang, definisi kolom, nilai atribut dan format. Tidak ada berkas fisik yang dibuat.` +
            `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="next">Lanjut ke Atribut Disetujui →</button>` +
            `<a class="btn btn-soft" href="${backUrl}" id="finish-later">Selesai, lanjutkan nanti</a></div></div>`
          : '')
      );
    }

    function fileOptions() {
      const own = state.savedFiles.map((f) => `<option value="s:${esc(f.fileName)}" ${state.fileKey === 's:' + f.fileName ? 'selected' : ''}>${esc(f.fileName)}</option>`).join('');
      const samples = SAMPLE_FILES.map((f) => `<option value="x:${f.fileName}" ${state.fileKey === 'x:' + f.fileName ? 'selected' : ''}>${f.fileName}${f.invalid ? ' (contoh tidak valid)' : ''}</option>`).join('');
      return `<option value="">Pilih berkas atribut...</option>` +
        (own ? `<optgroup label="Disimpan pada sesi ini">${own}</optgroup>` : '') +
        `<optgroup label="Berkas contoh (dummy)">${samples}</optgroup>`;
    }

    function recordsTable(file) {
      const cols = file.fields.map((f) => f.name);
      return (
        `<div class="table-wrap"><table class="stack"><thead><tr><th>${ID_FIELD}</th>${cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>` +
        file.records.map((r) => `<tr><td data-label="${ID_FIELD}"><div class="primary-cell">${esc(r.id)}</div></td>${cols.map((c) => `<td data-label="${esc(c)}">${esc(r.values[c] || '—')}</td>`).join('')}</tr>`).join('') +
        `</tbody></table></div>`
      );
    }

    function joinPanel() {
      const j = state.join;
      if (!j) return '';
      const matched = j.rows.filter((r) => r.parcel);
      const unmatched = j.rows.filter((r) => !r.parcel);
      const attrText = (r) => Object.entries(r.values).map(([k, v]) => `${esc(k)}: ${esc(v || '—')}`).join('; ');
      return (
        `<div class="card-head submissions-head"><div><h2>Hasil penggabungan</h2><p id="join-summary">${matched.length} cocok · ${unmatched.length} tidak ditemukan dari ${j.rows.length} baris.</p></div></div>` +
        (matched.length === 0
          ? `<div class="notice error" role="alert" id="join-error"><strong>Tidak ada ID yang cocok</strong>Tidak ada baris yang dapat digabungkan ke baseline. Periksa berkas atribut atau baseline yang dipakai.</div>`
          : `<div class="table-wrap"><table class="stack" id="join-table"><thead><tr><th>ID Bidang</th><th>Wilayah</th><th>Atribut tergabung</th></tr></thead><tbody>` +
            matched.map((r) => `<tr><td data-label="ID Bidang"><div class="primary-cell">${esc(r.id)}</div></td><td data-label="Wilayah">${esc(r.parcel.desa)}, ${esc(r.parcel.kecamatan)}</td><td data-label="Atribut tergabung">${attrText(r)}</td></tr>`).join('') +
            `</tbody></table></div>`) +
        (unmatched.length
          ? `<div class="notice warn" role="status" id="join-unmatched"><strong>${unmatched.length} ID tidak ditemukan di baseline</strong>Baris berikut tidak digabungkan ke bidang mana pun: ${unmatched.map((r) => esc(r.id)).join(', ')}.</div>`
          : '') +
        (state.notice ? `<div class="notice ok" role="status" id="show-result"><strong>Simulasi</strong>${esc(state.notice)}</div>` : '') +
        `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="show-in-qgis" id="show-in-qgis" ${matched.length ? '' : 'disabled'}><svg class="ri-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 3c5.392 0 9.878 3.88 10.819 9-.94 5.12-5.427 9-10.819 9-5.392 0-9.878-3.88-10.819-9C2.121 6.88 6.608 3 12 3zm0 16a9.005 9.005 0 0 0 8.777-7 9.005 9.005 0 0 0-17.554 0A9.005 9.005 0 0 0 12 19zm0-2.5a4.5 4.5 0 1 1 0-9 4.5 4.5 0 0 1 0 9zm0-2a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z"/></svg><span>Tampilkan</span></button></div>`
      );
    }

    function renderApproved() {
      const file = state.loadedFile;
      return (
        `<div class="notice"><strong>Simulasi penggabungan</strong>Berkas dan baseline di bawah adalah data contoh; tidak ada layanan WFS atau QGIS yang terhubung. ` +
        `Hanya baris dengan ID Bidang yang sama persis yang digabungkan; tidak ada penggabungan otomatis lainnya.</div>` +
        (state.sourceLoaded
          ? `<p class="summary-note" style="margin:0 0 10px">Sumber bidang: ${badge('ok', 'Baseline siap')} Baseline Bidang Tanah (contoh)</p>`
          : `<div class="notice warn" id="baseline-needed"><strong>Baseline belum dimuat</strong>Muat baseline agar bidang sumber dapat dicari berdasarkan ID Bidang.` +
            `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="load-baseline" id="load-baseline">▦ Load Baseline</button></div></div>`) +
        `<div class="field"><label for="file-select">BERKAS ATRIBUT TERSIMPAN</label><select id="file-select">${fileOptions()}</select></div>` +
        `<div class="toolbar"><button type="button" class="btn btn-soft" data-act="load-file" id="load-file" ${state.fileKey ? '' : 'disabled'}>Muat Berkas</button></div>` +
        (state.loadError ? `<div class="notice error" role="alert" id="load-error"><strong>Berkas tidak dapat dibaca</strong>${esc(state.loadError)}</div>` : '') +
        (file
          ? `<div class="card-head submissions-head"><div><h2>Isi berkas</h2><p>${esc(file.fileName)} · ${file.records.length} baris · kunci ${ID_FIELD}.</p></div></div>` +
            recordsTable(file) +
            `<div class="toolbar"><button type="button" class="btn btn-primary" data-act="run-join" id="run-join" ${state.sourceLoaded ? '' : 'disabled'}>⇄ Gabungkan berdasarkan ID Bidang</button></div>`
          : '') +
        joinPanel() +
        `<div class="toolbar"><a class="btn btn-soft" href="${backUrl}" id="finish">${finishLabel}</a></div>`
      );
    }

    // ---------------------------------------------------------------- frame

    const BODY = [renderSource, renderStructure, renderParcel, renderAttributes, renderSave, renderApproved];

    function stepper() {
      return (
        `<ol class="stepper wizard-steps" aria-label="Langkah alur kerja">` +
        STEPS.map((s, i) => {
          const n = i + 1;
          const cls = n === state.step ? ' active' : n < state.step && !blockers(n).length ? ' done' : '';
          return `<li class="step${cls}"><button type="button" class="step-btn" data-act="goto" data-step="${n}" ${canReach(n) ? '' : 'disabled'}${n === state.step ? ' aria-current="step"' : ''}>${s.short}</button></li>`;
        }).join('') +
        `</ol><p class="summary-note part-note">Bagian 1: buat atribut (langkah 1–5) · Bagian 2: atribut disetujui (langkah 6)</p>`
      );
    }

    function navHtml() {
      const s = state.step;
      const block = blockers(s)[0];
      const back = s === 1
        ? `<a class="btn btn-soft" href="${backUrl}" id="nav-back">← Kembali</a>`
        : `<button type="button" class="btn btn-soft" data-act="back" id="nav-back">← Kembali</button>`;
      const next = s === APPROVED
        ? ''
        : `<button type="button" class="btn btn-primary" data-act="next" id="nav-next" ${block ? 'disabled' : ''}>Lanjutkan →</button>`;
      return `${back}${next}` + (block && s !== APPROVED ? `<p class="nav-hint" id="nav-hint" role="status">${esc(block)}</p>` : '');
    }

    function render(focus) {
      const s = STEPS[state.step - 1];
      const headHtml = `<div class="card-head"><div><h2 id="step-title" tabindex="-1">Langkah ${state.step} dari ${STEPS.length} · ${s.title}</h2><p>${s.text}</p></div></div>`;
      view.innerHTML =
        `<section class="card wizard">` +
        (isV2 ? `${headHtml}${stepper()}` : `${stepper()}${headHtml}`) +
        `<div id="step-body">${BODY[state.step - 1]()}</div>` +
        `<div class="wizard-nav" id="wizard-nav">${navHtml()}</div></section>`;
      if (state.step === 4) refreshAttributeErrors();
      const target = focus && $(focus);
      if (target) target.focus();
    }

    function updateNav() {
      $('#wizard-nav').innerHTML = navHtml();
      document.querySelectorAll('.step-btn').forEach((b) => { b.disabled = !canReach(Number(b.dataset.step)); });
    }

    function refreshAttributeErrors() {
      currentFields().forEach((f, i) => {
        const input = $('#attr-' + i);
        const message = state.touched[f.name] ? fieldError(f, state.values[f.name]) : '';
        $('#attr-err-' + i).textContent = message;
        if (input) input.setAttribute('aria-invalid', message ? 'true' : 'false');
      });
    }

    function go(target, focus) {
      if (!canReach(target)) return;
      if (target === 4) {
        // Drop values of fields that are no longer part of the structure.
        const names = new Set(currentFields().map((f) => f.name));
        Object.keys(state.values).forEach((k) => { if (!names.has(k)) delete state.values[k]; });
      }
      if (target === 5 && !state.filenameEdited) state.filename = `derivatif_bidang_${state.parcelId}`;
      state.step = target;
      state.notice = '';
      render(focus || '#step-title');
      window.scrollTo(0, 0);
    }

    // ---------------------------------------------------------------- events

    function pickParcel(id) {
      if (!state.selectionActive || !findParcel(id)) return;
      if (state.parcelId !== id) touch();
      state.parcelId = id;
      render();
    }

    function addField() {
      const d = state.draft;
      const name = d.name.trim();
      let error = '';
      if (!name) error = 'Nama kolom wajib diisi.';
      else if (!FIELD_NAME.test(name)) error = 'Nama kolom harus diawali huruf dan hanya berisi huruf, angka, atau garis bawah (maks. 30 karakter).';
      else if (name.toLowerCase() === ID_FIELD || state.manualFields.some((f) => f.name.toLowerCase() === name.toLowerCase())) error = `Nama kolom "${name}" sudah dipakai.`;
      state.draftError = error;
      if (error) {
        $('#draft-error').textContent = error;
        $('#draft-name').setAttribute('aria-invalid', 'true');
        $('#draft-name').focus();
        return;
      }
      state.manualFields.push({ name, type: d.type, required: d.required });
      state.draft = { name: '', type: d.type, required: false };
      touch();
      render('#draft-name');
    }

    function saveFile() {
      if (filenameError()) return;
      const ext = FORMATS[state.format].ext;
      const fields = currentFields().map((f) => ({ name: f.name, type: f.type }));
      const values = {};
      fields.forEach((f) => { values[f.name] = String(state.values[f.name] === undefined ? '' : state.values[f.name]).trim(); });
      const fileName = state.filename.trim() + ext;
      const entry = { fileName, format: state.format, origin: 'session', savedAt: today(), fields, records: [{ id: state.parcelId, values }] };
      state.savedFiles = state.savedFiles.filter((f) => f.fileName !== fileName).concat(entry);
      persistSavedFiles(state.savedFiles);
      state.saveDone = true;
      render('#save-success');
    }

    function loadSavedForEdit() {
      state.loadError = '';
      const [kind, name] = [state.fileKey.slice(0, 1), state.fileKey.slice(2)];
      const file = (kind === 's' ? state.savedFiles : SAMPLE_FILES).find((f) => f.fileName === name);
      if (!file) {
        state.loadError = 'Pilih berkas yang tersedia terlebih dahulu.';
        state.notice = '';
        render('#resume-file-select');
        return;
      }
      if (file.invalid || !Array.isArray(file.fields) || !file.fields.length || !Array.isArray(file.records) || !file.records.length) {
        state.loadError = file.invalid || 'Berkas tidak memiliki definisi kolom atau baris data yang dapat dipulihkan.';
        state.notice = '';
        render('#resume-file-select');
        return;
      }
      const record = file.records[0];
      state.loadedFile = file;
      state.resumeMode = true;
      state.sourceLoaded = true;
      state.mode = 'manual';
      state.templateId = '';
      state.manualFields = file.fields.map((field) => ({
        name: String(field.name),
        type: FIELD_TYPES[field.type] ? field.type : 'text',
        required: Boolean(field.required),
      })).filter((field) => field.name.toLowerCase() !== ID_FIELD);
      state.values = { ...(record.values || {}) };
      state.parcelId = findParcel(String(record.id || '')) ? String(record.id) : '';
      state.selectionActive = Boolean(state.parcelId);
      state.filename = file.fileName.replace(/\.(gpkg|json)$/i, '');
      state.filenameEdited = true;
      state.format = file.format === 'json' ? 'json' : 'gpkg';
      state.saveDone = false;
      state.step = 2;
      state.join = null;
      state.notice = state.parcelId
        ? 'Data tersimpan dipulihkan. Struktur dan nilai atribut siap ditinjau; bidang dari berkas telah dikenali.'
        : 'Struktur dan nilai atribut dipulihkan, tetapi ID bidang pada berkas tidak ditemukan di baseline contoh. Pilih bidang pada langkah Bidang.';
      render('#step-title');
      window.scrollTo(0, 0);
    }

    function loadFile() {
      state.join = null;
      state.notice = '';
      state.loadedFile = null;
      state.loadError = '';
      const [kind, name] = [state.fileKey.slice(0, 1), state.fileKey.slice(2)];
      const file = (kind === 's' ? state.savedFiles : SAMPLE_FILES).find((f) => f.fileName === name);
      if (!file) state.loadError = 'Berkas tidak ditemukan.';
      else if (file.invalid) state.loadError = file.invalid;
      else state.loadedFile = file;
      render('#load-error, #run-join');
    }

    function runJoin() {
      if (!state.loadedFile || !state.sourceLoaded) return;
      state.notice = '';
      state.join = { rows: state.loadedFile.records.map((r) => ({ id: r.id, values: r.values, parcel: findParcel(r.id) })) };
      render('#join-summary');
    }

    view.addEventListener('click', (event) => {
      const target = event.target.closest('[data-act]');
      if (!target || target.disabled) return;
      const act = target.dataset.act;
      if (act === 'goto') go(Number(target.dataset.step));
      else if (act === 'goto-approved') go(APPROVED);
      else if (act === 'next') go(state.step + 1);
      else if (act === 'back') go(state.step - 1, '#step-title');
      else if (act === 'load-baseline') {
        state.sourceLoaded = true;
        state.notice = 'Baseline contoh ditandai siap digunakan. Tidak ada koneksi WFS atau QGIS yang dibuat.';
        render('#load-baseline');
      } else if (act === 'activate-selection') {
        state.selectionActive = true;
        render('#activate-selection');
      } else if (act === 'pick-parcel') pickParcel(target.dataset.id);
      else if (act === 'add-field') addField();
      else if (act === 'remove-field') {
        const [removed] = state.manualFields.splice(Number(target.dataset.index), 1);
        delete state.values[removed.name];
        touch();
        render();
      } else if (act === 'save-file') saveFile();
      else if (act === 'load-file') loadFile();
      else if (act === 'load-saved-for-edit') loadSavedForEdit();
      else if (act === 'run-join') runJoin();
      else if (act === 'show-in-qgis') {
        const n = state.join.rows.filter((r) => r.parcel).length;
        state.notice = `Simulasi: ${n} bidang dengan atribut tergabung akan ditampilkan sebagai layer sementara di QGIS. Koneksi QGIS belum aktif pada prototipe ini.`;
        render('#show-result');
      }
    });

    view.addEventListener('input', (event) => {
      const el = event.target;
      if (el.id === 'draft-name') {
        state.draft.name = el.value;
        if (state.draftError) { state.draftError = ''; $('#draft-error').textContent = ''; el.removeAttribute('aria-invalid'); }
      } else if (el.id === 'filename') {
        state.filename = el.value;
        state.filenameEdited = true;
        touch();
        const err = filenameError();
        $('#filename-error').textContent = err;
        $('#save-file').disabled = Boolean(err);
        const success = $('#save-success');
        if (success) success.remove();
        updateNav();
      } else if (el.dataset.attr !== undefined) {
        state.values[el.dataset.attr] = el.value;
        state.touched[el.dataset.attr] = true;
        touch();
        refreshAttributeErrors();
        updateNav();
      }
    });

    view.addEventListener('change', (event) => {
      const el = event.target;
      if (el.name === 'parcel') pickParcel(el.value);
      else if (el.name === 'mode') {
        state.mode = el.value;
        touch();
        render('input[name="mode"]:checked');
      } else if (el.id === 'template-select') {
        state.templateId = el.value;
        touch();
        render('#template-select');
      } else if (el.id === 'draft-type') state.draft.type = el.value;
      else if (el.id === 'draft-required') state.draft.required = el.checked;
      else if (el.name === 'format') {
        state.format = el.value;
        touch();
        render('input[name="format"]:checked');
      } else if (el.id === 'resume-file-select') {
        state.fileKey = el.value;
        state.loadError = '';
        const button = $('#load-saved-for-edit');
        if (button) button.disabled = !state.fileKey;
      } else if (el.id === 'file-select') {
        state.fileKey = el.value;
        state.loadedFile = null;
        state.loadError = '';
        state.join = null;
        state.notice = '';
        render('#file-select');
      }
    });

    // The last step can be opened directly with ?step=6 (e.g. to come back to it later).
    render();
    if (new URLSearchParams(location.search).get('step') === String(APPROVED)) go(APPROVED);
  }

  return { init };
})();

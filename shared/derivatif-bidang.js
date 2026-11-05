// Workflow page "Derivatif Per Bidang" (Mockup V2).
// Sesuai dengan spesifikasi dan alur kerja di plugin eksisting (IGTPR-PLUGIN-QGIS / derivatif_bidang_page.py):
// 1. ✍️ ISI TEMATIK (Pilih layer derivatif CMS, load baseline WMS, klik bidang, isi atribut CMS dinamis, simpan ke sesi, ekspor)
// 2. ➕ CREATE TEMATIK (Pengaturan layer baru & baseline CMS, pilih bidang baseline, atribut default terkunci 🔒, atribut custom tambahan dinamis, simpan ke sesi, ekspor)
// 3. 📂 LOAD TEMATIK (Pilih berkas tabel atribut derivatif hasil ekspor lokal, verifikasi baseline, re-join geometri & visualisasi kanvas)

const DerivatifBidang = (() => {
  const $ = (selector) => document.querySelector(selector);
  const esc = (value) =>
    String(value === undefined || value === null ? '' : value)
      .replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

  // Baseline dummy parcels
  const BASELINE_PARCELS = [
    { id: '123456789012345', nib: '12.01.04.01.00128', desa: 'Caturtunggal', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '842', hak: 'Hak Milik' },
    { id: '123456789012346', nib: '12.01.04.01.00129', desa: 'Condongcatur', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '1.215', hak: 'Hak Guna Bangunan' },
    { id: '123456789012347', nib: '12.01.04.01.00130', desa: 'Maguwoharjo', kecamatan: 'Depok', kabupaten: 'Sleman', luas: '530', hak: 'Hak Milik' },
    { id: '123456789012348', nib: '12.01.04.01.00131', desa: 'Sinduadi', kecamatan: 'Mlati', kabupaten: 'Sleman', luas: '2.060', hak: 'Hak Pakai' },
    { id: '123456789012349', nib: '12.01.04.01.00132', desa: 'Tirtomartani', kecamatan: 'Kalasan', kabupaten: 'Sleman', luas: '978', hak: 'Hak Milik' },
    { id: '123456789012350', nib: '12.01.04.01.00133', desa: 'Purwomartani', kecamatan: 'Kalasan', kabupaten: 'Sleman', luas: '1.430', hak: 'Hak Milik' },
  ];

  const CANVAS_SHAPES = [
    { points: '18,22 138,14 150,82 28,96', cx: 84, cy: 54 },
    { points: '150,14 282,24 270,92 160,84', cx: 216, cy: 54 },
    { points: '28,106 150,96 160,166 22,160', cx: 90, cy: 132 },
    { points: '160,96 270,104 282,162 170,166', cx: 220, cy: 132 },
  ];

  const DERIVATIF_CMS_LAYERS = [
    {
      id: 'kumuh',
      name: 'Kawasan Kumuh Bidang (Perkim)',
      summary: 'Tipe: Vektor Poligon | Target: 2.500 Bidang | CRS: EPSG:3857 | Pemilik: Ditjen Survei dan Pemetaan',
      fields: [
        { name: 'status_kumuh', label: 'Status Kekumuhan', type: 'select', options: ['Kumuh Ringan', 'Kumuh Sedang', 'Kumuh Berat', 'Bukan Kumuh'] },
        { name: 'kepadatan_bangunan', label: 'Kepadatan Bangunan', type: 'select', options: ['Tinggi (>70%)', 'Sedang (40-70%)', 'Rendah (<40%)'] },
        { name: 'tingkat_kerentanan', label: 'Tingkat Kerentanan Bencana', type: 'select', options: ['Tinggi', 'Sedang', 'Rendah'] },
        { name: 'luas_terdampak_m2', label: 'Luas Terdampak (m²)', type: 'number', default: '450' },
        { name: 'rekomendasi_penanganan', label: 'Rekomendasi Penanganan', type: 'text', default: 'Peningkatan drainase dan jalan lingkungan' },
        { name: 'tahun_analisis', label: 'Tahun Analisis', type: 'number', default: '2026' },
      ],
    },
    {
      id: 'kritis',
      name: 'Lahan Kritis Bidang (KLHK)',
      summary: 'Tipe: Vektor Poligon | Target: 1.800 Bidang | CRS: EPSG:3857 | Pemilik: Ditjen Tata Ruang',
      fields: [
        { name: 'tingkat_kritis', label: 'Tingkat Kekritisan', type: 'select', options: ['Sangat Kritis', 'Kritis', 'Agak Kritis', 'Potensial Kritis'] },
        { name: 'kemiringan_lereng', label: 'Kelas Lereng', type: 'select', options: ['Datar (0-8%)', 'Landai (8-15%)', 'Agak Curam (15-25%)', 'Sangat Curam (>40%)'] },
        { name: 'tutupan_vegetasi', label: 'Persentase Vegetasi (%)', type: 'number', default: '35' },
        { name: 'upaya_konservasi', label: 'Upaya Konservasi', type: 'text', default: 'Penanaman bibit pohon pelindung' },
        { name: 'tahun_analisis', label: 'Tahun Analisis', type: 'number', default: '2026' },
      ],
    },
    {
      id: 'gempa',
      name: 'Zona Kerentanan Sesar Aktif & Gempa (BNPB)',
      summary: 'Tipe: Vektor Poligon | Target: 3.200 Bidang | CRS: EPSG:3857 | Pemilik: Kantah Kab. Sleman',
      fields: [
        { name: 'zona_bahaya', label: 'Zona Bahaya Gempa', type: 'select', options: ['Zona Merah (Tinggi)', 'Zona Kuning (Sedang)', 'Zona Hijau (Aman)'] },
        { name: 'jarak_ke_sesar_m', label: 'Jarak ke Sesar Terdekat (m)', type: 'number', default: '250' },
        { name: 'jenis_tanah_pondasi', label: 'Jenis Tanah Pondasi', type: 'text', default: 'Alluvial sedang berpasir' },
        { name: 'kelayakan_struktur', label: 'Kelayakan Struktur Bangunan', type: 'select', options: ['Tahan Gempa', 'Perlu Penguatan', 'Rawan Roboh'] },
        { name: 'tahun_analisis', label: 'Tahun Analisis', type: 'number', default: '2026' },
      ],
    },
  ];

  const CMS_BASELINES = [
    { id: 'sleman', name: 'bidang_tanah_sleman_2026', typename: 'sppr:baseline_bidang_sleman', count: 32400 },
    { id: 'bantul', name: 'bidang_tanah_bantul_2026', typename: 'sppr:baseline_bidang_bantul', count: 28100 },
    { id: 'kulonprogo', name: 'bidang_tanah_kulonprogo_2026', typename: 'sppr:baseline_bidang_kulonprogo', count: 19800 },
  ];

  // Global state
  const state = {
    role: 'operator',
    currentMode: 'isi', // 'isi' | 'create' | 'load'
    activeParcelId: '123456789012345',
    isPicking: true,

    // Mode ISI
    isi: {
      selectedLayerId: 'kumuh',
      wmsLoaded: true,
      wmsLogOpen: false,
      formValues: {
        status_kumuh: 'Kumuh Sedang',
        kepadatan_bangunan: 'Tinggi (>70%)',
        tingkat_kerentanan: 'Sedang',
        luas_terdampak_m2: '450',
        rekomendasi_penanganan: 'Peningkatan drainase dan jalan lingkungan',
        tahun_analisis: '2026',
      },
      sessionParcels: [
        {
          id: '123456789012346',
          nib: '12.01.04.01.00129',
          desa: 'Condongcatur',
          kecamatan: 'Depok',
          summary: 'Kumuh Ringan · Drainase memadai · Luas: 280 m²',
          values: { status_kumuh: 'Kumuh Ringan', kepadatan_bangunan: 'Sedang (40-70%)', tingkat_kerentanan: 'Rendah', luas_terdampak_m2: '280' },
        },
      ],
      folder: '~/Documents/Derivatif_Kompilasi',
      format: 'gpkg',
    },

    // Mode CREATE
    create: {
      layerName: 'derivatif_bidang_kustom',
      selectedBaselineId: 'sleman',
      wmsLoaded: true,
      customColumns: [
        { name: 'kode_zona', type: 'Teks', length: 20, value: 'ZN-04' },
        { name: 'indeks_kerentanan', type: 'Desimal', length: 10, value: '0.78' },
        { name: 'prioritas_penanganan', type: 'Angka Bulat', length: 4, value: '1' },
      ],
      sessionParcels: [
        {
          id: '123456789012347',
          nib: '12.01.04.01.00130',
          desa: 'Maguwoharjo',
          kecamatan: 'Depok',
          summary: 'kode_zona=ZN-01, indeks_kerentanan=0.45, prioritas_penanganan=2',
        },
      ],
      folder: '~/Documents/Derivatif_Kustom',
      format: 'gpkg',
    },

    // Mode LOAD
    load: {
      filePath: 'atribut_kawasan_kumuh_sleman_2026.gpkg',
      fileLoaded: true,
      settingsOpen: false,
      detectedBaseline: {
        name: 'bidang_tanah_sleman_2026',
        typename: 'sppr:baseline_bidang_sleman',
        wmsUrl: 'https://geoportal.atrbpn.go.id/geoserver/sppr/wms',
        crs: 'EPSG:3857',
        idField: 'id_bidang',
        totalFeatures: 4,
      },
      loadedParcels: [
        { id: '123456789012345', nib: '12.01.04.01.00128', desa: 'Caturtunggal', kecamatan: 'Depok', status_kumuh: 'Kumuh Berat', luas_terdampak: '520 m²', aksi: 'Normalisasi saluran' },
        { id: '123456789012346', nib: '12.01.04.01.00129', desa: 'Condongcatur', kecamatan: 'Depok', status_kumuh: 'Kumuh Sedang', luas_terdampak: '410 m²', aksi: 'Perbaikan jalan lingkungan' },
        { id: '123456789012347', nib: '12.01.04.01.00130', desa: 'Maguwoharjo', kecamatan: 'Depok', status_kumuh: 'Kumuh Ringan', luas_terdampak: '180 m²', aksi: 'Penataan sanitasi' },
        { id: '123456789012348', nib: '12.01.04.01.00131', desa: 'Sinduadi', kecamatan: 'Mlati', status_kumuh: 'Kumuh Ringan', luas_terdampak: '230 m²', aksi: 'Pemasangan tong sampah pilah' },
      ],
    },
  };

  function getActiveParcel() {
    return BASELINE_PARCELS.find((p) => p.id === state.activeParcelId) || BASELINE_PARCELS[0];
  }

  function getIsiSavedIds() {
    return state.isi.sessionParcels.map((p) => p.id);
  }

  function getCreateSavedIds() {
    return state.create.sessionParcels.map((p) => p.id);
  }

  function getLoadedIds() {
    return state.load.loadedParcels.map((p) => p.id);
  }

  // -------------------------------------------------------------------------
  // RENDER SVG CANVAS SIMULATION
  // -------------------------------------------------------------------------
  function renderCanvasSvg(mode) {
    const savedIds = mode === 'isi' ? getIsiSavedIds() : mode === 'create' ? getCreateSavedIds() : getLoadedIds();
    const activeId = mode === 'load' ? '' : state.activeParcelId;

    return (
      `<div class="derivatif-canvas-wrap" style="position:relative;background:#f8fafc;border:1.5px solid #cbd5e1;border-radius:8px;padding:8px;margin:8px 0;overflow:hidden">` +
      `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">` +
      `<span style="font-size:11px;font-weight:700;color:#1e40af;background:#eff6ff;padding:2px 8px;border-radius:4px;border:1px solid #bfdbfe">` +
      `🗺️ QGIS Map Canvas · Baseline WMS (EPSG:3857)` +
      `</span>` +
      `<div style="display:flex;align-items:center;gap:10px;font-size:11px;font-weight:600">` +
      `<span style="display:inline-flex;align-items:center;gap:4px"><span style="display:inline-block;width:12px;height:12px;background:#fef3c7;border:1.5px solid #f59e0b;border-radius:2px"></span> Aktif Dipilih</span>` +
      `<span style="display:inline-flex;align-items:center;gap:4px"><span style="display:inline-block;width:12px;height:12px;background:#d1fae5;border:1.5px solid #10b981;border-radius:2px"></span> Sudah Tersimpan</span>` +
      `<span style="display:inline-flex;align-items:center;gap:4px"><span style="display:inline-block;width:12px;height:12px;background:#dbeafe;border:1.5px solid #93c5fd;border-radius:2px"></span> Belum Terisi</span>` +
      `</div></div>` +
      `<svg viewBox="0 0 300 180" style="display:block;width:100%;height:190px;background:#f1f5f9;border-radius:6px;cursor:crosshair" id="derivatif-canvas-svg">` +
      BASELINE_PARCELS.slice(0, 4).map((p, i) => {
        const isAct = p.id === activeId;
        const isSvd = savedIds.includes(p.id);
        const fill = isAct ? '#fef3c7' : isSvd ? '#d1fae5' : '#dbeafe';
        const stroke = isAct ? '#f59e0b' : isSvd ? '#10b981' : '#60a5fa';
        const strokeWidth = isAct ? '2.5' : '1.5';
        return (
          `<g class="parcel-canvas-group" data-parcel-id="${p.id}" style="cursor:pointer">` +
          `<polygon points="${CANVAS_SHAPES[i].points}" fill="${fill}" stroke="${stroke}" stroke-width="${strokeWidth}" data-act="select-canvas-parcel" data-id="${p.id}" />` +
          `<text x="${CANVAS_SHAPES[i].cx}" y="${CANVAS_SHAPES[i].cy - 4}" text-anchor="middle" font-size="9" font-weight="700" fill="#1e293b" pointer-events="none">${p.nib.split('.').pop()}</text>` +
          `<text x="${CANVAS_SHAPES[i].cx}" y="${CANVAS_SHAPES[i].cy + 8}" text-anchor="middle" font-size="8" fill="#64748b" pointer-events="none">${p.desa}</text>` +
          `</g>`
        );
      }).join('') +
      `</svg>` +
      `<div style="font-size:10.5px;color:#64748b;margin-top:4px;text-align:right">` +
      `Klik langsung poligon bidang di atas untuk memilih bidang yang akan diolah.` +
      `</div></div>`
    );
  }

  // -------------------------------------------------------------------------
  // 1. VIEW ISI TEMATIK
  // -------------------------------------------------------------------------
  function renderViewIsi() {
    const curLayer = DERIVATIF_CMS_LAYERS.find((l) => l.id === state.isi.selectedLayerId) || DERIVATIF_CMS_LAYERS[0];
    const parcel = getActiveParcel();
    const sessionCount = state.isi.sessionParcels.length;

    return (
      `<div class="derivatif-mode-view mode-isi-content">` +
      // KARTU 1: Pilih Layer Derivatif & Load Baseline WMS
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc">` +
      `<strong style="font-size:13px;color:#0f172a">1. Pilih Layer Derivatif &amp; Load Baseline WMS:</strong>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;gap:6px;margin-bottom:8px">` +
      `<select id="combo-derivatif-layer" style="flex:1;height:34px;padding:4px 10px;font-weight:700;border:1.5px solid #94a3b8;border-radius:6px;font-size:12.5px">` +
      DERIVATIF_CMS_LAYERS.map((l) => `<option value="${l.id}" ${l.id === curLayer.id ? 'selected' : ''}>${esc(l.name)}</option>`).join('') +
      `</select>` +
      `<button type="button" class="btn btn-soft" data-act="refresh-der" title="Muat ulang daftar layer derivatif dari server" style="width:36px;height:34px;padding:0;font-size:14px">🔄</button>` +
      `</div>` +
      `<div style="font-size:11.5px;color:#475569;background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:8px 10px;margin-bottom:10px">` +
      `${esc(curLayer.summary)}` +
      `</div>` +
      `<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">` +
      `<button type="button" class="btn btn-primary" data-act="load-baseline-isi" style="background:#0284c7;border-color:#0284c7;font-weight:700;font-size:12px">⚡ Load Baseline WMS</button>` +
      `<span style="font-size:12px;font-weight:700;color:${state.isi.wmsLoaded ? '#047857' : '#64748b'}">` +
      `${state.isi.wmsLoaded ? '✓ Baseline WMS Aktif: baseline_bidang_sleman (EPSG:3857)' : '⏳ Baseline WMS: Belum dimuat.'}` +
      `</span>` +
      `<button type="button" class="btn btn-soft btn-sm" data-act="open-wms-log" style="font-size:11px;font-weight:700;margin-left:auto">📋 Log GeoServer</button>` +
      `</div></div></div>` +

      // KARTU 2: Interaksi Canvas & Form Atribut CMS Dinamis
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:space-between">` +
      `<strong style="font-size:13px;color:#0f172a">2. Interaksi Kanvas &amp; Form Atribut CMS Dinamis:</strong>` +
      `<span style="background:#ecfdf5;color:#047857;font-size:11px;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid #a7f3d0">📦 ${sessionCount} Bidang Sesi</span>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">` +
      `<button type="button" class="btn ${state.isPicking ? 'btn-primary' : 'btn-soft'}" data-act="toggle-picker" style="font-size:12px;font-weight:700">🎯 ${state.isPicking ? 'Alat Pilih Bidang Aktif' : 'Klik Bidang di Peta'}</button>` +
      `<button type="button" class="btn btn-soft" data-act="import-bidang" style="font-size:12px;font-weight:700;color:#0284c7;border-color:#38bdf8">📥 Import Bidang</button>` +
      `<span style="font-size:12px;color:#1e40af;margin-left:4px">Klik bidang di peta untuk mulai mengisi atribut tematik.</span>` +
      `</div>` +
      renderCanvasSvg('isi') +
      `<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:6px;padding:8px 12px;margin:8px 0;display:flex;align-items:center;justify-content:space-between">` +
      `<div><strong style="color:#1e3a8a;font-size:12.5px">ID Bidang Terpilih: </strong><code style="font-size:13px;font-weight:800;color:#1d4ed8">${esc(parcel.id)}</code> <span style="font-size:11.5px;color:#475569">(${esc(parcel.desa)}, ${esc(parcel.kecamatan)})</span></div>` +
      `<span style="font-size:11px;background:#ffffff;border:1px solid #cbd5e1;padding:2px 6px;border-radius:4px;color:#334155">Luas: <strong>${esc(parcel.luas)} m²</strong></span>` +
      `</div>` +
      `<div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:6px;padding:12px;margin-bottom:10px">` +
      `<div style="font-size:11px;font-weight:800;color:#475569;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">Formulir Atribut Standar CMS (${esc(curLayer.name)})</div>` +
      `<div class="form-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:10px">` +
      curLayer.fields.map((fld) => {
        const val = state.isi.formValues[fld.name] || fld.default || '';
        return (
          `<div class="field" style="margin:0"><label style="font-size:11px;font-weight:700;color:#334155">${esc(fld.label)}</label>` +
          (fld.type === 'select'
            ? `<select data-isi-field="${esc(fld.name)}" style="height:32px;font-size:12px;padding:4px 8px;border:1px solid #cbd5e1;border-radius:5px">` +
              fld.options.map((opt) => `<option value="${esc(opt)}" ${val === opt ? 'selected' : ''}>${esc(opt)}</option>`).join('') +
              `</select>`
            : `<input type="${fld.type === 'number' ? 'number' : 'text'}" data-isi-field="${esc(fld.name)}" value="${esc(val)}" style="height:32px;font-size:12px;padding:4px 8px;border:1px solid #cbd5e1;border-radius:5px">`) +
          `</div>`
        );
      }).join('') +
      `</div></div>` +
      `<button type="button" class="btn btn-primary" data-act="isi-save-bidang" style="width:100%;height:38px;background:#0284c7;border-color:#0284c7;font-size:13px;font-weight:700">` +
      `Simpan Bidang (Simpan ke Sesi &amp; Lanjut Bidang Berikutnya)` +
      `</button>` +
      `</div></div>` +

      // KARTU 3: Daftar Bidang Terisi (Sesi Ini)
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:space-between">` +
      `<strong style="font-size:13px;color:#0f172a">3. Daftar Bidang Terisi (Sesi Ini): ${sessionCount} bidang</strong>` +
      `<div style="font-size:11.5px;font-weight:700"><span style="color:#f59e0b">■ Baru Diisi</span> &nbsp; <span style="color:#10b981">■ Sudah Tersimpan</span></div>` +
      `</div>` +
      `<div style="padding:10px 14px;max-height:220px;overflow:auto">` +
      `<table class="stack" style="width:100%;font-size:11.5px;margin:0">` +
      `<thead><tr style="background:#f1f5f9;text-align:left"><th style="padding:6px 8px;width:38px">No</th><th style="padding:6px 8px;width:140px">ID Bidang</th><th style="padding:6px 8px">Ringkasan Nilai</th><th style="padding:6px 8px;width:70px;text-align:center">Aksi</th></tr></thead>` +
      `<tbody>` +
      (sessionCount === 0
        ? `<tr><td colspan="4" style="text-align:center;padding:16px;color:#64748b;font-style:italic">Belum ada bidang tersimpan pada sesi ini. Lengkapi form di atas lalu klik "Simpan Bidang".</td></tr>`
        : state.isi.sessionParcels.map((sp, idx) =>
            `<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:6px 8px;font-weight:700">${idx + 1}</td><td style="padding:6px 8px"><code>${esc(sp.id)}</code><br><small style="color:#64748b">${esc(sp.desa)}</small></td><td style="padding:6px 8px;color:#334155">${esc(sp.summary)}</td><td style="padding:6px 8px;text-align:center"><button type="button" class="btn btn-danger btn-sm" data-act="delete-isi-parcel" data-index="${idx}" style="padding:2px 8px;font-size:10.5px">Hapus</button></td></tr>`
          ).join('')) +
      `</tbody></table></div></div>` +

      // KARTU 4: Opsi Penyimpanan & Format Ekspor
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc">` +
      `<strong style="font-size:13px;color:#0f172a">4. Opsi Penyimpanan &amp; Format Ekspor (Tabel Atribut Saja):</strong>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">` +
      `<label style="font-size:12px;font-weight:700;color:#334155;min-width:90px">Folder Simpan:</label>` +
      `<input type="text" id="isi-folder-input" value="${esc(state.isi.folder)}" style="flex:1;height:30px;font-size:12px;padding:3px 8px;border:1px solid #cbd5e1;border-radius:5px">` +
      `<button type="button" class="btn btn-soft" data-act="browse-folder" style="height:30px;padding:2px 10px;font-size:12px">...</button>` +
      `</div>` +
      `<div style="font-size:11px;color:#64748b;margin-bottom:10px;font-style:italic">Nama berkas otomatis menggunakan nama <strong>Layer Derivatif</strong> yang dipilih di atas.</div>` +
      `<div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">` +
      `<span style="font-size:12px;font-weight:700;color:#334155">Format:</span>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="isi-format" value="gpkg" ${state.isi.format === 'gpkg' ? 'checked' : ''}> .gpkg (GeoPackage)</label>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="isi-format" value="geojson" ${state.isi.format === 'geojson' ? 'checked' : ''}> .geojson (GeoJSON)</label>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="isi-format" value="shp" ${state.isi.format === 'shp' ? 'checked' : ''}> Esri Shapefile (.shp)</label>` +
      `</div>` +
      `<div style="font-size:11px;color:#64748b;background:#f8fafc;padding:6px 10px;border-radius:5px;border:1px solid #e2e8f0;margin-bottom:12px">` +
      `🔒 <i>Hanya poligon bidang terpilih yang disimpan (bukan seluruh baseline provinsi). Sesi akan direset setelah disimpan.</i>` +
      `</div>` +
      `<button type="button" class="btn btn-primary" data-act="execute-export-isi" style="width:100%;height:40px;background:#16a34a;border-color:#16a34a;font-size:14px;font-weight:800">` +
      `💾 Simpan Derivatif` +
      `</button>` +
      `</div></div></div>`
    );
  }

  // -------------------------------------------------------------------------
  // 2. VIEW CREATE TEMATIK
  // -------------------------------------------------------------------------
  function renderViewCreate() {
    const parcel = getActiveParcel();
    const sessionCount = state.create.sessionParcels.length;

    return (
      `<div class="derivatif-mode-view mode-create-content">` +
      // KARTU 1: Pengaturan Layer Baru & Baseline
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc">` +
      `<strong style="font-size:13px;color:#0f172a">1. Pengaturan Layer Baru &amp; Baseline (CMS Geoportal):</strong>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">` +
      `<label style="font-size:12px;font-weight:700;color:#334155;min-width:100px">Nama Layer:</label>` +
      `<input type="text" id="create-layer-name" value="${esc(state.create.layerName)}" placeholder="contoh: derivatif_bidang_kustom" style="flex:1;height:32px;font-size:12.5px;font-weight:700;padding:3px 8px;border:1.5px solid #94a3b8;border-radius:6px">` +
      `</div>` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">` +
      `<label style="font-size:12px;font-weight:700;color:#334155;min-width:100px">Baseline CMS:</label>` +
      `<select id="combo-create-baseline" style="flex:1;height:32px;font-size:12px;font-weight:700;padding:3px 8px;border:1px solid #94a3b8;border-radius:6px">` +
      CMS_BASELINES.map((b) => `<option value="${b.id}" ${b.id === state.create.selectedBaselineId ? 'selected' : ''}>${esc(b.name)} (${b.count.toLocaleString('id-ID')} bidang)</option>`).join('') +
      `</select>` +
      `<button type="button" class="btn btn-soft" data-act="refresh-bl" title="Muat ulang baseline dari CMS" style="width:34px;height:32px;padding:0;font-size:14px">🔄</button>` +
      `</div>` +
      `<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">` +
      `<button type="button" class="btn btn-primary" data-act="load-baseline-create" style="background:#7c3aed;border-color:#7c3aed;font-weight:700;font-size:12px">⚡ Load Baseline WMS</button>` +
      `<span style="font-size:12px;font-weight:700;color:${state.create.wmsLoaded ? '#047857' : '#64748b'}">` +
      `${state.create.wmsLoaded ? '✓ Baseline WMS Aktif: ' + state.create.selectedBaselineId + ' (EPSG:3857)' : '⏳ Baseline WMS: Belum dimuat.'}` +
      `</span>` +
      `<button type="button" class="btn btn-soft btn-sm" data-act="open-wms-log" style="font-size:11px;font-weight:700;margin-left:auto">📋 Log GeoServer</button>` +
      `</div></div></div>` +

      // KARTU 2: Pilih Bidang Baseline, Atribut Default (Terkunci) + Kustom
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:space-between">` +
      `<strong style="font-size:13px;color:#0f172a">2. Pilih Bidang, Atribut Default (Terkunci) + Kustom:</strong>` +
      `<span style="background:#ecfdf5;color:#047857;font-size:11px;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid #a7f3d0">📦 ${sessionCount} Bidang Sesi</span>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">` +
      `<button type="button" class="btn btn-primary" data-act="toggle-picker" style="background:#7c3aed;border-color:#7c3aed;font-size:12px;font-weight:700">🎯 Pilih Bidang Baseline</button>` +
      `<button type="button" class="btn btn-soft" data-act="import-bidang" style="font-size:12px;font-weight:700;color:#7c3aed;border-color:#c084fc">📥 Import Bidang</button>` +
      `<span style="font-size:12px;color:#5b21b6;margin-left:4px">Klik salah satu poligon bidang pada kanvas peta.</span>` +
      `</div>` +
      renderCanvasSvg('create') +
      `<div style="margin:8px 0;font-size:13px"><strong style="color:#7c3aed">ID: </strong><code style="font-size:13px;font-weight:800;color:#6d28d9">${esc(parcel.id)}</code> <span style="font-size:11.5px;color:#64748b">(${esc(parcel.desa)}, ${esc(parcel.kecamatan)})</span></div>` +

      // Sub A: Atribut Baseline Terkunci
      `<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:10px;margin-bottom:12px">` +
      `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">` +
      `<strong style="font-size:12px;color:#1e293b">A. Atribut Default Baseline (🔒 Terkunci):</strong>` +
      `<span style="font-size:11px;color:#64748b;background:#e2e8f0;padding:1px 6px;border-radius:3px">6 Kolom Bawaan</span>` +
      `</div>` +
      `<div style="max-height:140px;overflow:auto;border:1px solid #cbd5e1;border-radius:4px"><table class="stack" style="width:100%;font-size:11px;margin:0">` +
      `<thead><tr style="background:#f1f5f9;text-align:left"><th style="padding:4px 8px;width:130px">Kolom Baseline</th><th style="padding:4px 8px;width:70px">Tipe</th><th style="padding:4px 8px">Nilai (Terkunci 🔒)</th></tr></thead>` +
      `<tbody>` +
      `<tr><td style="padding:4px 8px"><code>id_bidang</code></td><td style="padding:4px 8px">String</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.id)}</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>nib</code></td><td style="padding:4px 8px">String</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.nib)}</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>desa</code></td><td style="padding:4px 8px">String</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.desa)}</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>kecamatan</code></td><td style="padding:4px 8px">String</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.kecamatan)}</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>luas_m2</code></td><td style="padding:4px 8px">Decimal</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.luas)}</td></tr>` +
      `<tr><td style="padding:4px 8px"><code>jenis_hak</code></td><td style="padding:4px 8px">String</td><td style="padding:4px 8px;color:#475569">🔒 ${esc(parcel.hak)}</td></tr>` +
      `</tbody></table></div></div>` +

      // Sub B: Atribut Custom Tambahan
      `<div style="background:#ffffff;border:1px solid #ddd6fe;border-radius:6px;padding:10px;margin-bottom:12px">` +
      `<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">` +
      `<strong style="font-size:12px;color:#5b21b6">B. Atribut Custom Tambahan:</strong>` +
      `<button type="button" class="btn btn-soft btn-sm" data-act="add-custom-col" style="font-size:11.5px;font-weight:700;color:#6d28d9;border-color:#c084fc">＋ Tambah Atribut</button>` +
      `</div>` +
      `<div style="overflow:auto;border:1px solid #cbd5e1;border-radius:4px"><table class="stack" style="width:100%;font-size:11.5px;margin:0" id="table-custom-cols">` +
      `<thead><tr style="background:#ede9fe;color:#5b21b6;text-align:left"><th style="padding:4px 8px;width:130px">Nama Kolom</th><th style="padding:4px 8px;width:100px">Tipe</th><th style="padding:4px 8px;width:65px">Length</th><th style="padding:4px 8px">Nilai (Isi)</th><th style="padding:4px 8px;width:34px;text-align:center"></th></tr></thead>` +
      `<tbody>` +
      state.create.customColumns.map((col, idx) =>
        `<tr>` +
        `<td style="padding:4px 6px"><input type="text" data-col-idx="${idx}" data-col-field="name" value="${esc(col.name)}" style="width:100%;height:26px;font-size:11.5px;padding:2px 4px;border:1px solid #cbd5e1;border-radius:4px"></td>` +
        `<td style="padding:4px 6px"><select data-col-idx="${idx}" data-col-field="type" style="width:100%;height:26px;font-size:11px;padding:1px 4px;border:1px solid #cbd5e1;border-radius:4px"><option ${col.type === 'Teks' ? 'selected' : ''}>Teks</option><option ${col.type === 'Angka Bulat' ? 'selected' : ''}>Angka Bulat</option><option ${col.type === 'Desimal' ? 'selected' : ''}>Desimal</option><option ${col.type === 'Tanggal' ? 'selected' : ''}>Tanggal</option></select></td>` +
        `<td style="padding:4px 6px"><input type="number" data-col-idx="${idx}" data-col-field="length" value="${col.length || 50}" style="width:100%;height:26px;font-size:11.5px;padding:2px 4px;border:1px solid #cbd5e1;border-radius:4px"></td>` +
        `<td style="padding:4px 6px"><input type="${col.type === 'Tanggal' ? 'date' : col.type === 'Angka Bulat' || col.type === 'Desimal' ? 'number' : 'text'}" data-col-idx="${idx}" data-col-field="value" value="${esc(col.value)}" style="width:100%;height:26px;font-size:11.5px;padding:2px 4px;border:1px solid #cbd5e1;border-radius:4px"></td>` +
        `<td style="padding:4px 6px;text-align:center"><button type="button" class="btn btn-soft btn-sm" data-act="remove-custom-col" data-idx="${idx}" style="color:#dc2626;padding:1px 6px;font-weight:700">✕</button></td>` +
        `</tr>`
      ).join('') +
      `</tbody></table></div></div>` +

      `<button type="button" class="btn btn-primary" data-act="create-save-bidang" style="width:100%;height:38px;background:#7c3aed;border-color:#7c3aed;font-size:13px;font-weight:700">` +
      `Simpan Bidang (Pertahankan Skema Kolom &amp; Siap Bidang Selanjutnya)` +
      `</button>` +
      `</div></div>` +

      // KARTU 3: Daftar Bidang Terisi Sesi Ini
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:space-between">` +
      `<strong style="font-size:13px;color:#0f172a">3. Daftar Bidang Terisi (Sesi Ini): ${sessionCount} bidang</strong>` +
      `<div style="font-size:11.5px;font-weight:700"><span style="color:#f59e0b">■ Baru Diisi</span> &nbsp; <span style="color:#10b981">■ Sudah Tersimpan</span></div>` +
      `</div>` +
      `<div style="padding:10px 14px;max-height:220px;overflow:auto">` +
      `<table class="stack" style="width:100%;font-size:11.5px;margin:0">` +
      `<thead><tr style="background:#f1f5f9;text-align:left"><th style="padding:6px 8px;width:38px">No</th><th style="padding:6px 8px;width:140px">ID Bidang</th><th style="padding:6px 8px">Ringkasan Nilai Kustom</th><th style="padding:6px 8px;width:70px;text-align:center">Aksi</th></tr></thead>` +
      `<tbody>` +
      (sessionCount === 0
        ? `<tr><td colspan="4" style="text-align:center;padding:16px;color:#64748b;font-style:italic">Belum ada bidang tersimpan pada sesi ini.</td></tr>`
        : state.create.sessionParcels.map((sp, idx) =>
            `<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:6px 8px;font-weight:700">${idx + 1}</td><td style="padding:6px 8px"><code>${esc(sp.id)}</code><br><small style="color:#64748b">${esc(sp.desa || '')}</small></td><td style="padding:6px 8px;color:#334155">${esc(sp.summary)}</td><td style="padding:6px 8px;text-align:center"><button type="button" class="btn btn-danger btn-sm" data-act="delete-create-parcel" data-index="${idx}" style="padding:2px 8px;font-size:10.5px">Hapus</button></td></tr>`
          ).join('')) +
      `</tbody></table></div></div>` +

      // KARTU 4: Opsi Penyimpanan & Format Ekspor
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc">` +
      `<strong style="font-size:13px;color:#0f172a">4. Opsi Penyimpanan &amp; Format Ekspor (Tabel Atribut Saja):</strong>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">` +
      `<label style="font-size:12px;font-weight:700;color:#334155;min-width:90px">Folder Simpan:</label>` +
      `<input type="text" id="create-folder-input" value="${esc(state.create.folder)}" style="flex:1;height:30px;font-size:12px;padding:3px 8px;border:1px solid #cbd5e1;border-radius:5px">` +
      `<button type="button" class="btn btn-soft" data-act="browse-folder" style="height:30px;padding:2px 10px;font-size:12px">...</button>` +
      `</div>` +
      `<div style="display:flex;align-items:center;gap:16px;margin-bottom:10px">` +
      `<span style="font-size:12px;font-weight:700;color:#334155">Format:</span>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="create-format" value="gpkg" ${state.create.format === 'gpkg' ? 'checked' : ''}> .gpkg (GeoPackage)</label>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="create-format" value="geojson" ${state.create.format === 'geojson' ? 'checked' : ''}> .geojson (GeoJSON)</label>` +
      `<label style="font-size:12px;cursor:pointer"><input type="radio" name="create-format" value="shp" ${state.create.format === 'shp' ? 'checked' : ''}> Esri Shapefile (.shp)</label>` +
      `</div>` +
      `<button type="button" class="btn btn-primary" data-act="execute-export-create" style="width:100%;height:40px;background:#16a34a;border-color:#16a34a;font-size:14px;font-weight:800">` +
      `💾 Simpan Derivatif` +
      `</button>` +
      `</div></div></div>`
    );
  }

  // -------------------------------------------------------------------------
  // 3. VIEW LOAD TEMATIK
  // -------------------------------------------------------------------------
  function renderViewLoad() {
    const loadedCount = state.load.loadedParcels.length;

    return (
      `<div class="derivatif-mode-view mode-load-content">` +
      // KARTU 1: Pilih File Tabel Atribut Derivatif Hasil Ekspor
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc">` +
      `<strong style="font-size:13px;color:#0f172a">1. Pilih File Tabel Atribut Derivatif Hasil Ekspor:</strong>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      `<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">` +
      `<input type="text" readonly id="load-filepath-input" value="${esc(state.load.filePath)}" placeholder="Pilih file (.gpkg, .geojson, .shp, .dbf, .csv)..." style="flex:1;height:32px;font-size:12.5px;padding:3px 8px;border:1px solid #cbd5e1;border-radius:5px;background:#f8fafc">` +
      `<button type="button" class="btn btn-primary" data-act="browse-load-file" style="height:32px;background:#0284c7;border-color:#0284c7;font-size:12px;font-weight:700">📁 Browse...</button>` +
      `<button type="button" class="btn btn-soft" data-act="open-load-settings" style="height:32px;font-size:12px;font-weight:700;color:#166534;background:#f0fdf4;border-color:#86efac">⚙️ Pengaturan Baseline...</button>` +
      `<button type="button" class="btn btn-soft" data-act="reset-load" style="height:32px;font-size:12px;font-weight:700;color:#dc2626">🔄 Reset</button>` +
      `</div>` +
      (state.load.fileLoaded
        ? `<div style="font-size:11.5px;font-weight:700;color:#166534;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:5px;padding:6px 10px;margin-bottom:6px">` +
          `✓ Berkas berhasil dimuat! Ditemukan ${loadedCount} baris data atribut dengan relasi ID Bidang (EPSG:3857).` +
          `</div>`
        : '') +
      `<div style="font-size:11px;color:#64748b;font-style:italic">` +
      `Format didukung: GeoPackage (.gpkg), GeoJSON (.geojson), Shapefile/dBASE (.dbf/.shp), CSV (.csv). Berkas ini tanpa geometri namun memuat relasi ID_BIDANG.` +
      `</div>` +
      `</div></div>` +

      // KARTU 2: Visualisasi Geometri & Tabel Atribut Bidang
      `<div class="card" style="margin-bottom:12px;border:1px solid #cbd5e1;border-radius:8px">` +
      `<div class="card-head" style="padding:10px 14px;border-bottom:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:space-between">` +
      `<strong style="font-size:13px;color:#0f172a">2. Daftar Bidang Derivatif yang Berhasil Dihubungkan (${loadedCount} bidang):</strong>` +
      `<span style="background:#ecfdf5;color:#047857;font-size:11px;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid #a7f3d0">✓ Terhubung ke Geometri WMS</span>` +
      `</div>` +
      `<div style="padding:12px 14px">` +
      renderCanvasSvg('load') +
      `<div style="max-height:260px;overflow:auto;border:1px solid #cbd5e1;border-radius:6px;margin-top:10px">` +
      `<table class="stack" style="width:100%;font-size:11.5px;margin:0">` +
      `<thead><tr style="background:#f1f5f9;text-align:left"><th style="padding:6px 8px">ID Bidang</th><th style="padding:6px 8px">NIB</th><th style="padding:6px 8px">Desa</th><th style="padding:6px 8px">Kecamatan</th><th style="padding:6px 8px">Status Kumuh</th><th style="padding:6px 8px">Luas Terdampak</th><th style="padding:6px 8px">Rekomendasi</th></tr></thead>` +
      `<tbody>` +
      state.load.loadedParcels.map((p) =>
        `<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:6px 8px;font-weight:700"><code>${esc(p.id)}</code></td><td style="padding:6px 8px">${esc(p.nib)}</td><td style="padding:6px 8px">${esc(p.desa)}</td><td style="padding:6px 8px">${esc(p.kecamatan)}</td><td style="padding:6px 8px"><span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:4px;font-weight:700">${esc(p.status_kumuh)}</span></td><td style="padding:6px 8px">${esc(p.luas_terdampak)}</td><td style="padding:6px 8px;color:#475569">${esc(p.aksi)}</td></tr>`
      ).join('') +
      `</tbody></table></div></div></div></div>`
    );
  }

  // -------------------------------------------------------------------------
  // MODALS: WMS LOG & BASELINE SETTINGS
  // -------------------------------------------------------------------------
  function renderModals() {
    return (
      // Modal WMS Log
      `<div id="wms-log-modal" class="modal-backdrop" ${state.isi.wmsLogOpen ? '' : 'hidden'} style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:${state.isi.wmsLogOpen ? 'flex' : 'none'};align-items:center;justify-content:center;padding:20px">` +
      `<section class="card" style="width:min(620px,100%);max-height:85vh;overflow:auto;margin:auto">` +
      `<div class="card-head" style="padding:12px 16px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between">` +
      `<div><h3 style="margin:0;font-size:14px;color:#0f172a">📋 Diagnostik &amp; Log Koneksi WMS GeoServer</h3><p style="margin:2px 0 0 0;font-size:11px;color:#64748b">Rincian parameter koneksi layer baseline geospasial</p></div>` +
      `<button type="button" class="btn btn-soft btn-sm" data-act="close-wms-log">✕ Tutup</button>` +
      `</div>` +
      `<div style="padding:14px 16px;font-family:monospace;font-size:11.5px;background:#0f172a;color:#f8fafc;border-radius:0 0 8px 8px;line-height:1.6">` +
      `[19:04:12] INFO: Inisialisasi request GetCapabilities ke GeoServer ATR/BPN...<br>` +
      `[19:04:13] SUCCESS: Endpoint WMS terdeteksi (HTTP 200 OK)<br>` +
      `[19:04:13] INFO: Layer Typename: sppr:baseline_bidang_sleman<br>` +
      `[19:04:14] INFO: SRS/CRS Terpilih: EPSG:3857 (WGS 84 / Pseudo-Mercator)<br>` +
      `[19:04:14] INFO: Bounding Box: [110.312, -7.785, 110.428, -7.682]<br>` +
      `[19:04:15] SUCCESS: 4 bidang sampel berhasil dirender ke buffer kanvas (Latency: 142ms)` +
      `</div></section></div>` +

      // Modal Baseline Settings
      `<div id="baseline-settings-modal" class="modal-backdrop" ${state.load.settingsOpen ? '' : 'hidden'} style="position:fixed;inset:0;z-index:1000;background:rgba(15,23,42,.55);display:${state.load.settingsOpen ? 'flex' : 'none'};align-items:center;justify-content:center;padding:20px">` +
      `<section class="card" style="width:min(580px,100%);max-height:85vh;overflow:auto;margin:auto">` +
      `<div class="card-head" style="padding:12px 16px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between">` +
      `<div><h3 style="margin:0;font-size:14px;color:#0f172a">⚙️ Pengaturan Baseline Layer</h3><p style="margin:2px 0 0 0;font-size:11px;color:#64748b">Konfigurasi sumber baseline untuk join geometri bidang</p></div>` +
      `<button type="button" class="btn btn-soft btn-sm" data-act="close-load-settings">✕ Tutup</button>` +
      `</div>` +
      `<div style="padding:16px;font-size:12px">` +
      `<div class="field" style="margin-bottom:10px"><label style="font-weight:700">Nama Baseline CMS</label><input type="text" value="${esc(state.load.detectedBaseline.name)}" readonly style="height:30px;width:100%;padding:4px 8px;border:1px solid #cbd5e1;border-radius:4px;background:#f8fafc"></div>` +
      `<div class="field" style="margin-bottom:10px"><label style="font-weight:700">Typename WMS Geoportal</label><input type="text" value="${esc(state.load.detectedBaseline.typename)}" readonly style="height:30px;width:100%;padding:4px 8px;border:1px solid #cbd5e1;border-radius:4px;background:#f8fafc"></div>` +
      `<div class="field" style="margin-bottom:10px"><label style="font-weight:700">Kolom Kunci ID Bidang (Join Key)</label><input type="text" value="${esc(state.load.detectedBaseline.idField)}" readonly style="height:30px;width:100%;padding:4px 8px;border:1px solid #cbd5e1;border-radius:4px;background:#f8fafc"></div>` +
      `<div class="field" style="margin-bottom:14px"><label style="font-weight:700">Sistem Koordinat Acuan (CRS)</label><input type="text" value="${esc(state.load.detectedBaseline.crs)}" readonly style="height:30px;width:100%;padding:4px 8px;border:1px solid #cbd5e1;border-radius:4px;background:#f8fafc"></div>` +
      `<button type="button" class="btn btn-primary" data-act="close-load-settings" style="width:100%;font-weight:700">Terapkan Pengaturan</button>` +
      `</div></section></div>`
    );
  }

  // -------------------------------------------------------------------------
  // MAIN RENDER
  // -------------------------------------------------------------------------
  function render() {
    const view = $('#view');
    if (!view) return;

    const mode = state.currentMode;
    const isV2 = Boolean(IgtData.ROLES[state.role] && IgtData.ROLES[state.role].v2);
    const backUrl = isV2 ? '../beranda/index.html' : '../upload-data/index.html?tab=derivatif';

    const activeBtnStyle = (color, border) =>
      `background-color:${color};color:#ffffff;font-weight:700;font-size:12px;border:1px solid ${border};border-radius:6px;padding:6px 14px;cursor:pointer;flex:1;text-align:center`;
    const inactiveBtnStyle =
      `background-color:#ffffff;color:#475569;font-weight:600;font-size:12px;border:1px solid #cbd5e1;border-radius:6px;padding:6px 14px;cursor:pointer;flex:1;text-align:center`;

    const badgeModeText = mode === 'isi' ? 'Mode: Isi Tematik' : mode === 'create' ? 'Mode: Create Tematik' : 'Mode: Load Tematik';
    const badgeModeColor = mode === 'isi' ? '#eff6ff;color:#1d4ed8;border-color:#bfdbfe' : mode === 'create' ? '#faf5ff;color:#7c3aed;border-color:#e9d5ff' : '#ecfdf5;color:#047857;border-color:#a7f3d0';

    view.innerHTML = (
      `<div class="derivatif-bidang-v2-container" style="max-width:1000px;margin:0 auto">` +
      // Top Navigation Frame
      `<div style="display:flex;align-items:center;justify-content:space-between;background:#ffffff;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px;margin-bottom:10px">` +
      `<a class="btn btn-soft btn-sm" href="${backUrl}" style="font-weight:700;color:#2563eb">← Kembali ke Manajemen</a>` +
      `<div style="display:flex;align-items:center;gap:10px">` +
      `<strong style="font-size:14px;color:#0f172a">▤ Derivatif Per Bidang</strong>` +
      `<span style="font-size:11px;font-weight:700;padding:3px 8px;border-radius:12px;border:1px solid;background:${badgeModeColor}">${badgeModeText}</span>` +
      `</div></div>` +

      // 3 Tombol Utama di Atas
      `<div style="display:flex;gap:8px;background:#ffffff;border:1px solid #cbd5e1;border-radius:8px;padding:6px;margin-bottom:12px">` +
      `<button type="button" data-act="switch-mode" data-mode="isi" style="${mode === 'isi' ? activeBtnStyle('#2563eb', '#1d4ed8') : inactiveBtnStyle}">✍️ Isi Tematik</button>` +
      `<button type="button" data-act="switch-mode" data-mode="create" style="${mode === 'create' ? activeBtnStyle('#7c3aed', '#6d28d9') : inactiveBtnStyle}">➕ Create Tematik</button>` +
      `<button type="button" data-act="switch-mode" data-mode="load" style="${mode === 'load' ? activeBtnStyle('#059669', '#047857') : inactiveBtnStyle}">📂 Load Tematik</button>` +
      `</div>` +

      // Sub-View Content
      (mode === 'isi' ? renderViewIsi() : mode === 'create' ? renderViewCreate() : renderViewLoad()) +
      renderModals() +
      `</div>`
    );
  }

  // -------------------------------------------------------------------------
  // EVENT LISTENERS
  // -------------------------------------------------------------------------
  function bindEvents() {
    const view = $('#view');
    if (!view) return;

    view.addEventListener('click', (e) => {
      const target = e.target.closest('[data-act]');
      if (!target) return;
      const act = target.getAttribute('data-act');

      // Mode Switcher
      if (act === 'switch-mode') {
        state.currentMode = target.getAttribute('data-mode');
        render();
        return;
      }

      // Canvas Parcel Picking
      if (act === 'select-canvas-parcel') {
        state.activeParcelId = target.getAttribute('data-id');
        render();
        return;
      }

      if (act === 'toggle-picker') {
        state.isPicking = !state.isPicking;
        render();
        return;
      }

      // WMS Log Modal
      if (act === 'open-wms-log') {
        state.isi.wmsLogOpen = true;
        render();
        return;
      }
      if (act === 'close-wms-log') {
        state.isi.wmsLogOpen = false;
        render();
        return;
      }

      // Load Settings Modal
      if (act === 'open-load-settings') {
        state.load.settingsOpen = true;
        render();
        return;
      }
      if (act === 'close-load-settings') {
        state.load.settingsOpen = false;
        render();
        return;
      }

      // Refresh Buttons
      if (act === 'refresh-der' || act === 'refresh-bl') {
        alert('Daftar layer berhasil disegarkan dari Geoportal.');
        return;
      }

      // Load Baseline WMS
      if (act === 'load-baseline-isi' || act === 'load-baseline-create') {
        alert('Layer Baseline WMS berhasil dimuat ke kanvas peta.');
        render();
        return;
      }

      // Import Bidang
      if (act === 'import-bidang') {
        alert('Simulasi: Berkas bidang tersimpan berhasil diimpor ke sesi.');
        return;
      }

      // Browse Folder
      if (act === 'browse-folder') {
        const folder = prompt('Tentukan folder simpan:', '~/Documents/Derivatif_Kompilasi');
        if (folder) {
          if (state.currentMode === 'isi') state.isi.folder = folder;
          if (state.currentMode === 'create') state.create.folder = folder;
          render();
        }
        return;
      }

      // Save Bidang (Mode ISI)
      if (act === 'isi-save-bidang') {
        const parcel = getActiveParcel();
        // Collect form values
        document.querySelectorAll('[data-isi-field]').forEach((inp) => {
          const k = inp.getAttribute('data-isi-field');
          state.isi.formValues[k] = inp.value;
        });
        const summary = `${state.isi.formValues.status_kumuh || 'Diisi'} · Luas: ${state.isi.formValues.luas_terdampak_m2 || '0'} m²`;
        // Check if exists
        const exIdx = state.isi.sessionParcels.findIndex((p) => p.id === parcel.id);
        if (exIdx >= 0) {
          state.isi.sessionParcels[exIdx] = { ...parcel, summary, values: { ...state.isi.formValues } };
        } else {
          state.isi.sessionParcels.push({ ...parcel, summary, values: { ...state.isi.formValues } });
        }
        // Pick next unselected parcel
        const nextParcel = BASELINE_PARCELS.find((p) => !state.isi.sessionParcels.some((sp) => sp.id === p.id));
        if (nextParcel) state.activeParcelId = nextParcel.id;
        render();
        return;
      }

      // Delete Parcel (Mode ISI)
      if (act === 'delete-isi-parcel') {
        const idx = parseInt(target.getAttribute('data-index'), 10);
        state.isi.sessionParcels.splice(idx, 1);
        render();
        return;
      }

      // Execute Export (Mode ISI)
      if (act === 'execute-export-isi') {
        if (state.isi.sessionParcels.length === 0) {
          alert('Peringatan: Belum ada bidang terisi pada sesi ini.');
          return;
        }
        alert(`Sukses! ${state.isi.sessionParcels.length} bidang derivatif berhasil disimpan ke format .${state.isi.format}.\nSesi telah direset.`);
        state.isi.sessionParcels = [];
        render();
        return;
      }

      // Add Custom Column (Mode CREATE)
      if (act === 'add-custom-col') {
        const colNum = state.create.customColumns.length + 1;
        state.create.customColumns.push({ name: 'kolom_baru_' + colNum, type: 'Teks', length: 50, value: '' });
        render();
        return;
      }

      // Remove Custom Column (Mode CREATE)
      if (act === 'remove-custom-col') {
        const idx = parseInt(target.getAttribute('data-idx'), 10);
        state.create.customColumns.splice(idx, 1);
        render();
        return;
      }

      // Save Bidang (Mode CREATE)
      if (act === 'create-save-bidang') {
        const parcel = getActiveParcel();
        // Read latest column values
        document.querySelectorAll('#table-custom-cols tbody tr').forEach((row, i) => {
          if (state.create.customColumns[i]) {
            const nameInp = row.querySelector('[data-col-field="name"]');
            const typeSel = row.querySelector('[data-col-field="type"]');
            const lenInp = row.querySelector('[data-col-field="length"]');
            const valInp = row.querySelector('[data-col-field="value"]');
            if (nameInp) state.create.customColumns[i].name = nameInp.value;
            if (typeSel) state.create.customColumns[i].type = typeSel.value;
            if (lenInp) state.create.customColumns[i].length = lenInp.value;
            if (valInp) state.create.customColumns[i].value = valInp.value;
          }
        });
        const summary = state.create.customColumns.map((c) => `${c.name}=${c.value || '-'}`).join(', ');
        const exIdx = state.create.sessionParcels.findIndex((p) => p.id === parcel.id);
        if (exIdx >= 0) {
          state.create.sessionParcels[exIdx] = { ...parcel, summary };
        } else {
          state.create.sessionParcels.push({ ...parcel, summary });
        }
        const nextParcel = BASELINE_PARCELS.find((p) => !state.create.sessionParcels.some((sp) => sp.id === p.id));
        if (nextParcel) state.activeParcelId = nextParcel.id;
        render();
        return;
      }

      // Delete Parcel (Mode CREATE)
      if (act === 'delete-create-parcel') {
        const idx = parseInt(target.getAttribute('data-index'), 10);
        state.create.sessionParcels.splice(idx, 1);
        render();
        return;
      }

      // Execute Export (Mode CREATE)
      if (act === 'execute-export-create') {
        if (state.create.sessionParcels.length === 0) {
          alert('Peringatan: Belum ada bidang terisi pada sesi ini.');
          return;
        }
        alert(`Sukses! ${state.create.sessionParcels.length} bidang derivatif kustom berhasil disimpan ke format .${state.create.format}.\nSesi telah direset.`);
        state.create.sessionParcels = [];
        render();
        return;
      }

      // Browse Load File (Mode LOAD)
      if (act === 'browse-load-file') {
        const path = prompt('Masukkan path berkas tabel derivatif:', 'atribut_kawasan_kumuh_sleman_2026.gpkg');
        if (path) {
          state.load.filePath = path;
          state.load.fileLoaded = true;
          render();
        }
        return;
      }

      // Reset Load (Mode LOAD)
      if (act === 'reset-load') {
        state.load.filePath = '';
        state.load.fileLoaded = false;
        render();
        return;
      }
    });

    view.addEventListener('change', (e) => {
      if (e.target.id === 'combo-derivatif-layer') {
        state.isi.selectedLayerId = e.target.value;
        const l = DERIVATIF_CMS_LAYERS.find((x) => x.id === e.target.value);
        if (l) {
          state.isi.formValues = {};
          l.fields.forEach((f) => { state.isi.formValues[f.name] = f.default || (f.options ? f.options[0] : ''); });
        }
        render();
      }
      if (e.target.id === 'combo-create-baseline') {
        state.create.selectedBaselineId = e.target.value;
        render();
      }
      if (e.target.name === 'isi-format') {
        state.isi.format = e.target.value;
      }
      if (e.target.name === 'create-format') {
        state.create.format = e.target.value;
      }
    });
  }

  // -------------------------------------------------------------------------
  // INITIALIZATION
  // -------------------------------------------------------------------------
  function init(role) {
    state.role = role || 'operator';
    const params = new URLSearchParams(window.location.search);
    const requestedMode = params.get('mode');
    const legacyStep = params.get('step');
    if (requestedMode === 'create') state.currentMode = 'create';
    else if (requestedMode === 'load' || legacyStep === '6') state.currentMode = 'load';
    else state.currentMode = 'isi';

    render();
    bindEvents();
  }

  return { init };
})();

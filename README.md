# IGT-PR QGIS UI Prototype

HTML/CSS/JavaScript **UI mockups** for the IGT-PR QGIS plugin. The root page previews each role inside a portrait 3:4 panel that imitates a QGIS plugin dock.

> All QGIS actions (WMS/WFS display, Load Baseline, Tampilkan di Canvas, Verifikasi Topologi, upload, run model, approve/reject, etc.) are **simulations**. There is no backend, authentication, database, WMS/WFS endpoint, or real QGIS integration. Example records and counts are illustrative.

## Information architecture

Browsing integrated data is separate from uploading and managing submissions.

| Page | Purpose |
| --- | --- |
| Dashboard | Repository overview: number of datasets that are **Terkompilasi** and **Terintegrasi** (total and per category). Below it, one *Lihat peta IGT* button per catalog (4, the same for every role) and one *Upload Data* button. This is the navigation hub. No upload controls on the page itself. |
| IGT Pertanahan | Catalog of integrated datasets (berbasis bidang) |
| IGT Tata Ruang | Catalog of integrated datasets (berbasis kawasan) |
| IGT Derivatif | Catalog of integrated derivative layers |
| IGT Lainnya | Catalog of integrated external layers |
| Upload Data | Submission dashboard, one tab per authorized category, upload controls and the submission table |

### Permissions

| Role | View catalogs | Upload Data tabs |
| --- | --- | --- |
| Superadmin | all four (Pertanahan, Tata Ruang, Derivatif, Lainnya) | all four |
| Admin | all four | Pertanahan, Tata Ruang, Derivatif (no Lainnya) |
| Operator | all four | Pertanahan, Tata Ruang, Derivatif (no Lainnya) |
| Umum | all four | IGT Derivatif only |

Every role gets the same Dashboard buttons (the four catalogs and Upload Data). Superadmin, Admin and Operator can reach Model Builder from the Dashboard; Umum cannot. Umum's Upload Data page shows only its own submissions, so it is empty until a (simulated) upload is made. There is no top menu or tab bar: every page except the Dashboard has a *← Kembali ke Dashboard* button. No role has a Verifikasi Data menu.

Permissions live in `shared/igt-data.js`. Two permission levels exist: `view` (catalogs) and `upload` (Upload Data tabs and actions). The Upload Data tabs and `?tab=` are checked against `upload`, so `?tab=lainnya` is ignored for Admin/Operator. Managing IGT Lainnya (upload layer, Hapus) stays Superadmin only.

### Catalog pages
Columns: **Nama IGT**, **Tanggal Update**, **Tampilkan WMS**, **Tampilkan WFS**. They list only records with status `Terintegrasi` and contain no upload or approval controls. The WMS and WFS buttons are labelled simulations: they show a message saying which service type would be added to QGIS and that no real service is connected. No service URLs exist in this repository. An empty category shows an empty state; a search with no match shows a different one.

### Upload Data page
1. **Submission dashboard** (Total pengajuan, Proses, Menunggu integrasi, Perlu perhatian) for the categories the role may use.
2. **Category tabs**: IGT Pertanahan, IGT Tata Ruang, IGT Derivatif, and IGT Lainnya (Superadmin only; Admin and Operator can still view it in the catalog). The tab can be preselected with `?tab=pertanahan|tata-ruang|derivatif|lainnya`.
3. **Upload controls and submission table** (ID Pengajuan, Layer Target, Tanggal Upload, Status, Aksi) for the selected tab:

| Tab | Upload controls | Row actions |
| --- | --- | --- |
| IGT Pertanahan | Load Baseline (only here) and Upload Data | Detail; Verifikasi Topologi on `Proses` rows (Admin, Superadmin); Revisi on `Revisi` rows (Operator) |
| IGT Tata Ruang | Upload form (dropzone, tema, nama layer, wilayah, deskripsi) | same as Pertanahan |
| IGT Derivatif | Admin: Upload Derivatif (goes straight to `Disetujui`). Umum: Upload Derivatif (becomes `Proses`). Operator: Derivative Kawasan / Bidang workflows (`legacy/`). Superadmin: review only | Detail; Setujui and Tolak on `Proses` rows (Admin, Superadmin) |
| IGT Lainnya | Upload layer (simulated; layers are added through QGIS) | Hapus |

### Statuses and data model
- One record in `shared/igt-data.js` is one dataset plus its latest submission, so counting records counts datasets. Re-submissions of an integrated dataset are not modelled.
- IGT Pertanahan / Tata Ruang: `Proses` → `Terkompilasi` → `Terintegrasi`; `Revisi` = returned to the Operator. *Verifikasi Topologi* moves a row to `Terkompilasi`.
- IGT Derivatif: `Proses` → `Disetujui` → `Terintegrasi`; `Ditolak` = rejected. Admin uploads start as `Disetujui`; Umum uploads start as `Proses` and wait for an Admin or Superadmin decision.
- IGT Lainnya: external layers are available immediately (`Terintegrasi`).
- Moving from `Terkompilasi`/`Disetujui` to `Terintegrasi` happens outside the mockup, so no button does it. Derivative layers that are only `Disetujui` count in neither Dashboard total.
- State changes (topology, approve/reject, upload, delete) live only in the open page; reloading restores the sample data. The Dashboard and catalogs always show the sample data.

### Detail pages are shared by query string
`roles/operator/igt-utama-detail/` and `roles/operator/layer-derivatif-detail/` are the detail pages for all roles, opened from the Upload Data table. The role is chosen with `?id=<n>&role=<superadmin|admin|operator>` (an unknown role falls back to Operator). The role decides the header chip, breadcrumb, back links (to that role's Dashboard and Upload Data tab) and which actions are shown.

`shared/model-builder/index.html` accepts `?role=superadmin|admin` so its back link returns to that role's Dashboard (default: Operator).

## Folder structure

```text
igtpr-qgis-ui/
├── index.html                  # Role preview (Superadmin / Admin / Operator / Umum), iframe in a 3:4 panel
├── styles.css                  # Shared design system
├── app.js                      # Shared interactions used by the legacy pages (tabs, filtering, simulated actions)
├── README.md
├── CLAUDE.md
├── tools/
│   └── check_links.py          # Static check that every local link/iframe/script path resolves
├── roles/
│   ├── {superadmin,admin}/{beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html
│   ├── operator/
│   │   ├── {beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html
│   │   ├── igt-utama-detail/index.html          # Shared detail page (all roles, ?role=)
│   │   └── layer-derivatif-detail/index.html    # Shared detail page (all roles, ?role=)
│   └── umum/{beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html   # public role
├── shared/
│   ├── igt-data.js             # Sample records, categories, role permissions
│   ├── igt-app.js              # Navigation, Dashboard, catalog and Upload Data logic
│   └── model-builder/index.html
└── legacy/                     # Earlier pages kept for reference only
    └── 02-beranda-superadmin.html … 08-verifikasi-data.html
```

Each role page is a thin shell: it loads `shared/igt-data.js` and `shared/igt-app.js` and calls `IgtApp.dashboard(role)`, `IgtApp.catalog(role, category)` or `IgtApp.upload(role)`.

### Legacy pages
`legacy/` holds the original numbered pages (`02`–`08`) with the old desktop sidebar. They are not part of the role navigation; their sidebar links now point to the matching Upload Data tab. The only link into `legacy/` from a role page is Operator → Upload Data → IGT Derivatif (Derivative Kawasan / Bidang workflows), because those workflow pages were never replaced.

## Shared styling
- Tables marked `class="stack"` (with a `data-label` on each cell) turn into labelled blocks below 600px of panel width, so lists do not scroll sideways in the portrait preview. `class="compact"` keeps a real table with tighter padding.
- Pages shown inside the 3:4 panel opt in to the compact layout with `<body class="panel ...">` (`panel-dash`, `panel-home`, `panel-list`, `panel-detail`).
- Navigation: the Dashboard uses `.menu-buttons` (one column) below its overview, and Model Builder is a small link under them. Other pages have a back button in the page header instead of a menu bar.

## Preview locally
No build step. Open `index.html` directly in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

Use the role drawer on the left to switch between Superadmin, Admin, Operator and Umum.

## Checks
```bash
python3 tools/check_links.py
```
Exits non-zero if any local `href`, `src`, iframe or JS-string path points to a missing file. The Dashboard buttons are built in JavaScript and are therefore not covered by this script; open each role's Dashboard to verify them.

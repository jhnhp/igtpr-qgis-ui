# IGT-PR QGIS UI Prototype

HTML/CSS/JavaScript **UI mockups** for the IGT-PR QGIS plugin. The root page previews each role inside a portrait 3:4 panel that imitates a QGIS plugin dock.

> All QGIS actions (Load Baseline, Tampilkan di Canvas, Verifikasi Topologi, upload, run model, approve/reject, etc.) are **simulations**. There is no backend, authentication, database, or real QGIS integration. Example records and counts are illustrative.

## Folder structure

```text
igtpr-qgis-ui/
├── index.html                  # Role preview (Superadmin / Admin / Operator / Umum), iframe in a 3:4 panel
├── styles.css                  # Shared design system
├── app.js                      # Shared interactions (tabs, filtering, file selection, simulated actions)
├── README.md
├── tools/
│   └── check_links.py          # Static check that every local link/iframe/script path resolves
├── roles/
│   ├── superadmin/
│   │   ├── beranda/index.html
│   │   ├── igt-utama/index.html
│   │   ├── igt-derivatif/index.html
│   │   └── igt-lainnya/index.html      # IGT Lainnya (Eksternal) — Superadmin only
│   ├── admin/
│   │   ├── beranda/index.html
│   │   ├── igt-utama/index.html
│   │   └── igt-derivatif/index.html
│   ├── operator/
│   │   ├── beranda/index.html
│   │   ├── igt-utama/index.html
│   │   ├── igt-utama-bidang/index.html
│   │   ├── igt-utama-kawasan/index.html
│   │   ├── igt-utama-detail/index.html
│   │   ├── igt-derivatif/index.html
│   │   └── layer-derivatif-detail/index.html
│   └── umum/                           # Empty: no Umum page exists yet (placeholder in index.html)
├── shared/
│   └── model-builder/index.html        # Model Builder, used by Superadmin, Admin and Operator
└── legacy/                             # Earlier pages kept for reference only
    ├── 02-beranda-superadmin.html
    ├── 03-katalog-data.html
    ├── 04-pengolahan-data.html
    ├── 05-tematik-derivative.html
    ├── 06-derivative-kawasan.html
    ├── 07-derivative-bidang.html
    └── 08-verifikasi-data.html
```

## Role pages

| Role | Pages |
| --- | --- |
| Superadmin | Beranda, IGT Utama, IGT Derivatif, IGT Lainnya (Eksternal), Model Builder |
| Admin | Beranda, IGT Utama, IGT Derivatif, Model Builder. No IGT Lainnya (Eksternal) and no Verifikasi Data menu |
| Operator | Beranda, IGT Utama (+ Bidang / Kawasan), IGT Derivatif, Model Builder |
| Umum | Placeholder only |

### Detail pages are shared by query string
`roles/operator/igt-utama-detail/` and `roles/operator/layer-derivatif-detail/` are the single detail pages for all roles. The role is chosen with `?id=<n>&role=<superadmin|admin>` (no `role` means Operator). The role decides the header chip, breadcrumb, back links (to that role's own Beranda/list) and which actions are shown. Example: `roles/operator/igt-utama-detail/index.html?id=0&role=admin`.

`shared/model-builder/index.html` accepts `?role=superadmin|admin` so its back link returns to that role's Beranda (default: Operator).

### Legacy pages
`legacy/` holds the original numbered pages (`02`–`08`) with the old sidebar layout. They are not part of the role navigation. Their sidebar links point to each other and to the Operator pages. The only remaining links into `legacy/` are the two derivative workflow shortcuts (Derivative Kawasan / Bidang) in Operator IGT Derivatif, because those workflow pages were never replaced.

## Shared assets
- `styles.css` and `app.js` live at the repository root; every page references them with a relative path from its own folder (e.g. `../../../styles.css`).
- Pages shown inside the 3:4 panel opt in to the compact layout in `styles.css` with `<body class="panel ...">` (`panel-dash`, `panel-home`, `panel-list`, `panel-detail` add stat cards, Beranda, list and detail rules). Only page-specific rules stay in each page's own `<style>`.
- Tables use `data-href` / plain links for list-to-detail navigation; `app.js` handles tabs (`data-tab`), search filtering (`data-filter`) and simulated actions (`data-action`).

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
Exits non-zero if any local `href`, `src`, iframe or JS-built path points to a missing file.

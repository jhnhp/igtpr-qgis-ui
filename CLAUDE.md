# Claude Code Instructions — IGT-PR QGIS UI Mockup

## Project context

This repository contains HTML/CSS/JavaScript **UI mockups for a QGIS plugin**. It is not a conventional website. Preserve the compact portrait 3:4 QGIS-panel preview and existing mockup style. Buttons and QGIS-related actions are simulated; do not invent backend, authentication, database, or real QGIS integration.

## General rules

- Inspect the repository, current branch, remotes, and `git status` before editing.
- Preserve unrelated and uncommitted user changes. Never discard user work.
- Make requested changes directly; do not stop after writing a plan.
- Keep existing UI content, sample records, styling, interactions, and role distinctions unless the task explicitly requests otherwise.
- Validate paths and navigation after moving files. Never claim a change or test succeeded unless it actually did.
- Do not force-push. If remote changes or authentication block the push, explain the issue and leave user data safe.

## Information architecture (current)

Browsing integrated data is separate from managing submissions. Keep it that way.

- Navigation has no tab/menu bar on any page. The Dashboard is the hub with buttons to IGT Pertanahan, IGT Tata Ruang, IGT Derivatif, IGT Lainnya and Upload Data; every other page has a single "← Kembali ke Dashboard" back button, and the shared detail pages go back to the role's Dashboard or Upload Data tab. Do not reintroduce a top menu.
- Permissions have two levels in `shared/igt-data.js`: `view` (browse a catalog) and `upload` (Upload Data tab and its actions). Every role may view all four catalogs, including IGT Lainnya. Upload and management of IGT Lainnya (upload layer, Hapus) is Superadmin only, so Admin and Operator get no IGT Lainnya tab in Upload Data. Admin has no Verifikasi Data menu. Umum (public users) may view all four catalogs but can only upload IGT Derivatif: its submissions start as `Proses`, it sees only its own submissions, and it has no Model Builder. Never expose a restricted action by only hiding its label: leave it out of the generated UI and guard the page.
- Statuses differ per category (see `shared/igt-data.js`). Only IGT Pertanahan and IGT Tata Ruang use Proses → Terkompilasi → Terintegrasi (+ Revisi). IGT Derivatif uses Diajukan, Disetujui, Ditolak and Kadaluwarsa. Everything uploaded to IGT Lainnya is available immediately (status Tersedia). Do not give Derivatif or Lainnya a Terkompilasi/Terintegrasi status.
- Catalog pages (the four IGT menus) list only records in their category's catalog status (Terintegrasi for Pertanahan/Tata Ruang, Disetujui for Derivatif, all Tersedia for Lainnya) with columns Nama IGT, Tanggal Update, Tampilkan WMS, Tampilkan WFS. No upload, approval or rejection controls there. No real WMS/WFS URLs exist, so those buttons are labelled simulations; do not invent endpoints.
- Upload Data holds all upload and submission management: submission dashboard, one tab per authorized category, upload controls (Load Baseline only under IGT Pertanahan), and the submission table with role-specific actions (Verifikasi Topologi, Revisi, Setujui/Tolak, Hapus, Detail). Admin derivative uploads enter `Disetujui` directly.
- The Dashboard shows repository status (Terkompilasi / Terintegrasi counts over Pertanahan and Tata Ruang only, computed from `shared/igt-data.js`), not submissions. Below the overview are one button per catalog (4, the same for every role) plus one Upload Data button. Model Builder is a small link under them.
- Records, statuses and permissions live only in `shared/igt-data.js`. Role pages are thin shells that call `IgtApp.dashboard`, `IgtApp.catalog` or `IgtApp.upload`. Detail pages are shared (`roles/operator/*-detail/`) and keep the role through `?role=`.
- Operator only: Upload Derivatif Bidang is a dedicated six-step workflow page (`roles/operator/derivatif-bidang/`, logic in `shared/derivatif-bidang.js`, guarded by `derivatifWorkflow` in `shared/igt-data.js`); Upload Derivatif Kawasan still links to `legacy/06`. Everything in it is simulated and it creates no submission row.
- The preview drawer in root `index.html` has a Login entry next to the four roles (selected first). `shared/login/index.html` is the same for every role; its LOGIN button is simulated (no authentication). Its illustration is a generated PNG: change `tools/make_login_illustration.py` and rerun it (it writes both `shared/login/illustration.png` and the plugin copy) instead of editing the PNG. `qgis-plugin-example/` holds a standalone Qt version of that page as an example QGIS plugin, built at the user's request; it is not part of the HTML mockup navigation.
- After changing pages or navigation, run `python3 tools/check_links.py` and open each role's pages: the Dashboard buttons are built in JavaScript and the script cannot see them.

## Folder-structure refactor task

When asked to organize the repository, carry out the complete refactor below. Do not merely create empty folders or duplicate pages.

### Structure (originally the refactor target; updated for the current information architecture)

```text
igtpr-qgis-ui/
├── index.html
├── styles.css
├── app.js
├── README.md
├── CLAUDE.md
├── tools/{check_links.py,make_login_illustration.py}
├── roles/
│   ├── {superadmin,admin}/{beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html
│   ├── operator/
│   │   ├── {beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html
│   │   ├── derivatif-bidang/index.html
│   │   ├── igt-utama-detail/index.html
│   │   └── layer-derivatif-detail/index.html
│   └── umum/{beranda,igt-pertanahan,igt-tata-ruang,igt-derivatif,igt-lainnya,upload-data}/index.html
├── shared/
│   ├── igt-data.js
│   ├── igt-app.js
│   ├── derivatif-bidang.js
│   ├── login/index.html
│   └── model-builder/index.html
├── qgis-plugin-example/igtpr_login_example/
└── legacy/
    ├── 02-beranda-superadmin.html
    ├── 03-katalog-data.html
    ├── 04-pengolahan-data.html
    ├── 05-tematik-derivative.html
    ├── 06-derivative-kawasan.html
    ├── 07-derivative-bidang.html
    └── 08-verifikasi-data.html
```

Adjust placement only if repository inspection reveals a clear reason; document any deviation. Keep the root entry point and shared assets at the root. Legacy pages should be retained for reference, not added to primary navigation unless the existing design requires it. (Historical: `roles/umum/` was kept empty while no Umum page existed; it now holds the Umum role's pages.)

### Refactor requirements

1. Inspect all repository files and references before editing, including `index.html`, `styles.css`, `app.js`, every HTML page, and the README.
2. Move the actual existing pages into the target folders. Remove their old root-level copies after verifying the new copies exist and work.
3. Update all paths correctly from each new file location:
   - role-preview iframe sources in root `index.html`;
   - internal links and back-to-dashboard links;
   - list-to-detail links and query strings such as `?id=0&role=admin`;
   - relative CSS, JavaScript, image, icon, and other asset references;
   - local file paths embedded in JavaScript or dynamically generated markup.
4. Preserve the 3:4 portrait role preview and the four roles: Superadmin, Admin, Operator, and Umum.
5. Keep role-specific pages separate. Admin pages must point to Admin pages, not Superadmin pages. (Historical: IGT Lainnya (Eksternal) was once Superadmin-only. Viewing it is now allowed for every role; only upload and management stay Superadmin-only.) Admin must not have a **Verifikasi Data** menu or link in its dashboard.
6. Preserve existing content, sample records, distinct IGT Utama details, tabs, query parameters, and simulated actions. This is a QGIS plugin mockup, not a redesign or real QGIS integration.
7. Keep `model-builder.html` as a shared module at `shared/model-builder/index.html`, preserving its behavior.
8. Update `README.md` to document the actual final folder tree, role pages, shared assets, how to preview locally, and the fact that QGIS actions are simulations.

### Required verification

Before committing:

- Run `git status` and inspect the diff. Do not include unrelated user changes.
- Verify the intended HTML pages exist in the new locations and moved pages no longer remain as root-level duplicates.
- Search all HTML and JavaScript for obsolete filenames and broken local references.
- Check every local link, iframe target, stylesheet, and script path resolves.
- Run practical automated/static HTML checks. If browser testing is available, test the role selector and main navigation flows; otherwise explicitly say browser testing was not performed.
- Fix issues found before committing.

### Commit and push

Once the refactor and checks are complete:

1. Stage only the intended refactor changes.
2. Commit with message: `refactor: organize QGIS mockup pages by role`.
3. Push to the configured remote and current working branch, without force-pushing.
4. Verify that the remote branch contains the commit.
5. Report the final tree, moved files, updated references, tests and results, commit hash, and whether the push succeeded.
6. Never report completion unless the files were truly moved, references checked, and commit/push succeeded.

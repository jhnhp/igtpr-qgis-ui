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

## Folder-structure refactor task

When asked to organize the repository, carry out the complete refactor below. Do not merely create empty folders or duplicate pages.

### Target structure

```text
igtpr-qgis-ui/
├── index.html
├── styles.css
├── app.js
├── README.md
├── roles/
│   ├── superadmin/
│   │   ├── beranda/index.html
│   │   ├── igt-utama/index.html
│   │   ├── igt-derivatif/index.html
│   │   └── igt-lainnya/index.html
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
│   └── umum/
├── shared/
│   └── model-builder/index.html
└── legacy/
    ├── 02-beranda-superadmin.html
    ├── 03-katalog-data.html
    ├── 04-pengolahan-data.html
    ├── 05-tematik-derivative.html
    ├── 06-derivative-kawasan.html
    ├── 07-derivative-bidang.html
    └── 08-verifikasi-data.html
```

Adjust placement only if repository inspection reveals a clear reason; document any deviation. Keep the root entry point and shared assets at the root. Legacy pages should be retained for reference, not added to primary navigation unless the existing design requires it. Keep `roles/umum/` empty if there is no existing Umum page; do not invent a feature to fill it.

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
5. Keep role-specific pages separate. Admin pages must point to Admin pages, not Superadmin pages. The Superadmin-only **IGT Lainnya (Eksternal)** module must not appear in the Admin dashboard. Admin must not have a **Verifikasi Data** menu or link in its dashboard.
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

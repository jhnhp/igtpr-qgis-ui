// Shared interactions for the IGT-PR QGIS UI mockup.
// Every QGIS-related action is a simulation: it only shows a toast.

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const ACTION_MESSAGES = {
  'load-baseline': 'Load Baseline siap disambungkan ke layer QGIS.',
  run: 'Parameter valid. Proses ini masih berupa prototipe UI.',
  approve: 'Aksi persetujuan masih berupa prototipe.',
  reject: 'Catatan perbaikan perlu dikonfigurasi sebelum dikirim.',
  export: 'Ekspor akan tersedia setelah data terhubung.',
};

document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initTabs();
  initFilters();
  initActions();
  initFileInput();
  initClickableRows();
});

// Highlight the sidebar link that matches <body data-page="...">.
function initNav() {
  const page = document.body.dataset.page || 'operator';
  $$('.nav a').forEach((link) => {
    if (link.dataset.page === page) link.classList.add('active');
  });
}

// <div data-tabs> with [data-tab] buttons and [data-panel] sections.
function initTabs() {
  $$('[data-tab]').forEach((button) => {
    button.addEventListener('click', () => {
      const group = button.closest('[data-tabs]');
      $$('[data-tab]', group).forEach((tab) => tab.classList.toggle('active', tab === button));
      $$('[data-panel]', group).forEach((panel) => {
        panel.hidden = panel.dataset.panel !== button.dataset.tab;
      });
    });
  });
}

// <input data-filter="#table"> hides table body rows that do not match the text.
function initFilters() {
  $$('[data-filter]').forEach((input) => {
    input.addEventListener('input', () => {
      const target = $(input.dataset.filter);
      if (!target) return;
      const query = input.value.toLowerCase();
      $$('tbody tr', target).forEach((row) => {
        row.hidden = !row.innerText.toLowerCase().includes(query);
      });
    });
  });
}

function initActions() {
  $$('[data-action]').forEach((button) => {
    button.addEventListener('click', () => {
      const { action } = button.dataset;
      if (action === 'upload') $('#fileInput')?.click();
      else if (Object.hasOwn(ACTION_MESSAGES, action)) toast(ACTION_MESSAGES[action]);
    });
  });
}

function initFileInput() {
  const input = $('#fileInput');
  if (!input) return;
  input.addEventListener('change', () => {
    const label = $('#fileName');
    if (label && input.files[0]) label.textContent = input.files[0].name;
  });
}

// Table rows with data-href behave like links (mouse and keyboard).
function initClickableRows() {
  $$('tbody tr[data-href]').forEach((row) => {
    const open = () => { location.href = row.dataset.href; };
    row.tabIndex = 0;
    row.addEventListener('click', open);
    row.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') open();
    });
  });
}

function toast(message) {
  let el = $('#toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toast';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    Object.assign(el.style, {
      position: 'fixed',
      bottom: '22px',
      right: '22px',
      zIndex: 9999,
      background: '#102b59',
      color: '#fff',
      padding: '13px 17px',
      borderRadius: '9px',
      boxShadow: '0 8px 28px #102b5930',
      fontSize: '12px',
      maxWidth: '340px',
      transition: 'opacity .2s',
    });
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.style.opacity = '1';
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { el.style.opacity = '0'; }, 3200);
}

// Status badge markup used by table renderers.
function status(label) {
  const cls = label === 'Disetujui' ? 'ok'
    : label === 'Perlu perbaikan' ? 'fix'
    : label === 'Dalam verifikasi' ? 'info'
    : '';
  return `<span class="status ${cls}">${label}</span>`;
}

# -*- coding: utf-8 -*-
"""Halaman Beranda / Dashboard (Mockup V2), responsif terhadap lebar dock.

Padanan dengan roles/*2/beranda/index.html:
- hero + filter tahun   : berdampingan >= 640 px, bertumpuk di bawahnya
- kartu statistik       : 2 kolom >= 560 px, 1 kolom di bawahnya
- tombol Katalog IGT    : 2 kolom >= 620 px
- kartu Unggah/Manajemen: 2 kolom >= 760 px
"""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QComboBox, QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from .catalog_page import CatalogPage
from .data import DATASETS, SUBMISSIONS
from .ui_kit import (
    ClickableCard, HeroHeader, HubItem, ResponsiveGrid, ResponsivePage, card, field, icon_badge,
    icon_label, label, pill,
)


class StatCard(QFrame):
    """Kartu ringkasan angka (Terkompilasi / Terintegrasi / dst.)."""

    def __init__(self, kind, title, pill_text, pill_kind, icon_key, icon_color, icon_bg, parent=None):
        super().__init__(parent)
        self.setProperty('card', kind)
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(16, 14, 16, 14)
        self.lay.setSpacing(10)
        info = QVBoxLayout()
        info.setSpacing(3)
        info.addWidget(label(title.upper(), 'statLabel', True, self))
        self.num = label('0', 'statNum', False, self)
        info.addWidget(self.num)
        info.addWidget(pill(pill_text, pill_kind, self), 0, Qt.AlignmentFlag.AlignLeft)
        self.lay.addLayout(info, 1)
        self.lay.addWidget(icon_badge(icon_key, icon_color, icon_bg, 44, 22, 12, self), 0, Qt.AlignmentFlag.AlignVCenter)

    def set_value(self, value):
        self.num.setText(str(value))

    def apply_width(self, width):
        m = 10 if width < 280 else 16
        self.lay.setContentsMargins(m, 10 if width < 280 else 14, m, 10 if width < 280 else 14)

    def minimumSizeHint(self):
        return QSize(100, 50)


class HubCard(QFrame):
    """Kartu hub: kepala berwarna (ikon, judul, deskripsi) dan daftar tombol HubItem."""

    itemClicked = pyqtSignal(str)

    def __init__(self, kind, head_kind, icon_key, icon_color, icon_bg, title, desc, items,
                 item_kind='hub', breakpoints=((0, 1),), stacked_head=False, parent=None):
        super().__init__(parent)
        self.setProperty('card', kind)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 12)
        lay.setSpacing(12)

        self.head = card(head_kind, self)
        h_lay = QVBoxLayout(self.head) if stacked_head else QHBoxLayout(self.head)
        h_lay.setContentsMargins(16, 14, 16, 14)
        h_lay.setSpacing(8 if stacked_head else 14)
        badge = icon_badge(icon_key, icon_color, icon_bg, 44, 22, 12, self.head)
        texts = QVBoxLayout()
        texts.setSpacing(3)
        texts.addWidget(label(title, 'h2', True, self.head))
        texts.addWidget(label(desc, 'muted', True, self.head))
        if stacked_head:
            top = QHBoxLayout()
            top.addWidget(badge)
            top.addStretch(1)
            top.addWidget(icon_label('chevron-right', icon_color, 16, self.head))
            h_lay.addLayout(top)
            h_lay.addLayout(texts)
        else:
            h_lay.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
            h_lay.addLayout(texts, 1)
        lay.addWidget(self.head)

        self.grid = ResponsiveGrid(list(breakpoints), 10, self)
        for key, item_icon, text, color in items:
            item = HubItem(item_icon, text, color, item_kind, parent=self.grid)
            item.clicked.connect(lambda k=key: self.itemClicked.emit(k))
            self.grid.add(item)
        wrap = QHBoxLayout()
        wrap.setContentsMargins(12, 0, 12, 0)
        wrap.addWidget(self.grid)
        lay.addLayout(wrap)

    def apply_width(self, width):
        self.grid.apply_width(width)
        m = 10 if width < 280 else 16
        if hasattr(self, 'head'):
            self.head.layout().setContentsMargins(m, 10 if width < 280 else 14, m, 10 if width < 280 else 14)

    def minimumSizeHint(self):
        return QSize(100, 60)


class WideCard(ClickableCard):
    """Kartu satu baris yang bisa diklik (Model Builder, Logout)."""

    def __init__(self, kind, icon_key, icon_color, icon_bg, title, desc, title_cls, desc_cls, parent=None):
        super().__init__(kind, parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(14)
        lay.addWidget(icon_badge(icon_key, icon_color, icon_bg, 44, 22, 12, self), 0, Qt.AlignmentFlag.AlignVCenter)
        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.addWidget(label(title, title_cls, True, self))
        texts.addWidget(label(desc, desc_cls, True, self))
        lay.addLayout(texts, 1)
        lay.addWidget(icon_label('chevron-right', icon_color, 16, self), 0, Qt.AlignmentFlag.AlignVCenter)

    def minimumSizeHint(self):
        return QSize(100, 48)


class DashboardPage(ResponsivePage):
    """Dashboard V2: hero, statistik repositori, hub katalog, hub unggah/manajemen, Model Builder."""

    openCatalogRequested = pyqtSignal(str)       # 'pertanahan', 'tata-ruang', 'derivatif', 'lainnya'
    openManagementRequested = pyqtSignal(str)    # 'igt-utama', 'derivatif', 'lainnya'
    openUploadRequested = pyqtSignal(str)        # kategori unggah
    openModelBuilderRequested = pyqtSignal()
    logoutRequested = pyqtSignal()
    wmsRequested = pyqtSignal(dict, object)      # (dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, object)      # (dataset, sublayer or None)

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__('dashboardPage', parent)
        self.current_role = current_role

        # 1. Hero + filter tahun (di kanan atas)
        year_box = card('heroFilter')
        yb = QVBoxLayout(year_box)
        yb.setContentsMargins(12, 6, 12, 6)
        yb.setSpacing(2)
        yb.addWidget(label('FILTER TAHUN', 'filterLabel', False, year_box))
        self.year_combo = QComboBox(year_box)
        self.year_combo.setProperty('field', 'hero')
        self.year_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.year_combo.addItems(['Semua tahun', '2026', '2025', '2024', '2023', '2021', '2019'])
        self.year_combo.currentIndexChanged.connect(self._update_counts)
        yb.addWidget(self.year_combo)
        year_box.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.hero = self.responsive(HeroHeader(
            'SISTEM INFORMASI GEOSPASIAL', 'Dashboard IGT-PR',
            'Ringkasan status data geospasial, katalog layer, dan pintasan fitur kerja.',
            'blue', year_box, 320, self.content))
        self.body.addWidget(self.hero)

        # 2. Statistik repositori (Pertanahan & Tata Ruang - 2 Kolom pada Tablet/Layar >= 460px)
        self.stats = self.responsive(ResponsiveGrid([(460, 2), (0, 1)], 12, self.content))
        self.card_compiled = StatCard('statAmber', 'Terkompilasi', 'Menunggu integrasi', 'amber',
                                      'folder-plus', '#d97706', '#fde9a8')
        self.card_integrated = StatCard('statGreen', 'Terintegrasi', 'Pertanahan & Tata Ruang', 'green',
                                        'check-circle', '#059669', '#c9f5df')
        self.stats.add(self.card_compiled)
        self.stats.add(self.card_integrated)
        self.body.addWidget(self.stats)

        # 3. Live Embedded Katalog IGT (Langsung aktif di dashboard)
        self.catalog_widget = self.responsive(CatalogPage(current_category='igt-pr', current_role=self.current_role, embedded=True, parent=self.content))
        self.catalog_widget.openFullCatalogRequested.connect(self.openCatalogRequested.emit)
        self.catalog_widget.wmsRequested.connect(self.wmsRequested.emit)
        self.catalog_widget.wfsRequested.connect(self.wfsRequested.emit)
        self.body.addWidget(self.catalog_widget)

        # 4. Hub Unggah & Manajemen (isinya bergantung peran - 2 Kolom pada Tablet/Layar >= 480px)
        self.workflow = self.responsive(ResponsiveGrid([(480, 2), (0, 1)], 12, self.content))
        self.body.addWidget(self.workflow)

        # 5. Model Builder & Logout
        self.mb_card = WideCard('mb', 'node-tree', '#7c3aed', '#ebe4fe', 'Model Builder',
                                'Bangun dan jalankan model pengolahan data geospasial.', 'mbTitle', 'mbDesc',
                                self.content)
        self.mb_card.clicked.connect(self.openModelBuilderRequested.emit)
        self.body.addWidget(self.mb_card)

        logout = WideCard('logout', 'logout', '#dc2626', '#fde2e2', 'Logout', 'Keluar dari akun Anda.',
                          'logoutTitle', 'logoutDesc', self.content)
        logout.clicked.connect(self.logoutRequested.emit)
        self.body.addWidget(logout)
        self.add_footer()

        self._build_workflow()
        self._update_counts()

    # ------------------------------------------------------------------ peran
    def set_role(self, role_id):
        self.current_role = role_id
        if hasattr(self, 'catalog_widget'):
            self.catalog_widget.set_role(role_id)
        self._build_workflow()
        self._update_counts()

    def _build_workflow(self):
        """Umum hanya boleh mengunggah IGT Derivatif dan tidak punya Model Builder;
        manajemen IGT Lainnya hanya untuk Superadmin (lihat CLAUDE.md)."""
        role = self.current_role
        is_umum = role == 'umum'

        upload_items = []
        if not is_umum:
            upload_items.append(('upload:pertanahan', 'database', 'Unggah IGT Utama', '#1f6fd6'))
        upload_items.append(('upload:derivatif', 'layers', 'Unggah IGT Derivatif Multiguna', '#1f6fd6'))
        if not is_umum:
            upload_items.append(('model', 'gear', 'Kustom Tematik Derivatif', '#1f6fd6'))
        if role == 'superadmin':
            upload_items.append(('upload:lainnya', 'globe', 'Unggah IGT Lainnya', '#1f6fd6'))

        manage_items = []
        if not is_umum:
            manage_items.append(('manage:igt-utama', 'database', 'IGT Utama', '#047857'))
        manage_items.append(('manage:derivatif', 'layers', 'IGT Derivatif Multiguna', '#047857'))
        if role == 'superadmin':
            manage_items.append(('manage:lainnya', 'globe', 'IGT Lainnya', '#047857'))

        self.workflow.clear()
        upload = HubCard('plain', 'headBlue', 'cloud-upload', '#1f6fd6', '#dceafe', 'Unggah Data',
                         'Kelola dan unggah data geospasial ke dalam sistem.', upload_items,
                         'hub', [(0, 1)], True)
        manage = HubCard('green', 'headGreen', 'database', '#047857', '#cdf3dd', 'Manajemen Data',
                         'Kelola proses, revisi, dan status data geospasial per kategori IGT.', manage_items,
                         'hubGreen', [(0, 1)], True)
        upload.itemClicked.connect(self._on_workflow_item)
        manage.itemClicked.connect(self._on_workflow_item)
        self.workflow.add(upload)
        self.workflow.add(manage)
        self.mb_card.setVisible(not is_umum)

    def _on_workflow_item(self, key):
        if key == 'model':
            self.openModelBuilderRequested.emit()
        elif key.startswith('upload:'):
            self.openUploadRequested.emit(key.split(':', 1)[1])
        elif key.startswith('manage:'):
            self.openManagementRequested.emit(key.split(':', 1)[1])

    # ------------------------------------------------------------------ angka
    def _update_counts(self, *_args):
        year = self.year_combo.currentText()
        utama = ('pertanahan', 'tata-ruang')
        compiled = [s for s in SUBMISSIONS if s.get('status') == 'Terkompilasi' and s.get('category') in utama]
        integrated = [d for d in DATASETS if d.get('status') == 'Terintegrasi' and d.get('category') in utama]
        if year != 'Semua tahun':
            compiled = [s for s in compiled if year in s.get('date', '')]
            integrated = [
                d for d in integrated
                if year in (d.get('updated') or d.get('date') or '')
                or (d.get('subLayers') and any(year in (s.get('year') or s.get('updated') or '') for s in d['subLayers']))
            ]
        self.card_compiled.set_value(len(compiled))
        self.card_integrated.set_value(len(integrated))
        if hasattr(self, 'catalog_widget') and hasattr(self.catalog_widget, 'set_year_filter'):
            self.catalog_widget.set_year_filter(year)

# -*- coding: utf-8 -*-
"""Halaman Katalog Data IGT-PR Mockup V2.

Fitur:
- 5 Tab Kategori:
    1. IGT-PR (Menampilkan IGT Pertanahan dan IGT Tata Ruang sekaligus)
    2. IGT Pertanahan
    3. IGT Tata Ruang
    4. IGT Derivatif
    5. IGT K/L Lainnya
- Menampilkan 8 data teratas per halaman (Paginasi).
- Kontrol navigasi paginasi: tombol Sebelumnya/Berikutnya, tombol nomor halaman, serta dropdown pemilih halaman.
- Desain dinamis & responsif: beradaptasi dari dock sempit (~280px-340px) hingga layar lebar (~900px+).
- Kartu hierarki multi-layer accordion dengan aksi WMS/WFS langsung ke kanvas peta QGIS.
"""

import math
from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QBoxLayout, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS, can_access_wfs
from .login_page import svg_pixmap
from .ui_kit import FlowLayout, icon_badge

CATEGORY_KEYS = ['igt-pr', 'pertanahan', 'tata-ruang', 'derivatif', 'lainnya']
PAGE_SIZE = 8


class DatasetCard(QFrame):
    """Kartu dataset yang adaptif untuk dock sempit maupun lebar."""

    wmsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, dataset, is_expanded=False, show_metadata=True, allow_wfs=True, parent=None):
        super().__init__(parent)
        self.dataset = dataset
        self.has_subs = bool(dataset.get('subLayers'))
        self.is_expanded = is_expanded
        self.show_metadata = show_metadata
        self.allow_wfs = allow_wfs
        self.setObjectName('datasetCard')

        self.setStyleSheet("""
            QFrame#datasetCard {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 12px;
            }
            QFrame#datasetCard:hover {
                border-color: #93c5fd;
            }
            QLabel {
                background: transparent;
            }
            QPushButton#actionWms {
                background-color: #eff6ff;
                color: #1f6fd6;
                border: 1px solid #bfdbfe;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 10px;
                min-width: 48px;
            }
            QPushButton#actionWms:hover {
                background-color: #1f6fd6;
                color: #ffffff;
            }
            QPushButton#actionWfs {
                background-color: #f5f3ff;
                color: #7c3aed;
                border: 1px solid #ddd6fe;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 10px;
                min-width: 48px;
            }
            QPushButton#actionWfs:hover {
                background-color: #7c3aed;
                color: #ffffff;
            }
            QPushButton#multiChip {
                background-color: #ecfdf5;
                color: #047857;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 10px;
            }
            QPushButton#multiChip:hover {
                background-color: #d1fae5;
                border-color: #34d399;
                color: #065f46;
            }
        """)

        card_layout = QVBoxLayout(self)
        top_bot = 6 if not self.show_metadata else 10
        card_layout.setContentsMargins(12, top_bot, 12, top_bot)
        card_layout.setSpacing(4 if not self.show_metadata else 6)

        # 1. Baris Utama: Kolom Kiri (Judul, Walidata, Tanggal) & Kolom Kanan (Aksi Vertikal di Tengah)
        self.main_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.main_row.setContentsMargins(0, 0, 0, 0)
        self.main_row.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(3)

        # Baris 1: Icon + Judul IGT + Chip Kategori
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)

        self.icon_lbl = QLabel(self)
        cat = dataset.get('category', '')
        icon_name = 'map' if cat == 'tata-ruang' else 'layers' if cat == 'derivatif' else 'globe' if cat == 'lainnya' else 'pin'
        icon_color = '#047857' if cat == 'tata-ruang' else '#7c3aed' if cat == 'derivatif' else '#0284c7' if cat == 'lainnya' else '#1f6fd6'
        self.icon_lbl.setPixmap(svg_pixmap(ICONS.get(icon_name, ICONS['layers']).format(color=icon_color), QSize(16, 16)))
        title_row.addWidget(self.icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        self.title_lbl = QLabel(dataset.get('name', ''), self)
        self.title_lbl.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 700;")
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title_row.addWidget(self.title_lbl, 1, Qt.AlignmentFlag.AlignVCenter)

        # Kategori Tag (Berdampingan di kanan nama IGT)
        cat_badge = QLabel(self)
        cat_badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if cat == 'pertanahan':
            cat_badge.setText('Pertanahan')
            cat_badge.setStyleSheet("background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 4px; font-size: 9.5px; font-weight: 700; padding: 1px 6px;")
        elif cat == 'tata-ruang':
            cat_badge.setText('Tata Ruang')
            cat_badge.setStyleSheet("background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; border-radius: 4px; font-size: 9.5px; font-weight: 700; padding: 1px 6px;")
        elif cat == 'derivatif':
            cat_badge.setText('Derivatif')
            cat_badge.setStyleSheet("background-color: #f5f3ff; color: #7c3aed; border: 1px solid #ddd6fe; border-radius: 4px; font-size: 9.5px; font-weight: 700; padding: 1px 6px;")
        else:
            cat_badge.setText('K/L Lainnya')
            cat_badge.setStyleSheet("background-color: #f0f9ff; color: #0284c7; border: 1px solid #bae6fd; border-radius: 4px; font-size: 9.5px; font-weight: 700; padding: 1px 6px;")
        title_row.addWidget(cat_badge, 0, Qt.AlignmentFlag.AlignVCenter)

        left_col.addLayout(title_row)

        # Baris 2 & 3: Nama Direktorat & Tanggal (hanya jika show_metadata=True, disembunyikan di dashboard agar tidak ramai)
        if self.show_metadata:
            org_text = dataset.get('direktorat') or dataset.get('satker') or dataset.get('instansi') or '—'
            self.org_lbl = QLabel(org_text, self)
            self.org_lbl.setStyleSheet("color: #475569; font-size: 11.5px; margin-left: 22px;")
            self.org_lbl.setWordWrap(True)
            left_col.addWidget(self.org_lbl)

            date_text = dataset.get('updated') or dataset.get('date') or '—'
            self.date_lbl = QLabel(f"Terintegrasi: {date_text}", self)
            self.date_lbl.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 22px;")
            left_col.addWidget(self.date_lbl)

        self.main_row.addLayout(left_col, 1)

        # Kolom Kanan: Tombol Aksi (Tepat di Tengah Vertikal)
        self.action_wrap = QHBoxLayout()
        self.action_wrap.setContentsMargins(0, 0, 0, 0)
        self.action_wrap.setSpacing(6)

        if self.has_subs:
            sub_count = len(dataset['subLayers'])
            caret = '▴' if self.is_expanded else '▾'
            self.chip_btn = QPushButton(f"Multi-Layer · {sub_count} Layer {caret}", self)
            self.chip_btn.setObjectName('multiChip')
            self.chip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.chip_btn.clicked.connect(self.toggle_expand)
            self.action_wrap.addWidget(self.chip_btn)
        else:
            self.btn_wms = QPushButton('WMS', self)
            self.btn_wms.setObjectName('actionWms')
            self.btn_wms.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_wms.clicked.connect(lambda: self.wmsClicked.emit(self.dataset, None))
            self.action_wrap.addWidget(self.btn_wms)

            if self.allow_wfs:
                self.btn_wfs = QPushButton('WFS', self)
                self.btn_wfs.setObjectName('actionWfs')
                self.btn_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
                self.btn_wfs.clicked.connect(lambda: self.wfsClicked.emit(self.dataset, None))
                self.action_wrap.addWidget(self.btn_wfs)

        self.main_row.addLayout(self.action_wrap, 0)
        self.main_row.setAlignment(self.action_wrap, Qt.AlignmentFlag.AlignVCenter)

        card_layout.addLayout(self.main_row)

        # 2. Sub-layers Container (Accordion)
        if self.has_subs:
            self.subs_container = QFrame(self)
            self.subs_container.setObjectName('subsContainer')
            self.subs_container.setStyleSheet("""
                QFrame#subsContainer {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    margin-top: 4px;
                    margin-left: 22px;
                }
            """)
            subs_layout = QVBoxLayout(self.subs_container)
            subs_layout.setContentsMargins(10, 6, 10, 6)
            subs_layout.setSpacing(6)

            for sub in dataset['subLayers']:
                sub_row = QWidget(self.subs_container)
                sr_layout = QHBoxLayout(sub_row)
                sr_layout.setContentsMargins(0, 2, 0, 2)
                sr_layout.setSpacing(6)

                branch_lbl = QLabel('└─', sub_row)
                branch_lbl.setStyleSheet("color: #94a3b8; font-weight: 800; font-size: 12px;")
                sr_layout.addWidget(branch_lbl)

                sub_title = QLabel(sub.get('name', ''), sub_row)
                sub_title.setStyleSheet("color: #1e293b; font-size: 11.5px; font-weight: 600;")
                sub_title.setWordWrap(True)
                sr_layout.addWidget(sub_title, 1)

                btn_sub_wms = QPushButton('WMS', sub_row)
                btn_sub_wms.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_sub_wms.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #1f6fd6;
                        border: 1px solid #bfdbfe;
                        border-radius: 5px;
                        font-size: 10px;
                        font-weight: 600;
                        padding: 2px 7px;
                    }
                    QPushButton:hover {
                        background-color: #eff6ff;
                        border-color: #1f6fd6;
                    }
                """)
                btn_sub_wms.clicked.connect(lambda checked, s=sub: self.wmsClicked.emit(self.dataset, s))
                sr_layout.addWidget(btn_sub_wms)

                if self.allow_wfs:
                    btn_sub_wfs = QPushButton('WFS', sub_row)
                    btn_sub_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_sub_wfs.setStyleSheet("""
                        QPushButton {
                            background-color: #ffffff;
                            color: #7c3aed;
                            border: 1px solid #ddd6fe;
                            border-radius: 5px;
                            font-size: 10px;
                            font-weight: 600;
                            padding: 2px 7px;
                        }
                        QPushButton:hover {
                            background-color: #f5f3ff;
                            border-color: #7c3aed;
                        }
                    """)
                    btn_sub_wfs.clicked.connect(lambda checked, s=sub: self.wfsClicked.emit(self.dataset, s))
                    sr_layout.addWidget(btn_sub_wfs)

                subs_layout.addWidget(sub_row)

            self.subs_container.setVisible(self.is_expanded)
            card_layout.addWidget(self.subs_container)

    def toggle_expand(self):
        if not self.has_subs:
            return
        self.is_expanded = not self.is_expanded
        self.subs_container.setVisible(self.is_expanded)
        sub_count = len(self.dataset['subLayers'])
        caret = '▴' if self.is_expanded else '▾'
        self.chip_btn.setText(f"Multi-Layer · {sub_count} Layer {caret}")

    def set_expanded(self, expanded):
        if not self.has_subs or self.is_expanded == expanded:
            return
        self.is_expanded = expanded
        self.subs_container.setVisible(self.is_expanded)
        sub_count = len(self.dataset['subLayers'])
        caret = '▴' if self.is_expanded else '▾'
        self.chip_btn.setText(f"Multi-Layer · {sub_count} Layer {caret}")

    def apply_width(self, width):
        is_narrow = width < 280
        if is_narrow:
            self.main_row.setDirection(QBoxLayout.Direction.TopToBottom)
            self.main_row.setSpacing(6)
            self.main_row.setAlignment(self.action_wrap, Qt.AlignmentFlag.AlignRight)
        else:
            self.main_row.setDirection(QBoxLayout.Direction.LeftToRight)
            self.main_row.setSpacing(10)
            self.main_row.setAlignment(self.action_wrap, Qt.AlignmentFlag.AlignVCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_width(event.size().width())

    def minimumSizeHint(self):
        return QSize(160, 36)


class CatalogPage(QWidget):
    """Halaman / Widget Katalog Data V2 dengan 5 Tab Kategori, Paginasi 8 Data, dan Desain Responsif."""

    backToDashboardRequested = pyqtSignal()
    openFullCatalogRequested = pyqtSignal(str)   # category key
    wmsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, current_category='igt-pr', current_role='superadmin', embedded=False, parent=None):
        super().__init__(parent)
        self.embedded = embedded
        self.current_category = current_category if current_category in CATEGORY_KEYS else 'igt-pr'
        self.current_role = current_role
        self.current_page = 1
        self.page_size = PAGE_SIZE
        self.expanded_states = {}
        self.setObjectName('catalogEmbedded' if embedded else 'catalogPage')

        self.setStyleSheet("""
            QWidget#catalogPage {
                background-color: #f4f7fb;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QWidget#catalogEmbedded {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 14px;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
                background: transparent;
            }
            QPushButton#backBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #1f6fd6;
                font-size: 11.5px;
                font-weight: 700;
                padding: 5px 10px;
            }
            QPushButton#backBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QLineEdit#searchInput {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 11.5px;
                color: #0f294d;
            }
            QLineEdit#searchInput:focus {
                border-color: #1f6fd6;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 5px 8px;
                font-size: 11.5px;
                color: #0f294d;
            }
            QComboBox:focus {
                border-color: #1f6fd6;
            }
            QScrollArea#catalogScroll {
                background: transparent;
                border: none;
            }
        """)

        # Main Outer Layout
        main_layout = QVBoxLayout(self)
        if self.embedded:
            main_layout.setContentsMargins(0, 0, 0, 0)
        else:
            main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        self.selected_year = 'Semua tahun'

        # 1. Header & Container Card
        if self.embedded:
            # Card Wrapper Katalog IGT untuk Dashboard Utama (Sejajar dengan HubCard di bawahnya)
            self.container_card = QFrame(self)
            self.container_card.setObjectName('catalogContainerCard')
            self.container_card.setStyleSheet("""
                QFrame#catalogContainerCard {
                    background-color: #ffffff;
                    border: 1px solid #bae6fd;
                    border-radius: 14px;
                }
            """)
            cc_layout = QVBoxLayout(self.container_card)
            cc_layout.setContentsMargins(0, 0, 0, 14)
            cc_layout.setSpacing(10)

            # Header Kartu dengan latar gradasi dan rounded top corners
            self.head_card = QFrame(self.container_card)
            self.head_card.setObjectName('headCard')
            self.head_card.setStyleSheet("""
                QFrame#headCard {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f2fe, stop:1 #f0f9ff);
                    border: none;
                    border-bottom: 1px solid #bae6fd;
                    border-top-left-radius: 13px;
                    border-top-right-radius: 13px;
                }
            """)
            hc_layout = QHBoxLayout(self.head_card)
            hc_layout.setContentsMargins(16, 14, 16, 14)
            hc_layout.setSpacing(12)

            badge = icon_badge('map', '#0284c7', '#c7e8fb', 44, 22, 12, self.head_card)
            hc_layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)

            ht_layout = QVBoxLayout()
            ht_layout.setSpacing(3)
            self.title_lbl = QLabel('Katalog IGT', self.head_card)
            self.title_lbl.setStyleSheet("color: #0f294d; font-size: 16px; font-weight: 800; background: transparent; border: none;")
            ht_layout.addWidget(self.title_lbl)

            self.desc_lbl = QLabel('Katalog terpadu data IGT Pertanahan dan Tata Ruang Kementerian ATR/BPN.', self.head_card)
            self.desc_lbl.setStyleSheet("color: #475569; font-size: 11px; background: transparent; border: none;")
            self.desc_lbl.setWordWrap(True)
            ht_layout.addWidget(self.desc_lbl)
            hc_layout.addLayout(ht_layout, 1)

            cc_layout.addWidget(self.head_card)

            # Inner Body Container (Padding 14px horizontal di dalam card)
            self.inner_body = QWidget(self.container_card)
            self.inner_body.setStyleSheet("background: transparent;")
            ib_layout = QVBoxLayout(self.inner_body)
            ib_layout.setContentsMargins(14, 2, 14, 0)
            ib_layout.setSpacing(10)
            cc_layout.addWidget(self.inner_body)

            target_layout = ib_layout
            main_layout.addWidget(self.container_card)
        else:
            # Standalone page header (Title, Desc, Back Button)
            self.head_widget = QWidget(self)
            self.head_layout = QHBoxLayout(self.head_widget)
            self.head_layout.setContentsMargins(0, 0, 0, 0)
            self.head_layout.setSpacing(8)

            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)

            self.title_lbl = QLabel('Katalog IGT-PR', self.head_widget)
            self.title_lbl.setStyleSheet("color: #0f294d; font-size: 17px; font-weight: 800;")
            text_layout.addWidget(self.title_lbl)

            self.desc_lbl = QLabel('Katalog terpadu IGT Pertanahan dan Tata Ruang Kementerian ATR/BPN.', self.head_widget)
            self.desc_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            self.desc_lbl.setWordWrap(True)
            text_layout.addWidget(self.desc_lbl)
            self.head_layout.addLayout(text_layout, 1)

            self.back_btn = QPushButton('← Kembali ke Dashboard', self.head_widget)
            self.back_btn.setObjectName('backBtn')
            self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.back_btn.clicked.connect(self.backToDashboardRequested.emit)
            self.head_layout.addWidget(self.back_btn, 0, Qt.AlignmentFlag.AlignTop)
            main_layout.addWidget(self.head_widget)
            target_layout = main_layout

        # 2. Subnav 5 Tab Kategori (Selalu 1 Baris Horizontal Scrollable)
        self.tabs_scroll = QScrollArea(self)
        self.tabs_scroll.setObjectName('tabsScroll')
        self.tabs_scroll.setWidgetResizable(True)
        self.tabs_scroll.setFixedHeight(40)
        self.tabs_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabs_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tabs_scroll.setStyleSheet("QScrollArea#tabsScroll { background: transparent; border: none; }")

        self.tabs_container = QWidget(self.tabs_scroll)
        self.tabs_container.setStyleSheet("background: transparent;")
        self.subnav_layout = QHBoxLayout(self.tabs_container)
        self.subnav_layout.setContentsMargins(0, 0, 0, 0)
        self.subnav_layout.setSpacing(6)
        self.nav_buttons = {}

        tabs_data = [
            ('igt-pr', 'IGT-PR'),
            ('pertanahan', 'IGT Pertanahan'),
            ('tata-ruang', 'IGT Tata Ruang'),
            ('derivatif', 'IGT Derivatif'),
            ('lainnya', 'IGT K/L Lainnya'),
        ]
        for cat_key, tab_title in tabs_data:
            btn = QPushButton(tab_title, self.tabs_container)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=cat_key: self.set_category(k))
            self.subnav_layout.addWidget(btn)
            self.nav_buttons[cat_key] = btn

        self.subnav_layout.addStretch(1)
        self.tabs_scroll.setWidget(self.tabs_container)
        target_layout.addWidget(self.tabs_scroll)

        # 3. Filter Controls (Pencarian, Direktorat, Provinsi, Kabupaten)
        self.filter_card = QFrame(self)
        self.filter_card.setObjectName('filterCard')
        self.filter_card.setStyleSheet("""
            QFrame#filterCard {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px 10px;
            }
        """)
        self.fc_main_layout = QVBoxLayout(self.filter_card)
        self.fc_main_layout.setContentsMargins(4, 4, 4, 4)
        self.fc_main_layout.setSpacing(6)

        # Search box
        search_box = QVBoxLayout()
        search_box.setSpacing(2)
        s_lbl = QLabel('PENCARIAN DATASET', self.filter_card)
        s_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        search_box.addWidget(s_lbl)
        self.search_input = QLineEdit(self.filter_card)
        self.search_input.setObjectName('searchInput')
        self.search_input.setPlaceholderText('Cari nama IGT, sublayer, wilayah...')
        self.search_input.textChanged.connect(self._on_filter_changed)
        search_box.addWidget(self.search_input)
        self.fc_main_layout.addLayout(search_box)

        # Dropdowns row (Provinsi + Kabupaten)
        self.filter_box_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.filter_box_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_box_layout.setSpacing(8)

        # Provinsi Filter
        prov_box = QWidget(self.filter_card)
        prov_box_layout = QVBoxLayout(prov_box)
        prov_box_layout.setContentsMargins(0, 0, 0, 0)
        prov_box_layout.setSpacing(2)
        self.prov_lbl = QLabel('PROVINSI', prov_box)
        self.prov_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        prov_box_layout.addWidget(self.prov_lbl)
        self.prov_combo = QComboBox(prov_box)
        self.prov_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.prov_combo.currentIndexChanged.connect(self._on_prov_changed)
        prov_box_layout.addWidget(self.prov_combo)
        self.filter_box_layout.addWidget(prov_box, 1)

        # Kabupaten Filter
        kab_box = QWidget(self.filter_card)
        kab_box_layout = QVBoxLayout(kab_box)
        kab_box_layout.setContentsMargins(0, 0, 0, 0)
        kab_box_layout.setSpacing(2)
        self.kab_lbl = QLabel('KABUPATEN / KOTA', kab_box)
        self.kab_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        kab_box_layout.addWidget(self.kab_lbl)
        self.kab_combo = QComboBox(kab_box)
        self.kab_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.kab_combo.currentIndexChanged.connect(self._on_kab_changed)
        kab_box_layout.addWidget(self.kab_combo)
        self.filter_box_layout.addWidget(kab_box, 1)

        self.fc_main_layout.addLayout(self.filter_box_layout)
        target_layout.addWidget(self.filter_card)

        # 4. Count & Summary Info
        self.count_lbl = QLabel('', self)
        self.count_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 600;")
        self.count_lbl.setWordWrap(True)
        target_layout.addWidget(self.count_lbl)

        # 5. Daftar Kartu Dataset (Langsung di layout jika embedded, atau dalam QScrollArea jika standalone)
        if self.embedded:
            self.list_content = QWidget(self)
            self.list_layout = QVBoxLayout(self.list_content)
            self.list_layout.setContentsMargins(0, 2, 0, 4)
            self.list_layout.setSpacing(8)
            target_layout.addWidget(self.list_content)
        else:
            self.scroll = QScrollArea(self)
            self.scroll.setObjectName('catalogScroll')
            self.scroll.setWidgetResizable(True)
            self.scroll.setFrameShape(QFrame.Shape.NoFrame)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            self.list_content = QWidget()
            self.list_layout = QVBoxLayout(self.list_content)
            self.list_layout.setContentsMargins(0, 2, 6, 6)
            self.list_layout.setSpacing(8)
            self.scroll.setWidget(self.list_content)
            target_layout.addWidget(self.scroll, 1)

        # 6. Pagination Bar Responsif
        self.pag_card = QFrame(self)
        self.pag_card.setObjectName('pagCard')
        self.pag_card.setStyleSheet("""
            QFrame#pagCard {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px 10px;
            }
            QComboBox#sizeCombo {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: 600;
                color: #0f294d;
                background-color: #ffffff;
            }
            QPushButton#prevBtn, QPushButton#nextBtn {
                background-color: #ffffff;
                color: #1f6fd6;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                min-width: 24px;
                max-width: 26px;
                min-height: 26px;
                max-height: 26px;
                font-size: 12px;
                font-weight: 700;
                padding: 0;
            }
            QPushButton#prevBtn:hover, QPushButton#nextBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QPushButton#prevBtn:disabled, QPushButton#nextBtn:disabled {
                background-color: #f1f5f9;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            QPushButton[pageBtn="true"] {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                min-width: 24px;
                max-width: 28px;
                min-height: 26px;
                max-height: 26px;
                padding: 0;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton[pageBtn="true"]:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
            QPushButton[pageBtn="true"][active="true"] {
                background-color: #1f6fd6;
                color: #ffffff;
                border-color: #1f6fd6;
            }
        """)

        self.pag_main_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self.pag_card)
        self.pag_main_layout.setContentsMargins(6, 4, 6, 4)
        self.pag_main_layout.setSpacing(6)

        # Bagian Kiri Bawah: Pilihan menampilkan berapa card
        self.size_widget = QWidget(self.pag_card)
        self.size_wrap = QHBoxLayout(self.size_widget)
        self.size_wrap.setContentsMargins(0, 0, 0, 0)
        self.size_wrap.setSpacing(6)
        self.size_lbl = QLabel('Tampilkan:', self.size_widget)
        self.size_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700;")
        self.size_wrap.addWidget(self.size_lbl)

        self.size_combo = QComboBox(self.size_widget)
        self.size_combo.setObjectName('sizeCombo')
        for count in [4, 8, 12, 16, 24]:
            self.size_combo.addItem(f"{count} card", count)
        self.size_combo.setCurrentIndex(1)  # Default 8 card
        self.size_combo.currentIndexChanged.connect(self._on_page_size_changed)
        self.size_wrap.addWidget(self.size_combo)
        self.pag_main_layout.addWidget(self.size_widget)

        self.pag_stretch = self.pag_main_layout.addStretch(1)

        # Bagian Kanan Bawah: Seluruh navigasi page disatukan [←] [1] [2] [3] [4] [→]
        self.nav_widget = QWidget(self.pag_card)
        self.nav_group = QHBoxLayout(self.nav_widget)
        self.nav_group.setContentsMargins(0, 0, 0, 0)
        self.nav_group.setSpacing(4)

        self.prev_btn = QPushButton('←', self.nav_widget)
        self.prev_btn.setObjectName('prevBtn')
        self.prev_btn.setToolTip('Halaman sebelumnya')
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev_page)
        self.nav_group.addWidget(self.prev_btn)

        self.page_numbers_layout = QHBoxLayout()
        self.page_numbers_layout.setContentsMargins(0, 0, 0, 0)
        self.page_numbers_layout.setSpacing(4)
        self.nav_group.addLayout(self.page_numbers_layout)

        self.next_btn = QPushButton('→', self.nav_widget)
        self.next_btn.setObjectName('nextBtn')
        self.next_btn.setToolTip('Halaman berikutnya')
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next_page)
        self.nav_group.addWidget(self.next_btn)

        self.pag_main_layout.addWidget(self.nav_widget)

        target_layout.addWidget(self.pag_card)

        # Inisialisasi kategori awal
        self.set_category(self.current_category)

    # ------------------------------------------------------------------ Responsivitas
    def apply_width(self, width):
        is_narrow = width < 280
        if hasattr(self, 'filter_box_layout'):
            self.filter_box_layout.setDirection(
                QBoxLayout.Direction.TopToBottom if is_narrow else QBoxLayout.Direction.LeftToRight
            )
        if hasattr(self, 'pag_main_layout'):
            self.pag_main_layout.setDirection(
                QBoxLayout.Direction.TopToBottom if is_narrow else QBoxLayout.Direction.LeftToRight
            )
            if hasattr(self, 'size_widget') and hasattr(self, 'nav_widget'):
                self.pag_main_layout.setAlignment(self.size_widget, Qt.AlignmentFlag.AlignCenter if is_narrow else Qt.AlignmentFlag.AlignLeft)
                self.pag_main_layout.setAlignment(self.nav_widget, Qt.AlignmentFlag.AlignCenter if is_narrow else Qt.AlignmentFlag.AlignRight)
        if hasattr(self, 'size_lbl'):
            self.size_lbl.setVisible(width >= 360)
        if hasattr(self, 'list_layout'):
            for i in range(self.list_layout.count()):
                item = self.list_layout.itemAt(i)
                if item and item.widget() and hasattr(item.widget(), 'apply_width'):
                    item.widget().apply_width(width)
        is_narrow = width < 280
        if getattr(self, '_last_is_narrow', None) != is_narrow:
            self._last_is_narrow = is_narrow
            if hasattr(self, '_last_total_pages'):
                self._update_pagination_ui(self._last_total_pages, self._last_total_items)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if hasattr(self, 'back_btn'):
            if w < 380:
                self.back_btn.setText('← Kembali')
            else:
                self.back_btn.setText('← Kembali ke Dashboard')
        self.apply_width(w)

    def minimumSizeHint(self):
        return QSize(180, 120)

    # ------------------------------------------------------------------ Kategori & Filter
    def get_category_datasets(self, cat):
        if cat == 'igt-pr':
            return [d for d in DATASETS if d.get('category') in ('pertanahan', 'tata-ruang')]
        return [d for d in DATASETS if d.get('category') == cat]

    def _populate_prov_combo(self):
        self.prov_combo.blockSignals(True)
        curr = self.prov_combo.currentText()
        self.prov_combo.clear()
        datasets = self.get_category_datasets(self.current_category)
        provs = set()
        for d in datasets:
            p = d.get('prov')
            if p:
                provs.add(p)
        items = ['Semua Provinsi'] + sorted(list(provs))
        self.prov_combo.addItems(items)
        if curr in items:
            self.prov_combo.setCurrentText(curr)
        else:
            self.prov_combo.setCurrentIndex(0)
        self.prov_combo.blockSignals(False)

    def _populate_kab_combo(self):
        self.kab_combo.blockSignals(True)
        curr = self.kab_combo.currentText()
        self.kab_combo.clear()
        datasets = self.get_category_datasets(self.current_category)
        sel_prov = self.prov_combo.currentText()
        if sel_prov != 'Semua Provinsi':
            datasets = [d for d in datasets if sel_prov.lower() in ((d.get('prov') or '') + ' ' + (d.get('scope') or '')).lower()]
        kabs = set()
        for d in datasets:
            k = d.get('kab')
            if k:
                kabs.add(k)
        items = ['Semua Kab / Kota'] + sorted(list(kabs))
        self.kab_combo.addItems(items)
        if curr in items:
            self.kab_combo.setCurrentText(curr)
        else:
            self.kab_combo.setCurrentIndex(0)
        self.kab_combo.blockSignals(False)

    def set_year_filter(self, year_text):
        self.selected_year = year_text
        self.current_page = 1
        self._render_page()

    def set_role(self, role_id):
        self.current_role = role_id
        self._render_page()

    def _on_prov_changed(self):
        self._populate_kab_combo()
        self.current_page = 1
        self._render_page()

    def _on_kab_changed(self):
        self.current_page = 1
        self._render_page()

    def _on_filter_changed(self):
        self.current_page = 1
        self._render_page()

    def set_category(self, cat_key):
        if cat_key not in CATEGORY_KEYS:
            cat_key = 'igt-pr'
        self.current_category = cat_key
        self.current_page = 1

        cat_info = CATEGORIES.get(cat_key, CATEGORIES['igt-pr'])

        # Update Header jika bukan mode embedded
        if not self.embedded:
            self.title_lbl.setText(f"Katalog {cat_info['label']}")
            self.desc_lbl.setText(f"{cat_info['desc']} Memuat data WMS/WFS langsung ke kanvas QGIS.")

        self._populate_prov_combo()
        self._populate_kab_combo()

        # Update style tab aktif
        for key, btn in self.nav_buttons.items():
            if key == cat_key:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1f6fd6;
                        color: #ffffff;
                        border: none;
                        border-radius: 16px;
                        padding: 5px 12px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #475569;
                        border: 1px solid #cbd5e1;
                        border-radius: 16px;
                        padding: 5px 12px;
                        font-weight: 600;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        border-color: #94a3b8;
                    }
                """)

        self._render_page()

    def _get_filtered_records(self):
        query = self.search_input.text().strip().lower()
        selected_prov = self.prov_combo.currentText()
        selected_kab = self.kab_combo.currentText()

        records = self.get_category_datasets(self.current_category)

        filtered = []
        for d in records:
            # 1. Filter Tahun dari top-right hero filter
            if hasattr(self, 'selected_year') and self.selected_year != 'Semua tahun':
                match_p = self.selected_year in (d.get('updated') or d.get('date') or '')
                match_sub = any(self.selected_year in (s.get('year') or s.get('updated') or '') for s in d.get('subLayers', []))
                if not (match_p or match_sub):
                    continue

            # 2. Filter Provinsi
            if selected_prov != 'Semua Provinsi':
                prov_haystack = ((d.get('prov') or '') + ' ' + (d.get('scope') or '')).lower()
                if selected_prov.lower() not in prov_haystack:
                    continue

            # 3. Filter Kabupaten (mengikuti provinsi terpilih)
            if selected_kab != 'Semua Kab / Kota':
                kab_haystack = ((d.get('kab') or '') + ' ' + (d.get('scope') or '')).lower()
                if selected_kab.lower() not in kab_haystack:
                    continue

            # 4. Filter Pencarian
            if query:
                org_val = d.get('direktorat', '') or d.get('satker', '') or d.get('ditjen', '') or d.get('instansi', '') or d.get('source', '')
                subs_text = ' '.join([s.get('name', '') + ' ' + s.get('label', '') for s in d.get('subLayers', [])])
                haystack = (d.get('name', '') + ' ' + org_val + ' ' + (d.get('prov') or '') + ' ' + (d.get('kab') or '') + ' ' + (d.get('scope') or '') + ' ' + subs_text).lower()
                if query not in haystack:
                    continue

            filtered.append(d)

        return records, filtered

    # ------------------------------------------------------------------ Render Data & Paginasi
    def _render_page(self):
        # Bersihkan kartu sebelumnya
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        all_cat_records, filtered = self._get_filtered_records()
        total_items = len(filtered)
        total_pages = max(1, math.ceil(total_items / self.page_size))

        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)
        page_items = filtered[start_idx:end_idx]

        # Update Info Count
        cat_label = CATEGORIES[self.current_category]['label']
        if total_items > 0:
            self.count_lbl.setText(
                f"Menampilkan {start_idx + 1}–{end_idx} dari {total_items} dataset · "
                f"Halaman {self.current_page} dari {total_pages} · Kategori {cat_label}"
            )
        else:
            self.count_lbl.setText(f"Tidak ada dataset yang cocok · Kategori {cat_label}")

        # Render Kartu Dataset (8 data teratas untuk halaman aktif)
        if not page_items:
            empty_card = QFrame(self.list_content)
            empty_card.setStyleSheet("background-color: #ffffff; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 24px;")
            ec_layout = QVBoxLayout(empty_card)
            ec_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel('Tidak ada dataset yang cocok dengan kriteria filter atau pencarian.', empty_card)
            lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ec_layout.addWidget(lbl)
            self.list_layout.addWidget(empty_card)
        else:
            query = self.search_input.text().strip().lower()
            for d in page_items:
                d_id = d.get('id', '')
                is_exp = self.expanded_states.get(d_id, False)
                if query and d.get('subLayers'):
                    match_sub = any(query in s.get('name', '').lower() for s in d['subLayers'])
                    if match_sub:
                        is_exp = True

                allow_wfs = can_access_wfs(self.current_role, d)
                card = DatasetCard(d, is_expanded=is_exp, show_metadata=not self.embedded, allow_wfs=allow_wfs, parent=self.list_content)
                card.apply_width(self.width())
                card.wmsClicked.connect(lambda ds, sl: self.wmsRequested.emit(ds, sl))
                card.wfsClicked.connect(lambda ds, sl: self.wfsRequested.emit(ds, sl))
                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

        # Update Pagination Controls
        self._last_total_pages = total_pages
        self._last_total_items = total_items
        self._update_pagination_ui(total_pages, total_items)

    def _update_pagination_ui(self, total_pages, total_items):
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        # Clear number buttons
        while self.page_numbers_layout.count():
            item = self.page_numbers_layout.takeAt(0)
            w = item.widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()

        # Build number buttons (range aktif: 3 button jika dock sempit < 280px, 5 button jika normal)
        max_num_btns = 3 if self.width() < 280 else 5
        half = 1 if max_num_btns == 3 else 2
        start_p = max(1, self.current_page - half)
        end_p = min(total_pages, start_p + max_num_btns - 1)
        if end_p - start_p < max_num_btns - 1:
            start_p = max(1, end_p - max_num_btns + 1)

        for p in range(start_p, end_p + 1):
            btn = QPushButton(str(p), self.nav_widget)
            btn.setProperty('pageBtn', 'true')
            btn.setProperty('active', 'true' if p == self.current_page else 'false')
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, page_num=p: self._go_to_page(page_num))
            self.page_numbers_layout.addWidget(btn)

        # Sembunyikan pagination jika dataset <= page_size dan hanya 1 halaman
        self.pag_card.setVisible(total_items > self.page_size or total_pages > 1)

    def _on_page_size_changed(self, index):
        if index >= 0:
            sz = self.size_combo.itemData(index)
            if sz and sz != self.page_size:
                self.page_size = sz
                self.current_page = 1
                self._render_page()

    def _on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_page()

    def _on_next_page(self):
        all_cat_records, filtered = self._get_filtered_records()
        total_pages = max(1, math.ceil(len(filtered) / self.page_size))
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_page()

    def _go_to_page(self, page_num):
        if page_num != self.current_page:
            self.current_page = page_num
            self._render_page()

    def expand_all(self, expand=True):
        """Buka atau tutup seluruh accordion multi-layer."""
        for i in range(self.list_layout.count()):
            item = self.list_layout.itemAt(i)
            w = item.widget() if item else None
            if isinstance(w, DatasetCard):
                w.set_expanded(expand)

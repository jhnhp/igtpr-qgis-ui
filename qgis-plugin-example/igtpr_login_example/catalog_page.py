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
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS
from .login_page import svg_pixmap
from .ui_kit import FlowLayout

CATEGORY_KEYS = ['igt-pr', 'pertanahan', 'tata-ruang', 'derivatif', 'lainnya']
PAGE_SIZE = 8


class DatasetCard(QFrame):
    """Kartu dataset yang adaptif untuk dock sempit maupun lebar."""

    wmsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, dataset, is_expanded=False, parent=None):
        super().__init__(parent)
        self.dataset = dataset
        self.has_subs = bool(dataset.get('subLayers'))
        self.is_expanded = is_expanded
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
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(6)

        # 1. Baris Judul & Kategori Tag
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(6)

        # Icon Kategori
        self.icon_lbl = QLabel(self)
        cat = dataset.get('category', '')
        icon_name = 'map' if cat == 'tata-ruang' else 'layers' if cat == 'derivatif' else 'pin'
        icon_color = '#047857' if cat == 'tata-ruang' else '#7c3aed' if cat == 'derivatif' else '#1f6fd6'
        self.icon_lbl.setPixmap(svg_pixmap(ICONS.get(icon_name, ICONS['layers']).format(color=icon_color), QSize(16, 16)))
        top_row.addWidget(self.icon_lbl, 0, Qt.AlignmentFlag.AlignTop)

        # Nama IGT
        self.title_lbl = QLabel(dataset.get('name', ''), self)
        self.title_lbl.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 700;")
        self.title_lbl.setWordWrap(True)
        top_row.addWidget(self.title_lbl, 1)

        # Kategori Tag
        cat_badge = QLabel(self)
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
        top_row.addWidget(cat_badge, 0, Qt.AlignmentFlag.AlignTop)

        card_layout.addLayout(top_row)

        # 2. Baris Metadata Organisasi & Tanggal
        meta_row = QHBoxLayout()
        meta_row.setContentsMargins(22, 0, 0, 0)
        meta_row.setSpacing(6)

        org_text = dataset.get('direktorat') or dataset.get('satker') or dataset.get('instansi') or '—'
        date_text = dataset.get('updated') or dataset.get('date') or '—'
        self.meta_lbl = QLabel(f"{org_text}  ·  {date_text}", self)
        self.meta_lbl.setStyleSheet("color: #475569; font-size: 11px;")
        self.meta_lbl.setWordWrap(True)
        meta_row.addWidget(self.meta_lbl, 1)

        card_layout.addLayout(meta_row)

        # 3. Baris Tombol Aksi (WMS / WFS atau Multi-Layer Toggle Chip)
        action_row = QHBoxLayout()
        action_row.setContentsMargins(22, 2, 0, 0)
        action_row.setSpacing(6)
        action_row.addStretch(1)

        if self.has_subs:
            sub_count = len(dataset['subLayers'])
            caret = '▴' if self.is_expanded else '▾'
            self.chip_btn = QPushButton(f"Multi-Layer · {sub_count} Layer {caret}", self)
            self.chip_btn.setObjectName('multiChip')
            self.chip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.chip_btn.clicked.connect(self.toggle_expand)
            action_row.addWidget(self.chip_btn)
        else:
            self.btn_wms = QPushButton('WMS', self)
            self.btn_wms.setObjectName('actionWms')
            self.btn_wms.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_wms.clicked.connect(lambda: self.wmsClicked.emit(self.dataset, None))
            action_row.addWidget(self.btn_wms)

            self.btn_wfs = QPushButton('WFS', self)
            self.btn_wfs.setObjectName('actionWfs')
            self.btn_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_wfs.clicked.connect(lambda: self.wfsClicked.emit(self.dataset, None))
            action_row.addWidget(self.btn_wfs)

        card_layout.addLayout(action_row)

        # 4. Sub-layers Container (Accordion)
        if self.has_subs:
            self.subs_container = QFrame(self)
            self.subs_container.setObjectName('subsContainer')
            self.subs_container.setStyleSheet("""
                QFrame#subsContainer {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    margin-top: 4px;
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


class CatalogPage(QWidget):
    """Halaman Katalog Data V2 dengan 5 Tab Kategori, Paginasi 8 Data, dan Desain Responsif."""

    backToDashboardRequested = pyqtSignal()
    wmsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, current_category='igt-pr', current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_category = current_category if current_category in CATEGORY_KEYS else 'igt-pr'
        self.current_role = current_role
        self.current_page = 1
        self.page_size = PAGE_SIZE
        self.expanded_states = {}
        self.setObjectName('catalogPage')

        self.setStyleSheet("""
            QWidget#catalogPage {
                background-color: #f4f7fb;
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
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # 1. Header (Title, Desc, Back Button)
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

        # 2. Subnav 5 Tab Kategori (FlowLayout yang membungkus rapi)
        self.tabs_container = QWidget(self)
        self.subnav_layout = FlowLayout(self.tabs_container, h_spacing=6, v_spacing=6)
        self.subnav_layout.setContentsMargins(0, 0, 0, 0)
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

        main_layout.addWidget(self.tabs_container)

        # 3. Filter Controls (Pencarian, Tahun, Wilayah)
        self.filter_card = QFrame(self)
        self.filter_card.setObjectName('filterCard')
        self.filter_card.setStyleSheet("""
            QFrame#filterCard {
                background-color: #ffffff;
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
        self.search_input.setPlaceholderText('Cari nama IGT, sublayer, direktorat, wilayah...')
        self.search_input.textChanged.connect(self._on_filter_changed)
        search_box.addWidget(self.search_input)
        self.fc_main_layout.addLayout(search_box)

        # Dropdowns row (Tahun + Wilayah)
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        year_box = QVBoxLayout()
        year_box.setSpacing(2)
        y_lbl = QLabel('TAHUN', self.filter_card)
        y_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        year_box.addWidget(y_lbl)
        self.year_combo = QComboBox(self.filter_card)
        self.year_combo.addItems(['Semua tahun', '2026', '2025', '2024', '2023', '2021', '2019'])
        self.year_combo.currentIndexChanged.connect(self._on_filter_changed)
        year_box.addWidget(self.year_combo)
        filter_row.addLayout(year_box, 1)

        reg_box = QVBoxLayout()
        reg_box.setSpacing(2)
        r_lbl = QLabel('WILAYAH', self.filter_card)
        r_lbl.setStyleSheet("color: #64748b; font-size: 9px; font-weight: 800; letter-spacing: 0.5px;")
        reg_box.addWidget(r_lbl)
        self.reg_combo = QComboBox(self.filter_card)
        self.reg_combo.addItems(['Semua Wilayah', 'Kab. Sleman', 'Kab. Bantul', 'Kab. Kulon Progo', 'Kab. Gunungkidul', 'Kota Yogyakarta', 'Nasional'])
        self.reg_combo.currentIndexChanged.connect(self._on_filter_changed)
        reg_box.addWidget(self.reg_combo)
        filter_row.addLayout(reg_box, 1)

        self.fc_main_layout.addLayout(filter_row)
        main_layout.addWidget(self.filter_card)

        # 4. Count & Summary Info
        self.count_lbl = QLabel('', self)
        self.count_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 600;")
        main_layout.addWidget(self.count_lbl)

        # 5. Scroll Area memuat Daftar Kartu Dataset
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
        main_layout.addWidget(self.scroll, 1)

        # 6. Pagination Bar Responsif
        self.pag_card = QFrame(self)
        self.pag_card.setObjectName('pagCard')
        self.pag_card.setStyleSheet("""
            QFrame#pagCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 6px 8px;
            }
            QPushButton#prevBtn, QPushButton#nextBtn {
                background-color: #ffffff;
                color: #1f6fd6;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#prevBtn:hover, QPushButton#nextBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QPushButton#prevBtn:disabled, QPushButton#nextBtn:disabled {
                background-color: #f8fafc;
                color: #94a3b8;
                border-color: #e2e8f0;
            }
            QPushButton[pageBtn="true"] {
                background-color: #ffffff;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                min-width: 24px;
                max-width: 32px;
                padding: 3px 5px;
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

        self.pag_main_layout = QVBoxLayout(self.pag_card)
        self.pag_main_layout.setContentsMargins(2, 2, 2, 2)
        self.pag_main_layout.setSpacing(4)

        # Baris 1: Prev, Halaman Selector, Next
        nav_row = QHBoxLayout()
        nav_row.setContentsMargins(0, 0, 0, 0)
        nav_row.setSpacing(6)

        self.prev_btn = QPushButton('Sebelumnya', self.pag_card)
        self.prev_btn.setObjectName('prevBtn')
        self.prev_btn.setIcon(QIcon(svg_pixmap(ICONS['arrow-left'].format(color='#1f6fd6'), QSize(13, 13))))
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev_page)
        nav_row.addWidget(self.prev_btn)

        # Direct Page Selector ComboBox
        jump_layout = QHBoxLayout()
        jump_layout.setSpacing(3)
        self.jump_lbl = QLabel('Halaman:', self.pag_card)
        self.jump_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 600;")
        jump_layout.addWidget(self.jump_lbl)

        self.page_selector = QComboBox(self.pag_card)
        self.page_selector.setStyleSheet("font-size: 11px; padding: 2px 4px; min-width: 58px;")
        self.page_selector.currentIndexChanged.connect(self._on_page_selected)
        jump_layout.addWidget(self.page_selector)
        nav_row.addLayout(jump_layout)

        self.next_btn = QPushButton('Berikutnya', self.pag_card)
        self.next_btn.setObjectName('nextBtn')
        self.next_btn.setIcon(QIcon(svg_pixmap(ICONS['chevron-right'].format(color='#1f6fd6'), QSize(13, 13))))
        self.next_btn.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next_page)
        nav_row.addWidget(self.next_btn)

        self.pag_main_layout.addLayout(nav_row)

        # Baris 2: Tombol Nomor Halaman
        self.page_numbers_layout = QHBoxLayout()
        self.page_numbers_layout.setContentsMargins(0, 0, 0, 0)
        self.page_numbers_layout.setSpacing(4)
        self.page_numbers_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pag_main_layout.addLayout(self.page_numbers_layout)

        main_layout.addWidget(self.pag_card)

        # Inisialisasi kategori awal
        self.set_category(self.current_category)

    # ------------------------------------------------------------------ Responsivitas
    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = event.size().width()
        if w < 380:
            self.back_btn.setText('← Kembali')
            self.prev_btn.setText('Prev')
            self.next_btn.setText('Next')
            self.jump_lbl.setVisible(False)
        else:
            self.back_btn.setText('← Kembali ke Dashboard')
            self.prev_btn.setText('Sebelumnya')
            self.next_btn.setText('Berikutnya')
            self.jump_lbl.setVisible(True)

    # ------------------------------------------------------------------ Kategori & Filter
    def set_category(self, cat_key):
        if cat_key not in CATEGORY_KEYS:
            cat_key = 'igt-pr'
        self.current_category = cat_key
        self.current_page = 1

        cat_info = CATEGORIES.get(cat_key, CATEGORIES['igt-pr'])

        # Update Header
        self.title_lbl.setText(f"Katalog {cat_info['label']}")
        self.desc_lbl.setText(f"{cat_info['desc']} Memuat data WMS/WFS langsung ke kanvas QGIS.")

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

    def _on_filter_changed(self):
        self.current_page = 1
        self._render_page()

    def _get_filtered_records(self):
        query = self.search_input.text().strip().lower()
        selected_year = self.year_combo.currentText()
        selected_reg = self.reg_combo.currentText()

        # Tab IGT-PR menampilkan IGT Pertanahan dan IGT Tata Ruang sekaligus
        if self.current_category == 'igt-pr':
            records = [d for d in DATASETS if d.get('category') in ('pertanahan', 'tata-ruang')]
        else:
            records = [d for d in DATASETS if d.get('category') == self.current_category]

        filtered = []
        for d in records:
            # Filter Tahun
            if selected_year != 'Semua tahun':
                match_p = selected_year in d.get('updated', '') or selected_year in d.get('date', '')
                match_sub = any(selected_year in s.get('year', '') or selected_year in s.get('updated', '') for s in d.get('subLayers', []))
                if not (match_p or match_sub):
                    continue

            # Filter Wilayah
            if selected_reg != 'Semua Wilayah':
                reg_haystack = (d.get('prov', '') + ' ' + d.get('kab', '') + ' ' + d.get('scope', '')).lower()
                if selected_reg.lower() not in reg_haystack and 'nasional' not in d.get('prov', '').lower():
                    continue

            # Filter Pencarian
            if query:
                org_val = d.get('direktorat', '') or d.get('satker', '') or d.get('instansi', '')
                subs_text = ' '.join([s.get('name', '') + ' ' + s.get('label', '') for s in d.get('subLayers', [])])
                haystack = (d.get('name', '') + ' ' + org_val + ' ' + d.get('scope', '') + ' ' + subs_text).lower()
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

                card = DatasetCard(d, is_expanded=is_exp, parent=self.list_content)
                card.wmsClicked.connect(lambda ds, sl: self.wmsRequested.emit(ds, sl))
                card.wfsClicked.connect(lambda ds, sl: self.wfsRequested.emit(ds, sl))
                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

        # Update Pagination Controls
        self._update_pagination_ui(total_pages, total_items)

    def _update_pagination_ui(self, total_pages, total_items):
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        # Clear number buttons
        while self.page_numbers_layout.count():
            item = self.page_numbers_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Build number buttons (range aktif)
        max_num_btns = 5
        start_p = max(1, self.current_page - 2)
        end_p = min(total_pages, start_p + max_num_btns - 1)
        if end_p - start_p < max_num_btns - 1:
            start_p = max(1, end_p - max_num_btns + 1)

        for p in range(start_p, end_p + 1):
            btn = QPushButton(str(p), self.pag_card)
            btn.setProperty('pageBtn', 'true')
            btn.setProperty('active', 'true' if p == self.current_page else 'false')
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, page_num=p: self._go_to_page(page_num))
            self.page_numbers_layout.addWidget(btn)

        # Update Dropdown Selector
        self.page_selector.blockSignals(True)
        self.page_selector.clear()
        for p in range(1, total_pages + 1):
            self.page_selector.addItem(f"{p} / {total_pages}", p)
        self.page_selector.setCurrentIndex(self.current_page - 1)
        self.page_selector.blockSignals(False)

        # Sembunyikan pagination jika dataset <= 8 dan hanya 1 halaman
        self.pag_card.setVisible(total_items > self.page_size or total_pages > 1)

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

    def _on_page_selected(self, index):
        if index >= 0:
            target_page = self.page_selector.itemData(index)
            if target_page and target_page != self.current_page:
                self.current_page = target_page
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

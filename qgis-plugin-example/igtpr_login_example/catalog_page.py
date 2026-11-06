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
import os
from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QBoxLayout, QComboBox, QCompleter, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS, INDONESIA_REGIONS, can_access_wfs, match_province_name
from .login_page import svg_pixmap
from .ui_kit import FlowLayout, SearchableComboBox, icon_badge
from .igt_detail_dialog import IgtDetailDialog

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
CHEVRON_DOWN_SVG = os.path.join(PLUGIN_DIR, 'chevron_down_dark.svg').replace('\\', '/')

CATEGORY_KEYS = ['igt-pr', 'pertanahan', 'tata-ruang', 'derivatif', 'lainnya']
PAGE_SIZE = 8


class DatasetCard(QFrame):
    """Kartu dataset yang adaptif untuk dock sempit maupun lebar."""

    wmsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsClicked = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, dataset, seq_no=1, is_expanded=False, show_metadata=True, allow_wfs=True, parent=None):
        super().__init__(parent)
        self.dataset = dataset
        self.seq_no = seq_no
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
                padding: 4px 7px;
                min-width: 36px;
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
                padding: 4px 7px;
                min-width: 36px;
            }
            QPushButton#actionWfs:hover {
                background-color: #7c3aed;
                color: #ffffff;
            }
            QPushButton#actionBoth {
                background-color: #ecfdf5;
                color: #047857;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 8px;
                min-width: 58px;
            }
            QPushButton#actionBoth:hover {
                background-color: #047857;
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
            QLabel#titleLbl {
                color: #0f294d;
                font-size: 13px;
                font-weight: 400;
            }
            QLabel#titleLbl:hover {
                color: #1f6fd6;
                text-decoration: underline;
            }
            QPushButton#btnInfo {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 9px;
                padding: 0;
            }
            QPushButton#btnInfo:hover {
                background-color: #e0f2fe;
                border-color: #7dd3fc;
            }
        """)

        card_layout = QVBoxLayout(self)
        top_bot = 6 if not self.show_metadata else 10
        card_layout.setContentsMargins(12, top_bot, 12, top_bot)
        card_layout.setSpacing(4 if not self.show_metadata else 6)

        # 1. Baris Utama: Kolom Kiri (Nomor, Ikon Kategori, Judul, Walidata, Tanggal) & Kolom Kanan (Aksi Vertikal di Tengah)
        self.main_row = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.main_row.setContentsMargins(0, 0, 0, 0)
        self.main_row.setSpacing(10)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(3)

        # Baris 1: Nomor Urut + Ikon Kategori Ringkas + Judul IGT (tidak di-bold)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)

        self.num_lbl = QLabel(str(self.seq_no), self)
        self.num_lbl.setStyleSheet("""
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
            min-width: 16px;
        """)
        self.num_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_row.addWidget(self.num_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        self.icon_lbl = QLabel(self)
        cat = dataset.get('category', '')
        icon_name = 'map' if cat == 'tata-ruang' else 'layers' if cat == 'derivatif' else 'globe' if cat == 'lainnya' else 'pin'
        icon_color = '#047857' if cat == 'tata-ruang' else '#7c3aed' if cat == 'derivatif' else '#0284c7' if cat == 'lainnya' else '#1f6fd6'
        self.icon_lbl.setPixmap(svg_pixmap(ICONS.get(icon_name, ICONS['pin']).format(color=icon_color), QSize(16, 16)))
        title_row.addWidget(self.icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        self.title_lbl = QLabel(dataset.get('name', ''), self)
        self.title_lbl.setObjectName('titleLbl')
        font = self.title_lbl.font()
        font.setBold(False)
        font.setWeight(QFont.Weight.Normal)
        self.title_lbl.setFont(font)
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.title_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_lbl.setToolTip("Klik untuk melihat detail lengkap dataset IGT")
        self.title_lbl.mousePressEvent = lambda e: self.open_detail()
        title_row.addWidget(self.title_lbl, 1, Qt.AlignmentFlag.AlignVCenter)

        self.btn_info = QPushButton(self)
        self.btn_info.setObjectName('btnInfo')
        self.btn_info.setFixedSize(18, 18)
        self.btn_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_info.setToolTip("Detail Informasi & Metadata IGT")
        self.btn_info.setIcon(QIcon(svg_pixmap(ICONS.get('info', ICONS['pin']).format(color='#1f6fd6'), QSize(12, 12))))
        self.btn_info.setIconSize(QSize(12, 12))
        self.btn_info.clicked.connect(self.open_detail)
        title_row.addWidget(self.btn_info, 0, Qt.AlignmentFlag.AlignVCenter)

        if self.has_subs:
            sub_count = len(dataset['subLayers'])
            caret = '▴' if self.is_expanded else '▾'
            self.chip_btn = QPushButton(f"Multi-layer ({sub_count}) {caret}", self)
            self.chip_btn.setObjectName('multiChip')
            self.chip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.chip_btn.clicked.connect(self.toggle_expand)
            title_row.addWidget(self.chip_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        left_col.addLayout(title_row)

        # Baris 2 & 3: Nama Direktorat & Tanggal (hanya jika show_metadata=True, disembunyikan di dashboard agar tidak ramai)
        if self.show_metadata:
            org_text = dataset.get('direktorat') or dataset.get('satker') or dataset.get('instansi') or '—'
            self.org_lbl = QLabel(org_text, self)
            self.org_lbl.setStyleSheet("color: #475569; font-size: 12px; margin-left: 22px;")
            self.org_lbl.setWordWrap(True)
            left_col.addWidget(self.org_lbl)

            date_text = dataset.get('updated') or dataset.get('date') or '—'
            self.date_lbl = QLabel(f"Terintegrasi: {date_text}", self)
            self.date_lbl.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 22px;")
            left_col.addWidget(self.date_lbl)

        self.main_row.addLayout(left_col, 1)

        # Kolom Kanan: Tombol Aksi WMS dan WFS (Tepat di Tengah Vertikal)
        self.action_wrap = QHBoxLayout()
        self.action_wrap.setContentsMargins(0, 0, 0, 0)
        self.action_wrap.setSpacing(6)

        self.btn_wms = QPushButton('WMS', self)
        self.btn_wms.setObjectName('actionWms')
        self.btn_wms.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.has_subs:
            sub_count = len(dataset['subLayers'])
            self.btn_wms.setToolTip(f"Muat seluruh ({sub_count}) sub-IGT sekaligus sebagai layer WMS ke kanvas peta QGIS")
            self.btn_wms.clicked.connect(lambda: self._load_all_sublayers('wms'))
        else:
            self.btn_wms.setToolTip("Muat layer WMS ke kanvas peta QGIS")
            self.btn_wms.clicked.connect(lambda: self.wmsClicked.emit(self.dataset, None))
        self.action_wrap.addWidget(self.btn_wms)

        if self.allow_wfs:
            self.btn_wfs = QPushButton('WFS', self)
            self.btn_wfs.setObjectName('actionWfs')
            self.btn_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
            if self.has_subs:
                sub_count = len(dataset['subLayers'])
                self.btn_wfs.setToolTip(f"Muat seluruh ({sub_count}) sub-IGT sekaligus sebagai layer WFS ke kanvas peta QGIS")
                self.btn_wfs.clicked.connect(lambda: self._load_all_sublayers('wfs'))
            else:
                self.btn_wfs.setToolTip("Muat layer vektor WFS ke kanvas peta QGIS")
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
                sub_title.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 400;")
                s_font = sub_title.font()
                s_font.setBold(False)
                s_font.setWeight(QFont.Weight.Normal)
                sub_title.setFont(s_font)
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

    def open_detail(self):
        """Buka dialog modal detail informasi dan metadata IGT."""
        try:
            dlg = IgtDetailDialog(self.dataset, allow_wfs=self.allow_wfs, parent=self.window())
            dlg.wmsRequested.connect(lambda ds, sl: self.wmsClicked.emit(ds, sl))
            dlg.wfsRequested.connect(lambda ds, sl: self.wfsClicked.emit(ds, sl))
            dlg.exec_()
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _load_all_sublayers(self, mode='wms'):
        """Muat seluruh sub-IGT (2 atau lebih) sekaligus ke kanvas peta QGIS sebagai WMS atau WFS."""
        if not self.has_subs:
            return
        if mode == 'wfs':
            self.wfsClicked.emit(self.dataset, None)
        else:
            for s in self.dataset.get('subLayers', []):
                self.wmsClicked.emit(self.dataset, s)

    def toggle_expand(self):
        if not self.has_subs:
            return
        self.is_expanded = not self.is_expanded
        self.subs_container.setVisible(self.is_expanded)
        sub_count = len(self.dataset['subLayers'])
        caret = '▴' if self.is_expanded else '▾'
        self.chip_btn.setText(f"Multi-layer ({sub_count}) {caret}")

    def set_expanded(self, expanded):
        if not self.has_subs or self.is_expanded == expanded:
            return
        self.is_expanded = expanded
        self.subs_container.setVisible(self.is_expanded)
        sub_count = len(self.dataset['subLayers'])
        caret = '▴' if self.is_expanded else '▾'
        self.chip_btn.setText(f"Multi-layer ({sub_count}) {caret}")

    def apply_width(self, width):
        eff_w = self.width() if self.width() > 100 else width
        is_compact = eff_w < 380
        is_narrow = eff_w < 260
        if hasattr(self, 'icon_lbl'):
            self.icon_lbl.setVisible(not is_compact)
        if hasattr(self, 'title_lbl'):
            self.title_lbl.setStyleSheet(
                f"color: #0f294d; font-size: {'12px' if is_compact else '13px'}; font-weight: 400;"
            )
        if self.has_subs and hasattr(self, 'chip_btn'):
            sub_count = len(self.dataset['subLayers'])
            caret = '▴' if self.is_expanded else '▾'
            self.chip_btn.setText(f"({sub_count}) {caret}" if is_compact else f"Multi-layer ({sub_count}) {caret}")
        if is_narrow:
            self.main_row.setDirection(QBoxLayout.Direction.TopToBottom)
            self.main_row.setSpacing(6)
            self.main_row.setAlignment(self.action_wrap, Qt.AlignmentFlag.AlignRight)
        else:
            self.main_row.setDirection(QBoxLayout.Direction.LeftToRight)
            self.main_row.setSpacing(6 if is_compact else 10)
            self.main_row.setAlignment(self.action_wrap, Qt.AlignmentFlag.AlignVCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_width(event.size().width())

    def minimumSizeHint(self):
        return QSize(160, 36)


class DynamicTabButton(QPushButton):
    """Tombol tab kategori katalog dinamis yang dapat mengecil fleksibel dan mempertahankan icon."""

    def __init__(self, key, full_text, short_text, icon_key, color, parent=None):
        super().__init__(full_text, parent)
        self.key = key
        self.full_text = full_text
        self.short_text = short_text
        self.icon_key = icon_key
        self.color = color
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIcon(QIcon(svg_pixmap(ICONS.get(icon_key, ICONS['pin']).format(color=color), QSize(13, 13))))
        self.setIconSize(QSize(13, 13))

    def minimumSizeHint(self):
        return QSize(22, 28)


class CatalogPage(QWidget):
    """Halaman / Widget Katalog Data V2 dengan 5 Tab Kategori, Paginasi 8 Data, dan Desain Responsif."""

    backToDashboardRequested = pyqtSignal()
    openFullCatalogRequested = pyqtSignal(str)   # category key
    wmsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, current_category='igt-pr', current_role='superadmin', embedded=True, parent=None):
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
                font-size: 12px;
                font-weight: 700;
                padding: 5px 10px;
            }
            QPushButton#backBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QLineEdit#searchInput {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #0f294d;
            }
            QLineEdit#searchInput:focus {
                border-color: #1f6fd6;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 30px 6px 10px;
                font-size: 12px;
                color: #0f294d;
                font-weight: 600;
                min-height: 22px;
            }
            QComboBox:focus {
                border-color: #1f6fd6;
            }
            QComboBox:disabled {
                background: #f8fafc;
                color: #94a3b8;
                border: 1px solid #e2e8f0;
            }
            QComboBox QLineEdit {
                border: none;
                background: transparent;
                color: #0f294d;
                font-weight: 600;
                font-size: 12px;
                padding: 0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url('%CHEVRON%');
                width: 12px;
                height: 12px;
            }
            QComboBox::down-arrow:disabled {
                opacity: 0.35;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f294d;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                selection-background-color: #eff6ff;
                selection-color: #1d4ed8;
                outline: none;
                padding: 4px;
                max-height: 200px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 26px;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 8px;
                border-radius: 4px;
                margin: 2px 2px 2px 2px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollArea#catalogScroll {
                background: transparent;
                border: none;
            }
        """.replace('%CHEVRON%', CHEVRON_DOWN_SVG))

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

        # 2. Subnav 5 Tab Kategori (Dinamis, Stretch sampai ujung, Responsif)
        self.tabs_container = QWidget(self)
        self.tabs_container.setObjectName('tabsContainer')
        self.tabs_container.setStyleSheet("background: transparent;")
        self.subnav_layout = QGridLayout(self.tabs_container)
        self.subnav_layout.setContentsMargins(0, 0, 0, 0)
        self.subnav_layout.setHorizontalSpacing(4)
        self.subnav_layout.setVerticalSpacing(4)
        self.nav_buttons = {}
        self.tab_meta = {}
        self._subnav_mode = None

        # Memuat tab kategori secara dinamis dari CATEGORIES dengan stretch merata sampai ujung
        for idx, (cat_key, cat_info) in enumerate(CATEGORIES.items()):
            full_title = cat_info.get('label', cat_key)
            short_title = cat_info.get('shortLabel', full_title)
            icon_key = cat_info.get('icon', 'pin')
            color = cat_info.get('color', '#1f6fd6')

            btn = DynamicTabButton(cat_key, full_title, short_title, icon_key, color, self.tabs_container)
            btn.clicked.connect(lambda checked, k=cat_key: self.set_category(k))
            self.subnav_layout.addWidget(btn, 0, idx)
            self.subnav_layout.setColumnStretch(idx, 1)
            self.nav_buttons[cat_key] = btn
            self.tab_meta[cat_key] = (icon_key, color)

        target_layout.addWidget(self.tabs_container)

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

        # Search & Filter Row (Pencarian di kiri, tombol Filter di kanan)
        filter_top_row = QHBoxLayout()
        filter_top_row.setContentsMargins(0, 0, 0, 0)
        filter_top_row.setSpacing(6)

        self.search_input = QLineEdit(self.filter_card)
        self.search_input.setObjectName('searchInput')
        self.search_input.setPlaceholderText('Cari nama IGT, sublayer, wilayah...')
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_top_row.addWidget(self.search_input, 1)

        self.filter_toggle_btn = QPushButton('Filter', self.filter_card)
        self.filter_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_toggle_btn.setIcon(QIcon(svg_pixmap(ICONS.get('filter', ICONS['layers']).format(color='#1f6fd6'), QSize(14, 14))))
        self.filter_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #1f6fd6;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 9px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
        """)
        self.filter_toggle_btn.clicked.connect(self._toggle_filter_dropdowns)
        filter_top_row.addWidget(self.filter_toggle_btn)
        self.fc_main_layout.addLayout(filter_top_row)

        # Dropdowns container (Provinsi + Kabupaten) - Default tertutup/sembunyi, dibuka saat klik tombol Filter
        self._filter_dropdowns_open = False
        self.filter_dropdowns_container = QWidget(self.filter_card)
        self.filter_dropdowns_container.setVisible(False)
        self.filter_box_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.filter_dropdowns_container)
        self.filter_box_layout.setContentsMargins(0, 6, 0, 0)
        self.filter_box_layout.setSpacing(8)

        # Provinsi Filter (dengan header reset filter)
        prov_box = QWidget(self.filter_dropdowns_container)
        prov_box_layout = QVBoxLayout(prov_box)
        prov_box_layout.setContentsMargins(0, 0, 0, 0)
        prov_box_layout.setSpacing(3)

        prov_head = QHBoxLayout()
        prov_head.setContentsMargins(0, 0, 0, 0)
        self.prov_lbl = QLabel('PROVINSI', prov_box)
        self.prov_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        prov_head.addWidget(self.prov_lbl)
        prov_head.addStretch()

        self.filter_reset_btn = QPushButton('✕ Reset Filter', prov_box)
        self.filter_reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_reset_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ef4444;
                border: none;
                font-size: 10px;
                font-weight: 700;
                padding: 0 4px;
            }
            QPushButton:hover {
                color: #b91c1c;
                text-decoration: underline;
            }
        """)
        self.filter_reset_btn.clicked.connect(self._reset_filters)
        self.filter_reset_btn.setVisible(False)
        prov_head.addWidget(self.filter_reset_btn)
        prov_box_layout.addLayout(prov_head)

        self.prov_combo = SearchableComboBox(prov_box)
        self.prov_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.prov_combo.setMaxVisibleItems(8)
        if self.prov_combo.lineEdit():
            self.prov_combo.lineEdit().setPlaceholderText("Pilih atau ketik nama provinsi...")
            self.prov_combo.lineEdit().returnPressed.connect(self._on_prov_changed)
            self.prov_combo.lineEdit().editingFinished.connect(self._on_prov_changed)
            self.prov_combo.lineEdit().textChanged.connect(self._on_prov_text_changed)

        if self.prov_combo.view():
            self.prov_combo.view().setMaximumHeight(200)
            self.prov_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.prov_combo.view().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.prov_combo.currentIndexChanged.connect(self._on_prov_changed)
        prov_box_layout.addWidget(self.prov_combo)
        self.filter_box_layout.addWidget(prov_box)

        # Kabupaten Filter
        kab_box = QWidget(self.filter_dropdowns_container)
        kab_box_layout = QVBoxLayout(kab_box)
        kab_box_layout.setContentsMargins(0, 0, 0, 0)
        kab_box_layout.setSpacing(3)
        self.kab_lbl = QLabel('KABUPATEN / KOTA', kab_box)
        self.kab_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 800; letter-spacing: 1px;")
        kab_box_layout.addWidget(self.kab_lbl)
        self.kab_combo = QComboBox(kab_box)
        self.kab_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.kab_combo.setMaxVisibleItems(8)
        if self.kab_combo.view():
            self.kab_combo.view().setMaximumHeight(200)
            self.kab_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.kab_combo.view().setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.kab_combo.currentIndexChanged.connect(self._on_kab_changed)
        kab_box_layout.addWidget(self.kab_combo)
        self.filter_box_layout.addWidget(kab_box)

        self.fc_main_layout.addWidget(self.filter_dropdowns_container)
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
        self._update_tab_labels(width)
        is_filter_narrow = width < 480
        if hasattr(self, 'filter_box_layout'):
            self.filter_box_layout.setDirection(
                QBoxLayout.Direction.TopToBottom if is_filter_narrow else QBoxLayout.Direction.LeftToRight
            )
        is_narrow = width < 280
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
        if getattr(self, '_last_is_narrow', None) != is_narrow:
            self._last_is_narrow = is_narrow
            if hasattr(self, '_last_total_pages'):
                self._update_pagination_ui(self._last_total_pages, self._last_total_items)

    def _update_tab_labels(self, width=None):
        if not hasattr(self, 'nav_buttons') or not self.nav_buttons:
            return
        if width is None:
            width = self.width() if self.width() > 0 else 480

        btns = list(self.nav_buttons.values())
        new_mode = 'single' if width >= 580 else 'two_rows'
        if getattr(self, '_subnav_mode', None) != new_mode:
            self._subnav_mode = new_mode
            for b in btns:
                self.subnav_layout.removeWidget(b)
            for c in range(6):
                self.subnav_layout.setColumnStretch(c, 0)
            if new_mode == 'single':
                for idx, b in enumerate(btns):
                    self.subnav_layout.addWidget(b, 0, idx)
                    self.subnav_layout.setColumnStretch(idx, 1)
            else:
                # Baris 0: 3 tab pertama masing-masing span 2 kolom (dari 6 kolom)
                for idx in range(min(3, len(btns))):
                    self.subnav_layout.addWidget(btns[idx], 0, idx * 2, 1, 2)
                # Baris 1: 2 tab terakhir masing-masing span 3 kolom (dari 6 kolom)
                if len(btns) > 3:
                    self.subnav_layout.addWidget(btns[3], 1, 0, 1, 3)
                if len(btns) > 4:
                    self.subnav_layout.addWidget(btns[4], 1, 3, 1, 3)
                for c in range(6):
                    self.subnav_layout.setColumnStretch(c, 1)

        avail_w = max(60, width - 28)
        for idx, (key, btn) in enumerate(self.nav_buttons.items()):
            full_title = getattr(btn, 'full_text', btn.text())
            short_title = getattr(btn, 'short_text', full_title)

            if new_mode == 'single':
                tab_w = avail_w / max(1, len(btns))
            else:
                tab_w = (avail_w / 3.0) if idx < 3 else (avail_w / 2.0)

            avail_text = tab_w - 28
            fm = btn.fontMetrics()
            adv = getattr(fm, 'horizontalAdvance', fm.width)

            if adv(full_title) <= avail_text:
                btn.setText(full_title)
            elif adv(short_title) <= avail_text:
                btn.setText(short_title)
            else:
                btn.setText(fm.elidedText(short_title, Qt.TextElideMode.ElideRight, max(20, int(avail_text))))

            btn.setToolTip(full_title)

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
        if self.prov_combo.lineEdit():
            self.prov_combo.lineEdit().blockSignals(True)

        curr = self.prov_combo.currentText()
        self.prov_combo.clear()
        self.all_provs = sorted(list(INDONESIA_REGIONS.keys()))
        items = ['Semua Provinsi'] + self.all_provs
        self.prov_combo.addItems(items)

        # Update Completer
        if hasattr(self.prov_combo, '_setup_completer'):
            self.prov_combo._setup_completer()

        if curr in items and curr != 'Semua Provinsi':
            idx = self.prov_combo.findText(curr)
            if idx >= 0:
                self.prov_combo.setCurrentIndex(idx)
            if self.prov_combo.lineEdit():
                self.prov_combo.lineEdit().setText(curr)
        else:
            self.prov_combo.setCurrentIndex(0)
            if self.prov_combo.lineEdit():
                self.prov_combo.lineEdit().clear()
                self.prov_combo.lineEdit().setPlaceholderText("Pilih atau ketik provinsi...")

        if self.prov_combo.lineEdit():
            self.prov_combo.lineEdit().blockSignals(False)
        self.prov_combo.blockSignals(False)
        self._populate_kab_combo()

    def _get_selected_prov(self):
        """Mendapatkan nama provinsi yang valid jika dipilih atau diketik."""
        raw = self.prov_combo.currentText().strip()
        all_provs = getattr(self, 'all_provs', sorted(list(INDONESIA_REGIONS.keys())))
        return match_province_name(raw, all_provs)

    def _get_selected_kab(self):
        """Mendapatkan nama kabupaten/kota yang valid jika dipilih."""
        if not self.kab_combo.isEnabled():
            return None
        raw = self.kab_combo.currentText().strip()
        if not raw or raw in ('Semua Kabupaten / Kota', 'Semua Kab / Kota', '-- Pilih Provinsi Terlebih Dahulu --'):
            return None
        return raw

    def _populate_kab_combo(self):
        prov = self._get_selected_prov()
        self.kab_combo.blockSignals(True)
        curr = self.kab_combo.currentText()
        self.kab_combo.clear()

        if not prov:
            self.kab_combo.addItem('-- Pilih Provinsi Terlebih Dahulu --')
            self.kab_combo.setCurrentIndex(0)
            self.kab_combo.setEnabled(False)
        else:
            self.kab_combo.setEnabled(True)
            kabs = INDONESIA_REGIONS.get(prov, [])
            items = ['Semua Kabupaten / Kota'] + kabs
            self.kab_combo.addItems(items)
            matched_idx = -1
            if curr in items:
                matched_idx = items.index(curr)
            elif curr and curr != '-- Pilih Provinsi Terlebih Dahulu --':
                clean_curr = curr.lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').strip()
                for i, it in enumerate(items):
                    clean_it = it.lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').strip()
                    if clean_curr == clean_it or clean_curr in it.lower():
                        matched_idx = i
                        break
            if matched_idx >= 0:
                self.kab_combo.setCurrentIndex(matched_idx)
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

    def _toggle_filter_dropdowns(self, *args, **kwargs):
        if 'force_open' in kwargs and kwargs['force_open'] is not None:
            self._filter_dropdowns_open = bool(kwargs['force_open'])
        else:
            self._filter_dropdowns_open = not getattr(self, '_filter_dropdowns_open', False)

        self.filter_dropdowns_container.setVisible(self._filter_dropdowns_open)
        has_filter = bool(self.get_active_admin_filter())
        self.filter_toggle_btn.setText('Filter (1)' if has_filter else 'Filter')
        if self._filter_dropdowns_open:
            self.filter_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1f6fd6;
                    color: #ffffff;
                    border: 1px solid #1f6fd6;
                    border-radius: 8px;
                    padding: 6px 9px;
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
            """)
            self.filter_toggle_btn.setIcon(QIcon(svg_pixmap(ICONS.get('filter', ICONS['layers']).format(color='#ffffff'), QSize(14, 14))))
        else:
            if has_filter:
                self.filter_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #eff6ff;
                        color: #1f6fd6;
                        border: 1px solid #1f6fd6;
                        border-radius: 8px;
                        padding: 6px 9px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #dbeafe;
                    }
                """)
            else:
                self.filter_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #1f6fd6;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        padding: 6px 9px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #eff6ff;
                        border-color: #93c5fd;
                    }
                """)
            self.filter_toggle_btn.setIcon(QIcon(svg_pixmap(ICONS.get('filter', ICONS['layers']).format(color='#1f6fd6'), QSize(14, 14))))

    def _on_prov_text_changed(self, text):
        if not text.strip():
            self._on_prov_changed()

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

    def _reset_filters(self):
        """Mereset seluruh filter wilayah kembali ke kondisi awal."""
        self.set_admin_filter('', '')

    def get_active_admin_filter(self):
        """Mengambil pilihan filter wilayah aktif (provinsi & kabupaten) dari form filter katalog."""
        prov = self._get_selected_prov()
        if not prov:
            return None
        kab = self._get_selected_kab()
        return {
            'provinsi': prov,
            'kabupaten': kab or 'Semua Kabupaten / Kota'
        }

    def set_admin_filter(self, prov_name, kab_name=None):
        """Menyetel filter wilayah katalog secara terprogram (misal hasil dari dialog WFS)."""
        if not prov_name or prov_name in ('Semua Provinsi', '-- Pilih Provinsi Terlebih Dahulu --', ''):
            self.prov_combo.blockSignals(True)
            if self.prov_combo.lineEdit():
                self.prov_combo.lineEdit().blockSignals(True)
                self.prov_combo.lineEdit().clear()
                self.prov_combo.lineEdit().setPlaceholderText("Pilih atau ketik provinsi...")
                self.prov_combo.lineEdit().blockSignals(False)
            self.prov_combo.setCurrentIndex(0)
            self.prov_combo.blockSignals(False)
            self._populate_kab_combo()
            self.current_page = 1
            self._render_page()
            self.filter_toggle_btn.setText('Filter')
            if not getattr(self, '_filter_dropdowns_open', False):
                self.filter_toggle_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #1f6fd6;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        padding: 6px 9px;
                        font-size: 11px;
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #eff6ff;
                        border-color: #93c5fd;
                    }
                """)
                self.filter_toggle_btn.setIcon(QIcon(svg_pixmap(ICONS.get('filter', ICONS['layers']).format(color='#1f6fd6'), QSize(14, 14))))
            return

        all_provs = getattr(self, 'all_provs', sorted(list(INDONESIA_REGIONS.keys())))
        matched_prov = match_province_name(prov_name, all_provs)

        if matched_prov:
            # Pastikan drawer filter terbuka jika disetel wilayah spesifik
            if not getattr(self, '_filter_dropdowns_open', False):
                self._toggle_filter_dropdowns(force_open=True)

            self.prov_combo.blockSignals(True)
            if self.prov_combo.lineEdit():
                self.prov_combo.lineEdit().blockSignals(True)
                self.prov_combo.lineEdit().setText(matched_prov)
                self.prov_combo.lineEdit().blockSignals(False)
            idx = self.prov_combo.findText(matched_prov)
            if idx >= 0:
                self.prov_combo.setCurrentIndex(idx)
            else:
                self.prov_combo.setEditText(matched_prov)
            self.prov_combo.blockSignals(False)

            self._populate_kab_combo()

            if kab_name and kab_name not in ('Semua Kabupaten / Kota', 'Semua Kab / Kota', '-- Pilih Provinsi Terlebih Dahulu --', ''):
                self.kab_combo.blockSignals(True)
                clean_k = kab_name.lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').strip()
                for i in range(self.kab_combo.count()):
                    txt = self.kab_combo.itemText(i)
                    clean_txt = txt.lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').strip()
                    if (txt.lower() == kab_name.lower() or
                        clean_k == clean_txt or
                        clean_k in txt.lower()):
                        self.kab_combo.setCurrentIndex(i)
                        break
                self.kab_combo.blockSignals(False)

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
            icon_key, icon_color = self.tab_meta.get(key, ('pin', '#1f6fd6'))
            if key == cat_key:
                btn.setIcon(QIcon(svg_pixmap(ICONS.get(icon_key, ICONS['pin']).format(color='#ffffff'), QSize(13, 13))))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1f6fd6;
                        color: #ffffff;
                        border: none;
                        border-radius: 16px;
                        padding: 5px 6px;
                        font-weight: 700;
                        font-size: 11px;
                    }
                """)
            else:
                btn.setIcon(QIcon(svg_pixmap(ICONS.get(icon_key, ICONS['pin']).format(color=icon_color), QSize(13, 13))))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #475569;
                        border: 1px solid #cbd5e1;
                        border-radius: 16px;
                        padding: 5px 6px;
                        font-weight: 600;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        border-color: #94a3b8;
                    }
                """)

        self._update_tab_labels()
        self._render_page()

    def _get_filtered_records(self):
        query = self.search_input.text().strip().lower()
        selected_prov = self._get_selected_prov()
        selected_kab = self._get_selected_kab()

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
            if selected_prov:
                prov_haystack = ((d.get('prov') or '') + ' ' + (d.get('scope') or '')).lower()
                p_lower = selected_prov.lower()
                match_alias = (
                    ('yogyakarta' in p_lower and ('yogyakarta' in prov_haystack or 'd.i.' in prov_haystack))
                    or ('jakarta' in p_lower and ('jakarta' in prov_haystack or 'dki' in prov_haystack))
                    or ('bangka belitung' in p_lower and 'bangka' in prov_haystack)
                    or (p_lower in prov_haystack)
                )
                if not match_alias and 'nasional' not in prov_haystack:
                    continue

            # 3. Filter Kabupaten (mengikuti provinsi terpilih)
            if selected_kab:
                kab_haystack = ((d.get('kab') or '') + ' ' + (d.get('scope') or '')).lower()
                clean_kab = selected_kab.lower().replace('kabupaten', '').replace('kab.', '').replace('kota', '').strip()
                if clean_kab not in kab_haystack and selected_kab.lower() not in kab_haystack:
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
        year_suffix = f" · Tahun {self.selected_year}" if getattr(self, 'selected_year', 'Semua tahun') != 'Semua tahun' else ""
        if total_items > 0:
            self.count_lbl.setText(
                f"Menampilkan {start_idx + 1}–{end_idx} dari {total_items} dataset · "
                f"Halaman {self.current_page} dari {total_pages} · Kategori {cat_label}{year_suffix}"
            )
        else:
            self.count_lbl.setText(f"Tidak ada dataset yang cocok · Kategori {cat_label}{year_suffix}")

        # Update indikator tombol filter dan reset
        has_filter = bool(self.get_active_admin_filter())
        if hasattr(self, 'filter_reset_btn'):
            self.filter_reset_btn.setVisible(has_filter)
        if hasattr(self, 'filter_toggle_btn'):
            self.filter_toggle_btn.setText('Filter (1)' if has_filter else 'Filter')

        # Render Kartu Dataset (8 data teratas untuk halaman aktif)
        if not page_items:
            empty_card = QFrame(self.list_content)
            empty_card.setObjectName("emptyCard")
            empty_card.setStyleSheet("QFrame#emptyCard { background-color: #ffffff; border: 1px dashed #cbd5e1; border-radius: 10px; padding: 24px; }")
            ec_layout = QVBoxLayout(empty_card)
            ec_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl = QLabel('Tidak ada dataset yang cocok dengan kriteria filter atau pencarian.', empty_card)
            lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ec_layout.addWidget(lbl)
            self.list_layout.addWidget(empty_card)
        else:
            query = self.search_input.text().strip().lower()
            sel_yr = getattr(self, 'selected_year', 'Semua tahun')
            for idx, d in enumerate(page_items):
                d_id = d.get('id', '')
                is_exp = self.expanded_states.get(d_id, False)
                if query and d.get('subLayers'):
                    match_sub = any(query in s.get('name', '').lower() for s in d['subLayers'])
                    if match_sub:
                        is_exp = True
                if sel_yr != 'Semua tahun' and d.get('subLayers'):
                    match_year_sub = any(sel_yr in (s.get('year') or s.get('updated') or '') for s in d['subLayers'])
                    if match_year_sub:
                        is_exp = True

                allow_wfs = can_access_wfs(self.current_role, d)
                card = DatasetCard(d, seq_no=start_idx + idx + 1, is_expanded=is_exp, show_metadata=not self.embedded, allow_wfs=allow_wfs, parent=self.list_content)
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

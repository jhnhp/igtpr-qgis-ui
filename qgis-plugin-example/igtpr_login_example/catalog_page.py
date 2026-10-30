# -*- coding: utf-8 -*-
"""Halaman Katalog Data IGT-PR Mockup V2 dengan Opsi 2 (Hierarchical Accordion & Multi-layer Chips)."""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS
from .login_page import svg_pixmap

CATEGORY_KEYS = ['pertanahan', 'tata-ruang', 'derivatif', 'lainnya']


class MultiLayerChip(QPushButton):
    """Chip penanda 'Multi-Layer' di kolom aksi kanan (posisi WMS)."""

    def __init__(self, parent=None):
        super().__init__('Multi-Layer', parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                color: #047857;
                font-size: 11px;
                font-weight: 700;
                padding: 4px 6px;
            }
            QPushButton:hover {
                background-color: #d1fae5;
                border-color: #34d399;
                color: #065f46;
            }
        """)


class MultiLayerCountBtn(QPushButton):
    """Tombol jumlah layer dan caret di kolom aksi kanan (posisi WFS)."""

    def __init__(self, count, is_expanded=False, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.count = count
        self.is_expanded = is_expanded
        self.update_state(is_expanded)

    def update_state(self, is_expanded):
        self.is_expanded = is_expanded
        caret = '▴' if is_expanded else '▾'
        self.setText(f"{self.count} Layer {caret}")
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#d1fae5' if is_expanded else '#ecfdf5'};
                border: 1px solid {'#34d399' if is_expanded else '#a7f3d0'};
                border-radius: 6px;
                color: {'#065f46' if is_expanded else '#047857'};
                font-size: 10.5px;
                font-weight: 700;
                padding: 4px 6px;
            }}
            QPushButton:hover {{
                background-color: #a7f3d0;
                border-color: #059669;
                color: #065f46;
            }}
        """)


class CatalogPage(QWidget):
    """Halaman Katalog Data V2 dengan Accordion Tree Table, Filter, dan Tombol WMS/WFS."""

    backToDashboardRequested = pyqtSignal()
    wmsRequested = pyqtSignal(dict, dict)  # (parent_dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, dict)  # (parent_dataset, sublayer or None)

    def __init__(self, current_category='pertanahan', current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_category = current_category
        self.current_role = current_role
        self.setObjectName('catalogPage')

        self.setStyleSheet("""
            QWidget#catalogPage {
                background-color: #f4f7fb;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton#backBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #1f6fd6;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 12px;
            }
            QPushButton#backBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QLineEdit#searchInput {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 7px 10px;
                font-size: 12px;
                color: #0f294d;
            }
            QLineEdit#searchInput:focus {
                border-color: #1f6fd6;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
                color: #0f294d;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #1f6fd6;
            }
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 12px;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget::item {
                border-bottom: 1px solid #f1f5f9;
                padding: 6px 0;
            }
            QTreeWidget::item:selected {
                background-color: #f0f7ff;
                color: #0f294d;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: none;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: 700;
                font-size: 11.5px;
                border: none;
                border-bottom: 1.5px solid #e2e8f0;
                padding: 10px 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header (Title, Desc, Back Button)
        head_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_lbl = QLabel('Katalog IGT Pertanahan', self)
        self.title_lbl.setStyleSheet("color: #0f294d; font-size: 18px; font-weight: 800;")
        text_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel('Dataset IGT Pertanahan yang sudah terintegrasi dan siap dimuat ke kanvas QGIS.', self)
        self.desc_lbl.setStyleSheet("color: #64748b; font-size: 11.5px;")
        text_layout.addWidget(self.desc_lbl)
        head_layout.addLayout(text_layout, 1)

        back_btn = QPushButton('← Kembali ke Dashboard', self)
        back_btn.setObjectName('backBtn')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.backToDashboardRequested.emit)
        head_layout.addWidget(back_btn)

        layout.addLayout(head_layout)

        # 2. Subnav Category Pills
        self.subnav_layout = QHBoxLayout()
        self.subnav_layout.setSpacing(8)
        self.nav_buttons = {}
        for cat_key in CATEGORY_KEYS:
            cat_info = CATEGORIES[cat_key]
            btn = QPushButton(cat_info['label'], self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=cat_key: self.set_category(k))
            self.subnav_layout.addWidget(btn)
            self.nav_buttons[cat_key] = btn
        self.subnav_layout.addStretch()
        layout.addLayout(self.subnav_layout)

        # 3. Filter Controls (Search, Year, Region)
        filter_card = QFrame(self)
        filter_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 12px;
            }
        """)
        f_layout = QHBoxLayout(filter_card)
        f_layout.setContentsMargins(4, 4, 4, 4)
        f_layout.setSpacing(10)

        # Search box
        search_box = QVBoxLayout()
        search_box.setSpacing(2)
        s_lbl = QLabel('PENCARIAN DATASET', filter_card)
        s_lbl.setStyleSheet("color: #64748b; font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;")
        search_box.addWidget(s_lbl)
        self.search_input = QLineEdit(filter_card)
        self.search_input.setObjectName('searchInput')
        self.search_input.setPlaceholderText('Cari nama IGT, sublayer, direktorat...')
        self.search_input.textChanged.connect(self._render_table)
        search_box.addWidget(self.search_input)
        f_layout.addLayout(search_box, 2)

        # Year filter
        year_box = QVBoxLayout()
        year_box.setSpacing(2)
        y_lbl = QLabel('TAHUN', filter_card)
        y_lbl.setStyleSheet("color: #64748b; font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;")
        year_box.addWidget(y_lbl)
        self.year_combo = QComboBox(filter_card)
        self.year_combo.addItems(['Semua tahun', '2026', '2025', '2024', '2023'])
        self.year_combo.currentIndexChanged.connect(self._render_table)
        year_box.addWidget(self.year_combo)
        f_layout.addLayout(year_box, 1)

        # Region filter
        reg_box = QVBoxLayout()
        reg_box.setSpacing(2)
        r_lbl = QLabel('WILAYAH', filter_card)
        r_lbl.setStyleSheet("color: #64748b; font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;")
        reg_box.addWidget(r_lbl)
        self.reg_combo = QComboBox(filter_card)
        self.reg_combo.addItems(['Semua Wilayah', 'Kab. Sleman', 'Kab. Bantul', 'Kab. Kulon Progo', 'Kab. Gunungkidul', 'Kota Yogyakarta', 'Nasional'])
        self.reg_combo.currentIndexChanged.connect(self._render_table)
        reg_box.addWidget(self.reg_combo)
        f_layout.addLayout(reg_box, 1)

        layout.addWidget(filter_card)

        # 4. Count & Summary Info
        self.count_lbl = QLabel('', self)
        self.count_lbl.setStyleSheet("color: #475569; font-size: 11.5px; font-weight: 600; margin-top: 2px;")
        layout.addWidget(self.count_lbl)

        # 5. Tree Table (Opsi 2 Accordion)
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(['Nama IGT', 'Direktorat', 'Tanggal Pembaruan', 'Tampilkan WMS', 'Tampilkan WFS'])
        self.tree.setIndentation(16)
        self.tree.setAnimated(True)

        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(1, 230)
        self.tree.setColumnWidth(3, 105)
        self.tree.setColumnWidth(4, 105)
        self.tree.itemExpanded.connect(self._on_item_expanded_changed)
        self.tree.itemCollapsed.connect(self._on_item_expanded_changed)

        layout.addWidget(self.tree, 1)

        self.set_category(current_category)

    def _on_item_expanded_changed(self, item):
        w = self.tree.itemWidget(item, 4)
        if isinstance(w, MultiLayerCountBtn):
            w.update_state(item.isExpanded())

    def set_category(self, cat_key):
        self.current_category = cat_key
        cat_info = CATEGORIES.get(cat_key, CATEGORIES['pertanahan'])

        # Update title & desc
        self.title_lbl.setText(f"Katalog {cat_info['label']}")
        self.desc_lbl.setText(f"{cat_info['desc']} Memuat data WMS/WFS langsung ke kanvas QGIS.")

        # Update header column 1 (Direktorat or Instansi)
        org_title = 'Instansi' if cat_key == 'lainnya' else 'Direktorat'
        self.tree.headerItem().setText(1, org_title)

        # Update subnav styles
        for key, btn in self.nav_buttons.items():
            if key == cat_key:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1f6fd6;
                        color: #ffffff;
                        border: none;
                        border-radius: 20px;
                        padding: 7px 16px;
                        font-weight: 700;
                        font-size: 11.5px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #475569;
                        border: 1px solid #cbd5e1;
                        border-radius: 20px;
                        padding: 7px 16px;
                        font-weight: 600;
                        font-size: 11.5px;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        border-color: #94a3b8;
                    }
                """)

        self._render_table()

    def _render_table(self):
        self.tree.clear()
        query = self.search_input.text().strip().lower()
        selected_year = self.year_combo.currentText()
        selected_reg = self.reg_combo.currentText()

        records = [d for d in DATASETS if d.get('category') == self.current_category]

        filtered = []
        for d in records:
            # Year check
            if selected_year != 'Semua tahun':
                match_p = selected_year in d.get('updated', '') or selected_year in d.get('date', '')
                match_sub = any(selected_year in s.get('year', '') or selected_year in s.get('updated', '') for s in d.get('subLayers', []))
                if not (match_p or match_sub):
                    continue

            # Region check
            if selected_reg != 'Semua Wilayah':
                reg_haystack = (d.get('prov', '') + ' ' + d.get('kab', '') + ' ' + d.get('scope', '')).lower()
                if selected_reg.lower() not in reg_haystack and 'nasional' not in d.get('prov', '').lower():
                    continue

            # Query check
            if query:
                org_val = d.get('direktorat', '') or d.get('satker', '') or d.get('instansi', '')
                subs_text = ' '.join([s.get('name', '') + ' ' + s.get('label', '') for s in d.get('subLayers', [])])
                haystack = (d.get('name', '') + ' ' + org_val + ' ' + d.get('scope', '') + ' ' + subs_text).lower()
                if query not in haystack:
                    continue

            filtered.append(d)

        org_label = 'Instansi' if self.current_category == 'lainnya' else 'Direktorat'
        self.count_lbl.setText(f"Menampilkan {len(filtered)} dari {len(records)} dataset · Kategori {CATEGORIES[self.current_category]['label']}")

        for d in filtered:
            has_subs = bool(d.get('subLayers'))

            # Parent Item
            item = QTreeWidgetItem(self.tree)

            # Col 0: Custom Widget with Title only
            col0_widget = QWidget()
            col0_layout = QHBoxLayout(col0_widget)
            col0_layout.setContentsMargins(6, 4, 6, 4)
            col0_layout.setSpacing(8)

            name_lbl = QLabel(d['name'], col0_widget)
            name_lbl.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 700;")
            col0_layout.addWidget(name_lbl)
            col0_layout.addStretch()
            self.tree.setItemWidget(item, 0, col0_widget)

            # Col 1: Direktorat / Instansi
            org_lbl = QLabel(d.get('direktorat') or d.get('satker') or d.get('instansi') or '—')
            org_lbl.setWordWrap(True)
            org_lbl.setStyleSheet("color: #334155; font-size: 11.5px;")
            self.tree.setItemWidget(item, 1, org_lbl)

            # Col 2: Tanggal
            date_lbl = QLabel(d.get('updated') or d.get('date') or '—')
            date_lbl.setStyleSheet("color: #64748b; font-size: 11.5px;")
            self.tree.setItemWidget(item, 2, date_lbl)

            # Col 3 & 4: Actions (WMS/WFS for single layer, Multi-Layer Chip pair for multi-layer)
            if has_subs:
                chip_btn = MultiLayerChip(self.tree)
                count_btn = MultiLayerCountBtn(len(d['subLayers']), is_expanded=item.isExpanded(), parent=self.tree)

                def make_toggle(it, cb):
                    def _toggle():
                        exp = not it.isExpanded()
                        it.setExpanded(exp)
                        cb.update_state(exp)
                    return _toggle

                toggler = make_toggle(item, count_btn)
                chip_btn.clicked.connect(toggler)
                count_btn.clicked.connect(toggler)

                self.tree.setItemWidget(item, 3, chip_btn)
                self.tree.setItemWidget(item, 4, count_btn)
            else:
                btn_wms = QPushButton('WMS')
                btn_wms.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_wms.setStyleSheet("""
                    QPushButton {
                        background-color: #eff6ff;
                        color: #1f6fd6;
                        border: 1px solid #bfdbfe;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 700;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #1f6fd6;
                        color: #ffffff;
                    }
                """)
                btn_wms.clicked.connect(lambda checked, ds=d: self.wmsRequested.emit(ds, None))
                self.tree.setItemWidget(item, 3, btn_wms)

                btn_wfs = QPushButton('WFS')
                btn_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_wfs.setStyleSheet("""
                    QPushButton {
                        background-color: #f5f3ff;
                        color: #7c3aed;
                        border: 1px solid #ddd6fe;
                        border-radius: 6px;
                        font-size: 11px;
                        font-weight: 700;
                        padding: 4px 8px;
                    }
                    QPushButton:hover {
                        background-color: #7c3aed;
                        color: #ffffff;
                    }
                """)
                btn_wfs.clicked.connect(lambda checked, ds=d: self.wfsRequested.emit(ds, None))
                self.tree.setItemWidget(item, 4, btn_wfs)

            # Expand if searching and query matches sublayers
            if query and has_subs:
                item.setExpanded(True)

            # Add Sublayer Child Rows
            if has_subs:
                for sub in d['subLayers']:
                    child_item = QTreeWidgetItem(item)

                    # Col 0: Branch line └─ and Sublayer title
                    sub_widget = QWidget()
                    sub_layout = QHBoxLayout(sub_widget)
                    sub_layout.setContentsMargins(18, 2, 6, 2)
                    sub_layout.setSpacing(6)

                    branch_lbl = QLabel('└─', sub_widget)
                    branch_lbl.setStyleSheet("color: #94a3b8; font-weight: 800; font-size: 12px;")
                    sub_layout.addWidget(branch_lbl)

                    sub_title = QLabel(sub['name'], sub_widget)
                    sub_title.setStyleSheet("color: #1e293b; font-size: 11.5px; font-weight: 600;")
                    sub_layout.addWidget(sub_title)
                    sub_layout.addStretch()
                    self.tree.setItemWidget(child_item, 0, sub_widget)

                    # Col 1: Scope / Satker
                    sub_scope = QLabel(sub.get('scope') or d.get('direktorat') or '—')
                    sub_scope.setStyleSheet("color: #64748b; font-size: 11px;")
                    self.tree.setItemWidget(child_item, 1, sub_scope)

                    # Col 2: Sublayer date
                    sub_date = QLabel(sub.get('updated') or d.get('updated') or '—')
                    sub_date.setStyleSheet("color: #64748b; font-size: 11px;")
                    self.tree.setItemWidget(child_item, 2, sub_date)

                    # Col 3: Sub WMS Button
                    sub_wms = QPushButton('WMS')
                    sub_wms.setCursor(Qt.CursorShape.PointingHandCursor)
                    sub_wms.setStyleSheet("""
                        QPushButton {
                            background-color: #f8fafc;
                            color: #1f6fd6;
                            border: 1px solid #cbd5e1;
                            border-radius: 5px;
                            font-size: 10px;
                            font-weight: 600;
                            padding: 2px 6px;
                        }
                        QPushButton:hover {
                            background-color: #eff6ff;
                            border-color: #1f6fd6;
                        }
                    """)
                    sub_wms.clicked.connect(lambda checked, ds=d, sl=sub: self.wmsRequested.emit(ds, sl))
                    self.tree.setItemWidget(child_item, 3, sub_wms)

                    # Col 4: Sub WFS Button
                    sub_wfs = QPushButton('WFS')
                    sub_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
                    sub_wfs.setStyleSheet("""
                        QPushButton {
                            background-color: #f8fafc;
                            color: #7c3aed;
                            border: 1px solid #cbd5e1;
                            border-radius: 5px;
                            font-size: 10px;
                            font-weight: 600;
                            padding: 2px 6px;
                        }
                        QPushButton:hover {
                            background-color: #f5f3ff;
                            border-color: #7c3aed;
                        }
                    """)
                    sub_wfs.clicked.connect(lambda checked, ds=d, sl=sub: self.wfsRequested.emit(ds, sl))
                    self.tree.setItemWidget(child_item, 4, sub_wfs)

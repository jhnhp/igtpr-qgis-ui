# -*- coding: utf-8 -*-
"""Halaman Model Builder Spasial (Mockup V2) untuk pemrosesan geospasial tematik."""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .login_page import svg_pixmap

MODELS = [
    {
        'id': 'MB-001',
        'name': 'Analisis Kesesuaian Lahan (MCE)',
        'category': 'Tata Ruang & Pertanahan',
        'desc': 'Evaluasi multi-kriteria kesesuaian ruang berbasis kelerengan, jenis tanah, dan kerawanan bencana.',
    },
    {
        'id': 'MB-002',
        'name': 'Buffer Kawasan Lindung & Sempadan',
        'category': 'Tata Ruang',
        'desc': 'Pembuatan zona penyangga sempadan sungai, mata air, dan kawasan cagar alam otomatis.',
    },
    {
        'id': 'MB-003',
        'name': 'Overlay RTRW vs Bidang Kadastral',
        'category': 'Derivatif Multiguna',
        'desc': 'Tumpang susun pola ruang rencana tata ruang terhadap batas bidang tanah untuk verifikasi keselarasan KKPR.',
    },
    {
        'id': 'MB-004',
        'name': 'Deteksi Tumpang Tindih Kawasan Hutan',
        'category': 'Pertanahan',
        'desc': 'Identifikasi irisan spasial antara sertipikat hak atas tanah dengan kawasan hutan lindung / konservasi.',
    },
    {
        'id': 'MB-005',
        'name': 'Pemodelan Zonasi Nilai Tanah (ZNT)',
        'category': 'Pertanahan',
        'desc': 'Estimasi nilai pasar wajar bidang tanah berdasarkan aksesibilitas jalan, fasilitas umum, dan transaksi.',
    },
    {
        'id': 'MB-006',
        'name': 'Monitoring Lahan Baku Sawah (Multi-Year)',
        'category': 'Pertanahan & Pertanian',
        'desc': 'Deteksi alih fungsi sawah berbasis perbandingan citra satelit dan data multi-year 2024-2026.',
    },
]


class ModelBuilderPage(QWidget):
    """Halaman Model Builder V2 untuk menjalankan model spasial di QGIS."""

    backToDashboardRequested = pyqtSignal()
    runModelRequested = pyqtSignal(dict)

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_role = current_role
        self.setObjectName('modelBuilderPage')

        self.setStyleSheet("""
            QWidget#modelBuilderPage {
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
                color: #7c3aed;
                font-size: 12px;
                font-weight: 700;
                padding: 6px 12px;
            }
            QPushButton#backBtn:hover {
                background-color: #f5f3ff;
                border-color: #ddd6fe;
            }
            QLineEdit#searchInput {
                background-color: #ffffff;
                border: 1.5px solid #ddd6fe;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: #1e1b4b;
            }
            QLineEdit#searchInput:focus {
                border-color: #7c3aed;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1.5px solid #ddd6fe;
                border-radius: 12px;
                font-size: 12px;
                gridline-color: #faf5ff;
                outline: none;
            }
            QHeaderView::section {
                background-color: #f5f3ff;
                color: #4c1d95;
                font-weight: 700;
                font-size: 11.5px;
                border: none;
                border-bottom: 1.5px solid #ddd6fe;
                padding: 10px 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        head_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_lbl = QLabel('Model Builder Geoportal', self)
        title_lbl.setStyleSheet("color: #2e1065; font-size: 18px; font-weight: 800;")
        text_layout.addWidget(title_lbl)

        desc_lbl = QLabel('Katalog algoritma dan model pemrosesan spasial terotomatisasi untuk QGIS.', self)
        desc_lbl.setStyleSheet("color: #6b21a8; font-size: 11.5px;")
        text_layout.addWidget(desc_lbl)
        head_layout.addLayout(text_layout, 1)

        back_btn = QPushButton('← Kembali ke Dashboard', self)
        back_btn.setObjectName('backBtn')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.backToDashboardRequested.emit)
        head_layout.addWidget(back_btn)

        layout.addLayout(head_layout)

        # Search bar
        self.search_input = QLineEdit(self)
        self.search_input.setObjectName('searchInput')
        self.search_input.setPlaceholderText('Cari nama model atau analisis spasial...')
        self.search_input.textChanged.connect(self._render_table)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Model Analisis Spasial', 'Kategori', 'Aksi'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 125)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        layout.addWidget(self.table, 1)

        self._render_table()

    def _render_table(self):
        query = self.search_input.text().strip().lower()
        filtered = [m for m in MODELS if not query or query in m['name'].lower() or query in m['desc'].lower()]

        self.table.setRowCount(len(filtered))
        for row, m in enumerate(filtered):
            # Col 0: Name & Desc
            name_widget = QWidget()
            nw_layout = QVBoxLayout(name_widget)
            nw_layout.setContentsMargins(6, 4, 6, 4)
            nw_layout.setSpacing(2)

            name_lbl = QLabel(m['name'], name_widget)
            name_lbl.setStyleSheet("color: #1e1b4b; font-weight: 700; font-size: 12.5px;")
            nw_layout.addWidget(name_lbl)

            desc_lbl = QLabel(m['desc'], name_widget)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
            nw_layout.addWidget(desc_lbl)
            self.table.setCellWidget(row, 0, name_widget)

            # Col 1: Category
            cat_lbl = QLabel(m['category'])
            cat_lbl.setStyleSheet("color: #6d28d9; font-weight: 600; font-size: 11px;")
            self.table.setCellWidget(row, 1, cat_lbl)

            # Col 2: Run button
            btn_run = QPushButton('▶ Jalankan')
            btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_run.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed);
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background: #5b21b6;
                }
            """)
            btn_run.clicked.connect(lambda checked, model=m: self.runModelRequested.emit(model))
            self.table.setCellWidget(row, 2, btn_run)

            self.table.setRowHeight(row, 62)

# -*- coding: utf-8 -*-
"""Halaman & Formulir Unggah Data Geospasial IGT-PR (Mockup V2)."""

import os

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS
from .login_page import svg_pixmap


class UploadPage(QWidget):
    """Halaman unggah data IGT Utama, Derivatif Multiguna, dan Lainnya."""

    backToDashboardRequested = pyqtSignal()
    uploadSubmitted = pyqtSignal(dict)

    def __init__(self, current_category='pertanahan', current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_category = current_category
        self.current_role = current_role
        self.selected_file_path = None
        self.setObjectName('uploadPage')

        self.setStyleSheet("""
            QWidget#uploadPage {
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
            QFrame#card {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 14px;
                padding: 18px;
            }
            QFrame#dropzone {
                border: 2px dashed #93c5fd;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #eff6ff, stop:1 #f8fbff);
                padding: 20px;
            }
            QFrame#dropzone:hover {
                border-color: #1f6fd6;
                background-color: #eff6ff;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                color: #0f294d;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #1f6fd6;
            }
            QPushButton#browseBtn {
                background-color: #1f6fd6;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 8px;
                padding: 8px 16px;
                border: none;
            }
            QPushButton#browseBtn:hover {
                background-color: #1a63c7;
            }
            QPushButton#submitBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #047857);
                color: #ffffff;
                font-weight: 700;
                font-size: 13px;
                border-radius: 10px;
                padding: 12px 24px;
                border: none;
            }
            QPushButton#submitBtn:hover {
                background: #059669;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(16, 16, 16, 20)
        layout.setSpacing(14)

        # 1. Header
        head_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_lbl = QLabel('Unggah Data Geospasial', self)
        title_lbl.setStyleSheet("color: #0f294d; font-size: 18px; font-weight: 800;")
        text_layout.addWidget(title_lbl)

        desc_lbl = QLabel('Unggah data atribut bidang IGT Pertanahan, kawasan IGT Tata Ruang, atau Derivatif.', self)
        desc_lbl.setStyleSheet("color: #64748b; font-size: 11.5px;")
        text_layout.addWidget(desc_lbl)
        head_layout.addLayout(text_layout, 1)

        back_btn = QPushButton('← Kembali ke Dashboard', self)
        back_btn.setObjectName('backBtn')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.backToDashboardRequested.emit)
        head_layout.addWidget(back_btn)

        layout.addLayout(head_layout)

        # 2. Category Selector Pills
        self.cat_nav_layout = QHBoxLayout()
        self.cat_nav_layout.setSpacing(8)
        self.cat_buttons = {}

        cats = [
            ('pertanahan', 'IGT Pertanahan (Bidang)'),
            ('tata-ruang', 'IGT Tata Ruang (Kawasan)'),
            ('derivatif', 'IGT Derivatif Multiguna'),
            ('lainnya', 'IGT Lainnya (Eksternal)'),
        ]
        for c_id, c_lbl in cats:
            btn = QPushButton(c_lbl, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=c_id: self.set_category(k))
            self.cat_nav_layout.addWidget(btn)
            self.cat_buttons[c_id] = btn

        self.cat_nav_layout.addStretch()
        layout.addLayout(self.cat_nav_layout)

        # 3. Main Form Card
        form_card = QFrame(self)
        form_card.setObjectName('card')
        fc_layout = QVBoxLayout(form_card)
        fc_layout.setSpacing(14)

        # Dropzone
        self.dropzone = QFrame(form_card)
        self.dropzone.setObjectName('dropzone')
        dz_layout = QVBoxLayout(self.dropzone)
        dz_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.setSpacing(8)

        icon_lbl = QLabel(self.dropzone)
        icon_lbl.setPixmap(svg_pixmap(ICONS['upload'].format(color='#1f6fd6'), QSize(36, 36)))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.addWidget(icon_lbl)

        self.dz_title = QLabel('Pilih berkas geospasial yang akan diunggah', self.dropzone)
        self.dz_title.setStyleSheet("color: #0f294d; font-weight: 700; font-size: 13px;")
        self.dz_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.addWidget(self.dz_title)

        dz_sub = QLabel('Mendukung format GeoPackage (.gpkg), Shapefile (.zip), atau CSV (.csv)', self.dropzone)
        dz_sub.setStyleSheet("color: #64748b; font-size: 11px;")
        dz_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.addWidget(dz_sub)

        browse_btn = QPushButton('Pilih Berkas...', self.dropzone)
        browse_btn.setObjectName('browseBtn')
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_file)
        dz_layout.addWidget(browse_btn, 0, Qt.AlignmentFlag.AlignCenter)

        self.file_picked_lbl = QLabel('', self.dropzone)
        self.file_picked_lbl.setStyleSheet("color: #047857; font-weight: 700; font-size: 12px; margin-top: 4px;")
        self.file_picked_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.addWidget(self.file_picked_lbl)

        fc_layout.addWidget(self.dropzone)

        # Form Fields
        field_grid = QVBoxLayout()
        field_grid.setSpacing(10)

        # Satker Field
        s_box = QVBoxLayout()
        s_box.setSpacing(3)
        self.s_lbl = QLabel('SATUAN KERJA (SATKER)', form_card)
        self.s_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        s_box.addWidget(self.s_lbl)
        self.satker_combo = QComboBox(form_card)
        self.satker_combo.addItems([
            'Kantah Kab. Sleman',
            'Kantah Kab. Bantul',
            'Kantah Kab. Kulon Progo',
            'Kantah Kab. Gunungkidul',
            'Kantah Kota Yogyakarta',
            'Kanwil BPN D.I. Yogyakarta',
            'Ditjen Survei dan Pemetaan Pertanahan dan Ruang',
            'Ditjen Tata Ruang',
        ])
        s_box.addWidget(self.satker_combo)
        field_grid.addLayout(s_box)

        # Dataset Target Field
        d_box = QVBoxLayout()
        d_box.setSpacing(3)
        d_lbl = QLabel('DATASET TARGET', form_card)
        d_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        d_box.addWidget(d_lbl)
        self.dataset_combo = QComboBox(form_card)
        d_box.addWidget(self.dataset_combo)
        field_grid.addLayout(d_box)

        # Wilayah Field
        w_box = QVBoxLayout()
        w_box.setSpacing(3)
        w_lbl = QLabel('WILAYAH ADMINISTRASI', form_card)
        w_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        w_box.addWidget(w_lbl)
        self.wilayah_input = QLineEdit(form_card)
        self.wilayah_input.setText('Kab. Sleman, D.I. Yogyakarta')
        w_box.addWidget(self.wilayah_input)
        field_grid.addLayout(w_box)

        # Catatan Field
        c_box = QVBoxLayout()
        c_box.setSpacing(3)
        c_lbl = QLabel('KETERANGAN / CATATAN PEMBARUAN', form_card)
        c_lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        c_box.addWidget(c_lbl)
        self.catatan_input = QLineEdit(form_card)
        self.catatan_input.setPlaceholderText('Contoh: Pemutakhiran bidang tahun 2026')
        c_box.addWidget(self.catatan_input)
        field_grid.addLayout(c_box)

        fc_layout.addLayout(field_grid)

        # Notice
        notice = QFrame(form_card)
        notice.setStyleSheet("""
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 10px 12px;
        """)
        n_layout = QHBoxLayout(notice)
        n_layout.setContentsMargins(0, 0, 0, 0)
        n_text = QLabel('Setelah pengajuan dikirim, data akan masuk ke daftar Manajemen Data dengan status "Diajukan" untuk menunggu proses kompilasi.', notice)
        n_text.setWordWrap(True)
        n_text.setStyleSheet("color: #1e40af; font-size: 11px;")
        n_layout.addWidget(n_text)
        fc_layout.addWidget(notice)

        # Submit button
        submit_btn = QPushButton('✓ Validasi dan Kirim Pengajuan', form_card)
        submit_btn.setObjectName('submitBtn')
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self._on_submit)
        fc_layout.addWidget(submit_btn)

        layout.addWidget(form_card)
        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self.set_category(current_category)

    def set_category(self, cat_id):
        self.current_category = cat_id

        # Update subnav styles
        for cid, btn in self.cat_buttons.items():
            if cid == cat_id:
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

        # Update satker label if lainnya
        if cat_id == 'lainnya':
            self.s_lbl.setText('INSTANSI SUMBER DATA')
        else:
            self.s_lbl.setText('SATUAN KERJA (SATKER)')

        # Populate datasets for this category
        self.dataset_combo.clear()
        target_datasets = [d['name'] for d in DATASETS if d.get('category') == cat_id]
        if not target_datasets:
            target_datasets = ['Layer Baru...']
        self.dataset_combo.addItems(target_datasets)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Pilih Berkas Geospasial', '',
            'Geospatial Files (*.gpkg *.zip *.csv *.geojson *.shp);;All Files (*)'
        )
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_picked_lbl.setText(f"✓ Berkas terpilih: {filename}")

    def _on_submit(self):
        dataset_name = self.dataset_combo.currentText()
        satker = self.satker_combo.currentText()
        wilayah = self.wilayah_input.text().strip() or 'Kab. Sleman'
        catatan = self.catatan_input.text().strip() or 'Pengajuan data baru'

        submission = {
            'id': f"AJU-2026-{100 + len(DATASETS)}",
            'category': self.current_category,
            'name': dataset_name,
            'satker': satker,
            'date': '31 Okt 2026',
            'status': 'Diajukan',
            'note': f"{wilayah} · {catatan}",
            'scope': wilayah,
        }
        self.uploadSubmitted.emit(submission)

    def minimumSizeHint(self):
        return QSize(200, 120)

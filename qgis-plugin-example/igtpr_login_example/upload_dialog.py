# -*- coding: utf-8 -*-
"""Halaman & Formulir Unggah Data Geospasial IGT-PR (Mockup V2)."""

import os
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import QDate, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon, QIntValidator
from qgis.PyQt.QtWidgets import (
    QAbstractItemView, QButtonGroup, QCheckBox, QComboBox, QDialog,
    QFileDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLayout, QLineEdit, QMessageBox, QPushButton, QRadioButton, QScrollArea,
    QSizePolicy, QTabWidget, QTableWidget, QTableWidgetItem, QTextEdit,
    QVBoxLayout, QWidget,
)

try:
    from qgis.core import QgsProject, QgsVectorLayer
except ImportError:
    QgsProject = None
    QgsVectorLayer = None

from .assets import ICONS
from .data import CATEGORIES, DATASETS
from .login_page import svg_pixmap
from .ui_kit import icon


class _ScrollContent(QWidget):
    """Widget konten QScrollArea yang lebarnya selalu mengikuti viewport tanpa meluber ke kanan."""

    def minimumSizeHint(self):
        h = self.layout().totalMinimumSize().height() if self.layout() else 100
        return QSize(100, h)

    def sizeHint(self):
        h = self.layout().totalSizeHint().height() if self.layout() else 100
        return QSize(200, h)


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
                font-size: 11px;
                color: #334155;
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
                border: 1px solid #cbd5e1;
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
        desc_lbl.setStyleSheet("color: #64748b; font-size: 12px;")
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
                        font-size: 12px;
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
                        font-size: 12px;
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


class AttributeMappingDialog(QDialog):
    """
    Dialog Modal 'Verifikasi Data Kompilasi' (Attribute Mapping).
    Memeriksa dan memetakan field standar acuan IGT dengan kolom pada layer SHP input user.
    """
    def __init__(self, parent=None, igt_name="Data Dasar IGT", target_layer=None, attribute_masters=None):
        super().__init__(parent)
        self.setWindowTitle("Verifikasi Data Kompilasi")
        self.resize(920, 640)
        self.setMinimumSize(800, 520)
        self.setObjectName("attributeMappingDialog")

        self.igt_name = igt_name or "Data Dasar IGT"
        self.target_layer = target_layer
        self.attribute_masters = attribute_masters or [
            {"nama_kolom": "KODE_UNIK", "alias": "NIB / ID Objek Unik", "tipe_data": "String (32)", "is_required": True},
            {"nama_kolom": "NAMA_OBJEK", "alias": "Nama Objek / Hak / Penatagunaan", "tipe_data": "String (100)", "is_required": True},
            {"nama_kolom": "LUAS_HA", "alias": "Luas Bidang / Kawasan (Ha)", "tipe_data": "Decimal (10,2)", "is_required": True},
            {"nama_kolom": "TAHUN", "alias": "Tahun Penetapan / Survei", "tipe_data": "Integer (4)", "is_required": True},
            {"nama_kolom": "TEMA", "alias": "Tema Geospasial IGT", "tipe_data": "String (50)", "is_required": True},
            {"nama_kolom": "WADMPR", "alias": "Nama Provinsi", "tipe_data": "String (50)", "is_required": False},
            {"nama_kolom": "WADMKK", "alias": "Nama Kabupaten / Kota", "tipe_data": "String (50)", "is_required": False},
            {"nama_kolom": "WADMKC", "alias": "Nama Kecamatan", "tipe_data": "String (50)", "is_required": False},
            {"nama_kolom": "WADMKD", "alias": "Nama Kelurahan / Desa", "tipe_data": "String (50)", "is_required": False},
            {"nama_kolom": "REMARK", "alias": "Keterangan Tambahan", "tipe_data": "String (254)", "is_required": False},
        ]

        self.mappings = {}
        self.confirmed = False
        self.source_fields = []
        self.sample_values = {}
        self._extract_source_fields()

        self._init_ui()
        self._auto_match_and_populate()

    def _extract_source_fields(self):
        if self.target_layer and hasattr(self.target_layer, 'isValid') and self.target_layer.isValid():
            try:
                for f in self.target_layer.fields():
                    self.source_fields.append(f.name())
                for feat in self.target_layer.getFeatures():
                    for f in self.target_layer.fields():
                        val = feat[f.name()]
                        self.sample_values[f.name()] = str(val) if val is not None else ""
                    break
            except Exception:
                pass

        if not self.source_fields:
            # Fallback daftar kolom simulasi dari layer QGIS aktif
            self.source_fields = ["KODE_UNIK", "NIB", "NAMOBJ", "LUAS_HA", "LUASTERTUL", "TAHUN", "TEMA", "WADMPR", "WADMKK", "WADMKC", "WADMKD", "REMARK"]
            self.sample_values = {
                "KODE_UNIK": "12.01.04.01.00129",
                "NIB": "12.01.04.01.00129",
                "NAMOBJ": "Bidang Pertanahan 00129",
                "LUAS_HA": "0.035",
                "LUASTERTUL": "350.00",
                "TAHUN": "2026",
                "TEMA": "Bidang Tanah",
                "WADMPR": "D.I. Yogyakarta",
                "WADMKK": "Kabupaten Sleman",
                "WADMKC": "Kecamatan Depok",
                "WADMKD": "Kalurahan Condongcatur",
                "REMARK": "Terverifikasi Lengkap"
            }

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog#attributeMappingDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
                color: #334155;
            }
            QFrame.cardBox {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 10px;
                padding: 12px 14px;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                color: #0f294d;
                font-size: 11px;
                font-weight: 700;
                border: none;
                border-bottom: 2px solid #cbd5e1;
                padding: 6px;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QComboBox:focus {
                border-color: #1f6fd6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # 1. Header
        layer_name = self.target_layer.name() if (self.target_layer and hasattr(self.target_layer, 'name')) else "Layer Aktif QGIS"
        feat_count = self.target_layer.featureCount() if (self.target_layer and hasattr(self.target_layer, 'featureCount')) else 42
        
        h_box = QVBoxLayout()
        h_box.setSpacing(2)
        h_title = QLabel("Verifikasi Data Kompilasi", self)
        h_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #0f294d;")
        h_sub = QLabel(f"Dataset: <b>{self.igt_name}</b> • Layer: <b>{layer_name}</b> • {feat_count} objek spasial (Polygon)", self)
        h_sub.setStyleSheet("font-size: 11px; color: #64748b;")
        h_box.addWidget(h_title)
        h_box.addWidget(h_sub)
        layout.addLayout(h_box)

        # 2. Kotak Pemeriksaan Data Spasial
        spatial_card = QFrame(self)
        spatial_card.setProperty('class', 'cardBox')
        sc_lay = QHBoxLayout(spatial_card)
        sc_lay.setContentsMargins(12, 10, 12, 10)
        sc_lay.setSpacing(14)

        sc_left = QVBoxLayout()
        sc_left.setSpacing(2)
        lbl_sc_title = QLabel("Pemeriksaan Data Spasial & Proyeksi CRS", spatial_card)
        lbl_sc_title.setStyleSheet("font-size: 12px; font-weight: 700; color: #0f294d;")
        lbl_sc_info = QLabel(f"Penamaan Data: <b>{self.igt_name}</b> • Proyeksi: <b>EPSG:4326 (WGS 84)</b> • Geometri: Valid", spatial_card)
        lbl_sc_info.setStyleSheet("font-size: 11px; color: #475569;")
        sc_left.addWidget(lbl_sc_title)
        sc_left.addWidget(lbl_sc_info)
        sc_lay.addLayout(sc_left, 1)

        badge_crs = QLabel("✓ CRS & Geometri Sesuai", spatial_card)
        badge_crs.setStyleSheet("""
            background-color: #ecfdf5; color: #047857; font-size: 11px; font-weight: 700;
            padding: 4px 10px; border-radius: 6px; border: 1px solid #a7f3d0;
        """)
        sc_lay.addWidget(badge_crs, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(spatial_card)

        # 3. Alert Box (jika ada kolom wajib belum terpetakan)
        self.alert_box = QFrame(self)
        self.alert_box.setObjectName("alertBox")
        self.alert_box.setStyleSheet("""
            QFrame#alertBox {
                background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 6px 12px;
            }
        """)
        ab_lay = QHBoxLayout(self.alert_box)
        ab_lay.setContentsMargins(6, 6, 6, 6)
        self.alert_msg = QLabel("Perhatian: Pastikan seluruh kolom acuan bertanda (*) telah terpetakan dengan benar.", self.alert_box)
        self.alert_msg.setStyleSheet("color: #991b1b; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        ab_lay.addWidget(self.alert_msg)
        layout.addWidget(self.alert_box)

        # 4. Tabel Pemetaan Atribut
        table_card = QFrame(self)
        table_card.setProperty('class', 'cardBox')
        tc_lay = QVBoxLayout(table_card)
        tc_lay.setContentsMargins(10, 10, 10, 10)
        tc_lay.setSpacing(6)

        tc_head = QHBoxLayout()
        tc_title = QLabel("Pemetaan Field Atribut (Attribute Mapping)", table_card)
        tc_title.setStyleSheet("font-size: 13px; font-weight: 800; color: #0f294d;")
        tc_head.addWidget(tc_title)
        tc_head.addStretch()
        tc_hint = QLabel("Kolom bertanda <span style='color:#ef4444; font-weight:bold;'>* (Wajib)</span> harus dipetakan", table_card)
        tc_hint.setStyleSheet("font-size: 11px; color: #64748b;")
        tc_head.addWidget(tc_hint)
        tc_lay.addLayout(tc_head)

        self.table = QTableWidget(table_card)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Data Dasar (Acuan IGT)",
            "Data Input (Kolom SHP & Contoh Nilai)",
            "Status",
            "Aksi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 365)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tc_lay.addWidget(self.table)
        layout.addWidget(table_card, 1)

        # 5. Footer Buttons
        footer = QHBoxLayout()
        btn_cancel = QPushButton("Batal", self)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #475569; border: 1px solid #cbd5e1;
                border-radius: 8px; padding: 7px 16px; font-size: 12px; font-weight: 600;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        footer.addStretch()

        self.btn_confirm = QPushButton("✓ Gunakan Mapping Ini (Konfirmasi)", self)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #1f6fd6; color: #ffffff; font-weight: 700;
                font-size: 12px; border-radius: 8px; padding: 8px 20px; border: none;
            }
            QPushButton:hover { background-color: #1a63c7; }
        """)
        self.btn_confirm.clicked.connect(self._on_confirm_mapping)
        footer.addWidget(self.btn_confirm)
        layout.addLayout(footer)

    def _auto_match_and_populate(self):
        self.table.setRowCount(len(self.attribute_masters))
        source_map = {name.lower().replace('_', ''): name for name in self.source_fields}

        for row, attr in enumerate(self.attribute_masters):
            target_name = attr.get("nama_kolom", "").strip()
            alias = attr.get("alias", target_name)
            tipe = attr.get("tipe_data", "String")
            is_req = attr.get("is_required", True)

            clean_target = target_name.lower().replace('_', '')
            matched_src = None
            if clean_target in source_map:
                matched_src = source_map[clean_target]
            elif target_name.lower() in [s.lower() for s in self.source_fields]:
                for s in self.source_fields:
                    if s.lower() == target_name.lower():
                        matched_src = s
                        break
            # common synonym matches:
            if not matched_src:
                if target_name == "KODE_UNIK" and "NIB" in self.source_fields:
                    matched_src = "NIB"
                elif target_name == "NAMA_OBJEK" and "NAMOBJ" in self.source_fields:
                    matched_src = "NAMOBJ"
                elif target_name == "LUAS_HA" and "LUASTERTUL" in self.source_fields:
                    matched_src = "LUASTERTUL"

            self.mappings[target_name] = {
                "source_col": matched_src,
                "is_required": is_req,
            }
            self._render_row(row, attr, matched_src)

        self._validate_all()

    def _render_row(self, row, attr, current_src):
        target_name = attr.get("nama_kolom", "").strip()
        alias = attr.get("alias", target_name)
        tipe = attr.get("tipe_data", "String")
        is_req = attr.get("is_required", True)

        # Kolom 0: Acuan Target
        w_acuan = QWidget()
        lay_acuan = QVBoxLayout(w_acuan)
        lay_acuan.setContentsMargins(6, 6, 6, 6)
        lay_acuan.setSpacing(2)

        req_badge = "<span style='color:#ef4444; font-weight:bold;'> *</span>" if is_req else ""
        lbl_target = QLabel(f"<b>{target_name}</b>{req_badge}", w_acuan)
        lbl_desc = QLabel(f"{alias} • <small style='color:#64748b;'>{tipe}</small>", w_acuan)
        lbl_desc.setStyleSheet("color: #475569; font-size: 11px;")
        lay_acuan.addWidget(lbl_target)
        lay_acuan.addWidget(lbl_desc)
        self.table.setCellWidget(row, 0, w_acuan)

        # Kolom 1: Dropdown Field Input SHP + Sample
        w_input = QWidget()
        lay_input = QVBoxLayout(w_input)
        lay_input.setContentsMargins(6, 6, 6, 6)
        lay_input.setSpacing(2)

        combo = QComboBox(w_input)
        combo.addItem("-- Pilih Kolom SHP --", "")
        for sf in self.source_fields:
            combo.addItem(sf, sf)
        if current_src and current_src in self.source_fields:
            combo.setCurrentText(current_src)

        sample_txt = self.sample_values.get(current_src, "—") if current_src else "—"
        lbl_sample = QLabel(f"<small style='color:#64748b;'>Contoh nilai: <b>{sample_txt}</b></small>", w_input)
        lay_input.addWidget(combo)
        lay_input.addWidget(lbl_sample)
        self.table.setCellWidget(row, 1, w_input)

        # Kolom 2: Status Badge
        lbl_status = QLabel(w_input)
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_status_badge(lbl_status, bool(current_src), is_req)
        self.table.setCellWidget(row, 2, lbl_status)

        # Kolom 3: Tombol Reset
        btn_reset = QPushButton("Reset", w_input)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet("font-size: 10px; color: #dc2626; padding: 2px 8px; border: 1px solid #fca5a5; border-radius: 4px; background: #fff;")
        self.table.setCellWidget(row, 3, btn_reset)

        def on_change(idx):
            chosen = combo.currentData()
            self.mappings[target_name]["source_col"] = chosen or None
            s_val = self.sample_values.get(chosen, "—") if chosen else "—"
            lbl_sample.setText(f"<small style='color:#64748b;'>Contoh nilai: <b>{s_val}</b></small>")
            self._update_status_badge(lbl_status, bool(chosen), is_req)
            self._validate_all()

        combo.currentIndexChanged.connect(on_change)
        btn_reset.clicked.connect(lambda: combo.setCurrentIndex(0))
        self.table.setRowHeight(row, 60)

    def _update_status_badge(self, label, is_mapped, is_req):
        if is_mapped:
            label.setText("✓ Sesuai")
            label.setStyleSheet("color: #047857; font-weight: 700; font-size: 11px; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 4px; padding: 2px 8px;")
        elif is_req:
            label.setText("Belum Dipetakan")
            label.setStyleSheet("color: #b91c1c; font-weight: 700; font-size: 11px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 4px; padding: 2px 6px;")
        else:
            label.setText("Opsional")
            label.setStyleSheet("color: #64748b; font-size: 11px; background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 2px 6px;")

    def _validate_all(self):
        missing_req = []
        for target, data in self.mappings.items():
            if data.get("is_required") and not data.get("source_col"):
                missing_req.append(target)

        if missing_req:
            self.alert_msg.setText(f"Perhatian: Kolom wajib belum terpetakan: {', '.join(missing_req)}")
            self.alert_msg.setStyleSheet("color: #991b1b; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            self.alert_box.setStyleSheet("QFrame#alertBox { background-color: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 6px 12px; }")
            self.alert_box.setVisible(True)
            self.btn_confirm.setEnabled(False)
        else:
            self.alert_msg.setText("✓ Seluruh kolom wajib acuan telah terpetakan dengan benar!")
            self.alert_msg.setStyleSheet("color: #047857; font-size: 11px; font-weight: 600; border: none; background: transparent;")
            self.alert_box.setStyleSheet("QFrame#alertBox { background-color: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 8px; padding: 6px 12px; }")
            self.alert_box.setVisible(True)
            self.btn_confirm.setEnabled(True)

    def _on_confirm_mapping(self):
        self.confirmed = True
        self.accept()

    def get_result_mappings(self):
        return [
            {"target_column": target, "source_column": val.get("source_col")}
            for target, val in self.mappings.items()
            if val.get("source_col")
        ]


class MetadataPreviewDialog(QDialog):
    """Dialog pratinjau XML metadata resmi CMS/Geoportal dengan tampilan XPath dan XML Mentah."""

    def __init__(self, dataset_title="Data Potensi WP3WT", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Metadata XML: {dataset_title}")
        self.resize(720, 520)
        self.dataset_title = dataset_title

        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #cbd5e1;
                background-color: #ffffff;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #f1f5f9;
                color: #475569;
                padding: 6px 20px;
                min-width: 140px;
                font-weight: 600;
                font-size: 12px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1f6fd6;
                font-weight: 700;
                border-bottom: 2px solid #1f6fd6;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        head = QLabel(f"Pratinjau Metadata Geospasial ISO 19115: {dataset_title}", self)
        head.setStyleSheet("color: #0f294d; font-size: 14px; font-weight: 800;")
        lay.addWidget(head)

        tabs = QTabWidget(self)

        # Tab 1: XPath & Nilai
        tab_xpath = QWidget()
        tx_lay = QVBoxLayout(tab_xpath)
        tx_lay.setContentsMargins(8, 8, 8, 8)
        
        table_xp = QTableWidget(tab_xpath)
        table_xp.setColumnCount(2)
        table_xp.setHorizontalHeaderLabels(["Struktur XPath / Elemen", "Nilai Metadata CMS"])
        table_xp.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        table_xp.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table_xp.setColumnWidth(0, 320)
        table_xp.verticalHeader().setVisible(False)
        table_xp.setStyleSheet("font-size: 11px;")

        xpath_rows = [
            ("gmd:fileIdentifier / gco:CharacterString", f"urn:igtpr:dataset:{dataset_title.lower().replace(' ', '_')}"),
            ("gmd:identificationInfo / gmd:citation / gmd:title", dataset_title),
            ("gmd:identificationInfo / gmd:citation / gmd:date", QDate.currentDate().toString("yyyy-MM-dd")),
            ("gmd:identificationInfo / gmd:abstract", "Dataset spasial terkompilasi resmi Kementerian Agraria dan Tata Ruang / Badan Pertanahan Nasional."),
            ("gmd:identificationInfo / gmd:status", "completed / Terintegrasi"),
            ("gmd:spatialRepresentationInfo / gmd:spatialRepresentationType", "vector / Poligon Spasial"),
            ("gmd:referenceSystemInfo / gmd:referenceSystemIdentifier", "EPSG:4326 (WGS 84 / Geographic)"),
            ("gmd:contact / gmd:organisationName", "Kementerian ATR/BPN - Ditjen SPPR"),
            ("gmd:distributionInfo / gmd:transferOptions / gmd:onLine", "WMS / WFS GeoServer Geoportal IGT-PR"),
        ]
        table_xp.setRowCount(len(xpath_rows))
        for r_idx, (xp, val) in enumerate(xpath_rows):
            item_xp = QTableWidgetItem(xp)
            item_xp.setFlags(item_xp.flags() ^ Qt.ItemFlag.ItemIsEditable)
            item_xp.setFont(QFont("Consolas", 9))
            table_xp.setItem(r_idx, 0, item_xp)
            item_val = QTableWidgetItem(val)
            table_xp.setItem(r_idx, 1, item_val)

        tx_lay.addWidget(table_xp)
        tabs.addTab(tab_xpath, "Tabel XPath && Nilai")

        # Tab 2: Raw XML
        tab_raw = QWidget()
        tr_lay = QVBoxLayout(tab_raw)
        tr_lay.setContentsMargins(8, 8, 8, 8)

        txt = QTextEdit(tab_raw)
        txt.setReadOnly(True)
        txt.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                font-family: Consolas, "Courier New", monospace;
                font-size: 11px;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd"
                 xmlns:gco="http://www.isotc211.org/2005/gco">
  <gmd:fileIdentifier>
    <gco:CharacterString>urn:igtpr:dataset:{dataset_title.lower().replace(' ', '_')}</gco:CharacterString>
  </gmd:fileIdentifier>
  <gmd:identificationInfo>
    <gmd:MD_DataIdentification>
      <gmd:citation>
        <gmd:CI_Citation>
          <gmd:title>
            <gco:CharacterString>{dataset_title}</gco:CharacterString>
          </gmd:title>
          <gmd:date>
            <gmd:CI_Date>
              <gmd:date><gco:Date>{QDate.currentDate().toString("yyyy-MM-dd")}</gco:Date></gmd:date>
              <gmd:dateType><gmd:CI_DateTypeCode codeListValue="publication"/></gmd:dateType>
            </gmd:CI_Date>
          </gmd:date>
        </gmd:CI_Citation>
      </gmd:citation>
      <gmd:abstract>
        <gco:CharacterString>Dataset Spasial IGT Tematik Terkompilasi Kementerian Agraria dan Tata Ruang / Badan Pertanahan Nasional.</gco:CharacterString>
      </gmd:abstract>
      <gmd:status>
        <gmd:MD_ProgressCode codeListValue="completed"/>
      </gmd:status>
    </gmd:MD_DataIdentification>
  </gmd:identificationInfo>
</gmd:MD_Metadata>"""
        txt.setPlainText(xml_content)
        tr_lay.addWidget(txt)
        tabs.addTab(tab_raw, "Editor XML Mentah")

        lay.addWidget(tabs, 1)

        btn_close = QPushButton("Tutup", self)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #1f6fd6; color: #ffffff; font-weight: 700;
                border-radius: 6px; padding: 6px 16px; border: none; font-size: 12px;
            }
            QPushButton:hover { background-color: #1a63c7; }
        """)
        btn_close.clicked.connect(self.accept)
        lay.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignRight)


class UploadIgtUtamaDialog(QDialog):
    """Modal popup Upload Data IGT Utama sesuai spesifikasi."""

    uploadSubmitted = pyqtSignal(dict)

    def __init__(self, current_category='pertanahan', iface=None, record_to_revise=None, parent=None):
        super().__init__(parent)
        self.current_category = current_category
        self.iface = iface
        self.record_to_revise = record_to_revise
        self.is_revision = record_to_revise is not None
        self.selected_file_path = None
        self.is_attribute_verified = False

        is_derivatif = current_category == 'derivatif'
        if self.is_revision:
            rec_title = record_to_revise.get('name') or record_to_revise.get('layer', 'Layer')
            self.dialog_title = f"Perbaikan Revisi: {rec_title}"
        else:
            self.dialog_title = 'Upload Data IGT Derivatif Multiguna' if is_derivatif else 'Upload Data IGT Utama'
        self.setWindowTitle(self.dialog_title)
        self.resize(560, 720)
        self.setObjectName('uploadIgtUtamaDialog')

        self.setStyleSheet("""
            QDialog#uploadIgtUtamaDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
                font-size: 11px;
                color: #334155;
            }
            QFrame.sectionCard {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 12px;
                padding: 12px 16px;
            }
            QLineEdit, QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 7px;
                padding: 7px 10px;
                font-size: 12px;
                color: #0f294d;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #1f6fd6;
            }
            QPushButton#actionBtn {
                background-color: #eff6ff;
                border: 1px solid #93c5fd;
                border-radius: 7px;
                color: #1f6fd6;
                font-size: 11px;
                font-weight: 700;
                padding: 6px 12px;
            }
            QPushButton#actionBtn:hover {
                background-color: #dbeafe;
            }
            QPushButton#primaryActionBtn {
                background-color: #1f6fd6;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 7px;
                padding: 7px 14px;
                border: none;
            }
            QPushButton#primaryActionBtn:hover {
                background-color: #1a63c7;
            }
            QPushButton#submitBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #047857);
                color: #ffffff;
                font-weight: 700;
                font-size: 13px;
                border-radius: 8px;
                padding: 10px 22px;
                border: none;
            }
            QPushButton#submitBtn:hover {
                background: #059669;
            }
            QPushButton#cancelBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #475569;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton#cancelBtn:hover {
                background-color: #f1f5f9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header
        header = QHBoxLayout()
        header.setSpacing(10)
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(svg_pixmap(ICONS['upload-cloud-2-line'].format(color='#1f6fd6'), QSize(32, 32)))
        header.addWidget(icon_lbl)

        head_texts = QVBoxLayout()
        head_texts.setSpacing(2)
        head_title = QLabel(self.dialog_title, self)
        head_title.setStyleSheet("color: #0f294d; font-size: 16px; font-weight: 800;")
        head_texts.addWidget(head_title)

        if self.is_revision:
            head_sub = QLabel("Perbarui berkas spasial, verifikasi atribut, dan kirim ulang pengajuan ke antrean validasi.", self)
        else:
            head_sub = QLabel("Unggah dataset spasial terkompilasi, mapping atribut, terapkan SLD, dan sesuaikan metadata.", self)
        head_sub.setStyleSheet("color: #64748b; font-size: 11px;")
        head_sub.setWordWrap(True)
        head_texts.addWidget(head_sub)
        header.addLayout(head_texts, 1)
        layout.addLayout(header)

        # Scroll Area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = _ScrollContent()
        c_layout = QVBoxLayout(content)
        c_layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        c_layout.setContentsMargins(2, 2, 10, 8)
        c_layout.setSpacing(10)

        # ------------------------------------------------------------------ Section 1: Jenis IGT
        s1 = QFrame(content)
        s1.setProperty('class', 'sectionCard')
        s1_lay = QVBoxLayout(s1)
        s1_lay.setSpacing(8)

        s1_title_text = "1. Layer Derivatif (CMS Geoportal) (*)" if is_derivatif else "1. Jenis IGT (*)"
        s1_title = QLabel(s1_title_text, s1)
        s1_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s1_lay.addWidget(s1_title)

        self.jenis_combo = QComboBox(s1)
        self.jenis_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.jenis_combo.setMinimumContentsLength(6)
        if is_derivatif:
            self.jenis_combo.addItems([
                'Coba Derivatif Bidang',
                'Derivatif Potensi Pajak PBB-P2 (Bidang)',
                'Derivatif Zona Kerentanan Bencana',
                'Derivatif Konsolidasi Tanah',
                'Derivatif Indeks Aksesibilitas Fasilitas Publik',
            ])
        else:
            self.jenis_combo.addItems([
                'Data Potensi WP3WT (Pertanahan)',
                'Bidang Tanah Terdaftar (BTT)',
                'RDTR Kabupaten/Kota',
                'RTRW Provinsi/Kabupaten',
                'Hak Guna Usaha (HGU)',
                'Kawasan Hutan dan Konservasi',
            ])
        self.jenis_combo.currentIndexChanged.connect(self._on_jenis_changed)
        s1_lay.addWidget(self.jenis_combo)

        # Target Renaksi Container (Khusus IGT Utama)
        self.renaksi_box = QFrame(s1)
        self.renaksi_box.setObjectName("renaksiBox")
        self.renaksi_box.setStyleSheet("QFrame#renaksiBox { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px; }")
        rn_lay = QVBoxLayout(self.renaksi_box)
        rn_lay.setContentsMargins(6, 6, 6, 6)
        rn_lay.setSpacing(6)

        lbl_rn_head = QLabel("Target Rencana Aksi (Renaksi ATR/BPN)", self.renaksi_box)
        lbl_rn_head.setStyleSheet("color: #0f294d; font-size: 11px; font-weight: 700;")
        rn_lay.addWidget(lbl_rn_head)

        rn_grid = QGridLayout()
        rn_grid.setSpacing(6)
        rn_grid.setColumnStretch(1, 1)
        rn_grid.setColumnStretch(3, 1)

        rn_grid.addWidget(QLabel("Tahun:", self.renaksi_box), 0, 0)
        self.combo_tahun_renaksi = QComboBox(self.renaksi_box)
        self.combo_tahun_renaksi.setMinimumWidth(70)
        self.combo_tahun_renaksi.addItems(["2026", "2025", "2024"])
        rn_grid.addWidget(self.combo_tahun_renaksi, 0, 1)

        rn_grid.addWidget(QLabel("Target:", self.renaksi_box), 0, 2)
        self.inp_target = QLineEdit("1.500", self.renaksi_box)
        self.inp_target.setMinimumWidth(70)
        self.inp_target.setReadOnly(True)
        self.inp_target.setStyleSheet("background-color: #f1f5f9; color: #334155; font-weight: 700; border: 1px solid #cbd5e1;")
        rn_grid.addWidget(self.inp_target, 0, 3)

        rn_grid.addWidget(QLabel("Satuan:", self.renaksi_box), 1, 0)
        self.inp_satuan = QLineEdit("Bidang", self.renaksi_box)
        self.inp_satuan.setMinimumWidth(70)
        self.inp_satuan.setReadOnly(True)
        self.inp_satuan.setStyleSheet("background-color: #f1f5f9; color: #334155; font-weight: 700; border: 1px solid #cbd5e1;")
        rn_grid.addWidget(self.inp_satuan, 1, 1)

        rn_grid.addWidget(QLabel("Realisasi (*):", self.renaksi_box), 1, 2)
        self.inp_realisasi = QLineEdit("1.500", self.renaksi_box)
        self.inp_realisasi.setMinimumWidth(70)
        self.inp_realisasi.setValidator(QIntValidator(0, 999999999, self))
        rn_grid.addWidget(self.inp_realisasi, 1, 3)

        rn_lay.addLayout(rn_grid)
        s1_lay.addWidget(self.renaksi_box)
        if is_derivatif:
            self.renaksi_box.setVisible(False)

        sub_grid = QGridLayout()
        sub_grid.setSpacing(8)
        sub_grid.setColumnStretch(1, 1)
        sub_grid.setColumnStretch(3, 1)

        sub_grid.addWidget(QLabel('Tanggal Upload:', s1), 0, 0)
        self.tgl_upload_lbl = QLabel(QDate.currentDate().toString('yyyy-MM-dd'), s1)
        self.tgl_upload_lbl.setStyleSheet("color: #0f294d; font-weight: 700; font-size: 12px;")
        sub_grid.addWidget(self.tgl_upload_lbl, 0, 1)

        sub_grid.addWidget(QLabel('Jenis Data:', s1), 0, 2)
        self.format_combo = QComboBox(s1)
        self.format_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.format_combo.setMinimumContentsLength(5)
        self.format_combo.addItems(['SHP', 'GeoPackage (.gpkg)', 'GeoJSON (.geojson)'])
        sub_grid.addWidget(self.format_combo, 0, 3)

        s1_lay.addLayout(sub_grid)
        c_layout.addWidget(s1)

        # ------------------------------------------------------------------ Section 2: File SHP dari Layer Aktif
        s2 = QFrame(content)
        s2.setProperty('class', 'sectionCard')
        s2_lay = QVBoxLayout(s2)
        s2_lay.setSpacing(8)

        s2_title = QLabel("2. File SHP (Pilih dari Layer Aktif di QGIS) (*)", s2)
        s2_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s2_lay.addWidget(s2_title)

        layer_row = QHBoxLayout()
        layer_row.setSpacing(6)
        self.layer_combo = QComboBox(s2)
        self.layer_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.layer_combo.setMinimumContentsLength(6)
        layer_row.addWidget(self.layer_combo, 1)

        refresh_btn = QPushButton(s2)
        refresh_btn.setIcon(icon('refresh', '#1f6fd6', 15))
        refresh_btn.setIconSize(QSize(15, 15))
        refresh_btn.setToolTip("Perbarui daftar layer aktif di kanvas QGIS")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setFixedSize(34, 32)
        refresh_btn.setStyleSheet("background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 7px;")
        refresh_btn.clicked.connect(self._refresh_layers)
        layer_row.addWidget(refresh_btn)

        browse_shp_btn = QPushButton("Pilih File...", s2)
        browse_shp_btn.setObjectName("actionBtn")
        browse_shp_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_shp_btn.clicked.connect(self._browse_file)
        layer_row.addWidget(browse_shp_btn)
        s2_lay.addLayout(layer_row)

        self.layer_status_lbl = QLabel("Silakan buka file Shapefile atau muat layer ke kanvas QGIS terlebih dahulu.", s2)
        self.layer_status_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        s2_lay.addWidget(self.layer_status_lbl)

        # Attribute Check Button & Status
        verify_row = QHBoxLayout()
        verify_row.setSpacing(8)
        self.btn_verify_attr = QPushButton("Periksa Atribut (Verifikasi Kompilasi)", s2)
        self.btn_verify_attr.setObjectName("primaryActionBtn")
        self.btn_verify_attr.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_verify_attr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify_attr.clicked.connect(self._on_verify_attributes)
        verify_row.addWidget(self.btn_verify_attr)

        self.attr_status_lbl = QLabel("Pemeriksaan atribut harus diselesaikan terlebih dahulu", s2)
        self.attr_status_lbl.setStyleSheet("color: #b45309; font-size: 11px; font-weight: 600;")
        self.attr_status_lbl.setWordWrap(True)
        verify_row.addWidget(self.attr_status_lbl, 1)
        s2_lay.addLayout(verify_row)

        if is_derivatif:
            self.btn_verify_attr.setVisible(False)
            self.attr_status_lbl.setVisible(False)

        c_layout.addWidget(s2)

        # ------------------------------------------------------------------ Section 3: SLD Style
        s3 = QFrame(content)
        s3.setProperty('class', 'sectionCard')
        s3_lay = QVBoxLayout(s3)
        s3_lay.setSpacing(8)

        s3_title = QLabel("3. SLD Style", s3)
        s3_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s3_lay.addWidget(s3_title)

        sld_row = QHBoxLayout()
        sld_row.setSpacing(8)
        self.sld_name_lbl = QLabel(f"SLD: {self.jenis_combo.currentText()}", s3)
        self.sld_name_lbl.setStyleSheet("color: #334155; font-size: 11px; font-weight: 600;")
        sld_row.addWidget(self.sld_name_lbl, 1)

        self.btn_apply_sld = QPushButton("+ Terapkan SLD ke Layer QGIS", s3)
        self.btn_apply_sld.setObjectName("actionBtn")
        self.btn_apply_sld.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply_sld.clicked.connect(self._on_apply_sld)
        sld_row.addWidget(self.btn_apply_sld)
        s3_lay.addLayout(sld_row)

        self.sld_status_lbl = QLabel("", s3)
        self.sld_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 700;")
        s3_lay.addWidget(self.sld_status_lbl)
        c_layout.addWidget(s3)

        # ------------------------------------------------------------------ Section 4: Metadata
        s4 = QFrame(content)
        s4.setProperty('class', 'sectionCard')
        s4_lay = QVBoxLayout(s4)
        s4_lay.setSpacing(8)

        s4_title = QLabel("4. Metadata", s4)
        s4_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s4_lay.addWidget(s4_title)

        self.meta_check = QCheckBox("Gunakan metadata CMS (Resmi dari sistem)", s4)
        self.meta_check.setChecked(True)
        self.meta_check.setStyleSheet("color: #1e293b; font-size: 12px; font-weight: 600;")
        s4_lay.addWidget(self.meta_check)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        meta_desc = QLabel("Belum ada berkas metadata CMS untuk IGT ini di Geoportal (gunakan Unggah metadata sendiri jika diperlukan).", s4)
        meta_desc.setStyleSheet("color: #64748b; font-size: 10px;")
        meta_desc.setWordWrap(True)
        meta_row.addWidget(meta_desc, 1)

        btn_preview_xml = QPushButton("Preview / Edit Metadata XML", s4)
        btn_preview_xml.setObjectName("actionBtn")
        btn_preview_xml.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_preview_xml.clicked.connect(self._on_preview_metadata)
        meta_row.addWidget(btn_preview_xml)
        s4_lay.addLayout(meta_row)

        c_layout.addWidget(s4)
        if is_derivatif:
            s4.setVisible(False)

        # ------------------------------------------------------------------ Section 5: Dokumen Pendukung Lainnya
        s5 = QFrame(content)
        s5.setProperty('class', 'sectionCard')
        s5_lay = QVBoxLayout(s5)
        s5_lay.setSpacing(8)

        s5_title = QLabel("5. Dokumen Pendukung Lainnya (opsional)", s5)
        s5_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s5_lay.addWidget(s5_title)

        doc_row = QHBoxLayout()
        doc_row.setSpacing(8)
        self.doc_lbl = QLabel("Tidak ada dokumen pendukung dipilih", s5)
        self.doc_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        doc_row.addWidget(self.doc_lbl, 1)

        btn_doc = QPushButton("Pilih File...", s5)
        btn_doc.setObjectName("actionBtn")
        btn_doc.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_doc.clicked.connect(self._on_browse_doc)
        doc_row.addWidget(btn_doc)
        s5_lay.addLayout(doc_row)
        c_layout.addWidget(s5)
        if is_derivatif:
            s5.setVisible(False)

        # ------------------------------------------------------------------ Section 6: Keterangan
        s6 = QFrame(content)
        s6.setProperty('class', 'sectionCard')
        s6_lay = QVBoxLayout(s6)
        s6_lay.setSpacing(8)

        s6_title_txt = "4. Keterangan Pengajuan (*)" if is_derivatif else "6. Keterangan (opsional)"
        s6_title = QLabel(s6_title_txt, s6)
        s6_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        s6_lay.addWidget(s6_title)

        self.keterangan_input = QLineEdit(s6)
        ph_txt = "Isi keterangan pengajuan data derivatif (wajib)" if is_derivatif else "Catatan atau deskripsi pengajuan data kompilasi"
        self.keterangan_input.setPlaceholderText(ph_txt)
        s6_lay.addWidget(self.keterangan_input)
        c_layout.addWidget(s6)
        c_layout.addStretch(1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # ------------------------------------------------------------------ Actions Footer
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        batal_btn = QPushButton("Batal", self)
        batal_btn.setObjectName("cancelBtn")
        batal_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        batal_btn.clicked.connect(self.reject)
        footer.addWidget(batal_btn)

        submit_text = "Kirim Ulang Pengajuan Revisi" if self.is_revision else "Kirim Pengajuan"
        submit_btn = QPushButton(submit_text, self)
        submit_btn.setObjectName("submitBtn")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self._on_submit)
        footer.addWidget(submit_btn)

        layout.addLayout(footer)

        if self.is_revision and self.record_to_revise:
            r_name = self.record_to_revise.get('name') or self.record_to_revise.get('layer', '')
            idx = self.jenis_combo.findText(r_name)
            if idx >= 0:
                self.jenis_combo.setCurrentIndex(idx)
            else:
                self.jenis_combo.insertItem(0, r_name)
                self.jenis_combo.setCurrentIndex(0)

        self._refresh_layers()

    def _on_jenis_changed(self):
        jt = self.jenis_combo.currentText()
        self.sld_name_lbl.setText(f"SLD: {jt}")

    def _refresh_layers(self):
        self.layer_combo.clear()
        found_layers = []
        if QgsProject is not None and QgsProject.instance():
            for lyr in QgsProject.instance().mapLayers().values():
                if lyr.type() == 0:  # Vector layer
                    found_layers.append(lyr.name())

        if found_layers:
            self.layer_combo.addItems(found_layers)
            self.layer_status_lbl.setText(f"✓ Menemukan {len(found_layers)} layer vektor aktif di kanvas QGIS.")
            self.layer_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 600;")
        elif self.selected_file_path:
            self.layer_combo.addItem(os.path.basename(self.selected_file_path))
            self.layer_status_lbl.setText(f"✓ Berkas terpilih: {os.path.basename(self.selected_file_path)}")
            self.layer_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 600;")
        else:
            self.layer_combo.addItem("Tidak ada layer vektor aktif di kanvas QGIS")
            self.layer_status_lbl.setText("Silakan buka file Shapefile atau muat layer ke kanvas QGIS terlebih dahulu.")
            self.layer_status_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Pilih File Shapefile / Geopackage', '',
            'Geospatial Files (*.shp *.gpkg *.zip *.geojson);;All Files (*)'
        )
        if file_path:
            self.selected_file_path = file_path
            self._refresh_layers()

    def _on_verify_attributes(self):
        lyr = None
        if QgsProject is not None and QgsProject.instance():
            sel_text = self.layer_combo.currentText()
            matches = QgsProject.instance().mapLayersByName(sel_text)
            if matches:
                lyr = matches[0]

        dlg = AttributeMappingDialog(
            parent=self,
            igt_name=self.jenis_combo.currentText(),
            target_layer=lyr
        )
        if dlg.exec_() and dlg.confirmed:
            self.is_attribute_verified = True
            n_mapped = len(dlg.get_result_mappings())
            self.attr_status_lbl.setText(f"✓ Pemetaan atribut berhasil dikonfirmasi ({n_mapped} kolom sesuai skema standar IGT).")
            self.attr_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 700;")

    def _on_apply_sld(self):
        self.sld_status_lbl.setText("✓ SLD berhasil diterapkan ke layer kanvas QGIS")
        if self.iface and hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'SLD Diterapkan',
                f"Style SLD '{self.jenis_combo.currentText()}' berhasil diaplikasikan ke layer aktif di QGIS."
            )

    def _on_preview_metadata(self):
        dlg = MetadataPreviewDialog(self.jenis_combo.currentText(), self)
        dlg.exec_()

    def _on_browse_doc(self):
        p, _ = QFileDialog.getOpenFileName(self, 'Pilih Dokumen Pendukung', '', 'PDF/Doc Files (*.pdf *.docx *.doc *.zip);;All Files (*)')
        if p:
            self.doc_lbl.setText(f"✓ {os.path.basename(p)}")
            self.doc_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 700;")

    def _on_submit(self):
        is_derivatif = self.current_category == 'derivatif'
        sel_layer = self.layer_combo.currentText().strip()
        if not sel_layer or "Tidak ada layer" in sel_layer:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih layer SHP aktif di kanvas QGIS atau tentukan berkas data terlebih dahulu.")
            return

        if not is_derivatif and not self.is_attribute_verified:
            QMessageBox.warning(self, "Peringatan", "Pemeriksaan atribut (Verifikasi Kompilasi) wajib diselesaikan dan dikonfirmasi terlebih dahulu sebelum pengajuan.")
            return

        keterangan = self.keterangan_input.text().strip()
        if is_derivatif and not keterangan:
            QMessageBox.warning(self, "Peringatan", "Keterangan pengajuan data derivatif wajib diisi.")
            return

        if not is_derivatif and hasattr(self, 'inp_realisasi') and self.renaksi_box.isVisible() and not self.inp_realisasi.text().strip():
            QMessageBox.warning(self, "Peringatan", "Jumlah realisasi target rencana aksi wajib diisi.")
            return

        jenis = self.jenis_combo.currentText()
        if not keterangan:
            keterangan = "Pengajuan data kompilasi"

        if self.is_revision and self.record_to_revise:
            self.record_to_revise['status'] = 'Diajukan'
            self.record_to_revise['date'] = QDate.currentDate().toString('dd MMM yyyy')
            if keterangan:
                self.record_to_revise['note'] = f"Perbaikan revisi: {keterangan}"
            self.uploadSubmitted.emit(self.record_to_revise)
            self.accept()
            return

        submission = {
            'id': f"AJU-2026-{200 + len(DATASETS)}",
            'category': self.current_category,
            'name': jenis,
            'satker': 'Kantah Kab. Sleman',
            'date': QDate.currentDate().toString('dd MMM yyyy'),
            'status': 'Diajukan',
            'note': f"Kab. Sleman · {keterangan}",
            'scope': 'Kab. Sleman',
        }
        self.uploadSubmitted.emit(submission)
        self.accept()


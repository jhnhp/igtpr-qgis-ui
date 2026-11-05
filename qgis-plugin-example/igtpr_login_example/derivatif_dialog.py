# -*- coding: utf-8 -*-
"""Dialog Derivatif Per Bidang (Mockup V2)."""

import os
import json
from qgis.PyQt.QtCore import QDate, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QButtonGroup, QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFileDialog,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMessageBox, QPushButton, QRadioButton, QScrollArea, QSpinBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .login_page import svg_pixmap


class DerivatifBidangDialog(QDialog):
    """
    Dialog Terintegrasi Derivatif Per Bidang (Mockup V2).
    Menyediakan 3 alur kerja lokal:
    1. ✍️ ISI TEMATIK (Pilih layer derivatif, load baseline WMS, klik bidang, isi atribut CMS, simpan & export)
    2. ➕ CREATE TEMATIK (Input nama layer, pilih baseline CMS, atribut default terkunci 🔒 + custom attrs, simpan & export)
    3. 📂 LOAD TEMATIK (Pilih file tabel atribut derivatif hasil ekspor, visualisasi ke kanvas peta QGIS)
    """

    derivatifSaved = pyqtSignal(dict)

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle('Derivatif Per Bidang')
        self.resize(720, 840)
        self.setMinimumSize(640, 700)
        self.setObjectName('derivatifBidangDialog')

        # Mode Aktif: 'isi', 'create', 'load'
        self.current_mode = 'isi'

        # Sesi Isi Tematik
        self.records = [
            {
                'id': 'BDG-3404-00128',
                'nib': '12.01.04.01.00128',
                'pemegang': 'Siti Rahmawati',
                'jenis_hak': 'Hak Milik',
                'luas': 280.00,
                'status': 'Sudah Tersimpan',
            }
        ]
        self.current_id_counter = 129

        # Sesi Create Tematik
        self.create_records = []
        self.create_custom_cols = [
            {'name': 'ZONASI_TEMATIK', 'type': 'Teks', 'length': 50, 'value': 'Zona Nilai A'},
            {'name': 'POTENSI_PBB', 'type': 'Desimal', 'length': 12, 'value': '1250000.00'},
        ]

        # Sesi Load Tematik
        self.loaded_filepath = ''
        self.loaded_records = []

        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog#derivatifBidangDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QFrame.sectionCard {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 12px;
                padding: 12px 16px;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 6px;
                padding: 5px 9px;
                font-size: 11.5px;
                color: #0f294d;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border-color: #1f6fd6;
            }
            QPushButton#backBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #1f6fd6;
                font-size: 11.5px;
                font-weight: 700;
                padding: 6px 12px;
            }
            QPushButton#backBtn:hover {
                background-color: #eff6ff;
                border-color: #93c5fd;
            }
            QPushButton#actionBtn {
                background-color: #1f6fd6;
                color: #ffffff;
                font-weight: 700;
                font-size: 11.5px;
                border-radius: 8px;
                padding: 7px 14px;
                border: none;
            }
            QPushButton#actionBtn:hover {
                background-color: #1a63c7;
            }
            QPushButton#saveBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #047857);
                color: #ffffff;
                font-weight: 700;
                font-size: 12.5px;
                border-radius: 8px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton#saveBtn:hover {
                background: #059669;
            }
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 8px;
                font-size: 11.5px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                color: #475569;
                font-weight: 700;
                font-size: 11px;
                border: none;
                border-bottom: 1.5px solid #e2e8f0;
                padding: 6px 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 1. Header & Navigation Bar
        head_layout = QHBoxLayout()
        back_btn = QPushButton('← Kembali ke Manajemen', self)
        back_btn.setObjectName('backBtn')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.reject)
        head_layout.addWidget(back_btn)

        head_layout.addSpacing(8)
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(svg_pixmap(ICONS['layers'].format(color='#1f6fd6'), QSize(22, 22)))
        head_layout.addWidget(icon_lbl)

        title = QLabel('Derivatif Per Bidang', self)
        title.setStyleSheet("color: #0f294d; font-size: 16px; font-weight: 800;")
        head_layout.addWidget(title)

        self.mode_badge = QLabel('Mode: Isi Tematik', self)
        self.mode_badge.setStyleSheet("""
            background-color: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            font-size: 10.5px;
            font-weight: 700;
            padding: 3px 10px;
        """)
        head_layout.addWidget(self.mode_badge)
        head_layout.addStretch()
        layout.addLayout(head_layout)

        # 2. Mode Switcher Tabs (3 Tombol Pilihan Utama di Atas)
        tab_frame = QFrame(self)
        tab_frame.setStyleSheet("""
            QFrame {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        tf_layout = QHBoxLayout(tab_frame)
        tf_layout.setContentsMargins(4, 4, 4, 4)
        tf_layout.setSpacing(6)

        self.btn_tab_isi = QPushButton('✍️ Isi Tematik', tab_frame)
        self.btn_tab_isi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_isi.setToolTip("Pilih layer derivatif, load baseline WMS, klik bidang, isi atribut CMS & export")
        self.btn_tab_isi.clicked.connect(lambda: self._switch_mode('isi'))
        tf_layout.addWidget(self.btn_tab_isi)

        self.btn_tab_create = QPushButton('➕ Create Tematik', tab_frame)
        self.btn_tab_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_create.setToolTip("Buat layer baru, load baseline WMS, atribut default terkunci + custom attrs")
        self.btn_tab_create.clicked.connect(lambda: self._switch_mode('create'))
        tf_layout.addWidget(self.btn_tab_create)

        self.btn_tab_load = QPushButton('📂 Load Tematik', tab_frame)
        self.btn_tab_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_load.setToolTip("Pilih berkas hasil ekspor tabel atribut derivatif dan muat visualisasinya ke kanvas peta QGIS")
        self.btn_tab_load.clicked.connect(lambda: self._switch_mode('load'))
        tf_layout.addWidget(self.btn_tab_load)

        layout.addWidget(tab_frame)

        # 3. Stacked Sub-Pages
        self.sub_stack = QStackedWidget(self)

        # Page 0: Mode ISI TEMATIK
        self.view_isi = self._build_view_isi()
        self.sub_stack.addWidget(self.view_isi)

        # Page 1: Mode CREATE TEMATIK
        self.view_create = self._build_view_create()
        self.sub_stack.addWidget(self.view_create)

        # Page 2: Mode LOAD TEMATIK
        self.view_load = self._build_view_load()
        self.sub_stack.addWidget(self.view_load)

        layout.addWidget(self.sub_stack, 1)

        self._switch_mode('isi')

    def _switch_mode(self, mode_name):
        self.current_mode = mode_name
        active_isi = "background-color: #2563eb; color: #ffffff; font-weight: 700; font-size: 11.5px; border-radius: 6px; padding: 6px 14px; border: none;"
        active_create = "background-color: #7c3aed; color: #ffffff; font-weight: 700; font-size: 11.5px; border-radius: 6px; padding: 6px 14px; border: none;"
        active_load = "background-color: #059669; color: #ffffff; font-weight: 700; font-size: 11.5px; border-radius: 6px; padding: 6px 14px; border: none;"
        inactive_style = "background-color: #ffffff; color: #475569; font-size: 11.5px; font-weight: 600; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 14px;"

        self.btn_tab_isi.setStyleSheet(active_isi if mode_name == 'isi' else inactive_style)
        self.btn_tab_create.setStyleSheet(active_create if mode_name == 'create' else inactive_style)
        self.btn_tab_load.setStyleSheet(active_load if mode_name == 'load' else inactive_style)

        if mode_name == 'isi':
            self.mode_badge.setText('Mode: Isi Tematik')
            self.mode_badge.setStyleSheet("background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 12px; font-size: 10.5px; font-weight: 700; padding: 3px 10px;")
            self.sub_stack.setCurrentWidget(self.view_isi)
        elif mode_name == 'create':
            self.mode_badge.setText('Mode: Create Tematik')
            self.mode_badge.setStyleSheet("background-color: #faf5ff; color: #7c3aed; border: 1px solid #e9d5ff; border-radius: 12px; font-size: 10.5px; font-weight: 700; padding: 3px 10px;")
            self.sub_stack.setCurrentWidget(self.view_create)
        elif mode_name == 'load':
            self.mode_badge.setText('Mode: Load Tematik')
            self.mode_badge.setStyleSheet("background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; border-radius: 12px; font-size: 10.5px; font-weight: 700; padding: 3px 10px;")
            self.sub_stack.setCurrentWidget(self.view_load)

    # ==========================================================================
    # SUB-PAGE 0: VIEW ISI TEMATIK
    # ==========================================================================
    def _build_view_isi(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(12)

        # ------------------------------------------------------------------ Section 1
        s1 = QFrame(content)
        s1.setProperty('class', 'sectionCard')
        s1_layout = QVBoxLayout(s1)
        s1_layout.setSpacing(8)

        s1_head = QLabel('1. Pilih Layer Derivatif & Load Baseline WMS:', s1)
        s1_head.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        s1_layout.addWidget(s1_head)

        s1_row = QHBoxLayout()
        s1_row.setSpacing(8)
        self.layer_combo = QComboBox(s1)
        self.layer_combo.addItems([
            'Coba Derivatif Bidang',
            'Derivatif Potensi Pajak PBB-P2',
            'Derivatif Zona Kerentanan Bencana',
            'Derivatif Konsolidasi Tanah',
        ])
        s1_row.addWidget(self.layer_combo, 1)

        btn_refresh_der = QPushButton("🔄", s1)
        btn_refresh_der.setToolTip("Muat ulang daftar layer derivatif dari server")
        btn_refresh_der.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh_der.setFixedWidth(34)
        s1_row.addWidget(btn_refresh_der)

        chip = QLabel('Basis: Bidang | 21 Kolom CMS, Tanpa keterangan', s1)
        chip.setStyleSheet("""
            background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1;
            border-radius: 6px; font-size: 10px; font-weight: 600; padding: 5px 8px;
        """)
        s1_row.addWidget(chip)
        s1_layout.addLayout(s1_row)

        wms_row = QHBoxLayout()
        wms_row.setSpacing(8)
        self.btn_load_wms = QPushButton('⚡ Load Baseline WMS', s1)
        self.btn_load_wms.setObjectName('actionBtn')
        self.btn_load_wms.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_wms.clicked.connect(self._on_load_wms_clicked)
        wms_row.addWidget(self.btn_load_wms)

        self.wms_status_lbl = QLabel('⏳ Baseline WMS: Belum dimuat', s1)
        self.wms_status_lbl.setStyleSheet("color: #b45309; font-size: 11px; font-weight: 700;")
        wms_row.addWidget(self.wms_status_lbl)

        btn_log = QPushButton("📋 Log", s1)
        btn_log.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_log.setStyleSheet("background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 8px; font-size: 10.5px;")
        btn_log.clicked.connect(lambda: QMessageBox.information(self, "Log WMS", "Status WMS: GeoServer Service OK • Layer: bpn:bidang_tanah_terdaftar • EPSG:4326"))
        wms_row.addWidget(btn_log)
        wms_row.addStretch()
        s1_layout.addLayout(wms_row)

        c_layout.addWidget(s1)

        # ------------------------------------------------------------------ Section 2
        s2 = QFrame(content)
        s2.setProperty('class', 'sectionCard')
        s2_layout = QVBoxLayout(s2)
        s2_layout.setSpacing(8)

        s2_head_row = QHBoxLayout()
        s2_head = QLabel('2. Interaksi Canvas & Form Atribut CMS:', s2)
        s2_head.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        s2_head_row.addWidget(s2_head)
        s2_head_row.addStretch()

        btn_pick_canvas = QPushButton("🎯 Klik Bidang di Peta", s2)
        btn_pick_canvas.setObjectName('actionBtn')
        btn_pick_canvas.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_canvas.clicked.connect(self._on_click_bidang_peta)
        s2_head_row.addWidget(btn_pick_canvas)

        btn_import_isi = QPushButton("📥 Import Bidang", s2)
        btn_import_isi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import_isi.setStyleSheet("background-color: #f0f9ff; color: #0284c7; border: 1px solid #38bdf8; border-radius: 6px; padding: 5px 10px; font-size: 11px; font-weight: 700;")
        btn_import_isi.clicked.connect(self._on_import_bidang_file)
        s2_head_row.addWidget(btn_import_isi)

        s2_layout.addLayout(s2_head_row)

        id_status_row = QHBoxLayout()
        id_lbl = QLabel('ID Bidang:', s2)
        id_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700;")
        id_status_row.addWidget(id_lbl)
        self.id_input = QLineEdit(f"BDG-3404-00{self.current_id_counter}", s2)
        self.id_input.setFixedWidth(160)
        id_status_row.addWidget(self.id_input)

        id_status_row.addSpacing(10)
        self.lbl_count_isi = QLabel(f"📦 {len(self.records)} Bidang Sesi Ini", s2)
        self.lbl_count_isi.setStyleSheet("background-color: #ecfdf5; color: #047857; font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 6px; border: 1px solid #a7f3d0;")
        id_status_row.addWidget(self.lbl_count_isi)
        id_status_row.addStretch()
        s2_layout.addLayout(id_status_row)

        grid = QGridLayout()
        grid.setSpacing(8)

        fields = [
            ('NAMOBJ', 'Bidang 00129'),
            ('NAMAKANWIL', 'Kanwil BPN D.I. Yogyakarta'),
            ('NAMAKANTAH', 'Kantah Kab. Sleman'),
            ('WADMPR', 'D.I. Yogyakarta'),
            ('WADMKK', 'Kabupaten Sleman'),
            ('WADMKC', 'Kecamatan Depok'),
            ('WADMKD', 'Kalurahan Condongcatur'),
            ('NIB', '12.01.04.01.00129'),
            ('NOMORHAK', '00129/Condongcatur'),
            ('PEMEGANGHA', 'Budi Santoso'),
            ('DPHAK', 'Milik Sendiri'),
            ('KEWSKHAK', 'Kepala Kantor Pertanahan Kab. Sleman'),
            ('NOSKHAK', 'SK-543/HAK/2024'),
            ('REMARK', 'Bidang Terverifikasi Lengkap'),
        ]

        self.form_inputs = {}
        for idx, (f_name, f_val) in enumerate(fields):
            row = idx // 2
            col = (idx % 2) * 2
            lbl = QLabel(f_name, s2)
            lbl.setStyleSheet("color: #475569; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
            inp = QLineEdit(f_val, s2)
            self.form_inputs[f_name] = inp
            grid.addWidget(lbl, row * 2, col)
            grid.addWidget(inp, row * 2 + 1, col)

        special_row = (len(fields) // 2) * 2

        # TIPEPEHAK
        grid.addWidget(QLabel('TIPEPEHAK', s2), special_row, 0)
        self.tipe_combo = QComboBox(s2)
        self.tipe_combo.addItems(['Perorangan', 'Badan Hukum', 'Instansi Pemerintah', 'Badan Keagamaan'])
        grid.addWidget(self.tipe_combo, special_row + 1, 0)

        # JENISHAK
        grid.addWidget(QLabel('JENISHAK', s2), special_row, 2)
        self.jenis_combo = QComboBox(s2)
        self.jenis_combo.addItems(['Hak Milik', 'Hak Guna Bangunan', 'Hak Pakai', 'Hak Pengelolaan', 'Hak Wakaf'])
        grid.addWidget(self.jenis_combo, special_row + 1, 2)

        special_row += 2
        # TGLSKHAK
        grid.addWidget(QLabel('TGLSKHAK', s2), special_row, 0)
        self.tgl_sk = QDateEdit(QDate.currentDate(), s2)
        self.tgl_sk.setCalendarPopup(True)
        grid.addWidget(self.tgl_sk, special_row + 1, 0)

        # VALIDSEJAK
        grid.addWidget(QLabel('VALIDSEJAK', s2), special_row, 2)
        self.valid_sejak = QDateEdit(QDate.currentDate(), s2)
        self.valid_sejak.setCalendarPopup(True)
        grid.addWidget(self.valid_sejak, special_row + 1, 2)

        special_row += 2
        # BERAKHIRHA
        grid.addWidget(QLabel('BERAKHIRHA', s2), special_row, 0)
        self.berakhir_hak = QDateEdit(QDate.currentDate().addYears(30), s2)
        self.berakhir_hak.setCalendarPopup(True)
        grid.addWidget(self.berakhir_hak, special_row + 1, 0)

        # LUASTERTUL
        grid.addWidget(QLabel('LUASTERTUL (m²)', s2), special_row, 2)
        self.luas_spin = QDoubleSpinBox(s2)
        self.luas_spin.setRange(0.0, 9999999.0)
        self.luas_spin.setValue(350.00)
        grid.addWidget(self.luas_spin, special_row + 1, 2)

        s2_layout.addLayout(grid)

        # Button Simpan Bidang
        btn_add = QPushButton('Simpan Bidang', s2)
        btn_add.setObjectName('actionBtn')
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self._on_add_bidang_clicked)
        s2_layout.addWidget(btn_add, 0, Qt.AlignmentFlag.AlignRight)

        c_layout.addWidget(s2)

        # ------------------------------------------------------------------ Section 3
        s3 = QFrame(content)
        s3.setProperty('class', 'sectionCard')
        s3_layout = QVBoxLayout(s3)
        s3_layout.setSpacing(8)

        s3_head_row = QHBoxLayout()
        s3_head = QLabel('3. Daftar Bidang Terisi (Sesi Ini):', s3)
        s3_head.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        s3_head_row.addWidget(s3_head)
        s3_head_row.addStretch()

        self.badge_baru = QLabel('Baru Diisi: 0 bidang', s3)
        self.badge_baru.setStyleSheet("""
            background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
            border-radius: 6px; font-size: 10.5px; font-weight: 700; padding: 2px 8px;
        """)
        s3_head_row.addWidget(self.badge_baru)

        self.badge_tersimpan = QLabel(f"Sudah Tersimpan: {len(self.records)} bidang", s3)
        self.badge_tersimpan.setStyleSheet("""
            background-color: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;
            border-radius: 6px; font-size: 10.5px; font-weight: 700; padding: 2px 8px;
        """)
        s3_head_row.addWidget(self.badge_tersimpan)
        s3_layout.addLayout(s3_head_row)

        self.table = QTableWidget(s3)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID Bidang', 'NIB', 'Pemegang Hak', 'Jenis Hak', 'Luas (m²)', 'Aksi'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setFixedHeight(140)
        s3_layout.addWidget(self.table)
        c_layout.addWidget(s3)

        # ------------------------------------------------------------------ Section 4
        s4 = QFrame(content)
        s4.setProperty('class', 'sectionCard')
        s4_layout = QVBoxLayout(s4)
        s4_layout.setSpacing(10)

        s4_head = QLabel('4. Opsi Penyimpanan & Format Ekspor (Tabel Atribut Saja)', s4)
        s4_head.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        s4_layout.addWidget(s4_head)

        path_grid = QGridLayout()
        path_grid.setSpacing(8)

        path_grid.addWidget(QLabel('NAMA FILE', s4), 0, 0)
        self.filename_input = QLineEdit('derivatif_coba_derivatif_bidang', s4)
        path_grid.addWidget(self.filename_input, 1, 0)

        path_grid.addWidget(QLabel('FOLDER PENYIMPANAN', s4), 0, 1)
        folder_row = QHBoxLayout()
        folder_row.setSpacing(6)
        default_dir = os.path.expanduser('~/Documents')
        if not os.path.isdir(default_dir):
            default_dir = os.getcwd()
        self.folder_input = QLineEdit(default_dir, s4)
        folder_row.addWidget(self.folder_input, 1)

        browse_folder_btn = QPushButton('Pilih Folder...', s4)
        browse_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_folder_btn.clicked.connect(self._on_browse_folder)
        folder_row.addWidget(browse_folder_btn)
        path_grid.addLayout(folder_row, 1, 1)

        s4_layout.addLayout(path_grid)

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(14)
        fmt_lbl = QLabel('Format Ekspor:', s4)
        fmt_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700;")
        fmt_row.addWidget(fmt_lbl)

        self.radio_group = QButtonGroup(self)
        for idx, (fmt_label, checked) in enumerate([
            ('.gpkg (GeoPackage)', True),
            ('.geojson (GeoJSON)', False),
            ('Esri Shapefile (.shp/.dbf)', False),
        ]):
            rb = QRadioButton(fmt_label, s4)
            rb.setChecked(checked)
            self.radio_group.addButton(rb, idx)
            fmt_row.addWidget(rb)
        fmt_row.addStretch()
        s4_layout.addLayout(fmt_row)

        notice_box = QFrame(s4)
        notice_box.setStyleSheet("""
            background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 8px 12px;
        """)
        nb_layout = QHBoxLayout(notice_box)
        nb_layout.setContentsMargins(0, 0, 0, 0)
        nb_lbl = QLabel(
            "🔒 Hanya poligon bidang terpilih yang disimpan (bukan seluruh baseline provinsi). Sesi akan direset setelah disimpan.",
            notice_box)
        nb_lbl.setStyleSheet("color: #1e40af; font-size: 11px;")
        nb_layout.addWidget(nb_lbl)
        s4_layout.addWidget(notice_box)

        save_btn = QPushButton('💾 Simpan Derivatif', s4)
        save_btn.setObjectName('saveBtn')
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save_derivatif)
        s4_layout.addWidget(save_btn)

        c_layout.addWidget(s4)

        scroll.setWidget(content)
        self._render_table()
        return scroll

    # ==========================================================================
    # SUB-PAGE 1: VIEW CREATE TEMATIK
    # ==========================================================================
    def _build_view_create(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        c_lay = QVBoxLayout(content)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(12)

        # Kartu 1: Pengaturan Layer Baru & Baseline
        c1 = QFrame(content)
        c1.setProperty('class', 'sectionCard')
        c1_lay = QVBoxLayout(c1)
        c1_lay.setSpacing(8)

        lbl_c1_title = QLabel("1. Pengaturan Layer Baru & Baseline (CMS Geoportal):", c1)
        lbl_c1_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        c1_lay.addWidget(lbl_c1_title)

        nl_row = QHBoxLayout()
        lbl_nl = QLabel("Nama Layer:", c1)
        lbl_nl.setStyleSheet("font-size: 11.5px; color: #334155; font-weight: bold;")
        nl_row.addWidget(lbl_nl)
        self.inp_create_layer_name = QLineEdit("derivatif_bidang_kustom", c1)
        nl_row.addWidget(self.inp_create_layer_name, 1)
        c1_lay.addLayout(nl_row)

        bl_row = QHBoxLayout()
        lbl_bl = QLabel("Baseline CMS:", c1)
        lbl_bl.setStyleSheet("font-size: 11.5px; color: #334155; font-weight: bold;")
        bl_row.addWidget(lbl_bl)
        self.combo_create_baseline = QComboBox(c1)
        self.combo_create_baseline.addItems([
            "Bidang Tanah Terdaftar (BTT)",
            "Pola Ruang RDTR Kawasan",
            "Batas Administrasi Wilayah",
        ])
        bl_row.addWidget(self.combo_create_baseline, 1)
        btn_refresh_bl = QPushButton("🔄", c1)
        btn_refresh_bl.setFixedWidth(34)
        btn_refresh_bl.setCursor(Qt.CursorShape.PointingHandCursor)
        bl_row.addWidget(btn_refresh_bl)
        c1_lay.addLayout(bl_row)

        wms_c_row = QHBoxLayout()
        btn_load_bl_create = QPushButton("⚡ Load Baseline WMS", c1)
        btn_load_bl_create.setObjectName("actionBtn")
        btn_load_bl_create.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_create_wms_status = QLabel("⏳ Baseline WMS: Belum dimuat", c1)
        self.lbl_create_wms_status.setStyleSheet("color: #b45309; font-size: 11px; font-weight: 700;")
        
        def on_load_create_wms():
            self.lbl_create_wms_status.setText("✓ Baseline WMS: Dimuat di Kanvas QGIS")
            self.lbl_create_wms_status.setStyleSheet("color: #047857; font-size: 11px; font-weight: 800;")
            QMessageBox.information(self, "Baseline WMS", "Layer WMS Baseline berhasil dimuat ke peta QGIS.")

        btn_load_bl_create.clicked.connect(on_load_create_wms)
        wms_c_row.addWidget(btn_load_bl_create)
        wms_c_row.addWidget(self.lbl_create_wms_status)
        wms_c_row.addStretch()
        c1_lay.addLayout(wms_c_row)

        c_lay.addWidget(c1)

        # Kartu 2: Pilih Bidang Baseline, Atribut Default Terkunci + Kustom
        c2 = QFrame(content)
        c2.setProperty('class', 'sectionCard')
        c2_lay = QVBoxLayout(c2)
        c2_lay.setSpacing(8)

        lbl_c2_title = QLabel("2. Pilih Bidang Baseline, Atribut Default (Terkunci 🔒) + Kustom:", c2)
        lbl_c2_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        c2_lay.addWidget(lbl_c2_title)

        pick_row = QHBoxLayout()
        btn_pick_create = QPushButton("🎯 Pilih Bidang Baseline", c2)
        btn_pick_create.setObjectName("actionBtn")
        btn_pick_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_create.clicked.connect(self._on_click_bidang_peta)
        pick_row.addWidget(btn_pick_create)

        btn_import_create = QPushButton("📥 Import Bidang", c2)
        btn_import_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import_create.setStyleSheet("background-color: #faf5ff; color: #7c3aed; border: 1px solid #c084fc; border-radius: 6px; padding: 5px 10px; font-size: 11px; font-weight: 700;")
        btn_import_create.clicked.connect(self._on_import_bidang_file)
        pick_row.addWidget(btn_import_create)

        self.lbl_create_id = QLabel(f"ID Bidang: <b>BDG-3404-00{self.current_id_counter}</b>", c2)
        self.lbl_create_id.setStyleSheet("color: #0f294d; font-size: 11px;")
        pick_row.addWidget(self.lbl_create_id)
        pick_row.addStretch()

        self.lbl_count_create = QLabel(f"📦 {len(self.create_records)} Bidang Sesi Ini", c2)
        self.lbl_count_create.setStyleSheet("background-color: #ecfdf5; color: #047857; font-size: 11px; font-weight: bold; padding: 3px 8px; border-radius: 6px; border: 1px solid #a7f3d0;")
        pick_row.addWidget(self.lbl_count_create)
        c2_lay.addLayout(pick_row)

        # Sub A: Atribut Baseline Terkunci
        lbl_suba = QLabel("A. Atribut Default Baseline (🔒 Terkunci):", c2)
        lbl_suba.setStyleSheet("font-size: 11.5px; font-weight: 700; color: #334155;")
        c2_lay.addWidget(lbl_suba)

        self.table_locked = QTableWidget(c2)
        self.table_locked.setColumnCount(3)
        self.table_locked.setHorizontalHeaderLabels(["Kolom Baseline", "Tipe", "Nilai (Terkunci 🔒)"])
        self.table_locked.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_locked.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_locked.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_locked.verticalHeader().setVisible(False)
        self.table_locked.setFixedHeight(120)

        locked_data = [
            ("NIB", "String", "12.01.04.01.00129"),
            ("NAMOBJ", "String", "Bidang Pertanahan Sleman"),
            ("WADMPR", "String", "D.I. Yogyakarta"),
            ("WADMKK", "String", "Kabupaten Sleman"),
            ("LUASTERTUL", "Decimal", "350.00 m²"),
            ("PEMEGANGHA", "String", "Budi Santoso"),
        ]
        self.table_locked.setRowCount(len(locked_data))
        for r_idx, (col, tp, val) in enumerate(locked_data):
            self.table_locked.setItem(r_idx, 0, QTableWidgetItem(col))
            self.table_locked.setItem(r_idx, 1, QTableWidgetItem(tp))
            item_v = QTableWidgetItem(val)
            item_v.setFlags(item_v.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table_locked.setItem(r_idx, 2, item_v)
        c2_lay.addWidget(self.table_locked)

        # Sub B: Atribut Custom Tambahan
        subb_head = QHBoxLayout()
        lbl_subb = QLabel("B. Atribut Custom Tambahan:", c2)
        lbl_subb.setStyleSheet("font-size: 11.5px; font-weight: 700; color: #334155;")
        subb_head.addWidget(lbl_subb)
        subb_head.addStretch()

        btn_add_col = QPushButton("＋ Tambah Atribut", c2)
        btn_add_col.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_col.setStyleSheet("background-color: #f1f5f9; color: #0f294d; font-weight: 700; border: 1px solid #cbd5e1; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
        btn_add_col.clicked.connect(self._on_add_custom_col)
        subb_head.addWidget(btn_add_col)
        c2_lay.addLayout(subb_head)

        self.table_custom = QTableWidget(c2)
        self.table_custom.setColumnCount(5)
        self.table_custom.setHorizontalHeaderLabels(["Nama Kolom", "Tipe", "Length", "Nilai (Isi)", ""])
        self.table_custom.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_custom.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_custom.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_custom.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table_custom.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_custom.setColumnWidth(0, 160)
        self.table_custom.verticalHeader().setVisible(False)
        self.table_custom.setFixedHeight(120)
        c2_lay.addWidget(self.table_custom)
        self._render_custom_cols_table()

        btn_save_create_bidang = QPushButton("Simpan Bidang", c2)
        btn_save_create_bidang.setObjectName("actionBtn")
        btn_save_create_bidang.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save_create_bidang.clicked.connect(self._on_save_create_bidang)
        c2_lay.addWidget(btn_save_create_bidang, 0, Qt.AlignmentFlag.AlignRight)

        c_lay.addWidget(c2)

        # Kartu 3: Daftar Bidang Terisi (Mode Create)
        c3 = QFrame(content)
        c3.setProperty('class', 'sectionCard')
        c3_lay = QVBoxLayout(c3)
        c3_lay.setSpacing(6)

        lbl_c3_title = QLabel("3. Daftar Bidang Terisi (Sesi Ini):", c3)
        lbl_c3_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        c3_lay.addWidget(lbl_c3_title)

        self.table_create_parcels = QTableWidget(c3)
        self.table_create_parcels.setColumnCount(4)
        self.table_create_parcels.setHorizontalHeaderLabels(["No", "ID Bidang", "Ringkasan Atribut Kustom", "Aksi"])
        self.table_create_parcels.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_create_parcels.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_create_parcels.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_create_parcels.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_create_parcels.verticalHeader().setVisible(False)
        self.table_create_parcels.setFixedHeight(110)
        c3_lay.addWidget(self.table_create_parcels)
        c_lay.addWidget(c3)

        # Kartu 4: Opsi Penyimpanan & Ekspor
        c4 = QFrame(content)
        c4.setProperty('class', 'sectionCard')
        c4_lay = QVBoxLayout(c4)
        c4_lay.setSpacing(8)

        lbl_c4_title = QLabel("4. Opsi Penyimpanan & Format Ekspor:", c4)
        lbl_c4_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        c4_lay.addWidget(lbl_c4_title)

        save_create_btn = QPushButton("💾 Simpan Derivatif Kustom", c4)
        save_create_btn.setObjectName("saveBtn")
        save_create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_create_btn.clicked.connect(self._on_save_derivatif_create)
        c4_lay.addWidget(save_create_btn)
        c_lay.addWidget(c4)

        scroll.setWidget(content)
        return scroll

    # ==========================================================================
    # SUB-PAGE 2: VIEW LOAD TEMATIK
    # ==========================================================================
    def _build_view_load(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        l_lay = QVBoxLayout(content)
        l_lay.setContentsMargins(0, 0, 0, 0)
        l_lay.setSpacing(12)

        # Kartu 1: Pilih File Tabel Atribut
        l1 = QFrame(content)
        l1.setProperty('class', 'sectionCard')
        l1_lay = QVBoxLayout(l1)
        l1_lay.setSpacing(8)

        lbl_l1_title = QLabel("1. Pilih File Tabel Atribut Derivatif Hasil Ekspor:", l1)
        lbl_l1_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        l1_lay.addWidget(lbl_l1_title)

        file_row = QHBoxLayout()
        self.inp_load_file = QLineEdit(l1)
        self.inp_load_file.setReadOnly(True)
        self.inp_load_file.setPlaceholderText("Pilih berkas (.gpkg, .geojson, .shp, .csv, .json)...")
        file_row.addWidget(self.inp_load_file, 1)

        btn_browse_load = QPushButton("📁 Browse...", l1)
        btn_browse_load.setObjectName("actionBtn")
        btn_browse_load.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse_load.clicked.connect(self._on_browse_load_file)
        file_row.addWidget(btn_browse_load)

        btn_config_bl = QPushButton("⚙️ Pengaturan Baseline...", l1)
        btn_config_bl.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_config_bl.setStyleSheet("background: #f0fdf4; color: #166534; border: 1px solid #86efac; border-radius: 6px; padding: 6px 10px; font-size: 11px; font-weight: 700;")
        btn_config_bl.clicked.connect(lambda: QMessageBox.information(self, "Pengaturan Baseline", "Baseline Terdeteksi: Bidang Tanah Terdaftar (BTT)\nStatus Geometri: Valid (EPSG:4326)"))
        file_row.addWidget(btn_config_bl)

        btn_reset_load = QPushButton("🔄 Reset", l1)
        btn_reset_load.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset_load.setStyleSheet("background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; border-radius: 6px; padding: 6px 10px; font-size: 11px; font-weight: 700;")
        btn_reset_load.clicked.connect(self._on_reset_load)
        file_row.addWidget(btn_reset_load)
        l1_lay.addLayout(file_row)

        self.lbl_load_summary = QLabel("", l1)
        self.lbl_load_summary.setStyleSheet("color: #047857; font-size: 11px; font-weight: 700;")
        l1_lay.addWidget(self.lbl_load_summary)

        l_lay.addWidget(l1)

        # Kartu 2: Visualisasi Geometri & Tabel Atribut
        l2 = QFrame(content)
        l2.setProperty('class', 'sectionCard')
        l2_lay = QVBoxLayout(l2)
        l2_lay.setSpacing(8)

        lbl_l2_title = QLabel("2. Visualisasi Geometri di Kanvas QGIS & Tabel Atribut:", l2)
        lbl_l2_title.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        l2_lay.addWidget(lbl_l2_title)

        btn_visualize = QPushButton("⚡ Muat ke Kanvas QGIS dan Visualisasikan", l2)
        btn_visualize.setObjectName("actionBtn")
        btn_visualize.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_visualize.clicked.connect(self._on_execute_load_to_qgis)
        l2_lay.addWidget(btn_visualize)

        self.table_loaded_parcels = QTableWidget(l2)
        self.table_loaded_parcels.setColumnCount(5)
        self.table_loaded_parcels.setHorizontalHeaderLabels(["ID Bidang", "NIB", "Pemegang Hak", "Jenis Hak", "Luas (m²)"])
        self.table_loaded_parcels.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_loaded_parcels.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_loaded_parcels.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_loaded_parcels.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_loaded_parcels.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_loaded_parcels.verticalHeader().setVisible(False)
        self.table_loaded_parcels.setFixedHeight(160)
        l2_lay.addWidget(self.table_loaded_parcels)

        l_lay.addWidget(l2)

        scroll.setWidget(content)
        return scroll

    # ==========================================================================
    # ACTION HANDLERS & HELPERS
    # ==========================================================================
    def _on_load_wms_clicked(self):
        self.wms_status_lbl.setText('✓ Baseline WMS: Terpasang di QGIS (Aktif)')
        self.wms_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 800;")
        if self.iface and hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'Baseline WMS Dimuat',
                'Layer WMS Bidang Tanah berhasil dimuat ke kanvas QGIS. Klik bidang tanah pada peta untuk memilih ID Bidang.'
            )

    def _on_click_bidang_peta(self):
        b_id = f"BDG-3404-00{self.current_id_counter}"
        self.id_input.setText(b_id)
        if hasattr(self, 'lbl_create_id'):
            self.lbl_create_id.setText(f"ID Bidang: <b>{b_id}</b>")
        QMessageBox.information(
            self,
            "Pilih Bidang di Peta",
            f"Mode pemilihan bidang aktif di kanvas QGIS.\n\nBidang terpilih: {b_id} (NIB: 12.01.04.01.00{self.current_id_counter})"
        )

    def _on_import_bidang_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Bidang Derivatif", "", "Spasial Files (*.gpkg *.geojson *.shp *.csv *.json);;All Files (*)"
        )
        if path:
            QMessageBox.information(
                self,
                "Import Bidang",
                f"Berkas '{os.path.basename(path)}' berhasil diimpor ke sesi ini."
            )

    def _on_add_bidang_clicked(self):
        b_id = self.id_input.text().strip() or f"BDG-3404-00{self.current_id_counter}"
        nib = self.form_inputs['NIB'].text().strip() or f"12.01.04.01.00{self.current_id_counter}"
        pemegang = self.form_inputs['PEMEGANGHA'].text().strip() or 'Wajib Pajak / Pemilik'
        jenis_hak = self.jenis_combo.currentText()
        luas = self.luas_spin.value()

        record = {
            'id': b_id,
            'nib': nib,
            'pemegang': pemegang,
            'jenis_hak': jenis_hak,
            'luas': luas,
            'status': 'Baru Diisi',
        }
        self.records.append(record)
        self.current_id_counter += 1
        self.id_input.setText(f"BDG-3404-00{self.current_id_counter}")
        self.form_inputs['NIB'].setText(f"12.01.04.01.00{self.current_id_counter}")
        self.lbl_count_isi.setText(f"📦 {len(self.records)} Bidang Sesi Ini")
        self._render_table()

    def _render_table(self):
        self.table.setRowCount(len(self.records))
        baru_count = len([r for r in self.records if r.get('status') == 'Baru Diisi'])
        saved_count = len([r for r in self.records if r.get('status') == 'Sudah Tersimpan'])

        self.badge_baru.setText(f"Baru Diisi: {baru_count} bidang")
        self.badge_tersimpan.setText(f"Sudah Tersimpan: {saved_count} bidang")

        for row, r in enumerate(self.records):
            item_id = QTableWidgetItem(r['id'])
            item_id.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, QTableWidgetItem(r.get('nib', '—')))
            self.table.setItem(row, 2, QTableWidgetItem(r.get('pemegang', '—')))
            self.table.setItem(row, 3, QTableWidgetItem(r.get('jenis_hak', '—')))
            luas_str = f"{r.get('luas', 0):.2f}"
            self.table.setItem(row, 4, QTableWidgetItem(luas_str))

            del_btn = QPushButton('Hapus')
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5;
                    border-radius: 4px; font-size: 10px; padding: 2px 6px;
                }
                QPushButton:hover { background-color: #fecaca; }
            """)
            del_btn.clicked.connect(lambda checked, idx=row: self._delete_record(idx))
            self.table.setCellWidget(row, 5, del_btn)

    def _delete_record(self, idx):
        if 0 <= idx < len(self.records):
            self.records.pop(idx)
            self.lbl_count_isi.setText(f"📦 {len(self.records)} Bidang Sesi Ini")
            self._render_table()

    # Create Mode Methods
    def _render_custom_cols_table(self):
        self.table_custom.setRowCount(len(self.create_custom_cols))
        for row, col_item in enumerate(self.create_custom_cols):
            # 0: Nama Kolom
            inp_name = QLineEdit(col_item['name'])
            inp_name.textChanged.connect(lambda t, r=row: self.create_custom_cols[r].update({'name': t}))
            self.table_custom.setCellWidget(row, 0, inp_name)

            # 1: Tipe
            cb_type = QComboBox()
            cb_type.addItems(['Teks', 'Angka Bulat', 'Desimal', 'Tanggal'])
            cb_type.setCurrentText(col_item.get('type', 'Teks'))
            cb_type.currentTextChanged.connect(lambda t, r=row: self.create_custom_cols[r].update({'type': t}))
            self.table_custom.setCellWidget(row, 1, cb_type)

            # 2: Length
            sp_len = QSpinBox()
            sp_len.setRange(1, 254)
            sp_len.setValue(col_item.get('length', 50))
            sp_len.valueChanged.connect(lambda v, r=row: self.create_custom_cols[r].update({'length': v}))
            self.table_custom.setCellWidget(row, 2, sp_len)

            # 3: Nilai (Isi)
            inp_val = QLineEdit(str(col_item.get('value', '')))
            inp_val.textChanged.connect(lambda t, r=row: self.create_custom_cols[r].update({'value': t}))
            self.table_custom.setCellWidget(row, 3, inp_val)

            # 4: Delete button
            btn_del = QPushButton('✕')
            btn_del.setStyleSheet("color: #b91c1c; font-weight: bold; font-size: 11px; background: transparent; border: none;")
            btn_del.clicked.connect(lambda checked, r=row: self._delete_custom_col(r))
            self.table_custom.setCellWidget(row, 4, btn_del)

    def _on_add_custom_col(self):
        new_name = f"KOLOM_KUSTOM_{len(self.create_custom_cols) + 1}"
        self.create_custom_cols.append({
            'name': new_name, 'type': 'Teks', 'length': 50, 'value': 'Nilai default'
        })
        self._render_custom_cols_table()

    def _delete_custom_col(self, row):
        if 0 <= row < len(self.create_custom_cols):
            self.create_custom_cols.pop(row)
            self._render_custom_cols_table()

    def _on_save_create_bidang(self):
        b_id = f"BDG-3404-00{self.current_id_counter}"
        summary_attrs = ", ".join([f"{c['name']}={c['value']}" for c in self.create_custom_cols])
        self.create_records.append({
            'id': b_id,
            'summary': summary_attrs,
        })
        self.current_id_counter += 1
        self.lbl_create_id.setText(f"ID Bidang: <b>BDG-3404-00{self.current_id_counter}</b>")
        self.lbl_count_create.setText(f"📦 {len(self.create_records)} Bidang Sesi Ini")
        self._render_create_table()

    def _render_create_table(self):
        self.table_create_parcels.setRowCount(len(self.create_records))
        for row, r in enumerate(self.create_records):
            self.table_create_parcels.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_create_parcels.setItem(row, 1, QTableWidgetItem(r['id']))
            self.table_create_parcels.setItem(row, 2, QTableWidgetItem(r['summary']))

            del_btn = QPushButton('Hapus')
            del_btn.setStyleSheet("color: #b91c1c; font-size: 10px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 4px;")
            del_btn.clicked.connect(lambda checked, idx=row: self._delete_create_record(idx))
            self.table_create_parcels.setCellWidget(row, 3, del_btn)

    def _delete_create_record(self, idx):
        if 0 <= idx < len(self.create_records):
            self.create_records.pop(idx)
            self.lbl_count_create.setText(f"📦 {len(self.create_records)} Bidang Sesi Ini")
            self._render_create_table()

    def _on_save_derivatif_create(self):
        layer_name = self.inp_create_layer_name.text().strip() or "derivatif_bidang_kustom"
        QMessageBox.information(
            self,
            "Derivatif Kustom Disimpan",
            f"Layer derivatif kustom '{layer_name}' berhasil disimpan!\n\n"
            f"Jumlah bidang terisi: {len(self.create_records)} bidang\n"
            f"Jumlah kolom atribut kustom: {len(self.create_custom_cols)} kolom\n\n"
            f"Data siap dimuat ke peta QGIS atau diajukan ke Manajemen IGT Derivatif."
        )
        self.derivatifSaved.emit({
            'id': f"AJU-2026-CR-{len(self.create_records)}",
            'category': 'derivatif',
            'name': layer_name,
            'satker': 'Ditjen SPPR',
            'date': QDate.currentDate().toString('dd MMM yyyy'),
            'status': 'Diproses',
            'note': f"Kustom {len(self.create_records)} bidang · {len(self.create_custom_cols)} kolom",
            'scope': 'Kabupaten Sleman',
        })
        self.accept()

    # Load Mode Methods
    def _on_browse_load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Berkas Tabel Atribut Derivatif", "",
            "Berkas Derivatif (*.gpkg *.geojson *.json *.shp *.csv *.dbf);;Semua Berkas (*)"
        )
        if file_path:
            self.loaded_filepath = file_path
            self.inp_load_file.setText(file_path)
            fname = os.path.basename(file_path)
            self.lbl_load_summary.setText(f"✓ Berkas terdeteksi: {fname} • 4 objek • Baseline Bidang Tanah")
            
            # Populate preview table
            self.loaded_records = [
                {'id': 'BDG-3404-00120', 'nib': '12.01.04.01.00120', 'pemegang': 'Ahmad Fauzi', 'jenis_hak': 'Hak Milik', 'luas': 412.50},
                {'id': 'BDG-3404-00121', 'nib': '12.01.04.01.00121', 'pemegang': 'Nur Hidayah', 'jenis_hak': 'Hak Guna Bangunan', 'luas': 520.00},
                {'id': 'BDG-3404-00122', 'nib': '12.01.04.01.00122', 'pemegang': 'PT Mega Pratama', 'jenis_hak': 'Hak Pakai', 'luas': 1250.00},
                {'id': 'BDG-3404-00123', 'nib': '12.01.04.01.00123', 'pemegang': 'Yayasan Abadi', 'jenis_hak': 'Hak Wakaf', 'luas': 890.00},
            ]
            self.table_loaded_parcels.setRowCount(len(self.loaded_records))
            for row, r in enumerate(self.loaded_records):
                self.table_loaded_parcels.setItem(row, 0, QTableWidgetItem(r['id']))
                self.table_loaded_parcels.setItem(row, 1, QTableWidgetItem(r['nib']))
                self.table_loaded_parcels.setItem(row, 2, QTableWidgetItem(r['pemegang']))
                self.table_loaded_parcels.setItem(row, 3, QTableWidgetItem(r['jenis_hak']))
                self.table_loaded_parcels.setItem(row, 4, QTableWidgetItem(f"{r['luas']:.2f}"))

    def _on_reset_load(self):
        self.loaded_filepath = ''
        self.inp_load_file.clear()
        self.lbl_load_summary.clear()
        self.table_loaded_parcels.setRowCount(0)

    def _on_execute_load_to_qgis(self):
        if not self.loaded_filepath:
            self._on_browse_load_file()
            if not self.loaded_filepath:
                return

        fname = os.path.basename(self.loaded_filepath)
        layer_name = f"Derivatif - {os.path.splitext(fname)[0]}"
        try:
            from qgis.core import QgsProject, QgsVectorLayer
            layer = QgsVectorLayer(self.loaded_filepath, layer_name, 'ogr')
            if not layer.isValid():
                plugin_dir = os.path.dirname(os.path.abspath(__file__))
                fallback_path = os.path.join(plugin_dir, 'indonesia-kabupaten.geojson')
                layer = QgsVectorLayer(fallback_path, layer_name, 'ogr')

            if layer.isValid():
                for old in QgsProject.instance().mapLayersByName(layer_name):
                    QgsProject.instance().removeMapLayer(old.id())
                QgsProject.instance().addMapLayer(layer)
                if self.iface and hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                    self.iface.mapCanvas().setExtent(layer.extent())
                    self.iface.mapCanvas().refresh()
                if self.iface and hasattr(self.iface, 'messageBar') and self.iface.messageBar():
                    self.iface.messageBar().pushSuccess(
                        "Layer Derivatif Dimuat",
                        f"Layer '{layer_name}' berhasil divisualisasikan ke kanvas peta QGIS."
                    )
        except Exception:
            pass

        QMessageBox.information(
            self,
            "Layer Derivatif Dimuat",
            f"Berkas '{fname}' berhasil dimuat ke kanvas peta QGIS dan visualisasi poligon bidang diaktifkan!"
        )
        self.accept()

    def _on_browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Pilih Folder Penyimpanan', self.folder_input.text())
        if folder:
            self.folder_input.setText(folder)

    def _on_save_derivatif(self):
        filename = self.filename_input.text().strip() or 'derivatif_output'
        folder = self.folder_input.text().strip() or os.getcwd()
        fmt_id = self.radio_group.checkedId()
        ext = '.gpkg' if fmt_id == 0 else '.geojson' if fmt_id == 1 else '.shp'
        full_path = os.path.join(folder, f"{filename}{ext}")

        for r in self.records:
            r['status'] = 'Sudah Tersimpan'
        self._render_table()

        data_payload = {
            'id': f"AJU-2026-DERIV-{len(self.records)}",
            'category': 'derivatif',
            'name': self.layer_combo.currentText(),
            'satker': 'Ditjen SPPR',
            'date': QDate.currentDate().toString('dd MMM yyyy'),
            'status': 'Diproses',
            'note': f"Ekspor {len(self.records)} bidang · {full_path}",
            'scope': 'Kabupaten Sleman',
        }
        self.derivatifSaved.emit(data_payload)

        QMessageBox.information(
            self,
            'Derivatif Disimpan',
            f"Dataset derivatif per bidang berhasil diekspor!\n\n"
            f"Berkas: {full_path}\n"
            f"Jumlah Rekord: {len(self.records)} bidang\n\n"
            f"Data telah didaftarkan ke antrean Manajemen IGT Derivatif Multiguna."
        )
        self.accept()


class LoadDerivatifDialog(QDialog):
    """Dialog popup untuk memuat berkas Kustom Tematik Derivatif ke dalam kanvas peta QGIS."""

    layerLoaded = pyqtSignal(str)

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.selected_file_path = ''
        self.setWindowTitle('Muat Kustom Tematik Derivatif')
        self.resize(520, 380)
        self.setModal(True)
        self.setObjectName('loadDerivatifDialog')
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog#loadDerivatifDialog {
                background-color: #ffffff;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 1. Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel('Muat Kustom Tematik Derivatif', self)
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #0f294d;")
        desc = QLabel('Pilih berkas atribut atau layer tematik derivatif untuk dimuat ke QGIS.', self)
        desc.setStyleSheet("font-size: 11.5px; color: #64748b;")
        header.addWidget(title)
        header.addWidget(desc)
        layout.addLayout(header)

        # 2. File Dropzone Box
        dropzone = QFrame(self)
        dropzone.setCursor(Qt.CursorShape.PointingHandCursor)
        dropzone.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 2px dashed #93c5fd;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                background-color: #eff6ff;
                border-color: #3b82f6;
            }
        """)
        dz_layout = QVBoxLayout(dropzone)
        dz_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dz_layout.setSpacing(10)

        icon_lbl = QLabel(dropzone)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setPixmap(svg_pixmap(ICONS['layers'].format(color='#1f6fd6'), QSize(36, 36)))
        dz_layout.addWidget(icon_lbl)

        txt_main = QLabel('Pilih berkas Kustom Tematik Derivatif', dropzone)
        txt_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_main.setStyleSheet("font-size: 13px; font-weight: 700; color: #1e293b; background: transparent; border: none;")
        dz_layout.addWidget(txt_main)

        txt_sub = QLabel('Format GeoPackage (.gpkg), JSON (.json, .geojson), atau Shapefile (.shp, .zip)', dropzone)
        txt_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_sub.setStyleSheet("font-size: 11px; color: #64748b; background: transparent; border: none;")
        dz_layout.addWidget(txt_sub)

        btn_pick = QPushButton('Pilih Berkas dari Komputer', dropzone)
        btn_pick.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick.setStyleSheet("""
            QPushButton {
                background-color: #1f6fd6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 7px 16px;
                font-size: 11.5px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        btn_pick.clicked.connect(self._on_pick_file)
        dz_layout.addWidget(btn_pick, 0, Qt.AlignmentFlag.AlignCenter)

        self.picked_file_lbl = QLabel(dropzone)
        self.picked_file_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picked_file_lbl.setStyleSheet("""
            QLabel {
                color: #059669;
                font-size: 11.5px;
                font-weight: 700;
                background-color: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                padding: 4px 10px;
            }
        """)
        self.picked_file_lbl.setVisible(False)
        dz_layout.addWidget(self.picked_file_lbl)

        layout.addWidget(dropzone)

        # 3. Actions Row
        actions = QHBoxLayout()
        actions.setSpacing(10)

        btn_cancel = QPushButton('Batal', self)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #1e293b;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        actions.addStretch()

        self.btn_confirm = QPushButton('Muat ke Kanvas QGIS →', self)
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #1f6fd6;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        self.btn_confirm.clicked.connect(self._on_confirm_load)
        actions.addWidget(self.btn_confirm)

        layout.addLayout(actions)

    def _on_pick_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih Berkas Kustom Tematik Derivatif",
            "",
            "Berkas Spasial (*.gpkg *.geojson *.json *.shp *.zip);;Semua Berkas (*.*)"
        )
        if file_path:
            self.selected_file_path = file_path
            name = os.path.basename(file_path)
            self.picked_file_lbl.setText(f"✓ Berkas dipilih: {name}")
            self.picked_file_lbl.setVisible(True)

    def _on_confirm_load(self):
        if not self.selected_file_path:
            self._on_pick_file()
            if not self.selected_file_path:
                return

        file_path = self.selected_file_path
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        layer_name = f"Derivatif - {base_name}"

        # Load into QGIS
        try:
            from qgis.core import QgsProject, QgsVectorLayer
            layer = QgsVectorLayer(file_path, layer_name, 'ogr')
            if not layer.isValid():
                # Fallback jika parsing gagal, coba path geojson internal
                plugin_dir = os.path.dirname(os.path.abspath(__file__))
                fallback_path = os.path.join(plugin_dir, 'indonesia-kabupaten.geojson')
                layer = QgsVectorLayer(fallback_path, layer_name, 'ogr')

            if layer.isValid():
                for old in QgsProject.instance().mapLayersByName(layer_name):
                    QgsProject.instance().removeMapLayer(old.id())
                QgsProject.instance().addMapLayer(layer)
                if self.iface and hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                    self.iface.mapCanvas().setExtent(layer.extent())
                    self.iface.mapCanvas().refresh()
                if self.iface and hasattr(self.iface, 'messageBar') and self.iface.messageBar():
                    self.iface.messageBar().pushSuccess(
                        "Layer Derivatif Dimuat",
                        f"Layer '{layer_name}' berhasil dimuat ke kanvas QGIS."
                    )
        except Exception as e:
            QMessageBox.information(
                self,
                "Layer Derivatif Dimuat",
                f"Simulasi: Berkas '{base_name}' berhasil dimuat ke kanvas QGIS.\n\nDetail: {e}"
            )

        self.layerLoaded.emit(layer_name)
        self.accept()


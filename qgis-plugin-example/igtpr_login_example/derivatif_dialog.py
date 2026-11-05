# -*- coding: utf-8 -*-
"""Dialog Derivatif Per Bidang (Mockup V2)."""

import os
import json
from qgis.PyQt.QtCore import QDate, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QButtonGroup, QComboBox, QDateEdit, QDialog, QDoubleSpinBox, QFileDialog,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMessageBox, QPushButton, QRadioButton, QScrollArea, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .login_page import svg_pixmap


class DerivatifBidangDialog(QDialog):
    """Dialog Derivatif Per Bidang untuk pengisian data atribut tematik kustom."""

    derivatifSaved = pyqtSignal(dict)

    def __init__(self, iface=None, parent=None):
        super().__init__(parent)
        self.iface = iface
        self.setWindowTitle('Derivatif Per Bidang')
        self.resize(680, 800)
        self.setObjectName('derivatifBidangDialog')

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
                padding: 14px 16px;
            }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                background-color: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11.5px;
                color: #0f294d;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
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
        layout.setSpacing(12)

        # 1. Header & Navigation
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

        mode_badge = QLabel('Mode: Isi Tematik', self)
        mode_badge.setStyleSheet("""
            background-color: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            font-size: 10.5px;
            font-weight: 700;
            padding: 3px 10px;
        """)
        head_layout.addWidget(mode_badge)
        head_layout.addStretch()
        layout.addLayout(head_layout)

        # Tabs: Isi Tematik | + Create Tematik | Load Tematik
        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        for t_label, is_act in [('Isi Tematik', True), ('+ Create Tematik', False), ('Load Tematik', False)]:
            btn = QPushButton(t_label, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if t_label == 'Load Tematik':
                btn.clicked.connect(self._open_load_derivatif)
            if is_act:
                btn.setStyleSheet("""
                    background-color: #0f294d;
                    color: #ffffff;
                    border: none;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-weight: 700;
                    font-size: 11px;
                """)
            else:
                btn.setStyleSheet("""
                    background-color: #ffffff;
                    color: #475569;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-weight: 600;
                    font-size: 11px;
                """)
            tab_row.addWidget(btn)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        # Scrollable Form Content
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

        chip = QLabel('Basis: Bidang | 21 Kolom CMS, Tanpa keterangan', s1)
        chip.setStyleSheet("""
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 600;
            padding: 5px 8px;
        """)
        s1_row.addWidget(chip)
        s1_layout.addLayout(s1_row)

        wms_row = QHBoxLayout()
        wms_row.setSpacing(8)
        self.btn_load_wms = QPushButton('Muat Baseline WMS Bidang', s1)
        self.btn_load_wms.setObjectName('actionBtn')
        self.btn_load_wms.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load_wms.clicked.connect(self._on_load_wms_clicked)
        wms_row.addWidget(self.btn_load_wms)

        self.wms_status_lbl = QLabel('Baseline WMS: Belum dimuat', s1)
        self.wms_status_lbl.setStyleSheet("color: #b45309; font-size: 11px; font-weight: 700;")
        wms_row.addWidget(self.wms_status_lbl)
        wms_row.addStretch()
        s1_layout.addLayout(wms_row)

        hint_wms = QLabel('Buka layer atau klik bidang tanah pada WMS di peta QGIS.', s1)
        hint_wms.setStyleSheet("color: #64748b; font-size: 10.5px; font-style: italic;")
        s1_layout.addWidget(hint_wms)
        c_layout.addWidget(s1)

        # ------------------------------------------------------------------ Section 2
        s2 = QFrame(content)
        s2.setProperty('class', 'sectionCard')
        s2_layout = QVBoxLayout(s2)
        s2_layout.setSpacing(8)

        s2_head_row = QHBoxLayout()
        s2_head = QLabel('2. Klik Bidang di Peta & Isi Nilai Tematik:', s2)
        s2_head.setStyleSheet("color: #0f294d; font-size: 12.5px; font-weight: 800;")
        s2_head_row.addWidget(s2_head)
        s2_head_row.addStretch()

        id_row = QHBoxLayout()
        id_row.setSpacing(4)
        id_lbl = QLabel('ID Bidang:', s2)
        id_lbl.setStyleSheet("color: #475569; font-size: 11px; font-weight: 700;")
        id_row.addWidget(id_lbl)
        self.id_input = QLineEdit(f"BDG-3404-00{self.current_id_counter}", s2)
        self.id_input.setFixedWidth(140)
        id_row.addWidget(self.id_input)
        s2_head_row.addLayout(id_row)
        s2_layout.addLayout(s2_head_row)

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

        # Specialized combo / date fields
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

        # Button Isi Bidang Lain
        btn_add = QPushButton('+ Isi Bidang Lain', s2)
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

        # Format Radio Buttons
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
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 8px 12px;
        """)
        nb_layout = QHBoxLayout(notice_box)
        nb_layout.setContentsMargins(0, 0, 0, 0)
        nb_lbl = QLabel(
            "ℹ Hanya atribut data yang disimpan (tanpa geometri baseline). Sesi akan direset setelah disimpan.",
            notice_box)
        nb_lbl.setStyleSheet("color: #1e40af; font-size: 11px;")
        nb_layout.addWidget(nb_lbl)
        s4_layout.addWidget(notice_box)

        # Simpan Derivatif Button
        save_btn = QPushButton('💾 Simpan Derivatif', s4)
        save_btn.setObjectName('saveBtn')
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._on_save_derivatif)
        s4_layout.addWidget(save_btn)

        c_layout.addWidget(s4)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self._render_table()

    def _on_load_wms_clicked(self):
        self.wms_status_lbl.setText('Baseline WMS: Terpasang di QGIS (Aktif)')
        self.wms_status_lbl.setStyleSheet("color: #047857; font-size: 11px; font-weight: 800;")
        if self.iface and hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'Baseline WMS Dimuat',
                'Layer WMS Bidang Tanah berhasil dimuat ke kanvas QGIS. Klik bidang tanah pada peta untuk memilih ID Bidang.'
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
        self._render_table()

    def _render_table(self):
        self.table.setRowCount(len(self.records))
        baru_count = len([r for r in self.records if r.get('status') == 'Baru Diisi'])
        saved_count = len([r for r in self.records if r.get('status') == 'Sudah Tersimpan'])

        self.badge_baru.setText(f"Baru Diisi: {baru_count} bidang")
        self.badge_tersimpan.setText(f"Sudah Tersimpan: {saved_count} bidang")

        for row, r in enumerate(self.records):
            # ID Bidang
            item_id = QTableWidgetItem(r['id'])
            item_id.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.table.setItem(row, 0, item_id)

            # NIB
            self.table.setItem(row, 1, QTableWidgetItem(r.get('nib', '—')))

            # Pemegang
            self.table.setItem(row, 2, QTableWidgetItem(r.get('pemegang', '—')))

            # Jenis Hak
            self.table.setItem(row, 3, QTableWidgetItem(r.get('jenis_hak', '—')))

            # Luas
            luas_str = f"{r.get('luas', 0):.2f}"
            self.table.setItem(row, 4, QTableWidgetItem(luas_str))

            # Delete button
            del_btn = QPushButton('Hapus')
            del_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fee2e2;
                    color: #b91c1c;
                    border: 1px solid #fca5a5;
                    border-radius: 4px;
                    font-size: 10px;
                    padding: 2px 6px;
                }
                QPushButton:hover {
                    background-color: #fecaca;
                }
            """)
            del_btn.clicked.connect(lambda checked, idx=row: self._delete_record(idx))
            self.table.setCellWidget(row, 5, del_btn)

    def _delete_record(self, idx):
        if 0 <= idx < len(self.records):
            self.records.pop(idx)
            self._render_table()

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

        # Mark all as saved
        for r in self.records:
            r['status'] = 'Sudah Tersimpan'
        self._render_table()

        data_payload = {
            'id': f"AJU-2026-DERIV-{len(self.records)}",
            'category': 'derivatif',
            'name': self.layer_combo.currentText(),
            'satker': 'Ditjen SPPR',
            'date': '01 Nov 2026',
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

    def _open_load_derivatif(self):
        dlg = LoadDerivatifDialog(iface=self.iface, parent=self)
        dlg.exec_()


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


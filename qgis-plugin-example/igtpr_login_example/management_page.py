# -*- coding: utf-8 -*-
"""Halaman Manajemen Data (Mockup V2) dengan tab status dan alur persetujuan."""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS, SUBMISSIONS
from .login_page import svg_pixmap

STATUS_COLORS = {
    'Terintegrasi': {'bg': '#ecfdf5', 'border': '#a7f3d0', 'color': '#047857'},
    'Terkompilasi': {'bg': '#fffbeb', 'border': '#fde68a', 'color': '#b45309'},
    'Diajukan':     {'bg': '#eff6ff', 'border': '#bfdbfe', 'color': '#1d4ed8'},
    'Revisi':       {'bg': '#fef2f2', 'border': '#fecaca', 'color': '#b91c1c'},
    'Disetujui':    {'bg': '#ecfdf5', 'border': '#a7f3d0', 'color': '#047857'},
    'Ditolak':      {'bg': '#fef2f2', 'border': '#fecaca', 'color': '#b91c1c'},
}

# Definisi skema kolom tabel manajemen data untuk perulangan (looping) dinamis
MANAGEMENT_TABLE_COLUMNS = [
    {'key': 'id',      'title': 'ID Pengajuan',       'resize': QHeaderView.ResizeMode.ResizeToContents},
    {'key': 'layer',   'title': 'Layer Target',       'resize': QHeaderView.ResizeMode.Stretch},
    {'key': 'org',     'title': 'Satker / Direktorat','resize': QHeaderView.ResizeMode.Interactive, 'width': 220},
    {'key': 'date',    'title': 'Tanggal',            'resize': QHeaderView.ResizeMode.ResizeToContents},
    {'key': 'status',  'title': 'Status',             'resize': QHeaderView.ResizeMode.Fixed, 'width': 110},
    {'key': 'actions', 'title': 'Aksi',               'resize': QHeaderView.ResizeMode.Fixed, 'width': 200},
]


class StatusBadge(QLabel):
    """Badge status pengajuan data."""

    def __init__(self, status_text, parent=None):
        super().__init__(parent)
        self.setText(status_text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme = STATUS_COLORS.get(status_text, {'bg': '#f1f5f9', 'border': '#cbd5e1', 'color': '#475569'})
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {theme['bg']};
                border: 1px solid {theme['border']};
                border-radius: 6px;
                color: {theme['color']};
                font-size: 11px;
                font-weight: 700;
                padding: 3px 8px;
            }}
        """)


class ManagementPage(QWidget):
    """Halaman Manajemen Data V2 dengan alur kerja Kompilasi, Verifikasi, dan Persetujuan."""

    backToDashboardRequested = pyqtSignal()
    showLayerRequested = pyqtSignal(dict)
    actionPerformed = pyqtSignal(str, dict)  # action_name, submission_record

    def __init__(self, current_category='igt-utama', current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_category = current_category
        self.current_role = current_role
        self.current_status_tab = 'Diajukan' if current_role in ('superadmin', 'admin') else 'Semua'
        self.setObjectName('managementPage')

        self.submissions = list(SUBMISSIONS)  # local mutable copy for interactive simulation

        self.setStyleSheet("""
            QWidget#managementPage {
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
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 12px;
                font-size: 12px;
                gridline-color: #f1f5f9;
                outline: none;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: 700;
                font-size: 11.5px;
                border: none;
                border-bottom: 1.5px solid #e2e8f0;
                padding: 9px 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Header (Title, Desc, Back Button)
        head_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_lbl = QLabel('Manajemen IGT Utama', self)
        self.title_lbl.setStyleSheet("color: #0f294d; font-size: 18px; font-weight: 800;")
        text_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel('Pantau proses kompilasi, perbaikan revisi, dan persetujuan integrasi data.', self)
        self.desc_lbl.setStyleSheet("color: #64748b; font-size: 11.5px;")
        text_layout.addWidget(self.desc_lbl)
        head_layout.addLayout(text_layout, 1)

        back_btn = QPushButton('← Kembali ke Dashboard', self)
        back_btn.setObjectName('backBtn')
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.backToDashboardRequested.emit)
        head_layout.addWidget(back_btn)

        layout.addLayout(head_layout)

        # 2. Category Tabs (IGT Utama, IGT Derivatif Multiguna)
        self.cat_nav_layout = QHBoxLayout()
        self.cat_nav_layout.setSpacing(8)
        self.cat_buttons = {}
        layout.addLayout(self.cat_nav_layout)

        # 3. Stats Summary Cards
        self._build_stats_summary(layout)

        # 4. Status Filter Tabs
        self.status_nav_layout = QHBoxLayout()
        self.status_nav_layout.setSpacing(6)
        self.status_buttons = {}
        layout.addLayout(self.status_nav_layout)

        # 5. Table Submissions (Konfigurasi kolom menggunakan looping dari MANAGEMENT_TABLE_COLUMNS)
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(MANAGEMENT_TABLE_COLUMNS))
        self.table.setHorizontalHeaderLabels([col['title'] for col in MANAGEMENT_TABLE_COLUMNS])
        header = self.table.horizontalHeader()
        for idx, col in enumerate(MANAGEMENT_TABLE_COLUMNS):
            header.setSectionResizeMode(idx, col['resize'])
            if 'width' in col:
                self.table.setColumnWidth(idx, col['width'])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        layout.addWidget(self.table, 1)

        self._update_category_nav()
        self.set_category('derivatif' if current_role == 'umum' else current_category)

    def _build_stats_summary(self, parent_layout):
        grid = QGridLayout()
        grid.setSpacing(10)

        self.stat_boxes = {}
        labels = [
            ('total', 'Total Pengajuan', '#1e293b', '#f1f5f9', '#cbd5e1'),
            ('process', 'Dalam Proses', '#1d4ed8', '#eff6ff', '#bfdbfe'),
            ('waiting', 'Menunggu Integrasi', '#b45309', '#fffbeb', '#fde68a'),
        ]

        for col, (k, title, color, bg, border) in enumerate(labels):
            box = QFrame(self)
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px solid {border};
                    border-radius: 10px;
                    padding: 8px 12px;
                }}
            """)
            b_layout = QVBoxLayout(box)
            b_layout.setContentsMargins(4, 2, 4, 2)
            b_layout.setSpacing(2)

            t_lbl = QLabel(title.upper(), box)
            t_lbl.setStyleSheet(f"color: {color}; font-size: 9.5px; font-weight: 800; letter-spacing: 0.5px;")
            b_layout.addWidget(t_lbl)

            num_lbl = QLabel('0', box)
            num_lbl.setStyleSheet(f"color: #0f294d; font-size: 18px; font-weight: 900;")
            b_layout.addWidget(num_lbl)

            grid.addWidget(box, 0, col)
            self.stat_boxes[k] = num_lbl

        parent_layout.addLayout(grid)

    def set_role(self, role_id):
        self.current_role = role_id
        self._update_category_nav()
        if self.current_role == 'umum' and self.current_category != 'derivatif':
            self.current_category = 'derivatif'
        self.set_category(self.current_category)

    def _update_category_nav(self):
        while self.cat_nav_layout.count():
            item = self.cat_nav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.cat_buttons.clear()

        cats = []
        if self.current_role != 'umum':
            cats.append(('igt-utama', 'IGT Utama'))
        cats.append(('derivatif', 'IGT Derivatif Multiguna'))

        for c_id, c_lbl in cats:
            btn = QPushButton(c_lbl, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=c_id: self.set_category(k))
            self.cat_nav_layout.addWidget(btn)
            self.cat_buttons[c_id] = btn

        self.cat_nav_layout.addStretch()
        self._style_category_nav()

    def _style_category_nav(self):
        for cid, btn in self.cat_buttons.items():
            if cid == self.current_category:
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

    def set_category(self, cat_id):
        if self.current_role == 'umum':
            cat_id = 'derivatif'
        elif cat_id not in ('igt-utama', 'derivatif'):
            cat_id = 'igt-utama'

        self.current_category = cat_id
        self._style_category_nav()

        # Update Titles
        if cat_id == 'igt-utama':
            self.title_lbl.setText('Manajemen IGT Utama')
            self.desc_lbl.setText('Pantau status kompilasi, revisi, dan verifikasi integrasi IGT Pertanahan & IGT Tata Ruang.')
        else:
            self.title_lbl.setText('Manajemen IGT Derivatif Multiguna')
            self.desc_lbl.setText('Pantau pengajuan dan persetujuan layer IGT Derivatif Multiguna hasil analisis spasial.')

        # Reset status tab for selected category
        if cat_id == 'igt-utama':
            self.current_status_tab = 'Cek Topologi' if self.current_role in ('superadmin', 'admin') else 'Revisi'
        elif cat_id == 'derivatif':
            self.current_status_tab = 'Diproses' if self.current_role in ('superadmin', 'admin') else 'Semua'
        else:
            self.current_status_tab = 'Semua'

        self._update_status_nav()
        self._render_table()

    def _update_status_nav(self):
        # Clear existing buttons
        while self.status_nav_layout.count():
            item = self.status_nav_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.status_buttons.clear()

        if self.current_category == 'igt-utama':
            if self.current_role in ('superadmin', 'admin'):
                tabs = ['Cek Topologi', 'Diajukan', 'Revisi']
            else:
                tabs = ['Revisi', 'Diajukan', 'Terkompilasi', 'Terintegrasi', 'Semua']
        elif self.current_category == 'derivatif':
            tabs = ['Diproses', 'Disetujui', 'Semua']
        else:
            tabs = ['Semua']

        for tab_name in tabs:
            btn = QPushButton(tab_name, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=tab_name: self._set_status_tab(t))
            self.status_nav_layout.addWidget(btn)
            self.status_buttons[tab_name] = btn

        self.status_nav_layout.addStretch()
        self._style_status_nav()
        self._style_status_nav()

    def _set_status_tab(self, tab_name):
        self.current_status_tab = tab_name
        self._style_status_nav()
        self._render_table()

    def _style_status_nav(self):
        for t_name, btn in self.status_buttons.items():
            if t_name == self.current_status_tab:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0f294d;
                        color: #ffffff;
                        border: none;
                        border-radius: 6px;
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
                        border-radius: 6px;
                        padding: 5px 12px;
                        font-weight: 600;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                    }
                """)

    def _render_table(self):
        # Filter records by category
        if self.current_category == 'igt-utama':
            recs = [s for s in self.submissions if s.get('category') in ('pertanahan', 'tata-ruang')]
        elif self.current_category == 'derivatif':
            recs = [s for s in self.submissions if s.get('category') == 'derivatif']
        else:
            recs = [s for s in self.submissions if s.get('category') == 'lainnya']

        # Update stats
        total = len(recs)
        process = len([r for r in recs if r.get('status') in ('Diajukan', 'Proses', 'Diproses')])
        waiting = len([r for r in recs if r.get('status') == 'Terkompilasi'])

        self.stat_boxes['total'].setText(str(total))
        self.stat_boxes['process'].setText(str(process))
        self.stat_boxes['waiting'].setText(str(waiting))

        # Filter records by status tab
        if self.current_status_tab != 'Semua':
            if self.current_status_tab == 'Cek Topologi':
                filtered = [r for r in recs if r.get('status') == 'Terkompilasi']
            elif self.current_status_tab == 'Diproses':
                filtered = [r for r in recs if r.get('status') in ('Diajukan', 'Proses', 'Diproses')]
            elif self.current_status_tab == 'Diajukan':
                filtered = [r for r in recs if r.get('status') in ('Diajukan', 'Proses')]
            else:
                filtered = [r for r in recs if r.get('status') == self.current_status_tab]
        else:
            filtered = recs

        # Dynamic Org header
        org_header = 'Instansi' if self.current_category == 'lainnya' else 'Direktorat' if self.current_status_tab == 'Terintegrasi' else 'Satker'
        self.table.horizontalHeaderItem(2).setText(org_header)

        # Hapus (sembunyikan) kolom tanggal pada manajemen data IGT Utama untuk admin dan superadmin
        is_reviewer_main = (self.current_category == 'igt-utama' and self.current_role in ('superadmin', 'admin'))
        self.table.setColumnHidden(3, is_reviewer_main)
        if not is_reviewer_main:
            date_header = 'Tanggal Terintegrasi' if self.current_status_tab == 'Terintegrasi' else 'Tanggal Disetujui' if self.current_category == 'derivatif' else 'Tanggal Unggah'
            self.table.horizontalHeaderItem(3).setText(date_header)

        self.table.setRowCount(len(filtered))
        for row, r in enumerate(filtered):
            # LOOPING KOLOM: Memetakan setiap kolom secara dinamis dari definisi skema
            for col_idx, col_def in enumerate(MANAGEMENT_TABLE_COLUMNS):
                col_key = col_def['key']

                if col_key == 'id':
                    id_item = QTableWidgetItem(r.get('id', ''))
                    id_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                    id_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    self.table.setItem(row, col_idx, id_item)

                elif col_key == 'layer':
                    name_widget = QWidget()
                    nw_layout = QVBoxLayout(name_widget)
                    nw_layout.setContentsMargins(6, 4, 6, 4)
                    nw_layout.setSpacing(2)
                    layer_name = r.get('name') or r.get('layer', '')
                    n_lbl = QLabel(layer_name)
                    n_lbl.setStyleSheet("color: #0f294d; font-weight: 700; font-size: 12px;")
                    nw_layout.addWidget(n_lbl)
                    if r.get('note'):
                        note_lbl = QLabel(r['note'])
                        note_lbl.setStyleSheet("color: #64748b; font-size: 10.5px;")
                        nw_layout.addWidget(note_lbl)
                    self.table.setCellWidget(row, col_idx, name_widget)

                elif col_key == 'org':
                    org_text = (r.get('direktorat') if self.current_status_tab == 'Terintegrasi' else r.get('satker')) or r.get('instansi') or r.get('source') or '—'
                    org_lbl = QLabel(org_text)
                    org_lbl.setWordWrap(True)
                    org_lbl.setStyleSheet("color: #334155; font-size: 11px;")
                    self.table.setCellWidget(row, col_idx, org_lbl)

                elif col_key == 'date':
                    date_item = QTableWidgetItem(r.get('date', ''))
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                    date_item.setForeground(QColor('#64748b'))
                    self.table.setItem(row, col_idx, date_item)

                elif col_key == 'status':
                    status_widget = QWidget()
                    sw_layout = QHBoxLayout(status_widget)
                    sw_layout.setContentsMargins(4, 4, 4, 4)
                    badge = StatusBadge(r.get('status', ''))
                    sw_layout.addWidget(badge)
                    sw_layout.addStretch()
                    self.table.setCellWidget(row, col_idx, status_widget)

                elif col_key == 'actions':
                    actions_widget = self._create_actions_widget(r)
                    self.table.setCellWidget(row, col_idx, actions_widget)

            self.table.setRowHeight(row, 54)

    def _create_actions_widget(self, record):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        status = record.get('status')
        role = self.current_role
        is_reviewer = role in ('superadmin', 'admin')

        # Action: Cek Topologi (for Terkompilasi by reviewer)
        if is_reviewer and status == 'Terkompilasi':
            btn = QPushButton('Cek Topologi')
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #eff6ff;
                    color: #1f6fd6;
                    border: 1px solid #93c5fd;
                    border-radius: 6px;
                    font-size: 10.5px;
                    font-weight: 700;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background-color: #dbeafe;
                }
            """)
            btn.clicked.connect(lambda checked, rec=record: self._on_verify_topology(rec))
            layout.addWidget(btn)

        # Action: Perbaiki Revisi (hanya untuk operator saat status Revisi; superadmin & admin fokus cuma Cek Topologi)
        if role == 'operator' and status == 'Revisi':
            btn = QPushButton('Perbaiki Revisi')
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #fef2f2;
                    color: #b91c1c;
                    border: 1px solid #fecaca;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #fee2e2;
                }
            """)
            btn.clicked.connect(lambda checked, rec=record: self._on_repair_revision(rec))
            layout.addWidget(btn)

        # Action: Tampilkan Layer (Simulation in QGIS)
        btn_show = QPushButton('Tampilkan')
        btn_show.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_show.setStyleSheet("""
            QPushButton {
                background-color: #f8fafc;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 10.5px;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #0f294d;
            }
        """)
        btn_show.clicked.connect(lambda checked, rec=record: self.showLayerRequested.emit(rec))
        layout.addWidget(btn_show)

        layout.addStretch()
        return w

    # ------------------------------------------------------------------ Actions Simulation
    def _on_compile(self, record):
        record['status'] = 'Terkompilasi'
        self.actionPerformed.emit('compile', record)
        self._render_table()

    def _on_verify_topology(self, record):
        self.actionPerformed.emit('topology', record)

    def _on_approve_integration(self, record):
        record['status'] = 'Terintegrasi'
        self.actionPerformed.emit('approve-integration', record)
        self._render_table()

    def _on_repair_revision(self, record):
        from .upload_dialog import UploadIgtUtamaDialog
        cat = record.get('category', 'pertanahan')
        main_win = self.window()
        dlg = UploadIgtUtamaDialog(current_category=cat, iface=self.iface, record_to_revise=record, parent=main_win)
        if dlg.exec_() == QDialog.DialogCode.Accepted:
            record['status'] = 'Diajukan'
            self.actionPerformed.emit('revision-submitted', record)
            self._render_table()

    def minimumSizeHint(self):
        return QSize(200, 120)

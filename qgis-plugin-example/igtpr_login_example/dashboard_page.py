# -*- coding: utf-8 -*-
"""Halaman Beranda / Dashboard (Mockup V2: Feature-Based Card UI)."""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .data import CATEGORIES, DATASETS, ROLES, SUBMISSIONS
from .login_page import svg_pixmap


class HubItemButton(QPushButton):
    """Tombol item di dalam kartu hub beranda."""

    def __init__(self, icon_key, label_text, color='#1f6fd6', bg='#f0f9ff', border='#e0f2fe', parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 10px 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #ffffff;
                border-color: {color};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(10)

        # Icon
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(svg_pixmap(ICONS.get(icon_key, ICONS['layers']).format(color=color), QSize(20, 20)))
        layout.addWidget(icon_lbl)

        # Label
        lbl = QLabel(label_text, self)
        lbl.setStyleSheet(f"color: #0f294d; font-weight: 700; font-size: 12px;")
        layout.addWidget(lbl, 1)

        # Chevron arrow
        arrow_lbl = QLabel(self)
        arrow_lbl.setPixmap(svg_pixmap(ICONS['chevron-right'].format(color='#94a3b8'), QSize(14, 14)))
        layout.addWidget(arrow_lbl)


class DashboardPage(QWidget):
    """Halaman Dashboard V2 lengkap dengan Header Hero, Stat Cards, Katalog Hub, dan Alur Kerja."""

    openCatalogRequested = pyqtSignal(str)       # category_id ('pertanahan', 'tata-ruang', 'derivatif', 'lainnya')
    openManagementRequested = pyqtSignal(str)    # tab_id ('igt-utama', 'derivatif', 'lainnya')
    openUploadRequested = pyqtSignal(str)        # tab_id
    openModelBuilderRequested = pyqtSignal()
    logoutRequested = pyqtSignal()

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__(parent)
        self.current_role = current_role
        self.setObjectName('dashboardPage')

        self.setStyleSheet("""
            QWidget#dashboardPage {
                background-color: #f4f7fb;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area for responsive display in narrow docks
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(16, 16, 16, 20)
        self.content_layout.setSpacing(14)

        # 1. Header Hero Card + Year Filter
        self._build_hero_header()

        # 2. Stat Cards (Terkompilasi & Terintegrasi)
        self._build_stat_cards()

        # 3. Hub Card: Katalog IGT (Card UI)
        self._build_catalog_hub()

        # 4. Hub Cards Grid: Unggah Data & Manajemen Data
        self._build_workflow_hubs()

        # 5. Hub Card: Model Builder
        self._build_model_builder_hub()

        # 6. Logout Bar
        self._build_logout_bar()

        self.content_layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self._update_counts()

    def set_role(self, role_id):
        self.current_role = role_id
        self._update_counts()

    # ------------------------------------------------------------------ UI Sections
    def _build_hero_header(self):
        hero = QFrame(self)
        hero.setObjectName('heroHeader')
        hero.setStyleSheet("""
            QFrame#heroHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #102b59, stop:1 #1b4588);
                border-radius: 14px;
            }
        """)
        h_layout = QHBoxLayout(hero)
        h_layout.setContentsMargins(18, 16, 18, 16)
        h_layout.setSpacing(14)

        # Left Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        eyebrow = QLabel('SISTEM INFORMASI GEOSPASIAL', hero)
        eyebrow.setStyleSheet("""
            QLabel {
                background: rgba(255, 255, 255, 0.16);
                color: #bfdbfe;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.8px;
                padding: 3px 8px;
                border-radius: 8px;
            }
        """)
        text_layout.addWidget(eyebrow, 0, Qt.AlignmentFlag.AlignLeft)

        title = QLabel('Dashboard IGT-PR', hero)
        title.setStyleSheet("color: #ffffff; font-size: 19px; font-weight: 800; margin-top: 3px;")
        text_layout.addWidget(title)

        desc = QLabel('Ringkasan status data geospasial, katalog layer, dan pintasan alur kerja.', hero)
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1; font-size: 11.5px;")
        text_layout.addWidget(desc)

        h_layout.addLayout(text_layout, 1)

        # Right Year Filter Box
        year_box = QFrame(hero)
        year_box.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 10px;
                padding: 6px 10px;
            }
            QLabel {
                color: #bfdbfe;
                font-size: 9px;
                font-weight: 800;
                letter-spacing: 0.5px;
            }
            QComboBox {
                background: transparent;
                border: none;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                min-width: 95px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f294d;
                selection-background-color: #eff6ff;
                selection-color: #1f6fd6;
            }
        """)
        yb_layout = QVBoxLayout(year_box)
        yb_layout.setContentsMargins(4, 2, 4, 2)
        yb_layout.setSpacing(2)

        yb_label = QLabel('FILTER TAHUN', year_box)
        yb_layout.addWidget(yb_label)

        self.year_combo = QComboBox(year_box)
        self.year_combo.addItems(['Semua tahun', '2026', '2025', '2024', '2023'])
        self.year_combo.currentIndexChanged.connect(self._on_year_changed)
        yb_layout.addWidget(self.year_combo)

        h_layout.addWidget(year_box, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.content_layout.addWidget(hero)

    def _build_stat_cards(self):
        grid = QGridLayout()
        grid.setSpacing(12)

        # Stat 1: Terkompilasi (Amber)
        self.card_compiled = QFrame(self)
        self.card_compiled.setObjectName('statCompiled')
        self.card_compiled.setStyleSheet("""
            QFrame#statCompiled {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fffbeb, stop:1 #ffffff);
                border: 1.5px solid #fde68a;
                border-radius: 14px;
            }
        """)
        c_layout = QHBoxLayout(self.card_compiled)
        c_layout.setContentsMargins(14, 12, 14, 12)
        info1 = QVBoxLayout()
        info1.setSpacing(2)

        lbl1 = QLabel('TERKOMPILASI', self.card_compiled)
        lbl1.setStyleSheet("color: #78350f; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        info1.addWidget(lbl1)

        self.num_compiled = QLabel('13', self.card_compiled)
        self.num_compiled.setStyleSheet("color: #0f294d; font-size: 26px; font-weight: 900;")
        info1.addWidget(self.num_compiled)

        pill1 = QLabel('Menunggu integrasi', self.card_compiled)
        pill1.setStyleSheet("""
            background-color: #fef3c7;
            color: #b45309;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
        """)
        info1.addWidget(pill1, 0, Qt.AlignmentFlag.AlignLeft)
        c_layout.addLayout(info1, 1)

        badge1 = QLabel(self.card_compiled)
        badge1.setPixmap(svg_pixmap(ICONS['folder'].format(color='#d97706'), QSize(28, 28)))
        c_layout.addWidget(badge1, 0, Qt.AlignmentFlag.AlignVCenter)

        grid.addWidget(self.card_compiled, 0, 0)

        # Stat 2: Terintegrasi (Emerald)
        self.card_integrated = QFrame(self)
        self.card_integrated.setObjectName('statIntegrated')
        self.card_integrated.setStyleSheet("""
            QFrame#statIntegrated {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ecfdf5, stop:1 #ffffff);
                border: 1.5px solid #a7f3d0;
                border-radius: 14px;
            }
        """)
        i_layout = QHBoxLayout(self.card_integrated)
        i_layout.setContentsMargins(14, 12, 14, 12)
        info2 = QVBoxLayout()
        info2.setSpacing(2)

        lbl2 = QLabel('TERINTEGRASI', self.card_integrated)
        lbl2.setStyleSheet("color: #065f46; font-size: 10px; font-weight: 800; letter-spacing: 0.5px;")
        info2.addWidget(lbl2)

        self.num_integrated = QLabel('24', self.card_integrated)
        self.num_integrated.setStyleSheet("color: #0f294d; font-size: 26px; font-weight: 900;")
        info2.addWidget(self.num_integrated)

        pill2 = QLabel('Pertanahan & Tata Ruang', self.card_integrated)
        pill2.setStyleSheet("""
            background-color: #d1fae5;
            color: #047857;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 5px;
        """)
        info2.addWidget(pill2, 0, Qt.AlignmentFlag.AlignLeft)
        i_layout.addLayout(info2, 1)

        badge2 = QLabel(self.card_integrated)
        badge2.setPixmap(svg_pixmap(ICONS['check'].format(color='#059669'), QSize(28, 28)))
        i_layout.addWidget(badge2, 0, Qt.AlignmentFlag.AlignVCenter)

        grid.addWidget(self.card_integrated, 0, 1)

        self.content_layout.addLayout(grid)

    def _build_catalog_hub(self):
        hub = QFrame(self)
        hub.setObjectName('catalogHub')
        hub.setStyleSheet("""
            QFrame#catalogHub {
                background-color: #ffffff;
                border: 1.5px solid #bae6fd;
                border-radius: 14px;
            }
        """)
        h_layout = QVBoxLayout(hub)
        h_layout.setContentsMargins(0, 0, 0, 12)
        h_layout.setSpacing(10)

        # Head
        head = QFrame(hub)
        head.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f2fe, stop:1 #f0f9ff);
            border-bottom: 1px solid #bae6fd;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 10px 14px;
        """)
        head_layout = QHBoxLayout(head)
        head_layout.setContentsMargins(6, 4, 6, 4)
        head_layout.setSpacing(12)

        badge = QLabel(head)
        badge.setPixmap(svg_pixmap(ICONS['map'].format(color='#0284c7'), QSize(22, 22)))
        head_layout.addWidget(badge)

        head_text = QVBoxLayout()
        head_text.setSpacing(2)
        h_title = QLabel('Katalog IGT', head)
        h_title.setStyleSheet("color: #0f294d; font-size: 14px; font-weight: 800;")
        head_text.addWidget(h_title)

        h_desc = QLabel('Pilih kategori untuk menjelajahi dataset dan memuat layer WMS/WFS ke QGIS.', head)
        h_desc.setStyleSheet("color: #5b6f8a; font-size: 11px;")
        head_text.addWidget(h_desc)
        head_layout.addLayout(head_text, 1)

        h_layout.addWidget(head)

        # 4 Category Buttons (Grid)
        cat_grid = QGridLayout()
        cat_grid.setContentsMargins(12, 4, 12, 4)
        cat_grid.setSpacing(10)

        btn_pertanahan = HubItemButton('pin', 'IGT Pertanahan', color='#1f6fd6', bg='#eff6ff', border='#dbeafe', parent=hub)
        btn_pertanahan.clicked.connect(lambda: self.openCatalogRequested.emit('pertanahan'))
        cat_grid.addWidget(btn_pertanahan, 0, 0)

        btn_tataruang = HubItemButton('map', 'IGT Tata Ruang', color='#047857', bg='#ecfdf5', border='#d1fae5', parent=hub)
        btn_tataruang.clicked.connect(lambda: self.openCatalogRequested.emit('tata-ruang'))
        cat_grid.addWidget(btn_tataruang, 0, 1)

        btn_derivatif = HubItemButton('layers', 'IGT Derivatif Multiguna', color='#7c3aed', bg='#f5f3ff', border='#ede9fe', parent=hub)
        btn_derivatif.clicked.connect(lambda: self.openCatalogRequested.emit('derivatif'))
        cat_grid.addWidget(btn_derivatif, 1, 0)

        btn_lainnya = HubItemButton('globe', 'IGT Lainnya', color='#0284c7', bg='#f0f9ff', border='#e0f2fe', parent=hub)
        btn_lainnya.clicked.connect(lambda: self.openCatalogRequested.emit('lainnya'))
        cat_grid.addWidget(btn_lainnya, 1, 1)

        h_layout.addLayout(cat_grid)
        self.content_layout.addWidget(hub)

    def _build_workflow_hubs(self):
        wf_grid = QGridLayout()
        wf_grid.setSpacing(12)

        # 1. Card Unggah Data
        upload_card = QFrame(self)
        upload_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 14px;
            }
        """)
        u_layout = QVBoxLayout(upload_card)
        u_layout.setContentsMargins(14, 14, 14, 14)
        u_layout.setSpacing(10)

        # Header Unggah
        u_head = QHBoxLayout()
        u_head.setSpacing(10)
        u_badge = QLabel(upload_card)
        u_badge.setPixmap(svg_pixmap(ICONS['upload'].format(color='#1f6fd6'), QSize(20, 20)))
        u_head.addWidget(u_badge)

        u_titles = QVBoxLayout()
        u_titles.setSpacing(2)
        u_t = QLabel('Unggah Data', upload_card)
        u_t.setStyleSheet("color: #0f294d; font-size: 13.5px; font-weight: 800;")
        u_titles.addWidget(u_t)
        u_d = QLabel('Kelola dan unggah data geospasial.', upload_card)
        u_d.setStyleSheet("color: #64748b; font-size: 11px;")
        u_titles.addWidget(u_d)
        u_head.addLayout(u_titles, 1)
        u_layout.addLayout(u_head)

        # Buttons Unggah
        btn_u_utama = HubItemButton('database', 'Unggah IGT Utama', color='#1f6fd6', bg='#f8fafc', border='#e2e8f0', parent=upload_card)
        btn_u_utama.clicked.connect(lambda: self.openUploadRequested.emit('pertanahan'))
        u_layout.addWidget(btn_u_utama)

        btn_u_deriv = HubItemButton('layers', 'Unggah IGT Derivatif', color='#7c3aed', bg='#f8fafc', border='#e2e8f0', parent=upload_card)
        btn_u_deriv.clicked.connect(lambda: self.openUploadRequested.emit('derivatif'))
        u_layout.addWidget(btn_u_deriv)

        btn_u_custom = HubItemButton('gear', 'Kustom Tematik Derivatif', color='#059669', bg='#f8fafc', border='#e2e8f0', parent=upload_card)
        btn_u_custom.clicked.connect(self.openModelBuilderRequested.emit)
        u_layout.addWidget(btn_u_custom)

        wf_grid.addWidget(upload_card, 0, 0)

        # 2. Card Manajemen Data
        manage_card = QFrame(self)
        manage_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dce5ef;
                border-radius: 14px;
            }
        """)
        m_layout = QVBoxLayout(manage_card)
        m_layout.setContentsMargins(14, 14, 14, 14)
        m_layout.setSpacing(10)

        # Header Manajemen
        m_head = QHBoxLayout()
        m_head.setSpacing(10)
        m_badge = QLabel(manage_card)
        m_badge.setPixmap(svg_pixmap(ICONS['database'].format(color='#047857'), QSize(20, 20)))
        m_head.addWidget(m_badge)

        m_titles = QVBoxLayout()
        m_titles.setSpacing(2)
        m_t = QLabel('Manajemen Data', manage_card)
        m_t.setStyleSheet("color: #0f294d; font-size: 13.5px; font-weight: 800;")
        m_titles.addWidget(m_t)
        m_d = QLabel('Pantau pengajuan & status verifikasi.', manage_card)
        m_d.setStyleSheet("color: #64748b; font-size: 11px;")
        m_titles.addWidget(m_d)
        m_head.addLayout(m_titles, 1)
        m_layout.addLayout(m_head)

        # Buttons Manajemen
        btn_m_utama = HubItemButton('database', 'IGT Utama', color='#1f6fd6', bg='#f8fafc', border='#e2e8f0', parent=manage_card)
        btn_m_utama.clicked.connect(lambda: self.openManagementRequested.emit('igt-utama'))
        m_layout.addWidget(btn_m_utama)

        btn_m_deriv = HubItemButton('layers', 'IGT Derivatif Multiguna', color='#7c3aed', bg='#f8fafc', border='#e2e8f0', parent=manage_card)
        btn_m_deriv.clicked.connect(lambda: self.openManagementRequested.emit('derivatif'))
        m_layout.addWidget(btn_m_deriv)

        btn_m_lainnya = HubItemButton('globe', 'IGT Lainnya', color='#0284c7', bg='#f8fafc', border='#e2e8f0', parent=manage_card)
        btn_m_lainnya.clicked.connect(lambda: self.openManagementRequested.emit('lainnya'))
        m_layout.addWidget(btn_m_lainnya)

        wf_grid.addWidget(manage_card, 0, 1)

        self.content_layout.addLayout(wf_grid)

    def _build_model_builder_hub(self):
        mb_card = QPushButton(self)
        mb_card.setObjectName('mbCard')
        mb_card.setCursor(Qt.CursorShape.PointingHandCursor)
        mb_card.clicked.connect(self.openModelBuilderRequested.emit)
        mb_card.setStyleSheet("""
            QPushButton#mbCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f5f3ff, stop:1 #ffffff);
                border: 1.5px solid #ddd6fe;
                border-radius: 14px;
                padding: 14px 16px;
                text-align: left;
            }
            QPushButton#mbCard:hover {
                border-color: #7c3aed;
                background-color: #faf5ff;
            }
        """)

        layout = QHBoxLayout(mb_card)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(12)

        badge = QLabel(mb_card)
        badge.setPixmap(svg_pixmap(ICONS['node-tree'].format(color='#7c3aed'), QSize(24, 24)))
        layout.addWidget(badge)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title = QLabel('Model Builder Spasial', mb_card)
        title.setStyleSheet("color: #2e1065; font-size: 13.5px; font-weight: 800;")
        text_layout.addWidget(title)

        desc = QLabel('Bangun dan jalankan pemrosesan analisis geospasial tematik langsung di QGIS.', mb_card)
        desc.setStyleSheet("color: #6b21a8; font-size: 11px;")
        text_layout.addWidget(desc)
        layout.addLayout(text_layout, 1)

        arrow = QLabel(mb_card)
        arrow.setPixmap(svg_pixmap(ICONS['chevron-right'].format(color='#7c3aed'), QSize(16, 16)))
        layout.addWidget(arrow)

        self.content_layout.addWidget(mb_card)

    def _build_logout_bar(self):
        logout_btn = QPushButton(self)
        logout_btn.setObjectName('logoutBar')
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logoutRequested.emit)
        logout_btn.setStyleSheet("""
            QPushButton#logoutBar {
                background-color: #ffffff;
                border: 1px solid #fee2e2;
                border-radius: 12px;
                padding: 12px 14px;
                text-align: left;
            }
            QPushButton#logoutBar:hover {
                background-color: #fef2f2;
                border-color: #f87171;
            }
        """)

        layout = QHBoxLayout(logout_btn)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(12)

        icon_lbl = QLabel(logout_btn)
        icon_lbl.setPixmap(svg_pixmap(ICONS['logout'].format(color='#b91c1c'), QSize(20, 20)))
        layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title = QLabel('Keluar dari Akun Geoportal', logout_btn)
        title.setStyleSheet("color: #991b1b; font-size: 12.5px; font-weight: 700;")
        text_layout.addWidget(title)

        desc = QLabel('Akhiri sesi dan kembali ke halaman login utama IGT-PR.', logout_btn)
        desc.setStyleSheet("color: #7f1d1d; font-size: 10.5px;")
        text_layout.addWidget(desc)
        layout.addLayout(text_layout, 1)

        arrow = QLabel(logout_btn)
        arrow.setPixmap(svg_pixmap(ICONS['chevron-right'].format(color='#b91c1c'), QSize(14, 14)))
        layout.addWidget(arrow)

        self.content_layout.addWidget(logout_btn)

    # ------------------------------------------------------------------ Logic
    def _on_year_changed(self):
        self._update_counts()

    def _update_counts(self):
        year = self.year_combo.currentText()
        all_ds = DATASETS
        if year != 'Semua tahun':
            compiled = [d for d in SUBMISSIONS if d.get('status') == 'Terkompilasi' and year in d.get('date', '')]
            integrated = [d for d in all_ds if year in d.get('updated', '') or year in d.get('date', '')]
        else:
            compiled = [d for d in SUBMISSIONS if d.get('status') == 'Terkompilasi']
            integrated = [d for d in all_ds if d.get('status') == 'Terintegrasi']

        self.num_compiled.setText(str(len(compiled)))
        self.num_integrated.setText(str(len(integrated)))

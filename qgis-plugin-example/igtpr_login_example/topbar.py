# -*- coding: utf-8 -*-
"""Komponen Header Topbar terpadu untuk Geoportal IGT-PR Mockup V2."""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QCursor, QFont, QIcon
from qgis.PyQt.QtWidgets import (
    QAction, QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QSizePolicy, QWidget,
)

from .assets import ICONS
from .data import ROLES
from .login_page import svg_pixmap


class TopbarWidget(QFrame):
    """Header topbar aplikasi dengan breadcrumb, indikator koneksi QGIS, chip peran, dan tombol logout."""

    homeRequested = pyqtSignal()
    catalogRequested = pyqtSignal()
    switchRoleRequested = pyqtSignal()
    logoutRequested = pyqtSignal()

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__(parent)
        self.setObjectName('topbar')
        self.current_role = current_role
        self.role_info = ROLES.get(current_role, ROLES['superadmin'])

        self.setFixedHeight(48)
        self.setStyleSheet("""
            QFrame#topbar {
                background-color: #ffffff;
                border-bottom: 1px solid #dce5ef;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel#crumbBase {
                color: #64748b;
                font-size: 11.5px;
                font-weight: 500;
            }
            QLabel#crumbCurrent {
                color: #0f294d;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#crumbBtn {
                background: transparent;
                border: none;
                color: #1f6fd6;
                font-size: 11.5px;
                font-weight: 600;
                padding: 2px 4px;
            }
            QPushButton#crumbBtn:hover {
                text-decoration: underline;
            }
            QFrame#statusBadge {
                background-color: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 12px;
                padding: 2px 8px;
            }
            QLabel#statusText {
                color: #047857;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#userChip {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 15px;
                padding: 2px 10px 2px 3px;
                text-align: left;
            }
            QPushButton#userChip:hover {
                background-color: #e2e8f0;
                border-color: #94a3b8;
            }
            QPushButton#logoutBtn {
                background: transparent;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton#logoutBtn:hover {
                background-color: #fef2f2;
                border-color: #f87171;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        # Breadcrumbs
        self.crumb_layout = QHBoxLayout()
        self.crumb_layout.setSpacing(4)
        layout.addLayout(self.crumb_layout, 1)

        # QGIS Status Badge
        status_badge = QFrame(self)
        status_badge.setObjectName('statusBadge')
        sb_layout = QHBoxLayout(status_badge)
        sb_layout.setContentsMargins(6, 2, 8, 2)
        sb_layout.setSpacing(5)

        dot = QLabel('●', status_badge)
        dot.setStyleSheet("color: #10b981; font-size: 12px;")
        sb_layout.addWidget(dot)

        status_text = QLabel('QGIS Aktif', status_badge)
        status_text.setObjectName('statusText')
        sb_layout.addWidget(status_text)
        layout.addWidget(status_badge)

        # User Chip with Dropdown Menu
        self.user_chip = QPushButton(self)
        self.user_chip.setObjectName('userChip')
        self.user_chip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_chip.clicked.connect(self._show_user_menu)

        chip_inner = QHBoxLayout(self.user_chip)
        chip_inner.setContentsMargins(0, 0, 0, 0)
        chip_inner.setSpacing(6)

        self.avatar_lbl = QLabel(self.role_info['avatar'], self.user_chip)
        self.avatar_lbl.setFixedSize(26, 26)
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_avatar_style()
        chip_inner.addWidget(self.avatar_lbl)

        self.role_lbl = QLabel(self.role_info['label'] + '  ▾', self.user_chip)
        self.role_lbl.setStyleSheet("color: #1e293b; font-size: 11.5px; font-weight: 700;")
        chip_inner.addWidget(self.role_lbl)

        layout.addWidget(self.user_chip)

        # Logout button
        self.logout_btn = QPushButton(self)
        self.logout_btn.setObjectName('logoutBtn')
        self.logout_btn.setToolTip('Keluar / Logout')
        self.logout_btn.setFixedSize(28, 28)
        self.logout_btn.setIcon(QIcon(svg_pixmap(ICONS['logout'].format(color='#b91c1c'), self.logout_btn.size())))
        self.logout_btn.clicked.connect(self.logoutRequested.emit)
        layout.addWidget(self.logout_btn)

        self.set_breadcrumbs(['Dashboard'])

    def set_role(self, role_id):
        self.current_role = role_id
        self.role_info = ROLES.get(role_id, ROLES['superadmin'])
        self.avatar_lbl.setText(self.role_info['avatar'])
        self.role_lbl.setText(self.role_info['label'] + '  ▾')
        self._update_avatar_style()

    def _update_avatar_style(self):
        self.avatar_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {self.role_info['bg']};
                color: {self.role_info['color']};
                font-weight: 800;
                font-size: 10.5px;
                border-radius: 13px;
            }}
        """)

    def set_breadcrumbs(self, crumbs):
        """Update breadcrumbs display.

        crumbs can be a list of strings or tuples (text, is_clickable_home).
        Example: ['Dashboard'] or ['Katalog IGT', 'IGT Pertanahan']
        """
        # Clear existing
        while self.crumb_layout.count():
            item = self.crumb_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Base label
        base_btn = QPushButton('Geoportal IGT-PR', self)
        base_btn.setObjectName('crumbBtn')
        base_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        base_btn.clicked.connect(self.homeRequested.emit)
        self.crumb_layout.addWidget(base_btn)

        for i, c in enumerate(crumbs):
            sep = QLabel('/', self)
            sep.setStyleSheet("color: #94a3b8; font-size: 11px;")
            self.crumb_layout.addWidget(sep)

            is_last = (i == len(crumbs) - 1)
            if is_last:
                lbl = QLabel(c, self)
                lbl.setObjectName('crumbCurrent')
                self.crumb_layout.addWidget(lbl)
            else:
                btn = QPushButton(c, self)
                btn.setObjectName('crumbBtn')
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                if c in ('Dashboard', 'Beranda'):
                    btn.clicked.connect(self.homeRequested.emit)
                elif c in ('Katalog IGT', 'Katalog Data'):
                    btn.clicked.connect(self.catalogRequested.emit)
                else:
                    btn.clicked.connect(self.homeRequested.emit)
                self.crumb_layout.addWidget(btn)

        self.crumb_layout.addStretch()

    def _show_user_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 4px;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 6px;
                color: #1e293b;
            }
            QMenu::item:selected {
                background-color: #f1f5f9;
                color: #1f6fd6;
            }
        """)

        switch_act = QAction('🔄 Ganti Peran Pengguna...', menu)
        switch_act.triggered.connect(self.switchRoleRequested.emit)
        menu.addAction(switch_act)

        menu.addSeparator()

        logout_act = QAction('🚪 Keluar (Logout)', menu)
        logout_act.triggered.connect(self.logoutRequested.emit)
        menu.addAction(logout_act)

        menu.exec_(QCursor.pos())

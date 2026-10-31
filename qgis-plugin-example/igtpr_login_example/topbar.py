# -*- coding: utf-8 -*-
"""Topbar (header) Geoportal IGT-PR Mockup V2, responsif terhadap lebar dock.

Di dock sempit, bagian yang kurang penting disembunyikan bertahap:
< 560 px badge "QGIS Aktif", < 460 px nama peran dan crumb dasar, crumb terakhir dipotong '…'.
"""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QCursor
from qgis.PyQt.QtWidgets import QAction, QFrame, QHBoxLayout, QLabel, QMenu, QPushButton, QSizePolicy

from .data import ROLES
from .ui_kit import ElidedLabel, clear_layout, icon, theme_qss

TOPBAR_QSS = """
QFrame#topbar { background: #ffffff; border: none; border-bottom: 1px solid #e2e8f0; }
QPushButton#crumbBase { background: transparent; border: none; color: #64748b; font-size: 12px; padding: 2px 0; }
QPushButton#crumbBase:hover { color: #1f6fd6; text-decoration: underline; }
QPushButton#crumbMid {
    background: #e0f2fe; border: none; border-radius: 6px; color: #0369a1; font-size: 12px; font-weight: 700;
    padding: 3px 8px;
}
QPushButton#crumbMid:hover { background: #bae6fd; }
QPushButton#crumbMid[tone="green"] { background: #dcfce7; color: #15803d; }
QLabel#crumbSep { color: #94a3b8; font-size: 12px; }
QLabel#crumbCurrent { color: #0f294d; font-size: 12px; font-weight: 800; }
QFrame#statusBadge { background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; }
QLabel#statusDot { color: #10b981; font-size: 10px; }
QLabel#statusText { color: #047857; font-size: 11px; font-weight: 700; }
QPushButton#userChip {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 17px; padding: 2px 10px 2px 2px;
    color: #1e293b; font-size: 12px; font-weight: 700; text-align: left;
}
QPushButton#userChip[compact="true"] { padding: 2px; }
QPushButton#userChip:hover { background: #eef2f7; border-color: #cbd5e1; }
QPushButton#logoutBtn { background: #ffffff; border: 1px solid #fecaca; border-radius: 9px; }
QPushButton#logoutBtn:hover { background: #fef2f2; border-color: #f87171; }
"""


class TopbarWidget(QFrame):
    """Header aplikasi: breadcrumb, indikator koneksi QGIS, chip peran, dan tombol logout."""

    homeRequested = pyqtSignal()
    catalogRequested = pyqtSignal()
    switchRoleRequested = pyqtSignal()
    logoutRequested = pyqtSignal()

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__(parent)
        self.setObjectName('topbar')
        self.setStyleSheet(theme_qss() + TOPBAR_QSS)
        self.setFixedHeight(48)
        self.current_role = current_role
        self.role_info = ROLES.get(current_role, ROLES['superadmin'])
        self._crumbs = ['Dashboard']
        self._base_btn = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.setSpacing(8)

        self.crumb_layout = QHBoxLayout()
        self.crumb_layout.setSpacing(6)
        layout.addLayout(self.crumb_layout, 1)

        self.status_badge = QFrame(self)
        self.status_badge.setObjectName('statusBadge')
        sb = QHBoxLayout(self.status_badge)
        sb.setContentsMargins(8, 3, 10, 3)
        sb.setSpacing(5)
        dot = QLabel('●', self.status_badge)
        dot.setObjectName('statusDot')
        sb.addWidget(dot)
        txt = QLabel('QGIS Aktif', self.status_badge)
        txt.setObjectName('statusText')
        sb.addWidget(txt)
        layout.addWidget(self.status_badge)

        self.user_chip = QPushButton(self)
        self.user_chip.setObjectName('userChip')
        self.user_chip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_chip.setIconSize(QSize(28, 28))
        self.user_chip.clicked.connect(self._show_user_menu)
        layout.addWidget(self.user_chip)

        self.logout_btn = QPushButton(self)
        self.logout_btn.setObjectName('logoutBtn')
        self.logout_btn.setToolTip('Keluar / Logout')
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.setFixedSize(32, 32)
        self.logout_btn.setIcon(icon('logout', '#b91c1c', 16))
        self.logout_btn.setIconSize(QSize(16, 16))
        self.logout_btn.clicked.connect(self.logoutRequested.emit)
        layout.addWidget(self.logout_btn)

        self._update_chip()
        self.set_breadcrumbs(['Dashboard'])

    # ------------------------------------------------------------------ peran
    def set_role(self, role_id):
        self.current_role = role_id
        self.role_info = ROLES.get(role_id, ROLES['superadmin'])
        self._update_chip()

    def _avatar_icon(self):
        from qgis.PyQt.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
        size, ratio = 28, 2
        pm = QPixmap(size * ratio, size * ratio)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.scale(ratio, ratio)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(self.role_info['bg']))
        p.drawEllipse(0, 0, size, size)
        font = QFont(self.font())
        font.setPixelSize(11)
        font.setBold(True)
        p.setFont(font)
        p.setPen(QColor(self.role_info['color']))
        p.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, self.role_info['avatar'])
        p.end()
        pm.setDevicePixelRatio(ratio)
        return QIcon(pm)

    def _update_chip(self):
        self.user_chip.setIcon(self._avatar_icon())
        self.user_chip.setToolTip(f"{self.role_info['label']} · klik untuk ganti peran / logout")
        self._apply_compact(self.width())

    # ------------------------------------------------------------------ breadcrumb
    def set_breadcrumbs(self, crumbs):
        """crumbs: daftar teks, mis. ['Dashboard'] atau ['Katalog IGT', 'IGT Pertanahan']."""
        self._crumbs = list(crumbs)
        clear_layout(self.crumb_layout)

        self._base_btn = QPushButton('Geoportal IGT-PR', self)
        self._base_btn.setObjectName('crumbBase')
        self._base_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._base_btn.clicked.connect(self.homeRequested.emit)
        self.crumb_layout.addWidget(self._base_btn)
        self._base_sep = self._sep()
        self.crumb_layout.addWidget(self._base_sep)

        for i, text in enumerate(crumbs):
            if i == len(crumbs) - 1:
                cur = ElidedLabel(text, self)
                cur.setObjectName('crumbCurrent')
                self.crumb_layout.addWidget(cur, 1)
            else:
                btn = QPushButton(text, self)
                btn.setObjectName('crumbMid')
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                if text.startswith('Manajemen'):
                    btn.setProperty('tone', 'green')
                if text in ('Katalog IGT', 'Katalog Data'):
                    btn.clicked.connect(self.catalogRequested.emit)
                else:
                    btn.clicked.connect(self.homeRequested.emit)
                self.crumb_layout.addWidget(btn)
                self.crumb_layout.addWidget(self._sep())
        self._apply_compact(self.width())

    def _sep(self):
        sep = QLabel('/', self)
        sep.setObjectName('crumbSep')
        return sep

    # ------------------------------------------------------------------ responsif
    def minimumSizeHint(self):
        return QSize(160, 48)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_compact(event.size().width())

    def _apply_compact(self, width):
        self.status_badge.setVisible(width >= 560)
        compact = width < 460
        self.user_chip.setText('' if compact else f"{self.role_info['label']}  ▾")
        self.user_chip.setProperty('compact', 'true' if compact else 'false')
        self.user_chip.style().unpolish(self.user_chip)
        self.user_chip.style().polish(self.user_chip)
        if self._base_btn is not None:
            show_base = width >= 380
            self._base_btn.setVisible(show_base)
            self._base_sep.setVisible(show_base)
        # Crumb tengah ('Katalog IGT', 'Manajemen Data') disembunyikan di dock sangat sempit.
        for i in range(self.crumb_layout.count()):
            w = self.crumb_layout.itemAt(i).widget()
            if w is not None and w.objectName() == 'crumbMid':
                w.setVisible(width >= 360)
                nxt = self.crumb_layout.itemAt(i + 1).widget() if i + 1 < self.crumb_layout.count() else None
                if nxt is not None and nxt.objectName() == 'crumbSep':
                    nxt.setVisible(width >= 360)

    # ------------------------------------------------------------------ menu pengguna
    def _show_user_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 14px; border-radius: 6px; color: #1e293b; font-size: 12px; }
            QMenu::item:selected { background: #f1f5f9; color: #1f6fd6; }
            QMenu::item:disabled { color: #64748b; font-weight: 700; }
        """)
        who = QAction(f"Masuk sebagai {self.role_info['label']}", menu)
        who.setEnabled(False)
        menu.addAction(who)
        menu.addSeparator()
        switch_act = QAction('Ganti Peran Pengguna…', menu)
        switch_act.triggered.connect(self.switchRoleRequested.emit)
        menu.addAction(switch_act)
        logout_act = QAction('Keluar (Logout)', menu)
        logout_act.triggered.connect(self.logoutRequested.emit)
        menu.addAction(logout_act)
        menu.exec_(QCursor.pos())

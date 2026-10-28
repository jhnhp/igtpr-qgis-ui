# -*- coding: utf-8 -*-
"""Mendaftarkan tombol toolbar/menu dan dock halaman login ke QGIS."""

import os

from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .assets import Q_ICON
from .login_page import LoginDockWidget, svg_pixmap

PLUGIN_DIR = os.path.dirname(__file__)
MENU = '&IGT-PR (Contoh)'


class IgtprLoginExample:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dock = None

    def initGui(self):  # pylint: disable=invalid-name
        icon = QIcon(svg_pixmap(Q_ICON.format(color='#1f6fd6'), QSize(24, 24)))
        self.action = QAction(icon, 'Login IGT-PR (contoh)', self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.toggled.connect(self.toggle_dock)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(MENU, self.action)

    def unload(self):
        self.iface.removePluginMenu(MENU, self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None

    def toggle_dock(self, visible):
        if self.dock is None:
            # Gunakan logo dari Examples saat dijalankan dari repository; fallback ke aset di folder plugin.
            examples_dir = os.path.abspath(os.path.join(PLUGIN_DIR, '..', '..', 'Examples'))
            bpn_logo = os.path.join(examples_dir, 'logo-bpn.png')
            igtpr_logo = os.path.join(examples_dir, 'logo-igtpr.png')
            if not os.path.isfile(bpn_logo):
                bpn_logo = os.path.join(PLUGIN_DIR, 'logo-bpn.png')
            if not os.path.isfile(igtpr_logo):
                igtpr_logo = os.path.join(PLUGIN_DIR, 'logo-igtpr.png')
            self.dock = LoginDockWidget(bpn_logo, igtpr_logo, self.iface.mainWindow())
            self.dock.page.loginRequested.connect(self.on_login)
            self.dock.page.adminLoginRequested.connect(self.on_admin_login)
            self.dock.page.guideRequested.connect(self.on_guide)
            self.dock.visibilityChanged.connect(self.action.setChecked)
            self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.setVisible(visible)

    def on_login(self):
        # Di plugin IGT-PR, sambungkan ke alur SSO yang sudah ada (PluginIGRPR.login_sso_keycloak).
        self.iface.messageBar().pushInfo(
            'IGT-PR', 'Contoh: tombol LOGIN belum terhubung ke SSO. Sambungkan sinyal loginRequested ke alur login.')

    def on_admin_login(self):
        self.iface.messageBar().pushInfo(
            'IGT-PR', 'Login administrator belum dikonfigurasi pada plugin contoh.')

    def on_guide(self):
        self.iface.messageBar().pushInfo(
            'IGT-PR', 'Panduan penggunaan belum dikonfigurasi. Tambahkan URL atau dokumen panduan panduan untuk mengaktifkan tombol ini.')

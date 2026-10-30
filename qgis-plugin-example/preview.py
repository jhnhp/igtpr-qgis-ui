#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runner interaktif mandiri untuk menguji plugin Geoportal IGT-PR (Mockup V2).

Menjalankan kanvas peta QGIS dan dock widget IGT-PR secara langsung
tanpa perlu membuka aplikasi QGIS lengkap.
"""

import os
import sys

# Tambahkan direktori saat ini ke sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from qgis.core import (
    QgsApplication, QgsCoordinateReferenceSystem, QgsProject, QgsRectangle,
)
from qgis.gui import QgsMapCanvas, QgsMessageBar
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (
    QAction, QMainWindow, QStatusBar, QToolBar, QVBoxLayout, QWidget,
)

from igtpr_login_example.plugin import IgtprLoginExample


class MockIface:
    """Implementasi antarmuka tiruan QgisInterface untuk preview mandiri."""

    def __init__(self, main_window, canvas, message_bar):
        self._main_window = main_window
        self._canvas = canvas
        self._message_bar = message_bar

    def mainWindow(self):
        return self._main_window

    def mapCanvas(self):
        return self._canvas

    def messageBar(self):
        return self._message_bar

    def addDockWidget(self, area, dock):
        self._main_window.addDockWidget(area, dock)

    def removeDockWidget(self, dock):
        self._main_window.removeDockWidget(dock)

    def addToolBarIcon(self, action):
        pass

    def removeToolBarIcon(self, action):
        pass

    def addPluginToMenu(self, title, action):
        pass

    def removePluginMenu(self, title, action):
        pass


class StandalonePreviewWindow(QMainWindow):
    """Jendela utama untuk preview interaktif plugin IGT-PR."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Preview Plugin Geoportal IGT-PR (Mockup V2) · Standalone QGIS Canvas')
        self.resize(1260, 820)

        # Container tengah
        central = QWidget(self)
        self.setCentralWidget(central)
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Message Bar QGIS di bagian atas kanvas
        self.message_bar = QgsMessageBar(central)
        central_layout.addWidget(self.message_bar)

        # Kanvas Peta QGIS
        self.canvas = QgsMapCanvas(central)
        self.canvas.setCanvasColor(QColor('#f8fafc'))
        self.canvas.enableAntiAliasing(True)

        # Set CRS & extent awal (Wilayah D.I. Yogyakarta)
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        self.canvas.setDestinationCrs(crs)
        QgsProject.instance().setCrs(crs)
        extent = QgsRectangle(110.15, -8.05, 110.60, -7.60)
        self.canvas.setExtent(extent)

        central_layout.addWidget(self.canvas, 1)

        # Sambungkan QgsProject ke MapCanvas
        QgsProject.instance().layersAdded.connect(self._on_layers_changed)
        QgsProject.instance().layersRemoved.connect(self._on_layers_changed)

        # Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('Siap · Klik tombol LOGIN di panel kanan untuk masuk ke Geoportal.')

        # Inisialisasi Mock Interface dan Plugin
        self.iface = MockIface(self, self.canvas, self.message_bar)
        self.plugin = IgtprLoginExample(self.iface)
        self.plugin.initGui()
        self.plugin.toggle_dock(True)

        # Sambungkan aksi login langsung membuka dashboard
        self.plugin.dock.login_page.loginRequested.disconnect()
        self.plugin.dock.login_page.loginRequested.connect(self.plugin.on_login_clicked)

    def _on_layers_changed(self, *args):
        layers = list(QgsProject.instance().mapLayers().values())
        self.canvas.setLayers(layers)
        if layers:
            self.canvas.setExtent(layers[-1].extent())
        self.canvas.refresh()
        self.status_bar.showMessage(f"Total layer aktif di kanvas: {len(layers)}")


def main():
    # Inisialisasi QGIS Application
    app = QgsApplication(sys.argv, True)
    QgsApplication.initQgis()

    win = StandalonePreviewWindow()
    win.show()

    ret = app.exec_()
    QgsApplication.exitQgis()
    sys.exit(ret)


if __name__ == '__main__':
    main()

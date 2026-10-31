# -*- coding: utf-8 -*-
"""Plugin Geoportal IGT-PR Mockup V2 untuk QGIS.

Menyediakan panel dock native terpadu dengan antarmuka berbasis fitur (Mockup V2):
- Halaman Login (SSO ATR/BPN & Administrator)
- Pemilihan Peran Pengguna (Superadmin, Admin, Operator Pusat, Pengguna Umum)
- Dashboard / Beranda V2 (Hero Card, Stat Cards, Katalog Hub, Alur Kerja)
- Katalog Data V2 (Hierarchical Accordion Tree, Multi-Layer Chips, WMS/WFS)
- Manajemen Data V2 (Tab Status, Kompilasi, Verifikasi Topologi, Persetujuan)
- Formulir Unggah Data V2
- Model Builder Spasial V2
"""

import os

from qgis.PyQt.QtCore import QSize, Qt, QUrl, pyqtSignal
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import (
    QAction, QDockWidget, QFrame, QMessageBox, QScrollArea, QStackedWidget,
    QVBoxLayout, QWidget,
)

from qgis.core import (
    QgsFeature, QgsField, QgsFillSymbol, QgsGeometry, QgsProject,
    QgsSingleSymbolRenderer, QgsVectorLayer,
)

from .assets import ICONS, Q_ICON
from .catalog_page import CatalogPage
from .dashboard_page import DashboardPage
from .data import CATEGORIES, DATASETS, ROLES, SUBMISSIONS, can_access_wfs
from .login_page import LoginPage, svg_pixmap
from .management_page import ManagementPage
from .model_builder_page import ModelBuilderPage
from .role_dialog import RoleDialog
from .topbar import TopbarWidget
from .upload_dialog import UploadPage

PLUGIN_DIR = os.path.dirname(__file__)
MENU_TITLE = '&Geoportal IGT-PR'


class DynamicStackedWidget(QStackedWidget):
    """QStackedWidget dengan minimumSizeHint dan sizeHint dinamis mengikuti halaman aktif.

    Secara bawaan di Qt, QStackedWidget mengambil ukuran maksimum dari seluruh halaman di stack,
    sehingga halaman yang lebar (misal Management / Model Builder) dapat mengunci dock widget
    tidak bisa dikecilkan meskipun sedang berada di Dashboard atau Katalog.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentChanged.connect(lambda idx: self.updateGeometry())

    def minimumSizeHint(self):
        cur = self.currentWidget()
        if cur is not None:
            sz = cur.minimumSizeHint()
            return QSize(min(200, sz.width()), sz.height())
        return QSize(200, 120)

    def sizeHint(self):
        cur = self.currentWidget()
        if cur is not None:
            return cur.sizeHint()
        return super().sizeHint()


class IgtprDockWidget(QDockWidget):
    """Panel dock terpadu yang memuat seluruh alur Mockup V2 dalam QStackedWidget."""

    def __init__(self, iface, bpn_logo=None, igtpr_logo=None, qgis_icon=None, parent=None):
        super().__init__('Geoportal IGT-PR', parent)
        self.iface = iface
        self.setObjectName('IgtprV2DockWidget')
        self.current_role = 'superadmin'

        container = QWidget(self)
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Topbar (Persisten untuk seluruh halaman aplikasi setelah login)
        self.topbar = TopbarWidget(current_role=self.current_role, parent=container)
        self.main_layout.addWidget(self.topbar)
        self.topbar.hide()  # tersembunyi di halaman login

        # 2. Stacked Pages
        self.stack = DynamicStackedWidget(container)

        # Page 0: Login Page (di dalam QScrollArea)
        self.login_page = LoginPage(bpn_logo, igtpr_logo, qgis_icon)
        login_scroll = QScrollArea(self.stack)
        login_scroll.setWidgetResizable(True)
        login_scroll.setFrameShape(QFrame.Shape.NoFrame)
        login_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        login_scroll.setWidget(self.login_page)
        self.stack.addWidget(login_scroll)

        # Page 1: Dashboard V2
        self.dashboard_page = DashboardPage(current_role=self.current_role, parent=self.stack)
        self.stack.addWidget(self.dashboard_page)

        # Page 2: Catalog Data V2
        self.catalog_page = CatalogPage(current_category='igt-pr', current_role=self.current_role, parent=self.stack)
        self.stack.addWidget(self.catalog_page)

        # Page 3: Management Data V2
        self.management_page = ManagementPage(current_category='igt-utama', current_role=self.current_role, parent=self.stack)
        self.stack.addWidget(self.management_page)

        # Page 4: Upload Data V2
        self.upload_page = UploadPage(current_category='pertanahan', current_role=self.current_role, parent=self.stack)
        self.stack.addWidget(self.upload_page)

        # Page 5: Model Builder V2
        self.model_builder_page = ModelBuilderPage(current_role=self.current_role, parent=self.stack)
        self.stack.addWidget(self.model_builder_page)

        self.main_layout.addWidget(self.stack, 1)
        self.setWidget(container)
        self.setMinimumWidth(200)

        # Connect Topbar Navigation
        self.topbar.homeRequested.connect(self.show_dashboard)
        self.topbar.catalogRequested.connect(lambda: self.show_catalog('igt-pr'))
        self.topbar.logoutRequested.connect(self.show_login)

        # Connect Dashboard Navigation
        self.dashboard_page.openCatalogRequested.connect(self.show_catalog)
        self.dashboard_page.openManagementRequested.connect(self.show_management)
        self.dashboard_page.openUploadRequested.connect(self.show_upload)
        self.dashboard_page.openModelBuilderRequested.connect(self.show_model_builder)
        self.dashboard_page.logoutRequested.connect(self.show_login)

        # Connect Sub-Pages Back to Dashboard
        self.catalog_page.backToDashboardRequested.connect(self.show_dashboard)
        self.management_page.backToDashboardRequested.connect(self.show_dashboard)
        self.upload_page.backToDashboardRequested.connect(self.show_dashboard)
        self.model_builder_page.backToDashboardRequested.connect(self.show_dashboard)

    # ------------------------------------------------------------------ Page Transitions
    def show_login(self):
        self.topbar.hide()
        self.stack.setCurrentIndex(0)

    def show_dashboard(self):
        self.topbar.show()
        self.topbar.set_breadcrumbs(['Dashboard'])
        self.dashboard_page.set_role(self.current_role)
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_catalog(self, category_key='igt-pr'):
        self.topbar.show()
        cat_info = CATEGORIES.get(category_key, CATEGORIES['igt-pr'])
        self.topbar.set_breadcrumbs(['Katalog IGT', cat_info['label']])
        if hasattr(self.dashboard_page, 'year_combo'):
            self.catalog_page.set_year_filter(self.dashboard_page.year_combo.currentText())
        self.catalog_page.set_category(category_key)
        self.stack.setCurrentWidget(self.catalog_page)

    def show_management(self, tab_key='igt-utama'):
        self.topbar.show()
        lbl = 'IGT Utama' if tab_key == 'igt-utama' else 'IGT Derivatif Multiguna' if tab_key == 'derivatif' else 'IGT Lainnya'
        self.topbar.set_breadcrumbs(['Manajemen Data', lbl])
        self.management_page.set_category(tab_key)
        self.stack.setCurrentWidget(self.management_page)

    def show_upload(self, category_key='pertanahan'):
        self.topbar.show()
        self.topbar.set_breadcrumbs(['Unggah Data'])
        self.upload_page.set_category(category_key)
        self.stack.setCurrentWidget(self.upload_page)

    def show_model_builder(self):
        self.topbar.show()
        self.topbar.set_breadcrumbs(['Model Builder'])
        self.stack.setCurrentWidget(self.model_builder_page)

    def set_role(self, role_id):
        self.current_role = role_id
        self.topbar.set_role(role_id)
        self.dashboard_page.set_role(role_id)
        self.catalog_page.set_role(role_id)
        self.management_page.set_role(role_id)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_width(event.size().width())

    def apply_width(self, width):
        for widget in (
            getattr(self, 'topbar', None),
            getattr(self, 'dashboard_page', None),
            getattr(self, 'catalog_page', None),
            getattr(self, 'management_page', None),
            getattr(self, 'upload_page', None),
            getattr(self, 'model_builder_page', None),
        ):
            if widget and hasattr(widget, 'apply_width'):
                widget.apply_width(width)


# Alias untuk backwards compatibility
LoginDockWidget = IgtprDockWidget


class IgtprLoginExample:
    """Kontroler utama plugin QGIS untuk Geoportal IGT-PR."""

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dock = None

    def _asset_path(self, filename):
        examples_path = os.path.abspath(os.path.join(PLUGIN_DIR, '..', '..', 'Examples', filename))
        if os.path.isfile(examples_path):
            return examples_path
        return os.path.join(PLUGIN_DIR, filename)

    def initGui(self):  # pylint: disable=invalid-name
        icon_path = self._asset_path('icon.png')
        icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon(
            svg_pixmap(Q_ICON.format(color='#1f6fd6'), QSize(24, 24)))
        self.action = QAction(icon, 'Geoportal IGT-PR (V2)', self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.toggled.connect(self.toggle_dock)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(MENU_TITLE, self.action)

    def unload(self):
        self.iface.removePluginMenu(MENU_TITLE, self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dock:
            self.iface.removeDockWidget(self.dock)
            self.dock.deleteLater()
            self.dock = None

    def toggle_dock(self, visible):
        if self.dock is None:
            bpn_logo = self._asset_path('logo-bpn.png')
            igtpr_logo = self._asset_path('logo-igtpr.png')
            qgis_icon = self._asset_path('qgis_icon.svg')

            self.dock = IgtprDockWidget(self.iface, bpn_logo, igtpr_logo, qgis_icon, self.iface.mainWindow())

            # Connect Login Page
            self.dock.login_page.loginRequested.connect(self.on_login_clicked)
            self.dock.login_page.adminLoginRequested.connect(self.on_admin_login_clicked)
            self.dock.login_page.guideRequested.connect(self.on_guide)

            # Connect Role Switching
            self.dock.topbar.switchRoleRequested.connect(self.on_switch_role_clicked)

            # Connect Catalog & Dashboard Layer Load Actions
            self.dock.catalog_page.wmsRequested.connect(self.on_load_wms)
            self.dock.catalog_page.wfsRequested.connect(self.on_load_wfs)
            self.dock.dashboard_page.wmsRequested.connect(self.on_load_wms)
            self.dock.dashboard_page.wfsRequested.connect(self.on_load_wfs)

            # Connect Management Actions
            self.dock.management_page.showLayerRequested.connect(self.on_show_submission_layer)
            self.dock.management_page.actionPerformed.connect(self.on_management_action)

            # Connect Upload Action
            self.dock.upload_page.uploadSubmitted.connect(self.on_upload_submitted)

            # Connect Model Builder Action
            self.dock.model_builder_page.runModelRequested.connect(self.on_run_model)

            self.dock.visibilityChanged.connect(self.action.setChecked)
            self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

        self.dock.setVisible(visible)

    # ------------------------------------------------------------------ Login & Role Handlers
    def on_login_clicked(self):
        """Menampilkan dialog peran saat tombol LOGIN diklik, lalu masuk ke Dashboard."""
        main_win = self.iface.mainWindow() if hasattr(self.iface, 'mainWindow') else None
        dlg = RoleDialog(current_role=self.dock.current_role, parent=main_win)
        dlg.roleSelected.connect(self._do_login)
        dlg.exec_()

    def on_admin_login_clicked(self):
        """Menampilkan dialog peran dengan admin/superadmin terfokus."""
        main_win = self.iface.mainWindow() if hasattr(self.iface, 'mainWindow') else None
        dlg = RoleDialog(current_role='admin', parent=main_win)
        dlg.roleSelected.connect(self._do_login)
        dlg.exec_()

    def on_switch_role_clicked(self):
        """Mengganti peran pengguna yang sedang aktif."""
        main_win = self.iface.mainWindow() if hasattr(self.iface, 'mainWindow') else None
        dlg = RoleDialog(current_role=self.dock.current_role, parent=main_win)
        if dlg.exec_() == RoleDialog.DialogCode.Accepted:
            self.dock.set_role(dlg.selected_role)
            if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
                self.iface.messageBar().pushSuccess(
                    'Peran Diperbarui', f"Peran pengguna aktif beralih ke: {ROLES[dlg.selected_role]['label']}")

    def _do_login(self, role_id):
        self.dock.set_role(role_id)
        self.dock.show_dashboard()
        if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'Selamat Datang', f"Berhasil masuk ke Geoportal IGT-PR sebagai {ROLES[role_id]['label']} (Mockup V2)")

    def on_guide(self):
        QDesktopServices.openUrl(QUrl('https://igtpr.atrbpn.go.id/'))

    # ------------------------------------------------------------------ QGIS Map Layer Integration
    def on_load_wms(self, dataset, sublayer=None):
        self._load_simulated_layer(dataset, sublayer, is_wms=True)

    def on_load_wfs(self, dataset, sublayer=None):
        if not can_access_wfs(self.dock.current_role, dataset):
            if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
                self.iface.messageBar().pushWarning(
                    'Akses WFS Dibatasi',
                    f"Akses fitur WFS dibatasi untuk satker terkait ({dataset.get('satker') or 'Satker Terkait'})."
                )
            return
        self._load_simulated_layer(dataset, sublayer, is_wms=False)

    def _get_geojson_path(self):
        """Mendapatkan path ke berkas batas administrasi kabupaten Indonesia."""
        candidates = [
            os.path.join(PLUGIN_DIR, 'indonesia-kabupaten.geojson'),
            '/home/jhn/projects/SPPR/Mitraeka/IGTPR-UI-mockup/assets/data/indonesia-kabupaten.geojson',
            os.path.abspath(os.path.join(PLUGIN_DIR, '..', '..', '..', 'IGTPR-UI-mockup', 'assets', 'data', 'indonesia-kabupaten.geojson')),
        ]
        for p in candidates:
            if os.path.isfile(p):
                return p
        return None

    def _load_simulated_layer(self, dataset, sublayer=None, is_wms=True):
        """Membuat layer di QGIS dari berkas geojson kabupaten Indonesia dan menampilkannya pada kanvas peta."""
        service_type = 'WMS' if is_wms else 'WFS'
        layer_title = dataset['name']
        if sublayer:
            layer_title = f"{dataset['name']} ({sublayer.get('label') or sublayer.get('name')})"

        layer_name = f"[{service_type}] {layer_title}"
        geojson_path = self._get_geojson_path()

        layer = None
        if geojson_path and os.path.isfile(geojson_path):
            layer = QgsVectorLayer(geojson_path, layer_name, "ogr")

        if layer and layer.isValid():
            try:
                if is_wms:
                    sym = QgsFillSymbol.createSimple({
                        'color': '191,219,254,110',        # #bfdbfe dengan transparansi
                        'outline_color': '31,111,214,255',  # #1f6fd6 biru tegas
                        'outline_width': '0.5',
                    })
                else:
                    sym = QgsFillSymbol.createSimple({
                        'color': '237,233,254,110',        # #ede9fe dengan transparansi
                        'outline_color': '124,58,237,255',  # #7c3aed ungu tegas
                        'outline_width': '0.5',
                    })
                layer.setRenderer(QgsSingleSymbolRenderer(sym))
                layer.triggerRepaint()
            except Exception:
                pass

            for old_layer in QgsProject.instance().mapLayersByName(layer_name):
                QgsProject.instance().removeMapLayer(old_layer.id())

            QgsProject.instance().addMapLayer(layer)

            # Arahkan zoom kanvas ke wilayah dataset yang sesuai jika ada
            target_extent = None
            if hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                kab_name = (dataset.get('kab') or '').lower().replace('kab.', '').replace('kota', '').strip()
                if kab_name and kab_name not in ('seluruh indonesia', 'multi-kabupaten', 'semua kab / kota'):
                    for f in layer.getFeatures():
                        f_kab = (f['kabupaten'] or '').lower()
                        if kab_name in f_kab or f_kab in kab_name:
                            target_extent = f.geometry().boundingBox()
                            target_extent.scale(1.3)
                            break

                if not target_extent:
                    prov_name = (dataset.get('prov') or '').lower().strip()
                    if 'yogyakarta' in prov_name or 'd.i.' in prov_name:
                        prov_name = 'yogyakarta'
                    elif 'jakarta' in prov_name or 'dki' in prov_name:
                        prov_name = 'jakarta'
                    if prov_name and prov_name not in ('nasional', 'semua provinsi'):
                        for f in layer.getFeatures():
                            f_prov = (f['provinsi'] or '').lower()
                            if prov_name in f_prov:
                                if target_extent is None:
                                    target_extent = f.geometry().boundingBox()
                                else:
                                    target_extent.combineExtentWith(f.geometry().boundingBox())
                        if target_extent:
                            target_extent.scale(1.15)

                if target_extent:
                    self.iface.mapCanvas().setExtent(target_extent)
                else:
                    self.iface.mapCanvas().setExtent(layer.extent())
                self.iface.mapCanvas().refresh()

        else:
            # Fallback jika berkas geojson tidak ditemukan
            mem_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", layer_name, "memory")
            if not mem_layer.isValid():
                if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
                    self.iface.messageBar().pushWarning('Geoportal IGT-PR', f"Gagal menginisialisasi layer {layer_name}")
                return

            pr = mem_layer.dataProvider()
            pr.addAttributes([
                QgsField("nama_igt"),
                QgsField("kategori"),
                QgsField("direktorat"),
                QgsField("satker"),
                QgsField("tahun"),
                QgsField("layanan"),
            ])
            mem_layer.updateFields()

            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromWkt(
                "POLYGON((110.33 -7.73, 110.42 -7.73, 110.42 -7.82, 110.33 -7.82, 110.33 -7.73))"
            ))
            feat.setAttributes([
                layer_title,
                dataset.get('category', 'IGT'),
                dataset.get('direktorat', 'Ditjen SPPR'),
                dataset.get('satker', 'Kantah Kab. Sleman'),
                dataset.get('updated', '2026'),
                service_type,
            ])
            pr.addFeatures([feat])
            mem_layer.updateExtents()

            for old_layer in QgsProject.instance().mapLayersByName(layer_name):
                QgsProject.instance().removeMapLayer(old_layer.id())

            QgsProject.instance().addMapLayer(mem_layer)

            if hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                self.iface.mapCanvas().setExtent(mem_layer.extent())
                self.iface.mapCanvas().refresh()

        sub_msg = f" (Sub-layer: {sublayer['name']})" if sublayer else ""
        if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                f"Layer {service_type} Dimuat",
                f"Layanan {service_type} untuk '{dataset['name']}'{sub_msg} berhasil ditambahkan ke kanvas peta QGIS!"
            )

    def on_show_submission_layer(self, record):
        """Menampilkan layer data pengajuan ke kanvas QGIS."""
        layer_title = record.get('name') or record.get('layer', 'Layer')
        layer_name = f"[Pengajuan] {layer_title}"
        geojson_path = self._get_geojson_path()

        layer = None
        if geojson_path and os.path.isfile(geojson_path):
            layer = QgsVectorLayer(geojson_path, layer_name, "ogr")

        if layer and layer.isValid():
            try:
                sym = QgsFillSymbol.createSimple({
                    'color': '254,243,199,120',        # Amber lembut
                    'outline_color': '217,119,6,255',   # #d97706 oranye tua
                    'outline_width': '0.5',
                })
                layer.setRenderer(QgsSingleSymbolRenderer(sym))
                layer.triggerRepaint()
            except Exception:
                pass

            for old_layer in QgsProject.instance().mapLayersByName(layer_name):
                QgsProject.instance().removeMapLayer(old_layer.id())

            QgsProject.instance().addMapLayer(layer)

            target_extent = None
            if hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                satker = (record.get('satker') or '').lower()
                for f in layer.getFeatures():
                    f_kab = (f['kabupaten'] or '').lower()
                    if f_kab and f_kab in satker:
                        target_extent = f.geometry().boundingBox()
                        target_extent.scale(1.3)
                        break

                if target_extent:
                    self.iface.mapCanvas().setExtent(target_extent)
                else:
                    self.iface.mapCanvas().setExtent(layer.extent())
                self.iface.mapCanvas().refresh()
        else:
            mem_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", layer_name, "memory")
            if mem_layer.isValid():
                pr = mem_layer.dataProvider()
                pr.addAttributes([QgsField("id_pengajuan"), QgsField("status"), QgsField("satker")])
                mem_layer.updateFields()
                feat = QgsFeature()
                feat.setGeometry(QgsGeometry.fromWkt(
                    "POLYGON((110.35 -7.75, 110.40 -7.75, 110.40 -7.80, 110.35 -7.80, 110.35 -7.75))"
                ))
                feat.setAttributes([record.get('id', ''), record.get('status', ''), record.get('satker', '')])
                pr.addFeatures([feat])
                mem_layer.updateExtents()
                for old_layer in QgsProject.instance().mapLayersByName(layer_name):
                    QgsProject.instance().removeMapLayer(old_layer.id())
                QgsProject.instance().addMapLayer(mem_layer)
                if hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                    self.iface.mapCanvas().setExtent(mem_layer.extent())
                    self.iface.mapCanvas().refresh()

        if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushInfo(
                'Layer Pengajuan Dimuat',
                f"Data pengajuan '{layer_title}' berhasil ditampilkan pada kanvas peta QGIS."
            )

    def on_management_action(self, action, record):
        if not (hasattr(self.iface, 'messageBar') and self.iface.messageBar()):
            return

        rec_name = record.get('name') or record.get('layer', 'Layer')
        rec_id = record.get('id', '')

        if action == 'compile':
            self.iface.messageBar().pushSuccess(
                'Kompilasi Berhasil',
                f"Data '{rec_name}' ({rec_id}) berhasil dikompilasi ke sistem integrasi."
            )
        elif action == 'topology':
            self.iface.messageBar().pushInfo(
                'Verifikasi Topologi Selesai',
                f"Hasil verifikasi topologi '{rec_name}': 0 gap error, 0 overlap error. Topologi VALID."
            )
        elif action == 'approve-integration':
            self.iface.messageBar().pushSuccess(
                'Integrasi Disetujui',
                f"Superadmin telah menyetujui integrasi '{rec_name}'. Layer kini tersedia di Katalog IGT!"
            )
        elif action == 'revision-submitted':
            self.iface.messageBar().pushInfo(
                'Revisi Diajukan Kembali',
                f"Perbaikan data untuk pengajuan '{rec_id}' telah dikirim kembali ke antrean verifikasi."
            )

    def on_upload_submitted(self, record):
        SUBMISSIONS.insert(0, record)
        self.dock.management_page.submissions = list(SUBMISSIONS)
        self.dock.management_page._render_table()
        self.dock.show_management(record.get('category', 'igt-utama'))
        rec_name = record.get('name') or record.get('layer', 'Layer')
        rec_id = record.get('id', '')
        if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'Unggah Berhasil',
                f"Pengajuan '{rec_name}' ({rec_id}) berhasil didaftarkan dengan status 'Diajukan'!"
            )

    def on_run_model(self, model):
        # Tambahkan layer hasil analisis ke QGIS
        output_name = f"[Hasil Analisis] {model['name']}"
        mem_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", output_name, "memory")
        if mem_layer.isValid():
            pr = mem_layer.dataProvider()
            pr.addAttributes([QgsField("model"), QgsField("kategori"), QgsField("status")])
            mem_layer.updateFields()
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromWkt(
                "POLYGON((110.36 -7.76, 110.39 -7.76, 110.39 -7.79, 110.36 -7.79, 110.36 -7.76))"
            ))
            feat.setAttributes([model['name'], model['category'], "Selesai"])
            pr.addFeatures([feat])
            mem_layer.updateExtents()
            QgsProject.instance().addMapLayer(mem_layer)
            if hasattr(self.iface, 'mapCanvas') and self.iface.mapCanvas():
                self.iface.mapCanvas().setExtent(mem_layer.extent())
                self.iface.mapCanvas().refresh()

        if hasattr(self.iface, 'messageBar') and self.iface.messageBar():
            self.iface.messageBar().pushSuccess(
                'Model Berhasil Dijalankan',
                f"Model '{model['name']}' berhasil dieksekusi! Layer spasial hasil pemodelan telah ditambahkan ke kanvas."
            )

# -*- coding: utf-8 -*-
"""Halaman login IGT-PR sebagai widget Qt, dibuat mengikuti mockup HTML (shared/login/index.html).

Pemetaan dari HTML ke Qt:
- CSS                -> Qt Style Sheet (QSS) di LOGIN_QSS
- box-shadow         -> QGraphicsDropShadowEffect
- ilustrasi & ikon   -> SVG yang dirender QSvgRenderer (lihat assets.py)
- dekorasi latar     -> digambar QPainter di LoginPage.paintEvent
- media query        -> LoginPage._relayout() dipanggil dari resizeEvent
"""

import os

from qgis.PyQt.QtCore import QByteArray, QPointF, QRectF, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import (
    QBrush, QColor, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient,
)
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.PyQt.QtWidgets import (
    QDockWidget, QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import CONTOUR_SVG, ICONS, ILLUSTRATION_SVG, Q_ICON

NAVY = '#123a86'
PIXEL_RATIO = 2  # pixmap dirender 2x supaya tetap tajam di layar HiDPI

# Batas lebar (px) untuk tata letak responsif, setara media query di versi HTML.
NARROW = 560
VERY_NARROW = 360

FEATURES = [
    ('layers', '#1f6fd6', '#e2eefc', 'Akses Data Terintegrasi',
     'Mengakses data IGT-PR secara langsung di lingkungan QGIS.'),
    ('pin', '#24914a', '#e3f4e6', 'Visualisasi Tematik',
     'Menampilkan data tematik dalam bentuk peta yang interaktif dan informatif.'),
    ('gear', '#7a46cf', '#eee6fb', 'Mendukung Analisis Spasial',
     'Mempermudah analisis dan pengolahan data spasial untuk pengambilan keputusan.'),
    ('link', '#18888c', '#e0f3f3', 'Integrasi Langsung',
     'Terhubung dengan Geoportal IGT-PR secara aman dan efisien.'),
    ('shield', '#1c5fc0', '#e4edfa', 'Mudah Digunakan',
     'Antarmuka sederhana dan intuitif untuk mendukung produktivitas pengguna.'),
]

LOGIN_QSS = f"""
QLabel {{ color: #3f5675; font-family: "Segoe UI", Arial, sans-serif; background: transparent; }}
QLabel#title {{ color: {NAVY}; font-size: 22px; font-weight: bold; }}
QLabel#title[compact="true"] {{ font-size: 18px; }}
QLabel#intro {{ font-size: 13px; }}
QLabel#sectionTitle {{ color: {NAVY}; font-size: 19px; font-weight: bold; }}
QLabel#featureTitle {{ color: {NAVY}; font-size: 13px; font-weight: bold; }}
QLabel#featureText {{ color: #5b6f8a; font-size: 12px; }}
QLabel#hint {{ color: #6b7f9a; font-size: 11px; }}
QLabel#copyright {{ color: #4b5f7c; font-size: 13px; }}
QPushButton#loginButton {{
    color: white;
    font-size: 20px;
    font-weight: bold;
    letter-spacing: 1px;
    border: none;
    border-radius: 14px;
    padding: 16px 20px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1f6fd6, stop:1 #0f58c4);
}}
QPushButton#loginButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a63c7, stop:1 #0b4cad);
}}
QPushButton#loginButton:pressed {{ background: #0b4cad; }}
QPushButton#loginButton:focus {{ border: 3px solid #9cc6ff; }}
QPushButton#adminLoginButton {{
    color: #174a91; font-size: 11px; font-weight: 600;
    border: 1px solid #b8cce7; border-radius: 8px;
    padding: 7px 12px; background: rgba(255, 255, 255, 220);
}}
QPushButton#adminLoginButton:hover {{ background: #eaf3ff; border-color: #7da8df; }}
QPushButton#guideButton {{
    color: #174a91; font-size: 13px; font-weight: 600;
    border: 1px solid #b8cce7; border-radius: 8px;
    padding: 9px 14px; background: rgba(255, 255, 255, 225);
}}
QPushButton#guideButton:hover {{ background: #eaf3ff; border-color: #7da8df; }}
"""


def svg_pixmap(svg, size):
    """Render string SVG ke QPixmap berukuran logis `size` (QSize)."""
    pixmap = QPixmap(size * PIXEL_RATIO)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(QByteArray(svg.encode('utf-8'))).render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(PIXEL_RATIO)
    return pixmap


def circle_icon(svg, diameter, icon_size, background):
    """Ikon SVG di tengah lingkaran berwarna (ikon Fitur Utama)."""
    pixmap = QPixmap(QSize(diameter, diameter) * PIXEL_RATIO)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(PIXEL_RATIO, PIXEL_RATIO)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(background))
    painter.drawEllipse(QRectF(0, 0, diameter, diameter))
    offset = (diameter - icon_size) / 2
    QSvgRenderer(QByteArray(svg.encode('utf-8'))).render(painter, QRectF(offset, offset, icon_size, icon_size))
    painter.end()
    pixmap.setDevicePixelRatio(PIXEL_RATIO)
    return pixmap


def emblem_pixmap(diameter, logo_path=None):
    """Logo instansi bila file tersedia, selain itu lambang placeholder (globe dalam cincin emas)."""
    if logo_path and os.path.isfile(logo_path):
        logo = QPixmap(logo_path)
        if not logo.isNull():
            logo = logo.scaled(QSize(diameter, diameter) * PIXEL_RATIO, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
            logo.setDevicePixelRatio(PIXEL_RATIO)
            return logo
    pixmap = QPixmap(QSize(diameter, diameter) * PIXEL_RATIO)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.scale(PIXEL_RATIO, PIXEL_RATIO)
    ring = QRadialGradient(QPointF(diameter / 2, diameter / 2), diameter / 2)
    ring.setColorAt(0.70, QColor('#f2c14e'))
    ring.setColorAt(1.00, QColor('#e39a1f'))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(ring))
    painter.drawEllipse(QRectF(0, 0, diameter, diameter))
    painter.setBrush(QColor('white'))
    inset = diameter * 0.14
    painter.drawEllipse(QRectF(inset, inset, diameter - 2 * inset, diameter - 2 * inset))
    globe = diameter * 0.52
    offset = (diameter - globe) / 2
    QSvgRenderer(QByteArray(ICONS['globe'].format(color=NAVY).encode('utf-8'))).render(
        painter, QRectF(offset, offset, globe, globe))
    painter.end()
    pixmap.setDevicePixelRatio(PIXEL_RATIO)
    return pixmap


class SvgView(QWidget):
    """Menampilkan SVG selebar widget dengan rasio aspek tetap."""

    def __init__(self, svg, parent=None):
        super().__init__(parent)
        self._renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')), self)
        size = self._renderer.defaultSize()
        self._ratio = size.height() / size.width()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(200)

    def resizeEvent(self, event):
        self.setFixedHeight(round(self.width() * self._ratio))
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._renderer.render(painter, QRectF(self.rect()))


class AccentBar(QWidget):
    """Garis aksen hijau-biru di bawah judul."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 4)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        half = self.width() / 2
        painter.setBrush(QColor('#4cb860'))
        painter.drawRoundedRect(QRectF(0, 0, half + 2, 4), 2, 2)
        painter.setBrush(QColor('#1f6fd6'))
        painter.drawRoundedRect(QRectF(half, 0, half, 4), 2, 2)


class FeatureItem(QWidget):
    def __init__(self, icon, color, background, title, text, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        icon_label = QLabel(self)
        icon_label.setPixmap(circle_icon(ICONS[icon].format(color=color), 54, 27, background))
        layout.addWidget(icon_label)
        layout.addSpacing(4)
        for object_name, value in (('featureTitle', title), ('featureText', text)):
            label = QLabel(value, self)
            label.setObjectName(object_name)
            label.setWordWrap(True)
            layout.addWidget(label)
        layout.addStretch()



class BrandHeader(QWidget):
    """Header kiri atas dengan logo BPN dan IGT-PR serta pola garis diagonal halus."""

    def __init__(self, bpn_logo_path=None, igtpr_logo_path=None, parent=None):
        super().__init__(parent)
        self.bpn_logo_path = bpn_logo_path
        self.igtpr_logo_path = igtpr_logo_path
        # Header harus tembus pandang agar dekorasi background LoginPage tetap terlihat.
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.setMinimumHeight(76)
        self.setMaximumHeight(112)
        self._bpn = QLabel(self)
        self._igtpr = QLabel(self)
        self._brand_title = QLabel('GEOPORTAL IGT-PR', self)
        self._brand_title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._brand_title.setWordWrap(True)
        self._bpn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._igtpr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)
        self._layout.addWidget(self._bpn, 0, Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(self._igtpr, 0, Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(self._brand_title, 1)
        self._refresh_logos()

    def _load_logo(self, path, max_size):
        if path and os.path.isfile(path):
            if path.lower().endswith('.svg'):
                renderer = QSvgRenderer(path)
                if renderer.isValid():
                    pixmap = QPixmap(max_size)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter, QRectF(0, 0, max_size.width(), max_size.height()))
                    painter.end()
                    return pixmap
            else:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(max_size, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        return QPixmap()

    def _refresh_logos(self):
        compact = self.width() < 470
        height = max(32, min(44 if compact else 68, self.height() - 12))
        self._bpn.setPixmap(self._load_logo(self.bpn_logo_path, QSize(height, height)))
        self._igtpr.setPixmap(self._load_logo(self.igtpr_logo_path, QSize(height, height)))
        self._bpn.setFixedSize(height, height)
        self._igtpr.setFixedSize(height, height)
        self._brand_title.setStyleSheet(
            'color: #080b12; font-family: "Segoe UI", Arial, sans-serif; '
            'font-size: %dpx; font-weight: 500; background: transparent;' % (16 if compact else 26))

    def resizeEvent(self, event):
        self._refresh_logos()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Tidak mengecat bidang latar; tampilkan background induk melalui header."""
        # Sengaja kosong agar background induk terlihat di belakang logo.
        return


class LoginPage(QWidget):
    """Halaman pertama plugin sebelum pengguna masuk."""

    loginRequested = pyqtSignal()
    adminLoginRequested = pyqtSignal()
    guideRequested = pyqtSignal()

    def __init__(self, logo_path=None, igtpr_logo_path=None, qgis_icon_path=None, parent=None):
        super().__init__(parent)
        self.qgis_icon_path = qgis_icon_path
        self.setObjectName('loginPage')
        self.setStyleSheet(LOGIN_QSS)
        self._layout_mode = None
        self._contour = QSvgRenderer(QByteArray(CONTOUR_SVG.encode('utf-8')), self)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 26, 24, 0)
        root.setSpacing(0)

        # Header branding: logo BPN, logo IGT-PR, dan judul seperti contoh visual.
        root.addWidget(BrandHeader(logo_path, igtpr_logo_path, self))

        root.addSpacing(22)
        root.addWidget(AccentBar(self))
        root.addSpacing(14)
        intro = QLabel(
            'Integrasi Plugin QGIS dengan Geoportal IGT-PR memudahkan pengguna mengakses, memvisualisasikan, '
            'dan mengelola data Informasi Geospasial Tematik Pertanahan dan Ruang secara langsung melalui QGIS.',
            self)
        intro.setObjectName('intro')
        intro.setWordWrap(True)
        root.addWidget(intro)

        # Hero: ilustrasi + tombol LOGIN (posisinya diatur _relayout)
        root.addSpacing(18)
        self._hero = QGridLayout()
        self._hero.setHorizontalSpacing(18)
        self._hero.setVerticalSpacing(10)
        self._illustration = SvgView(ILLUSTRATION_SVG, self)
        self._login_box = self._build_login_box()
        root.addLayout(self._hero)

        # Fitur Utama
        root.addSpacing(18)
        root.addWidget(AccentBar(self))
        root.addSpacing(12)
        section = QLabel('Fitur Utama', self)
        section.setObjectName('sectionTitle')
        root.addWidget(section)
        root.addSpacing(16)
        self._features_grid = QGridLayout()
        self._features_grid.setHorizontalSpacing(16)
        self._features_grid.setVerticalSpacing(20)
        self._features = [FeatureItem(*feature, parent=self) for feature in FEATURES]
        root.addLayout(self._features_grid)

        # Footer; tombol Panduan diletakkan di atas informasi copyright.
        root.addStretch(1)
        root.addSpacing(30)
        footer = QVBoxLayout()
        footer.setContentsMargins(0, 0, 0, 112)
        footer.setSpacing(6)

        guide_button = QPushButton('Panduan', self)
        guide_button.setObjectName('guideButton')
        guide_button.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_button.setToolTip('Buka panduan penggunaan Geoportal IGT-PR')
        guide_button.clicked.connect(self.guideRequested)
        self.guide_button = guide_button
        footer.addWidget(guide_button, 0, Qt.AlignmentFlag.AlignLeft)

        # Bungkus ikon dan teks dalam widget mandiri yang ukurannya mengikuti konten.
        # Widget ini diratakan ke kiri agar layout footer tidak mendorong copyright ke kanan.
        copyright_container = QWidget(self)
        copyright_container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        copyright_row = QHBoxLayout(copyright_container)
        copyright_row.setContentsMargins(0, 0, 0, 0)
        copyright_row.setSpacing(0)

        globe = QLabel(copyright_container)
        globe.setPixmap(svg_pixmap(ICONS['globe'].format(color=NAVY), QSize(22, 22)))
        globe.setAlignment(Qt.AlignmentFlag.AlignTop)
        copyright_label = QLabel(
            'Copyright © 2026 Kementerian Agraria dan\nTata Ruang / Badan Pertanahan Nasional',
            copyright_container,
        )
        copyright_label.setObjectName('copyright')
        copyright_label.setWordWrap(True)
        copyright_label.setMaximumWidth(360)
        copyright_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        copyright_row.addWidget(globe, 0, Qt.AlignmentFlag.AlignTop)
        copyright_row.addWidget(copyright_label, 0, Qt.AlignmentFlag.AlignTop)
        footer.addWidget(
            copyright_container, 0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        root.addLayout(footer)

        self._relayout(self.width())

    def _build_login_box(self):
        box = QWidget(self)
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addStretch()
        button = QPushButton('  LOGIN    →', box)
        button.setObjectName('loginButton')
        button.setIcon(QIcon(self.qgis_icon_path) if self.qgis_icon_path and os.path.isfile(self.qgis_icon_path) else QIcon(svg_pixmap(Q_ICON.format(color='white'), QSize(30, 30))))
        button.setIconSize(QSize(30, 30))
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(64)
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(26)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(15, 88, 196, 90))
        button.setGraphicsEffect(shadow)
        button.clicked.connect(self.loginRequested)
        self.login_button = button
        layout.addWidget(button)

        # Hint SSO dan tombol administrator ditempatkan berdampingan dalam satu baris.
        secondary_row = QHBoxLayout()
        secondary_row.setContentsMargins(0, 0, 0, 0)
        secondary_row.setSpacing(8)

        hint = QLabel('Masuk dengan SSO', box)
        hint.setObjectName('hint')
        hint.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hint.setWordWrap(True)
        secondary_row.addWidget(hint, 1)

        admin_button = QPushButton('Administator', box)
        admin_button.setObjectName('adminLoginButton')
        admin_button.setCursor(Qt.CursorShape.PointingHandCursor)
        admin_button.setToolTip('Login khusus administrator')
        admin_button.clicked.connect(self.adminLoginRequested)
        self.admin_login_button = admin_button
        secondary_row.addWidget(admin_button, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(secondary_row)
        layout.addStretch()
        return box

    # ------------------------------------------------------------------ tata letak responsif
    def resizeEvent(self, event):
        self._relayout(event.size().width())
        super().resizeEvent(event)

    def _relayout(self, width):
        if width >= NARROW:
            mode = 'wide'
        elif width >= VERY_NARROW:
            mode = 'narrow'
        else:
            mode = 'very-narrow'
        if mode == self._layout_mode:
            return
        self._layout_mode = mode

        # Ukuran judul branding ditangani responsif oleh BrandHeader.

        # Hero: berdampingan bila lebar, tombol LOGIN di atas ilustrasi bila sempit.
        for widget in (self._illustration, self._login_box):
            self._hero.removeWidget(widget)
        for column in range(2):
            self._hero.setColumnStretch(column, 0)
        if mode == 'wide':
            self._hero.addWidget(self._illustration, 0, 0)
            self._hero.addWidget(self._login_box, 0, 1)
            self._hero.setColumnStretch(0, 5)
            self._hero.setColumnStretch(1, 4)
        else:
            self._hero.addWidget(self._login_box, 0, 0)
            self._hero.addWidget(self._illustration, 1, 0)
            self._hero.setColumnStretch(0, 1)

        # Fitur Utama: 3, 2 atau 1 kolom.
        columns = {'wide': 3, 'narrow': 2, 'very-narrow': 1}[mode]
        for item in self._features:
            self._features_grid.removeWidget(item)
        for column in range(3):
            self._features_grid.setColumnStretch(column, 1 if column < columns else 0)
        for index, item in enumerate(self._features):
            self._features_grid.addWidget(item, index // columns, index % columns)

    # ------------------------------------------------------------------ dekorasi latar
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        base = QLinearGradient(0, 0, 0, h)
        base.setColorAt(0.0, QColor('#f7fbff'))
        base.setColorAt(0.55, QColor('#eef5fc'))
        base.setColorAt(1.0, QColor('#f6faff'))
        painter.fillRect(self.rect(), base)

        glow = QRadialGradient(QPointF(0, h * 0.35), w * 0.7)
        glow.setColorAt(0, QColor(220, 236, 251, 200))
        glow.setColorAt(1, QColor(220, 236, 251, 0))
        painter.fillRect(self.rect(), glow)

        # Lingkaran di kanan atas dan cincin di sisi kanan
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(191, 220, 247, 150))
        painter.drawEllipse(QPointF(w + 25, 45), 115, 115)
        painter.setBrush(QColor(159, 213, 154, 140))
        painter.drawEllipse(QPointF(w - 150, 5), 85, 85)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(169, 209, 242, 110), 30))
        painter.drawEllipse(QPointF(w + 10, h * 0.45), 85, 85)

        # Garis kontur di kanan atas
        self._contour.render(painter, QRectF(w * 0.3, -30, w * 0.7 + 40, 560))

        self._paint_scene(painter, w, h)

    def _paint_scene(self, painter, w, h):
        """Bukit, gedung dan pin lokasi di bagian bawah halaman."""
        top = h - 130
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor('#cfe2f4'))
        right = w - 120
        for dx, dy, bw in ((-200, 50, 18), (-178, 66, 14), (-160, 40, 16), (-140, 60, 20), (-116, 54, 14),
                           (-98, 70, 18)):
            painter.drawRect(QRectF(right + dx, top + dy, bw, 130 - dy))

        def hill(color, points):
            path = QPainterPath(QPointF(*points[0]))
            for c1, c2, end in points[1]:
                path.cubicTo(QPointF(*c1), QPointF(*c2), QPointF(*end))
            path.lineTo(points[2])
            path.closeSubpath()
            painter.setBrush(QColor(color))
            painter.drawPath(path)

        hill('#d8ecd9', ((w * 0.45, h), [((w * 0.6, top + 40), (w * 0.75, top + 30), (w, top + 25))], QPointF(w, h)))
        hill('#bfe0c4', ((w * 0.55, h), [((w * 0.68, top + 70), (w * 0.82, top + 64), (w, top + 62))], QPointF(w, h)))
        hill('#a8d2f0', ((w * 0.68, h), [((w * 0.78, top + 100), (w * 0.86, top + 88), (w, top + 85))], QPointF(w, h)))
        hill('#1f6fd6', ((0, top + 62), [((w * 0.15, top + 92), (w * 0.27, top + 115), (w * 0.42, h))], QPointF(0, h)))
        hill('#6cc46a', ((0, top + 95), [((w * 0.1, top + 110), (w * 0.2, top + 122), (w * 0.3, h))], QPointF(0, h)))

        # Pin lokasi
        cx, cy = w - 54, top + 30
        pin = QPainterPath(QPointF(cx, cy + 30))
        pin.cubicTo(cx - 6, cy + 22, cx - 16, cy + 12, cx - 16, cy)
        pin.arcTo(QRectF(cx - 16, cy - 16, 32, 32), 180, -180)
        pin.cubicTo(cx + 16, cy + 12, cx + 6, cy + 22, cx, cy + 30)
        painter.setBrush(QColor('#4f9be8'))
        painter.drawPath(pin)
        painter.setBrush(QColor('white'))
        painter.drawEllipse(QPointF(cx, cy), 5, 5)


class LoginDockWidget(QDockWidget):
    """Dock plugin yang berisi LoginPage di dalam area gulir."""

    def __init__(self, logo_path=None, igtpr_logo_path=None, qgis_icon_path=None, parent=None):
        super().__init__('IGT-PR', parent)
        self.setObjectName('IgtprLoginExampleDock')
        self.page = LoginPage(logo_path, igtpr_logo_path, qgis_icon_path)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.page)
        self.setWidget(scroll)
        self.setMinimumWidth(300)

# -*- coding: utf-8 -*-
"""Komponen UI responsif bersama untuk halaman aplikasi Geoportal IGT-PR (Mockup V2).

Qt tidak punya media query seperti CSS. Penggantinya di sini:
- ResponsivePage meneruskan lebar halaman (= lebar dock) ke setiap komponen terdaftar lewat
  apply_width(width), setiap kali dock dipersempit atau dilebarkan.
- ResponsiveGrid menyusun ulang kartu menjadi 1..N kolom sesuai breakpoint.
- ResponsiveBox membalik arah tata letak (berdampingan <-> bertumpuk).
- FlowLayout membungkus tombol/chip ke baris berikutnya bila tidak muat.

Breakpoint selalu dihitung dari lebar halaman, bukan lebar komponen itu sendiri. Lebar komponen
bisa "tertahan" oleh minimum size anak-anaknya, sehingga tidak bisa dipakai untuk memutuskan
kapan harus bertumpuk.

Semua gaya memakai selector properti (mis. QLabel[cls="h2"], QFrame[card="plain"]) supaya tidak
bocor ke widget anak. Catatan penting: QLabel adalah turunan QFrame, jadi selector "QFrame {...}"
tanpa properti/objectName akan ikut memberi border dan padding ke semua label di dalamnya.
"""

from qgis.PyQt.QtCore import QPoint, QRect, QSize, Qt, pyqtSignal
from qgis.PyQt.QtGui import QFontDatabase, QIcon
from qgis.PyQt.QtWidgets import (
    QApplication, QBoxLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLayout, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .login_page import svg_pixmap

# Urutan font mengikuti mockup web (Inter, lalu font sistem).
_FONT_CANDIDATES = ('Inter', 'Segoe UI', 'Noto Sans', 'Ubuntu', 'Cantarell', 'Helvetica Neue', 'Arial',
                    'DejaVu Sans')
_font_family = None


def ui_font_family():
    """Font pertama yang terpasang dari daftar kandidat (QSS Qt5 hanya membaca satu family)."""
    global _font_family
    if _font_family is None:
        families = set(QFontDatabase().families())
        _font_family = next((f for f in _FONT_CANDIDATES if f in families), QApplication.font().family())
    return _font_family


THEME_QSS = """
* { font-family: "@FONT@"; font-size: 12px; color: #0f294d; }
QWidget#pageContent, QWidget#appPage { background: #f3f6fb; }
QScrollArea#pageScroll { background: #f3f6fb; border: none; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #c7d3e2; border-radius: 4px; min-height: 32px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: #9fb2c9; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
QToolTip { color: #0f294d; background: #ffffff; border: 1px solid #cbd5e1; }

/* ---------- Teks ---------- */
QLabel { background: transparent; }
QLabel[cls="eyebrow"] {
    background: rgba(255, 255, 255, 40); color: #e0ecff; border: 1px solid rgba(255, 255, 255, 70);
    border-radius: 9px; padding: 2px 9px; font-size: 9px; font-weight: 800;
}
QLabel[cls="heroTitle"] { color: #ffffff; font-size: 20px; font-weight: 800; }
QLabel[cls="heroDesc"] { color: #dbe8fb; font-size: 12px; }
QLabel[cls="h2"] { color: #0f294d; font-size: 15px; font-weight: 800; }
QLabel[cls="h3"] { color: #0f294d; font-size: 13px; font-weight: 800; }
QLabel[cls="body"] { color: #334155; font-size: 12px; }
QLabel[cls="muted"] { color: #5b6f8a; font-size: 11px; }
QLabel[cls="caption"] { color: #475569; font-size: 10px; font-weight: 800; }
QLabel[cls="statLabel"] { color: #0f294d; font-size: 10px; font-weight: 800; }
QLabel[cls="statNum"] { color: #0f294d; font-size: 26px; font-weight: 900; }
QLabel[cls="hubItem"] { color: #0f294d; font-size: 12px; font-weight: 700; }
QLabel[cls="kvKey"] { color: #64748b; font-size: 10px; font-weight: 800; }
QLabel[cls="kvVal"] { color: #0f294d; font-size: 12px; }
QLabel[cls="rowTitle"] { color: #0f294d; font-size: 13px; font-weight: 700; }
QLabel[cls="cell"] { color: #334155; font-size: 11px; }
QLabel[cls="cellMuted"] { color: #64748b; font-size: 11px; }
QLabel[cls="thead"] { color: #334155; font-size: 10px; font-weight: 800; }
QLabel[cls="branch"] { color: #94a3b8; font-size: 12px; font-weight: 800; }
QLabel[cls="subTitle"] { color: #1e293b; font-size: 12px; font-weight: 600; }
QLabel[cls="calloutTitle"] { color: #0369a1; font-size: 11px; font-weight: 700; }
QLabel[cls="calloutText"] { color: #334155; font-size: 11px; }
QLabel[cls="dzTitle"] { color: #0f294d; font-size: 13px; font-weight: 800; }
QLabel[cls="picked"] { color: #047857; font-size: 12px; font-weight: 700; }
QLabel[cls="filterLabel"] { color: #c7dbf7; font-size: 9px; font-weight: 800; }
QLabel[cls="mbTitle"] { color: #2e1065; font-size: 14px; font-weight: 800; }
QLabel[cls="mbDesc"] { color: #5b4a86; font-size: 11px; }
QLabel[cls="logoutTitle"] { color: #7f1d1d; font-size: 14px; font-weight: 800; }
QLabel[cls="logoutDesc"] { color: #9f4a4a; font-size: 11px; }
QLabel[cls="footer"] { color: #94a3b8; font-size: 10px; }

/* ---------- Pill / badge ---------- */
QLabel[pill] { border-radius: 5px; padding: 1px 7px; font-size: 10px; font-weight: 700; }
QLabel[pill="amber"] { background: #fef3c7; color: #b45309; }
QLabel[pill="green"] { background: #d1fae5; color: #047857; }
QLabel[pill="blue"] { background: #dbeafe; color: #1d4ed8; }
QLabel[pill="sky"] { background: #e0f2fe; color: #0369a1; }
QLabel[pill="red"] { background: #ffe4e6; color: #be123c; }
QLabel[pill="violet"] { background: #ede9fe; color: #6d28d9; }
QLabel[pill="slate"] { background: #f1f5f9; color: #475569; }
QLabel[pill="idGreen"] { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; font-size: 11px; }
QLabel[pill="count"] { background: #d1fae5; color: #047857; border-radius: 6px; font-size: 9px; padding: 1px 5px; }

/* ---------- Kartu ---------- */
QFrame[card="plain"] { background: #ffffff; border: 1px solid #dce6f2; border-radius: 14px; }
QFrame[card="sky"] { background: #ffffff; border: 1px solid #bae6fd; border-radius: 14px; }
QFrame[card="green"] { background: #ffffff; border: 1px solid #bbf7d0; border-radius: 14px; }
QFrame[card="headSky"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f2fe, stop:1 #f0f9ff);
    border: none; border-bottom: 1px solid #bae6fd;
    border-top-left-radius: 13px; border-top-right-radius: 13px;
}
QFrame[card="headBlue"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eaf3ff, stop:1 #f7fbff);
    border: none; border-bottom: 1px solid #dce6f2;
    border-top-left-radius: 13px; border-top-right-radius: 13px;
}
QFrame[card="headGreen"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e9fbf1, stop:1 #f7fdf9);
    border: none; border-bottom: 1px solid #d1f2df;
    border-top-left-radius: 13px; border-top-right-radius: 13px;
}
QFrame[card="statAmber"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fffbeb, stop:1 #ffffff);
    border: 1px solid #fde68a; border-radius: 14px;
}
QFrame[card="statGreen"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ecfdf5, stop:1 #ffffff);
    border: 1px solid #a7f3d0; border-radius: 14px;
}
QFrame[card="statBlue"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eff6ff, stop:1 #ffffff);
    border: 1px solid #bfdbfe; border-radius: 14px;
}
QFrame[card="statRed"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff1f2, stop:1 #ffffff);
    border: 1px solid #fecdd3; border-radius: 14px;
}
QFrame[card="hub"] { background: #f4f9ff; border: 1px solid #d6e8fb; border-radius: 10px; }
QFrame[card="hub"]:hover { background: #ffffff; border-color: #1f6fd6; }
QFrame[card="hubGreen"] { background: #f4fbf7; border: 1px solid #d4efdf; border-radius: 10px; }
QFrame[card="hubGreen"]:hover { background: #ffffff; border-color: #059669; }
QFrame[card="mb"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f5f3ff, stop:1 #fbfaff);
    border: 1px solid #e4dcfd; border-radius: 14px;
}
QFrame[card="mb"]:hover { border-color: #7c3aed; }
QFrame[card="logout"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fff5f5, stop:1 #fffafa);
    border: 1px solid #fde0e0; border-radius: 14px;
}
QFrame[card="logout"]:hover { border-color: #f87171; }
QFrame[card="callout"] {
    background: #f0f9ff; border: 1px solid #bae6fd; border-left: 4px solid #0284c7; border-radius: 10px;
}
QFrame[card="dropzone"] {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f3f8ff, stop:1 #fbfdff);
    border: 2px dashed #bcd6f5; border-radius: 14px;
}
QFrame[card="seg"] { background: #ffffff; border: 1px solid #dbeafe; border-radius: 12px; }
QFrame[card="segSoft"] { background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 12px; }
QFrame[card="table"] { background: #ffffff; border: 1px solid #dbe7f3; border-radius: 12px; }
QFrame[card="thead"] {
    background: #eaf4ff; border: none; border-bottom: 1px solid #cfe3f7;
    border-top-left-radius: 11px; border-top-right-radius: 11px;
}
QFrame[card="theadGreen"] {
    background: #ecfdf3; border: none; border-bottom: 1px solid #ccefdc;
    border-top-left-radius: 11px; border-top-right-radius: 11px;
}
QFrame[card="row"] { background: transparent; border: none; border-bottom: 1px solid #eef2f7; }
QFrame[card="subRow"] { background: #f8fbff; border: none; border-bottom: 1px solid #eef2f7; }
QFrame[card="kvCard"] { background: #ffffff; border: none; border-bottom: 1px solid #e5edf6; }
QFrame[card="subCard"] { background: #f8fbff; border: 1px solid #e2ecf7; border-radius: 10px; }
QFrame[card="heroFilter"] {
    background: rgba(255, 255, 255, 30); border: 1px solid rgba(255, 255, 255, 60); border-radius: 12px;
}
QFrame[card="modelCard"] { background: #ffffff; border: 1px solid #e4dcfd; border-radius: 14px; }
QFrame[card="chipMulti"] { background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 8px; }
QFrame[card="chipMulti"]:hover { background: #d1fae5; border-color: #10b981; }
QFrame[card="chipMulti"][open="true"] { background: #d1fae5; border-color: #10b981; }
QFrame[card="divider"] { background: #e5edf6; border: none; max-height: 1px; min-height: 1px; }

QFrame[hero="blue"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10306a, stop:1 #1e4f9c); border-radius: 16px;
}
QFrame[hero="catalog"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b4a7f, stop:1 #0479b7); border-radius: 16px;
}
QFrame[hero="upload"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #173c86, stop:1 #2563eb); border-radius: 16px;
}
QFrame[hero="green"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b5a3c, stop:1 #15803d); border-radius: 16px;
}
QFrame[hero="violet"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b1a7a, stop:1 #6d28d9); border-radius: 16px;
}

/* ---------- Tombol ---------- */
QPushButton[btn] { font-weight: 700; }
QPushButton[btn="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1d4fa8, stop:1 #2563eb);
    color: #ffffff; border: none; border-radius: 9px; padding: 9px 16px; font-size: 12px;
}
QPushButton[btn="primary"]:hover { background: #1d4ed8; }
QPushButton[btn="primary"]:pressed { background: #1e40af; }
QPushButton[btn="link"] {
    background: #f1f5f9; color: #1d4fa8; border: 1px solid #e2e8f0; border-radius: 9px;
    padding: 8px 14px; font-size: 12px; text-decoration: underline;
}
QPushButton[btn="link"]:hover { background: #e2e8f0; }
QPushButton[btn="heroBack"] {
    background: rgba(255, 255, 255, 36); color: #ffffff; border: 1px solid rgba(255, 255, 255, 90);
    border-radius: 10px; padding: 8px 14px; font-size: 12px; text-align: left;
}
QPushButton[btn="heroBack"]:hover { background: rgba(255, 255, 255, 60); }
QPushButton[btn="soft"] {
    background: #eef6ff; color: #1f6fd6; border: 1px solid #cfe3fb; border-radius: 9px;
    padding: 5px 12px; font-size: 11px;
}
QPushButton[btn="soft"]:hover { background: #1f6fd6; color: #ffffff; border-color: #1f6fd6; }
QPushButton[btn="softGreen"] {
    background: #f0fdf4; color: #047857; border: 1px solid #bbf7d0; border-radius: 9px;
    padding: 5px 12px; font-size: 11px;
}
QPushButton[btn="softGreen"]:hover { background: #dcfce7; border-color: #4ade80; }
QPushButton[btn="softRed"] {
    background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; border-radius: 9px;
    padding: 5px 12px; font-size: 11px;
}
QPushButton[btn="softRed"]:hover { background: #ffe4e6; }
QPushButton[btn="solidGreen"] {
    background: #047857; color: #ffffff; border: none; border-radius: 9px; padding: 6px 12px; font-size: 11px;
}
QPushButton[btn="solidGreen"]:hover { background: #065f46; }
QPushButton[btn="solidBlue"] {
    background: #1f6fd6; color: #ffffff; border: none; border-radius: 9px; padding: 6px 12px; font-size: 11px;
}
QPushButton[btn="solidBlue"]:hover { background: #1a5fc0; }
QPushButton[btn="run"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed);
    color: #ffffff; border: none; border-radius: 9px; padding: 7px 14px; font-size: 11px;
}
QPushButton[btn="run"]:hover { background: #5b21b6; }
QPushButton[btn="seg"], QPushButton[btn="segGreen"] {
    background: transparent; color: #0f294d; border: 1px solid transparent; border-radius: 9px;
    padding: 7px 8px; font-size: 12px;
}
QPushButton[btn="seg"] { background: #f5f9ff; border-color: #e3eefb; }
QPushButton[btn="seg"]:hover { background: #e8f2fe; }
QPushButton[btn="seg"]:checked { background: #0369a1; color: #ffffff; border-color: #0369a1; }
QPushButton[btn="segGreen"]:hover { background: #e2e8f0; }
QPushButton[btn="segGreen"]:checked { background: #15803d; color: #ffffff; border-color: #15803d; }

/* ---------- Input ---------- */
QLineEdit[field="true"], QComboBox[field="true"] {
    background: #f8fafc; border: 1px solid #d5e0ec; border-radius: 9px; padding: 7px 10px;
    font-size: 12px; color: #0f294d;
}
QLineEdit[field="true"]:focus, QComboBox[field="true"]:focus { border-color: #1f6fd6; background: #ffffff; }
QComboBox[field="true"]::drop-down { border: none; width: 24px; }
QComboBox[field="hero"] {
    background: transparent; border: none; color: #ffffff; font-size: 13px; font-weight: 800; padding: 2px 0;
}
QComboBox[field="hero"]::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #ffffff; color: #0f294d; border: 1px solid #cbd5e1;
    selection-background-color: #eff6ff; selection-color: #1f6fd6;
}
"""


def theme_qss():
    return THEME_QSS.replace('@FONT@', ui_font_family())


def repolish(widget):
    """Terapkan ulang QSS setelah properti dinamis berubah."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def icon(key, color, size=16):
    return QIcon(svg_pixmap(ICONS[key].format(color=color), QSize(size, size)))


# ---------------------------------------------------------------- pembuat widget sederhana
def label(text, cls='body', wrap=True, parent=None):
    lbl = QLabel(text, parent)
    lbl.setProperty('cls', cls)
    lbl.setWordWrap(wrap)
    return lbl


def pill(text, kind='slate', parent=None):
    lbl = QLabel(text, parent)
    lbl.setProperty('pill', kind)
    lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lbl


def button(text, kind='soft', icon_key=None, icon_color=None, parent=None):
    btn = QPushButton(text, parent)
    btn.setProperty('btn', kind)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if icon_key:
        btn.setIcon(icon(icon_key, icon_color or '#1f6fd6', 16))
        btn.setIconSize(QSize(14, 14))
    return btn


def card(kind='plain', parent=None):
    frame = QFrame(parent)
    frame.setProperty('card', kind)
    return frame


def icon_badge(icon_key, color, background, box=40, glyph=22, radius=11, parent=None):
    """Ikon di dalam kotak membulat berwarna (seperti .hub-badge di web)."""
    lbl = QLabel(parent)
    lbl.setFixedSize(box, box)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setPixmap(svg_pixmap(ICONS[icon_key].format(color=color), QSize(glyph, glyph)))
    lbl.setStyleSheet(f'QLabel {{ background: {background}; border-radius: {radius}px; }}')
    return lbl


def icon_label(icon_key, color, size=16, parent=None):
    lbl = QLabel(parent)
    lbl.setPixmap(svg_pixmap(ICONS[icon_key].format(color=color), QSize(size, size)))
    lbl.setFixedSize(size, size)
    return lbl


def field(widget):
    widget.setProperty('field', 'true')
    if hasattr(widget, 'setSizeAdjustPolicy'):
        # Combo boleh lebih sempit dari teks item terpanjang agar dock bisa dipersempit.
        widget.setSizeAdjustPolicy(widget.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        widget.setMinimumContentsLength(6)
    return widget


def clear_layout(layout):
    """Kosongkan layout; widget disembunyikan dulu agar tidak sempat tergambar bertumpuk."""
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.hide()
            w.setParent(None)
            w.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


# ---------------------------------------------------------------- komponen interaktif
class ClickableCard(QFrame):
    """QFrame yang bisa diklik dan punya efek hover via QSS.

    Dipakai menggantikan QPushButton berisi layout: QPushButton tidak menghitung ukuran dari
    layout anak, sehingga label di dalamnya terpotong.
    """

    clicked = pyqtSignal()

    def __init__(self, kind='hub', parent=None):
        super().__init__(parent)
        self.setProperty('card', kind)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def minimumSizeHint(self):
        return QSize(80, 32)


class HubItem(ClickableCard):
    """Baris tombol hub: ikon, label, chevron."""

    def __init__(self, icon_key, text, color='#1f6fd6', kind='hub', bold=True, parent=None):
        super().__init__(kind, parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(10)
        lay.addWidget(icon_label(icon_key, color, 18, self))
        lbl = label(text, 'hubItem' if bold else 'body', True, self)
        lay.addWidget(lbl, 1)
        lay.addWidget(icon_label('chevron-right', '#64748b', 14, self))

    def minimumSizeHint(self):
        return QSize(80, 32)


class ElidedLabel(QLabel):
    """Label satu baris yang memotong teks dengan '…' bila ruangnya sempit."""

    def __init__(self, text='', parent=None):
        super().__init__(parent)
        self._full = text
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setText(text)

    def set_full_text(self, text):
        self._full = text
        self._elide()

    def minimumSizeHint(self):
        return QSize(24, super().minimumSizeHint().height())

    def sizeHint(self):
        return QSize(self.fontMetrics().horizontalAdvance(self._full) + 4, super().sizeHint().height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._elide()

    def _elide(self):
        shown = self.fontMetrics().elidedText(self._full, Qt.TextElideMode.ElideRight, max(self.width(), 10))
        if shown != self.text():
            QLabel.setText(self, shown)
        self.setToolTip(self._full if shown != self._full else '')


# ---------------------------------------------------------------- tata letak responsif
class FlowLayout(QLayout):
    """Layout yang membungkus item ke baris berikutnya (setara flex-wrap)."""

    def __init__(self, parent=None, h_spacing=6, v_spacing=6, align_right=False):
        super().__init__(parent)
        self._items = []
        self._h = h_spacing
        self._v = v_spacing
        self._align_right = align_right
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        return size + QSize(m.left() + m.right(), m.top() + m.bottom())

    def _do_layout(self, rect, test_only):
        m = self.contentsMargins()
        area = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        rows, row, row_w, row_h = [], [], 0, 0
        for item in self._items:
            if item.widget() is not None and item.widget().isHidden():
                continue
            hint = item.sizeHint()
            w = min(hint.width(), area.width())
            if row and row_w + self._h + w > area.width():
                rows.append((row, row_w, row_h))
                row, row_w, row_h = [], 0, 0
            row_w = w if not row else row_w + self._h + w
            row.append((item, w, hint.height()))
            row_h = max(row_h, hint.height())
        if row:
            rows.append((row, row_w, row_h))
        y = area.y()
        for r_items, r_w, r_h in rows:
            x = area.x() + (area.width() - r_w if self._align_right else 0)
            for item, w, h in r_items:
                if not test_only:
                    item.setGeometry(QRect(QPoint(x, y + (r_h - h) // 2), QSize(w, h)))
                x += w + self._h
            y += r_h + self._v
        total = (y - self._v if rows else y) - rect.y() + m.bottom()
        return max(total, 0)


class ResponsiveGrid(QWidget):
    """Grid kartu dengan jumlah kolom berdasarkan breakpoint lebar halaman.

    breakpoints: daftar (lebar_halaman_minimum, jumlah_kolom), mis. [(720, 2), (0, 1)].
    """

    def __init__(self, breakpoints, spacing=12, parent=None):
        super().__init__(parent)
        self._bps = sorted(breakpoints, reverse=True)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(spacing)
        self._items = []
        self._cols = None
        self._last_width = 480

    def add(self, widget):
        # Ignored: lebar kolom murni dari stretch, jadi semua kolom sama lebar seperti CSS 1fr.
        widget.setSizePolicy(QSizePolicy.Policy.Ignored, widget.sizePolicy().verticalPolicy())
        self._items.append(widget)
        self._relayout(self._columns_for(self._last_width))
        return widget

    def clear(self):
        for w in self._items:
            self._grid.removeWidget(w)
            w.hide()
            w.setParent(None)
            w.deleteLater()
        self._items = []

    def _columns_for(self, width):
        return next((c for (min_w, c) in self._bps if width >= min_w), 1)

    def apply_width(self, width):
        self._last_width = width
        cols = self._columns_for(width)
        if cols != self._cols:
            self._relayout(cols)
        for w in self._items:
            if hasattr(w, 'apply_width'):
                w.apply_width(width)

    def _relayout(self, cols):
        self._cols = cols
        for w in self._items:
            self._grid.removeWidget(w)
        for i, w in enumerate(self._items):
            self._grid.addWidget(w, i // cols, i % cols)
        for c in range(6):
            self._grid.setColumnStretch(c, 1 if c < cols else 0)


class ResponsiveBox(QWidget):
    """Kotak yang berdampingan di halaman lebar dan bertumpuk di halaman sempit."""

    def __init__(self, breakpoint, spacing=12, parent=None):
        super().__init__(parent)
        self.breakpoint = breakpoint
        self.box = QBoxLayout(QBoxLayout.Direction.TopToBottom, self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.setSpacing(spacing)
        self.wide = False

    def apply_width(self, width):
        wide = width >= self.breakpoint
        if wide != self.wide:
            self.wide = wide
            self.box.setDirection(QBoxLayout.Direction.LeftToRight if wide else QBoxLayout.Direction.TopToBottom)


class ResponsivePage(QWidget):
    """Halaman bergulir yang meneruskan lebar dock ke komponen responsif terdaftar."""

    def __init__(self, object_name, parent=None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setProperty('page', 'true')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(theme_qss())
        self.page_width = 480
        self._responsive = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.scroll = QScrollArea(self)
        self.scroll.setObjectName('pageScroll')
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content = QWidget()
        self.content.setObjectName('pageContent')
        self.body = QVBoxLayout(self.content)
        self.body.setContentsMargins(14, 14, 14, 18)
        self.body.setSpacing(12)
        self.scroll.setWidget(self.content)
        outer.addWidget(self.scroll)

    def responsive(self, component):
        self._responsive.append(component)
        component.apply_width(self.page_width)
        return component

    def minimumSizeHint(self):
        return QSize(200, 120)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.page_width = event.size().width()
        m = 8 if self.page_width < 280 else (10 if self.page_width < 380 else 14)
        self.body.setContentsMargins(m, m, m, m + 4)
        for comp in list(self._responsive):
            comp.apply_width(self.page_width)

    def add_footer(self):
        self.body.addStretch(1)
        foot = label('Mockup UI plugin QGIS · data contoh', 'footer', False, self.content)
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body.addWidget(foot)


# ---------------------------------------------------------------- komponen berukuran sedang
class HeroHeader(QFrame):
    """Kartu hero berwarna: eyebrow, judul, deskripsi, dan widget samping (filter/tombol kembali)."""

    def __init__(self, eyebrow, title, desc, theme='blue', side_widget=None, breakpoint=640, parent=None):
        super().__init__(parent)
        self.setProperty('hero', theme)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(0)
        self.row = ResponsiveBox(breakpoint, 14, self)
        texts = QWidget(self.row)
        t_lay = QVBoxLayout(texts)
        t_lay.setContentsMargins(0, 0, 0, 0)
        t_lay.setSpacing(5)
        self.eyebrow = label(eyebrow, 'eyebrow', False, texts)
        self.eyebrow.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        t_lay.addWidget(self.eyebrow, 0, Qt.AlignmentFlag.AlignLeft)
        self.title = label(title, 'heroTitle', True, texts)
        t_lay.addWidget(self.title)
        self.desc = label(desc, 'heroDesc', True, texts)
        t_lay.addWidget(self.desc)
        texts.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.row.box.addWidget(texts, 1)
        if side_widget is not None:
            side_widget.setParent(self.row)
            self.row.box.addWidget(side_widget, 0)
        lay.addWidget(self.row)
        self.side_widget = side_widget

    def apply_width(self, width):
        self.row.apply_width(width)
        m = 10 if width < 280 else (14 if width < 380 else 18)
        self.layout().setContentsMargins(m, 12 if width < 280 else 14, m, 12 if width < 280 else 14)
        if self.side_widget is not None:
            # Di layar sempit tombol/filter mengisi selebar kartu (seperti web).
            self.side_widget.setMinimumWidth(0 if not self.row.wide else 170)

    def minimumSizeHint(self):
        return QSize(140, 60)

    def set_texts(self, title=None, desc=None):
        if title is not None:
            self.title.setText(title)
        if desc is not None:
            self.desc.setText(desc)


class SegmentedTabs(QFrame):
    """Deret tab bergaya segmented control (subnav kategori di web)."""

    changed = pyqtSignal(str)

    def __init__(self, options, breakpoints, kind='seg', container='seg', parent=None):
        super().__init__(parent)
        self.setProperty('card', container)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        self.grid = ResponsiveGrid(breakpoints, 6, self)
        lay.addWidget(self.grid)
        self.buttons = {}
        for key, text, icon_key in options:
            btn = button(text, kind, parent=self.grid)
            btn.setCheckable(True)
            if icon_key:
                btn.setProperty('iconKey', icon_key)
            btn.clicked.connect(lambda _checked=False, k=key: self.select(k, emit=True))
            self.grid.add(btn)
            btn.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            self.buttons[key] = btn
        self.current = None

    def select(self, key, emit=False):
        self.current = key
        for k, btn in self.buttons.items():
            btn.setChecked(k == key)
            icon_key = btn.property('iconKey')
            if icon_key:
                btn.setIcon(icon(icon_key, '#ffffff' if k == key else '#0369a1', 16))
                btn.setIconSize(QSize(14, 14))
        if emit:
            self.changed.emit(key)

    def set_visible_keys(self, keys):
        for k, btn in self.buttons.items():
            btn.setVisible(k in keys)

    def apply_width(self, width):
        self.grid.apply_width(width)


class KVRow(QWidget):
    """Baris label-nilai untuk tampilan kartu di layar sempit (seperti tabel web versi mobile)."""

    def __init__(self, key, value, parent=None, key_width=96):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 7, 0, 7)
        lay.setSpacing(10)
        k = label(key.upper(), 'kvKey', True, self)
        k.setFixedWidth(key_width)
        lay.addWidget(k, 0, Qt.AlignmentFlag.AlignVCenter)
        if isinstance(value, str):
            v = label(value, 'kvVal', True, self)
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            v.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
            lay.addWidget(v, 1)
        else:
            lay.addStretch(1)
            lay.addWidget(value, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.value_widget = value

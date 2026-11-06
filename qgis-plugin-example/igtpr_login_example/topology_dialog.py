# -*- coding: utf-8 -*-
"""Dialog Pemeriksaan & Verifikasi Topologi IGT (Mockup V2)."""

from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QLayout, QPushButton,
    QScrollArea, QVBoxLayout, QWidget,
)

from .assets import ICONS
from .login_page import svg_pixmap


class _ScrollContent(QWidget):
    def minimumSizeHint(self):
        h = self.layout().totalMinimumSize().height() if self.layout() else 100
        return QSize(100, h)

    def sizeHint(self):
        h = self.layout().totalSizeHint().height() if self.layout() else 100
        return QSize(200, h)


class TopologyCheckDialog(QDialog):
    """Dialog Verifikasi Topologi untuk Reviewer (Superadmin & Admin)."""

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record or {}
        layer_name = self.record.get('name') or self.record.get('layer', 'IGT Dataset')
        self.setWindowTitle(f"Cek Topologi: {layer_name}")
        self.resize(540, 620)
        self.setObjectName('topologyCheckDialog')

        self.setStyleSheet("""
            QDialog#topologyCheckDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QFrame.ruleCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px 12px;
            }
            QPushButton#primaryBtn {
                background-color: #1f6fd6;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 8px;
                padding: 8px 18px;
                border: none;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1a63c7;
            }
            QPushButton#closeBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #475569;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton#closeBtn:hover {
                background-color: #f1f5f9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Header
        header = QHBoxLayout()
        header.setSpacing(12)
        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(svg_pixmap(ICONS['shield'].format(color='#1f6fd6'), QSize(36, 36)))
        header.addWidget(icon_lbl)

        h_texts = QVBoxLayout()
        h_texts.setSpacing(2)
        title = QLabel(f"Cek Topologi: {layer_name}", self)
        title.setStyleSheet("color: #0f294d; font-size: 16px; font-weight: 800;")
        title.setWordWrap(True)
        h_texts.addWidget(title)

        meta_info = f"ID: {self.record.get('id', 'AJU-2026')} · Satker: {self.record.get('satker', 'Kantah Sleman')} · Status: Terkompilasi"
        sub = QLabel(meta_info, self)
        sub.setWordWrap(True)
        sub.setStyleSheet("color: #64748b; font-size: 11px;")
        h_texts.addWidget(sub)
        header.addLayout(h_texts, 1)
        layout.addLayout(header)

        # 2. Scroll Area of Rules
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = _ScrollContent()
        c_layout = QVBoxLayout(content)
        c_layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        c_layout.setContentsMargins(0, 0, 6, 0)
        c_layout.setSpacing(10)

        rules = [
            ("1. Aturan Tumpang Tindih (Must Not Have Overlaps)",
             "Pemeriksaan batas antar poligon tidak saling beririsan / tumpang-tindih.",
             "✓ 0 Error (Valid)", "#047857", "#ecfdf5", "#a7f3d0"),
            ("2. Aturan Celah Antar Poligon (Must Not Have Gaps)",
             "Pemeriksaan tidak ada rongga kosong atau sliver antar batas bidang bersebelahan.",
             "✓ 0 Error (Valid)", "#047857", "#ecfdf5", "#a7f3d0"),
            ("3. Geometri Valid & Self-Intersection",
             "Pemeriksaan garis poligon tidak memotong dirinya sendiri dan bebas dari loop tertutup.",
             "✓ 0 Error (Valid)", "#047857", "#ecfdf5", "#a7f3d0"),
            ("4. Node & Titik Simpul Duplikat (Duplicate Vertices)",
             "Pemeriksaan vertex ganda yang tidak diperlukan dalam segmen garis.",
             "✓ 0 Error (Valid)", "#047857", "#ecfdf5", "#a7f3d0"),
            ("5. Kesesuaian Skema Atribut Standar IGT-PR",
             "Pemeriksaan 21 atribut wajib sesuai dengan katalog atribut Geoportal Nasional.",
             "✓ 100% Sesuai Skema", "#047857", "#ecfdf5", "#a7f3d0"),
        ]

        for r_title, r_desc, r_stat, s_color, s_bg, s_border in rules:
            card = QFrame(content)
            card.setObjectName('ruleCard')
            card.setProperty('class', 'ruleCard')
            card.setStyleSheet("""
                QFrame#ruleCard {
                    background-color: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 6px 10px;
                }
            """)
            rc_layout = QHBoxLayout(card)
            rc_layout.setContentsMargins(6, 4, 6, 4)
            rc_layout.setSpacing(8)

            txts = QVBoxLayout()
            txts.setSpacing(2)
            t_lbl = QLabel(r_title, card)
            t_lbl.setWordWrap(True)
            t_lbl.setStyleSheet("color: #0f294d; font-size: 12px; font-weight: 700; border: none; background: transparent;")
            txts.addWidget(t_lbl)
            d_lbl = QLabel(r_desc, card)
            d_lbl.setWordWrap(True)
            d_lbl.setStyleSheet("color: #64748b; font-size: 11px; border: none; background: transparent;")
            txts.addWidget(d_lbl)
            rc_layout.addLayout(txts, 1)

            stat_badge = QLabel(r_stat, card)
            stat_badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {s_bg};
                    color: {s_color};
                    border: 1px solid {s_border};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 700;
                    padding: 4px 10px;
                }}
            """)
            rc_layout.addWidget(stat_badge, 0, Qt.AlignmentFlag.AlignVCenter)
            c_layout.addWidget(card)

        # Summary box
        summary = QFrame(content)
        summary.setObjectName('topoSummaryCard')
        summary.setStyleSheet("""
            QFrame#topoSummaryCard {
                background-color: #ecfdf5;
                border: 1px solid #6ee7b7;
                border-radius: 10px;
                padding: 10px 12px;
            }
        """)
        s_layout = QVBoxLayout(summary)
        s_layout.setSpacing(4)
        s_head = QLabel("✓ STATUS TOPOLOGI: VALID & SIAP INTEGRASI", summary)
        s_head.setWordWrap(True)
        s_head.setStyleSheet("color: #065f46; font-size: 13px; font-weight: 800; border: none; background: transparent;")
        s_layout.addWidget(s_head)
        s_body = QLabel(
            "Dataset telah lolos uji topologi standar Kementerian ATR/BPN tanpa kesalahan spasial. "
            "Layer dapat dilanjutkan ke tahap Persetujuan Integrasi Geoportal Pusat.", summary)
        s_body.setStyleSheet("color: #047857; font-size: 11px; border: none; background: transparent;")
        s_body.setWordWrap(True)
        s_layout.addWidget(s_body)
        c_layout.addWidget(summary)
        c_layout.addStretch(1)

        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # 3. Actions Footer
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        close_btn = QPushButton("Tutup", self)
        close_btn.setObjectName("closeBtn")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        footer.addWidget(close_btn)

        confirm_btn = QPushButton("✓ Konfirmasi Verifikasi Topologi", self)
        confirm_btn.setObjectName("primaryBtn")
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        footer.addWidget(confirm_btn)

        layout.addLayout(footer)

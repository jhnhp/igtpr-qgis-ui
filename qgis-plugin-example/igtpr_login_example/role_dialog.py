# -*- coding: utf-8 -*-
"""Dialog pemilihan peran (Role Selection) untuk simulasi mockup IGT-PR V2."""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QButtonGroup, QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QVBoxLayout, QWidget,
)

from .data import ROLES

ROLE_ORDER = ['superadmin', 'admin', 'operator', 'umum']


class RoleCard(QFrame):
    """Kartu opsi role dengan radio button dan avatar peran."""

    clicked = pyqtSignal(str)

    def __init__(self, role_id, role_info, is_checked=False, parent=None):
        super().__init__(parent)
        self.role_id = role_id
        self.role_info = role_info
        self.setObjectName('roleCard')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = is_checked

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        # Radio button
        self.radio = QRadioButton(self)
        self.radio.setChecked(is_checked)
        self.radio.toggled.connect(self._on_toggled)
        layout.addWidget(self.radio)

        # Avatar
        self.avatar_lbl = QLabel(role_info['avatar'], self)
        self.avatar_lbl.setFixedSize(38, 38)
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {role_info['bg']};
                color: {role_info['color']};
                font-weight: 800;
                font-size: 13px;
                border-radius: 19px;
            }}
        """)
        layout.addWidget(self.avatar_lbl)

        # Text column
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_lbl = QLabel(role_info['label'], self)
        self.title_lbl.setStyleSheet(f"""
            QLabel {{
                color: #0f294d;
                font-weight: 700;
                font-size: 13px;
            }}
        """)
        text_layout.addWidget(self.title_lbl)

        self.desc_lbl = QLabel(role_info['desc'], self)
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setStyleSheet("QLabel { color: #5b6f8a; font-size: 11px; }")
        text_layout.addWidget(self.desc_lbl)

        layout.addLayout(text_layout, 1)
        self._update_style()

    def setChecked(self, checked):
        self._checked = checked
        self.radio.setChecked(checked)
        self._update_style()

    def isChecked(self):
        return self.radio.isChecked()

    def _on_toggled(self, checked):
        self._checked = checked
        self._update_style()
        if checked:
            self.clicked.emit(self.role_id)

    def mousePressEvent(self, event):
        self.radio.setChecked(True)
        super().mousePressEvent(event)

    def _update_style(self):
        if self._checked:
            self.setStyleSheet("""
                QFrame#roleCard {
                    background-color: #f0f7ff;
                    border: 2px solid #1f6fd6;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#roleCard {
                    background-color: #ffffff;
                    border: 1px solid #dce5ef;
                    border-radius: 12px;
                }
                QFrame#roleCard:hover {
                    background-color: #f8fafc;
                    border-color: #93c5fd;
                }
            """)


class RoleDialog(QDialog):
    """Dialog modal untuk memilih peran pengguna."""

    roleSelected = pyqtSignal(str)

    def __init__(self, current_role='superadmin', parent=None):
        super().__init__(parent)
        self.setWindowTitle('Pilih Peran Pengguna - Geoportal IGT-PR')
        self.setFixedWidth(440)
        self.selected_role = current_role
        self.cards = {}

        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QPushButton#submitBtn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1f6fd6, stop:1 #0f58c4);
                color: #ffffff;
                font-weight: 700;
                font-size: 13px;
                padding: 10px 18px;
                border-radius: 8px;
                border: none;
            }
            QPushButton#submitBtn:hover {
                background: #1a63c7;
            }
            QPushButton#cancelBtn {
                background: #ffffff;
                color: #475569;
                font-weight: 600;
                font-size: 13px;
                padding: 10px 16px;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
            }
            QPushButton#cancelBtn:hover {
                background: #f1f5f9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(14)

        # Header
        head_layout = QVBoxLayout()
        head_layout.setSpacing(4)
        title = QLabel('Pilih Peran untuk Masuk', self)
        title.setStyleSheet("QLabel { color: #0f294d; font-size: 17px; font-weight: 800; }")
        head_layout.addWidget(title)

        subtitle = QLabel(
            'Silakan tentukan peran pengguna untuk menguji hak akses dan alur kerja Geoportal IGT-PR V2.', self)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("QLabel { color: #64748b; font-size: 12px; }")
        head_layout.addWidget(subtitle)
        layout.addLayout(head_layout)

        # Cards container
        self.button_group = QButtonGroup(self)
        for rid in ROLE_ORDER:
            info = ROLES[rid]
            card = RoleCard(rid, info, is_checked=(rid == current_role), parent=self)
            card.clicked.connect(self._on_card_clicked)
            self.button_group.addButton(card.radio)
            self.cards[rid] = card
            layout.addWidget(card)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton('Batal', self)
        cancel_btn.setObjectName('cancelBtn')
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        submit_btn = QPushButton('Masuk ke Geoportal →', self)
        submit_btn.setObjectName('submitBtn')
        submit_btn.clicked.connect(self._on_submit)
        btn_layout.addWidget(submit_btn)

        layout.addLayout(btn_layout)

    def _on_card_clicked(self, role_id):
        self.selected_role = role_id
        for rid, card in self.cards.items():
            card.setChecked(rid == role_id)

    def _on_submit(self):
        self.roleSelected.emit(self.selected_role)
        self.accept()

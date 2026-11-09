# -*- coding: utf-8 -*-
"""Dialog Preview Metadata IGT (Read-Only).

Membaca berkas XML metadata standar ISO 19115 dari folder plugin
(`bidang_tanah_jawa_barat_kota_bekasi_metadata.xml` atau `LSD8PROV50002021.xml`)
dan menampilkan tabel pasangan Atribut (XPath) & Nilai secara read-only
(tanpa tombol Edit per baris maupun tombol Simpan Perubahan).
"""

import os
import xml.etree.ElementTree as ET

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


def resolve_metadata_xml(dataset_or_title):
    """Menentukan nama file XML dan path absolut berdasarkan kategori/nama dataset."""
    is_pertanahan = False
    if isinstance(dataset_or_title, dict):
        cat = str(dataset_or_title.get("category", "")).lower()
        name = str(dataset_or_title.get("name", "")).lower()
        if cat == "pertanahan" or any(k in name for k in ("bidang", "hak", "ptsl", "znt", "ip4t", "pertanahan")):
            is_pertanahan = True
    else:
        name = str(dataset_or_title or "").lower()
        if any(k in name for k in ("bidang", "hak", "ptsl", "znt", "ip4t", "pertanahan")):
            is_pertanahan = True

    file_name = (
        "bidang_tanah_jawa_barat_kota_bekasi_metadata.xml"
        if is_pertanahan
        else "LSD8PROV50002021.xml"
    )

    here = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(here)
    candidates = [
        os.path.join(here, file_name),
        os.path.join(parent_dir, file_name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return file_name, path
    return file_name, candidates[0]


def parse_metadata_xml(xml_path):
    """Mem-parsing berkas XML metadata ISO 19115 menjadi daftar pasangan (xpath, value)."""
    rows = []
    if not xml_path or not os.path.isfile(xml_path):
        return rows

    try:
        with open(xml_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read().strip()
    except Exception:
        return rows

    if not raw:
        return rows

    if raw.startswith("\ufeff"):
        raw = raw[1:].strip()
    if raw.startswith("ï»¿"):
        raw = raw[3:].strip()

    EMPTY_VAL = "— Kosong —"

    try:
        root = ET.fromstring(raw.encode("utf-8"))

        def visit(element, path):
            tag_clean = element.tag.split("}")[-1] if "}" in element.tag else element.tag
            current_path = path + [tag_clean]

            for attr_name, attr_val in element.attrib.items():
                clean_attr = attr_name.split("}")[-1] if "}" in attr_name else attr_name
                if clean_attr == "xmlns" or clean_attr.startswith("xmlns:"):
                    continue
                val_str = str(attr_val or "").strip()
                rows.append({
                    "xpath": f"{' / '.join(current_path)} / @{clean_attr}",
                    "value": val_str if val_str else EMPTY_VAL,
                })

            children = list(element)
            if len(children) == 0:
                val_str = (element.text or "").strip()
                rows.append({
                    "xpath": " / ".join(current_path),
                    "value": val_str if val_str else EMPTY_VAL,
                })
                return

            for child in children:
                visit(child, current_path)

        visit(root, [])
    except Exception as exc:
        print(f"[PreviewMetadata] Gagal mem-parsing XML: {exc}")

    return rows


class IgtDetailDialog(QDialog):
    """Dialog Modal 'Preview Metadata' (Read-Only)."""

    wmsRequested = pyqtSignal(dict, object)
    wfsRequested = pyqtSignal(dict, object)

    def __init__(self, dataset=None, allow_wfs=True, parent=None):
        super().__init__(parent)
        self.dataset = dataset if isinstance(dataset, dict) else {"name": str(dataset or "")}
        self.allow_wfs = allow_wfs

        self.file_name, self.xml_path = resolve_metadata_xml(self.dataset)
        self.rows_data = parse_metadata_xml(self.xml_path)

        self.setWindowTitle("Preview Metadata")
        self.resize(980, 660)
        self.setObjectName("igtDetailDialog")
        self.setStyleSheet("""
            QDialog#igtDetailDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
        """)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Header Title
        title_lbl = QLabel("Preview Metadata", self)
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        main_layout.addWidget(title_lbl)

        # Info Banner (Biru Muda)
        total_pairs = len(self.rows_data)
        self.banner = QFrame(self)
        self.banner.setStyleSheet(
            "QFrame { background-color: #e0f2fe; border: 1px solid #bae6fd; border-radius: 6px; padding: 8px 12px; }"
        )
        ban_lay = QHBoxLayout(self.banner)
        ban_lay.setContentsMargins(4, 4, 4, 4)
        self.banner_text = QLabel(
            f"ℹ️ {total_pairs} pasangan atribut dan nilai dari <b>{self.file_name}</b>.",
            self.banner,
        )
        self.banner_text.setStyleSheet("color: #0369a1; font-size: 11px; border: none; background: transparent;")
        self.banner_text.setWordWrap(True)
        ban_lay.addWidget(self.banner_text)
        main_layout.addWidget(self.banner)

        # Tabel 2 Kolom (Atribut & Nilai - Tanpa Kolom Aksi/Edit)
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Atribut", "Nilai"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 390)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setWordWrap(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                font-size: 11px;
                background-color: #ffffff;
                color: #1e293b;
                selection-background-color: #f0f9ff;
                selection-color: #0f172a;
            }
            QTableWidget::item {
                padding: 6px 8px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                border-right: 1px solid #f1f5f9;
                padding: 6px;
                font-size: 11px;
            }
        """)

        self._populate_table()
        main_layout.addWidget(self.table, 1)

        # Footer (Hanya Tombol Close / Tutup di Kanan Bawah)
        footer_lay = QHBoxLayout()
        footer_lay.setContentsMargins(0, 4, 0, 0)
        footer_lay.addStretch(1)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: #ffffff;
                border-radius: 4px;
                padding: 6px 18px;
                font-size: 11px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self.btn_close.clicked.connect(self.accept)
        footer_lay.addWidget(self.btn_close)

        main_layout.addLayout(footer_lay)

    def _populate_table(self):
        self.table.setRowCount(len(self.rows_data))

        font_attr = QFont("Segoe UI", 9)
        font_attr.setWeight(QFont.Weight.DemiBold)

        font_val = QFont("Segoe UI", 9)

        font_empty = QFont("Segoe UI", 9)
        font_empty.setItalic(True)

        color_attr = QColor("#1e293b")
        color_val = QColor("#1e293b")
        color_empty = QColor("#94a3b8")

        for row, item in enumerate(self.rows_data):
            xpath_str = item.get("xpath", "")
            val_str = item.get("value", "")
            is_empty = val_str == "— Kosong —" or not val_str.strip()

            item_attr = QTableWidgetItem(xpath_str)
            item_attr.setFlags(item_attr.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item_attr.setFont(font_attr)
            item_attr.setForeground(color_attr)
            self.table.setItem(row, 0, item_attr)

            item_val = QTableWidgetItem("— Kosong —" if is_empty else val_str)
            item_val.setFlags(item_val.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if is_empty:
                item_val.setFont(font_empty)
                item_val.setForeground(color_empty)
            else:
                item_val.setFont(font_val)
                item_val.setForeground(color_val)
            self.table.setItem(row, 1, item_val)

            self.table.setRowHeight(row, 40)

# -*- coding: utf-8 -*-
"""Dialog Detail Informasi IGT (Mockup V2).

Menampilkan informasi lengkap mengenai dataset IGT:
- Nama & ID IGT
- Direktorat Pembina & Satker
- Tanggal Integrasi / Pembaruan
- Jenis IGT & Kategori
- Ruang Lingkup / Wilayah
- Format Layanan & Skala
- Sistem Koordinat (CRS)
- Link Dokumen Metadata
- Rincian Sub-layer (bila multi-layer)
- Pintasan Muat Layer (WMS / WFS) ke kanvas peta QGIS
"""

from qgis.PyQt.QtCore import QSize, Qt, pyqtSignal, QUrl
from qgis.PyQt.QtGui import QColor, QFont, QDesktopServices
from qgis.PyQt.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QWidget, QGridLayout, QMessageBox,
)

from .assets import ICONS
from .login_page import svg_pixmap


class IgtDetailDialog(QDialog):
    """Dialog detail informasi dan metadata dataset IGT."""

    wmsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)
    wfsRequested = pyqtSignal(dict, object)   # (dataset, sublayer or None)

    def __init__(self, dataset, allow_wfs=True, parent=None):
        super().__init__(parent)
        self.dataset = dataset or {}
        self.allow_wfs = allow_wfs
        self.has_subs = bool(self.dataset.get('subLayers'))

        d_name = self.dataset.get('name', 'IGT Dataset')
        d_id = self.dataset.get('id', 'IGT-PR-000')
        cat = self.dataset.get('category', 'pertanahan')

        self.setWindowTitle(f"Detail IGT: {d_name} ({d_id})")
        self.resize(540, 660)
        self.setObjectName('igtDetailDialog')

        self.setStyleSheet("""
            QDialog#igtDetailDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QFrame.infoCard {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px 14px;
            }
            QPushButton#primaryBtn {
                background-color: #1f6fd6;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 8px;
                padding: 7px 16px;
                border: none;
            }
            QPushButton#primaryBtn:hover {
                background-color: #1a63c7;
            }
            QPushButton#wfsBtn {
                background-color: #7c3aed;
                color: #ffffff;
                font-weight: 700;
                font-size: 12px;
                border-radius: 8px;
                padding: 7px 16px;
                border: none;
            }
            QPushButton#wfsBtn:hover {
                background-color: #6d28d9;
            }
            QPushButton#closeBtn {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                color: #475569;
                font-size: 12px;
                font-weight: 600;
                padding: 7px 14px;
            }
            QPushButton#closeBtn:hover {
                background-color: #f1f5f9;
                color: #0f294d;
            }
            QPushButton#metadataLinkBtn {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 6px;
                color: #1d4ed8;
                font-size: 11px;
                font-weight: 700;
                padding: 5px 10px;
                text-align: left;
            }
            QPushButton#metadataLinkBtn:hover {
                background-color: #dbeafe;
                border-color: #93c5fd;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(12)

        # 1. Header Card (Gradasi lembut dengan ikon kategori)
        head_card = QFrame(self)
        head_card.setObjectName('headCard')
        head_card.setStyleSheet("""
            QFrame#headCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #102b59, stop:1 #1b4588);
                border-radius: 12px;
                border: none;
            }
        """)
        hc_layout = QHBoxLayout(head_card)
        hc_layout.setContentsMargins(16, 14, 16, 14)
        hc_layout.setSpacing(12)

        icon_name = 'map' if cat == 'tata-ruang' else 'layers' if cat == 'derivatif' else 'globe' if cat == 'lainnya' else 'pin'
        icon_badge = QLabel(head_card)
        icon_badge.setFixedSize(44, 44)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("background: rgba(255, 255, 255, 0.15); border-radius: 10px;")
        icon_badge.setPixmap(svg_pixmap(ICONS.get(icon_name, ICONS['pin']).format(color='#ffffff'), QSize(22, 22)))
        hc_layout.addWidget(icon_badge)

        ht_layout = QVBoxLayout()
        ht_layout.setSpacing(3)

        eyebrow = QLabel("SISTEM INFORMASI GEOSPASIAL ATR/BPN · DETAIL IGT", head_card)
        eyebrow.setStyleSheet("color: #bfdbfe; font-size: 9px; font-weight: 800; letter-spacing: 0.8px;")
        ht_layout.addWidget(eyebrow)

        title_lbl = QLabel(d_name, head_card)
        title_lbl.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: 800;")
        title_lbl.setWordWrap(True)
        ht_layout.addWidget(title_lbl)

        sub_info = QLabel(f"ID Dataset: {d_id} · Status: {self.dataset.get('status', 'Terintegrasi')}", head_card)
        sub_info.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        ht_layout.addWidget(sub_info)

        hc_layout.addLayout(ht_layout, 1)
        layout.addWidget(head_card)

        # 2. Scrollable Body
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        body_widget = QWidget()
        body_widget.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(10)

        # Card: Informasi Utama Metadata
        info_card = QFrame(body_widget)
        info_card.setProperty('class', 'infoCard')
        ic_layout = QVBoxLayout(info_card)
        ic_layout.setContentsMargins(14, 12, 14, 12)
        ic_layout.setSpacing(10)

        card_title = QLabel("Metadata Pokok Dataset", info_card)
        card_title.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        ic_layout.addWidget(card_title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(8)

        # Tentukan Jenis IGT deskriptif
        if cat == 'pertanahan':
            jenis_igt = 'IGT Pertanahan (Berbasis Bidang Tanah)'
        elif cat == 'tata-ruang':
            jenis_igt = 'IGT Tata Ruang (Berbasis Rencana & Pola Kawasan)'
        elif cat == 'derivatif':
            jenis_igt = 'IGT Derivatif Multiguna (Analisis Tematik Lanjutan)'
        else:
            jenis_igt = 'IGT K/L Lainnya (Data Tematik Eksternal)'

        direktorat_val = self.dataset.get('direktorat') or self.dataset.get('satker') or 'Direktorat Pengukuran dan Pemetaan Kadastral'
        satker_val = self.dataset.get('satker') or self.dataset.get('direktorat') or 'Kantah Kab. Sleman'
        tgl_val = self.dataset.get('updated') or self.dataset.get('date') or '18 Okt 2026'
        lingkup_val = self.dataset.get('scope') or f"{self.dataset.get('kab', 'Kab. Sleman')}, {self.dataset.get('prov', 'D.I. Yogyakarta')}"

        fields = [
            ("Direktorat Pembina", direktorat_val),
            ("Satuan Kerja (Satker)", satker_val),
            ("Tanggal Integrasi", tgl_val),
            ("Jenis IGT", jenis_igt),
            ("Ruang Lingkup / Wilayah", lingkup_val),
            ("Sistem Koordinat (CRS)", "EPSG:4326 (WGS 84) / EPSG:3857 (Web Mercator)"),
            ("Format Layanan", "WMS (Web Map Service), WFS (Web Feature Service)"),
            ("Skala Geospasial", "1:5.000 / 1:25.000 (Sesuai Standar IGT Nasional)"),
        ]

        for i, (lbl_txt, val_txt) in enumerate(fields):
            r = i // 2
            c = (i % 2) * 2

            lbl = QLabel(lbl_txt.upper(), info_card)
            lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700;")
            grid.addWidget(lbl, r * 2, c)

            val = QLabel(val_txt, info_card)
            val.setStyleSheet("color: #0f294d; font-size: 11px; font-weight: 600;")
            val.setWordWrap(True)
            grid.addWidget(val, r * 2 + 1, c)

        ic_layout.addLayout(grid)
        body_layout.addWidget(info_card)

        # Card: Link Metadata Resmi (ISO 19115)
        meta_card = QFrame(body_widget)
        meta_card.setProperty('class', 'infoCard')
        mc_layout = QVBoxLayout(meta_card)
        mc_layout.setContentsMargins(14, 12, 14, 12)
        mc_layout.setSpacing(6)

        m_head = QLabel("Dokumen & Spesifikasi Metadata", meta_card)
        m_head.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        mc_layout.addWidget(m_head)

        m_desc = QLabel("Metadata geospasial lengkap berstandar ISO 19115 / SNI ISO 19115 tersedia melalui geoportal kementerian:", meta_card)
        m_desc.setStyleSheet("color: #475569; font-size: 11px;")
        m_desc.setWordWrap(True)
        mc_layout.addWidget(m_desc)

        meta_url = f"https://geoportal.atrbpn.go.id/metadata/{d_id.lower()}"
        meta_link_btn = QPushButton(f"↗ Lihat Metadata Geospasial ({meta_url})", meta_card)
        meta_link_btn.setObjectName('metadataLinkBtn')
        meta_link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        meta_link_btn.setToolTip("Buka halaman dokumen metadata geospasial")
        meta_link_btn.clicked.connect(lambda: self._open_metadata(meta_url))
        mc_layout.addWidget(meta_link_btn)
        body_layout.addWidget(meta_card)

        # Card: Sub-Layer (Bila Multi-Layer)
        if self.has_subs:
            subs_card = QFrame(body_widget)
            subs_card.setProperty('class', 'infoCard')
            sc_layout = QVBoxLayout(subs_card)
            sc_layout.setContentsMargins(14, 12, 14, 12)
            sc_layout.setSpacing(8)

            sub_count = len(self.dataset['subLayers'])
            s_head = QLabel(f"Daftar Sub-Layer ({sub_count} Sub-IGT Terintegrasi)", subs_card)
            s_head.setStyleSheet("color: #047857; font-size: 13px; font-weight: 800;")
            sc_layout.addWidget(s_head)

            for s in self.dataset['subLayers']:
                s_box = QFrame(subs_card)
                s_box.setStyleSheet("background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 6px 10px;")
                sb_lay = QHBoxLayout(s_box)
                sb_lay.setContentsMargins(4, 2, 4, 2)
                sb_lay.setSpacing(8)

                s_txt = QVBoxLayout()
                s_txt.setSpacing(2)
                s_title = QLabel(f"• {s.get('name', 'Sub-layer')}", s_box)
                s_title.setStyleSheet("color: #065f46; font-size: 11.5px; font-weight: 700;")
                s_txt.addWidget(s_title)

                s_meta = QLabel(f"ID: {s.get('id', '—')} · Update: {s.get('updated', '—')} · Cakupan: {s.get('scope', '—')}", s_box)
                s_meta.setStyleSheet("color: #047857; font-size: 10px;")
                s_txt.addWidget(s_meta)
                sb_lay.addLayout(s_txt, 1)

                sc_layout.addWidget(s_box)

            body_layout.addWidget(subs_card)

        # Card: Deskripsi & Abstrak
        desc_card = QFrame(body_widget)
        desc_card.setProperty('class', 'infoCard')
        dc_layout = QVBoxLayout(desc_card)
        dc_layout.setContentsMargins(14, 12, 14, 12)
        dc_layout.setSpacing(6)

        d_head = QLabel("Abstrak & Keterangan Dataset", desc_card)
        d_head.setStyleSheet("color: #0f294d; font-size: 13px; font-weight: 800;")
        dc_layout.addWidget(d_head)

        abstrak = (
            f"Dataset '{d_name}' merupakan Informasi Geospasial Tematik (IGT) resmi yang diproduksi dan dikelola "
            f"oleh {direktorat_val}. Data ini telah melewati tahapan validasi atribut, penjaminan kualitas spasial, "
            f"dan verifikasi topologi sehingga siap untuk diintegrasikan dan dimanfaatkan pada sistem GIS Kementerian ATR/BPN."
        )
        d_text = QLabel(abstrak, desc_card)
        d_text.setStyleSheet("color: #334155; font-size: 11.5px; line-height: 1.4;")
        d_text.setWordWrap(True)
        dc_layout.addWidget(d_text)
        body_layout.addWidget(desc_card)

        scroll.setWidget(body_widget)
        layout.addWidget(scroll, 1)

        # 3. Footer Action Buttons
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 4, 0, 0)
        footer.setSpacing(8)

        btn_close = QPushButton("Tutup", self)
        btn_close.setObjectName('closeBtn')
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)

        footer.addStretch(1)

        btn_wms = QPushButton("Muat WMS ke Kanvas", self)
        btn_wms.setObjectName('primaryBtn')
        btn_wms.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_wms.setToolTip("Muat layer citra WMS ke kanvas QGIS")
        btn_wms.clicked.connect(self._on_load_wms)
        footer.addWidget(btn_wms)

        if self.allow_wfs:
            btn_wfs = QPushButton("Muat WFS ke Kanvas", self)
            btn_wfs.setObjectName('wfsBtn')
            btn_wfs.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_wfs.setToolTip("Muat fitur layer vektor WFS ke kanvas QGIS")
            btn_wfs.clicked.connect(self._on_load_wfs)
            footer.addWidget(btn_wfs)

        layout.addLayout(footer)

    def _open_metadata(self, url):
        # Membuka tautan metadata di peramban sistem atau simulasi dialog
        QDesktopServices.openUrl(QUrl(url))
        QMessageBox.information(
            self,
            "Tautan Metadata Geospasial",
            f"Membuka dokumen metadata resmi:\n{url}\n\nStandar format: ISO 19115 / SNI ISO 19115 (Metadata Geospasial Indonesia)."
        )

    def _on_load_wms(self):
        if self.has_subs:
            for s in self.dataset.get('subLayers', []):
                self.wmsRequested.emit(self.dataset, s)
        else:
            self.wmsRequested.emit(self.dataset, None)
        self.accept()

    def _on_load_wfs(self):
        if self.has_subs:
            for s in self.dataset.get('subLayers', []):
                self.wfsRequested.emit(self.dataset, s)
        else:
            self.wfsRequested.emit(self.dataset, None)
        self.accept()

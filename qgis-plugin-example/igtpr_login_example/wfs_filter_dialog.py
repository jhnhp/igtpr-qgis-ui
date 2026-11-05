# -*- coding: utf-8 -*-
"""Dialog Opsi Pemuatan Layer WFS (Load Semua, Batas Admin, AOI).

Mencegah beban unduhan data WFS nasional yang terlalu besar dengan memberikan opsi:
1. Load semua (seluruh Indonesia)
2. Load berdasarkan batas admin (Provinsi -> Kabupaten -> Kecamatan -> Desa)
3. Load berdasarkan AOI (Pilih layer AOI yang ada di QGIS atau Gambar AOI)
"""

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import (
    QButtonGroup, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QListView, QPushButton, QRadioButton, QVBoxLayout, QWidget,
)

from qgis.core import QgsProject, QgsWkbTypes

from .data import INDONESIA_REGIONS


# Referensi hirarki administrasi hingga tingkat Kecamatan dan Desa
ADMIN_HIERARCHY = {
    'D.I. Yogyakarta': {
        'Kab. Sleman': {
            'Kec. Depok': ['Kel. Caturtunggal', 'Kel. Maguwoharjo', 'Kel. Condongcatur'],
            'Kec. Mlati': ['Kel. Sendangadi', 'Kel. Sinduadi', 'Kel. Tirtoadi', 'Kel. Tlogoadi', 'Kel. Sumberadi'],
            'Kec. Gamping': ['Kel. Ambarketawang', 'Kel. Balecatur', 'Kel. Banyuraden', 'Kel. Nogotirto', 'Kel. Trihanggo'],
            'Kec. Ngaglik': ['Kel. Donoharjo', 'Kel. Minomartani', 'Kel. Sardonoharjo', 'Kel. Sariharjo', 'Kel. Sinduharjo'],
            'Kec. Kalasan': ['Kel. Purwomartani', 'Kel. Selomartani', 'Kel. Tamanmartani', 'Kel. Tirtomartani'],
            'Kec. Berbah': ['Kel. Jogotirto', 'Kel. Kalitirto', 'Kel. Sendangtirto', 'Kel. Tegaltirto'],
        },
        'Kab. Bantul': {
            'Kec. Sewon': ['Kel. Bangunharjo', 'Kel. Panggungharjo', 'Kel. Pendowoharjo', 'Kel. Timbulharjo'],
            'Kec. Banguntapan': ['Kel. Banguntapan', 'Kel. Baturetno', 'Kel. Jagalan', 'Kel. Potorono', 'Kel. Singosaren'],
            'Kec. Kasihan': ['Kel. Bangunjiwo', 'Kel. Ngestiharjo', 'Kel. Tamantirto', 'Kel. Tirtonirmolo'],
        },
        'Kota Yogyakarta': {
            'Kec. Danurejan': ['Kel. Bausasran', 'Kel. Suryatmajan', 'Kel. Tegalpanggung'],
            'Kec. Gondomanan': ['Kel. Ngupasan', 'Kel. Prawirodirjan'],
            'Kec. Umbulharjo': ['Kel. Giwangan', 'Kel. Muja Muju', 'Kel. Pandeyan', 'Kel. Semaki', 'Kel. Sorosutan'],
        },
        'Kab. Kulon Progo': {
            'Kec. Wates': ['Kel. Bendungan', 'Kel. Giripeni', 'Kel. Karangwuni', 'Kel. Wates'],
            'Kec. Temon': ['Kel. Glagah', 'Kel. Jangkaran', 'Kel. Palihan', 'Kel. Temon Kulon'],
        },
        'Kab. Gunungkidul': {
            'Kec. Wonosari': ['Kel. Baleharjo', 'Kel. Duwet', 'Kel. Kepek', 'Kel. Wonosari'],
            'Kec. Playen': ['Kel. Playen', 'Kel. Logandeng', 'Kel. Plembutan'],
        },
    },
    'Jawa Barat': {
        'Kota Bandung': {
            'Kec. Coblong': ['Kel. Dago', 'Kel. Lebakgede', 'Kel. Sadangserang'],
            'Kec. Sukasari': ['Kel. Gegerkalong', 'Kel. Sarijadi', 'Kel. Isola'],
        },
        'Kab. Bogor': {
            'Kec. Cibinong': ['Kel. Cirimekar', 'Kel. Pakansari', 'Kel. Tengah'],
        },
    },
    'DKI Jakarta': {
        'Kota Jakarta Selatan': {
            'Kec. Kebayoran Baru': ['Kel. Selong', 'Kel. Senayan', 'Kel. Melawai'],
            'Kec. Cilandak': ['Kel. Cilandak Barat', 'Kel. Cipete Selatan'],
        },
        'Kota Jakarta Pusat': {
            'Kec. Gambir': ['Kel. Gambir', 'Kel. Kebon Kelapa', 'Kel. Petojo Selatan'],
        },
    },
    'Jawa Tengah': {
        'Kota Semarang': {
            'Kec. Semarang Tengah': ['Kel. Miroto', 'Kel. Pandansari', 'Kel. Sekayu'],
        },
        'Kota Surakarta': {
            'Kec. Banjarsari': ['Kel. Manahan', 'Kel. Nusukan', 'Kel. Kadipiro'],
        },
    },
    'Jawa Timur': {
        'Kota Surabaya': {
            'Kec. Gubeng': ['Kel. Airlangga', 'Kel. Barata Jaya', 'Kel. Gubeng'],
        },
    },
    'Bali': {
        'Kota Denpasar': {
            'Kec. Denpasar Selatan': ['Kel. Sanur', 'Kel. Sidakarya', 'Kel. Panjer'],
        },
    },
}


class WfsFilterDialog(QDialog):
    """Modal popup opsi pemuatan layer WFS dengan 3 metode pembatasan spasial."""

    loadWfsConfirmed = pyqtSignal(dict)

    def __init__(self, dataset, sublayer=None, iface=None, parent=None):
        super().__init__(parent)
        self.dataset = dataset or {}
        self.sublayer = sublayer
        self.iface = iface

        d_name = self.dataset.get('name', 'Dataset IGT')
        if sublayer:
            d_name = f"{d_name} ({sublayer.get('label') or sublayer.get('name')})"
        self.layer_name = d_name

        self.setWindowTitle(f"Opsi Pemuatan WFS - {self.layer_name}")
        self.resize(540, 620)
        self.setObjectName('wfsFilterDialog')

        self.setStyleSheet("""
            QDialog#wfsFilterDialog {
                background-color: #f8fafc;
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QFrame.cardBox {
                background-color: #ffffff;
                border: 1.5px solid #e2e8f0;
                border-radius: 10px;
            }
            QFrame.cardBoxActive {
                background-color: #eff6ff;
                border: 1.5px solid #2563eb;
            }
            QComboBox {
                background: #ffffff;
                border: 1.5px solid #cbd5e1;
                border-radius: 7px;
                padding: 6px 28px 6px 10px;
                font-size: 11.5px;
                color: #0f294d;
                font-weight: 600;
            }
            QComboBox:focus {
                border-color: #2563eb;
            }
            QComboBox:disabled {
                background: #f1f5f9;
                color: #94a3b8;
                border: 1.5px solid #e2e8f0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #0f294d;
                border: 1.5px solid #cbd5e1;
                border-radius: 6px;
                padding: 2px;
                max-height: 200px;
                selection-background-color: #eff6ff;
                selection-color: #2563eb;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                min-height: 24px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f1f5f9;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                min-height: 24px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #94a3b8;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QRadioButton {
                font-weight: 700;
                font-size: 12.5px;
                color: #0f294d;
            }
            QPushButton#btnConfirm {
                background-color: #7c3aed;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnConfirm:hover {
                background-color: #6d28d9;
            }
            QPushButton#btnCancel {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btnCancel:hover {
                background-color: #e2e8f0;
            }
            QPushButton#btnDrawAoi {
                background-color: #ffffff;
                color: #1d4ed8;
                border: 1.5px dashed #3b82f6;
                border-radius: 7px;
                padding: 7px 12px;
                font-size: 11.5px;
                font-weight: 700;
            }
            QPushButton#btnDrawAoi:hover {
                background-color: #dbeafe;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Header card
        header_card = QFrame(self)
        header_card.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #102b59, stop:1 #1e40af);
            border-radius: 10px;
            color: #ffffff;
        """)
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(16, 14, 16, 14)
        h_layout.setSpacing(4)

        eyebrow = QLabel("SISTEM INFORMASI GEOSPASIAL ATR/BPN · LAYANAN FITUR WFS", header_card)
        eyebrow.setStyleSheet("color: #bfdbfe; font-size: 9.5px; font-weight: 800; letter-spacing: 0.6px;")
        h_layout.addWidget(eyebrow)

        title_lbl = QLabel("Opsi Pemuatan Layer WFS", header_card)
        title_lbl.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 800;")
        h_layout.addWidget(title_lbl)

        target_lbl = QLabel(f"Layer: <b>{self.layer_name}</b>", header_card)
        target_lbl.setStyleSheet("color: #e0e7ff; font-size: 12px;")
        h_layout.addWidget(target_lbl)

        main_layout.addWidget(header_card)

        # Warning banner
        warn_box = QFrame(self)
        warn_box.setStyleSheet("""
            background-color: #fef3c7;
            border: 1px solid #fde68a;
            border-radius: 8px;
            color: #92400e;
        """)
        w_layout = QHBoxLayout(warn_box)
        w_layout.setContentsMargins(12, 10, 12, 10)
        w_layout.setSpacing(8)
        w_icon = QLabel("⚠️", warn_box)
        w_icon.setStyleSheet("font-size: 14px;")
        w_layout.addWidget(w_icon)
        w_text = QLabel("<b>Perhatian:</b> Data WFS nasional berukuran sangat besar. Disarankan menggunakan batasan wilayah (Batas Admin atau AOI) agar proses unduh dan visualisasi lebih cepat.", warn_box)
        w_text.setWordWrap(True)
        w_text.setStyleSheet("color: #92400e; font-size: 11px;")
        w_layout.addWidget(w_text, 1)
        main_layout.addWidget(warn_box)

        # Button group for 3 main options
        self.btn_group = QButtonGroup(self)

        # =====================================================================
        # OPTION 1: LOAD SEMUA
        # =====================================================================
        self.card_all = QFrame(self)
        self.card_all.setProperty('class', 'cardBox')
        ca_layout = QVBoxLayout(self.card_all)
        ca_layout.setContentsMargins(14, 10, 14, 10)
        ca_layout.setSpacing(3)

        self.rb_all = QRadioButton("1. Load Semua (Seluruh Indonesia)", self.card_all)
        self.btn_group.addButton(self.rb_all, 1)
        ca_layout.addWidget(self.rb_all)

        desc_all = QLabel("Memuat seluruh data fitur spasial cakupan nasional tanpa batasan wilayah.", self.card_all)
        desc_all.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 22px;")
        desc_all.setWordWrap(True)
        ca_layout.addWidget(desc_all)
        main_layout.addWidget(self.card_all)

        # =====================================================================
        # OPTION 2: BATAS ADMINISTRASI (DEFAULT)
        # =====================================================================
        self.card_admin = QFrame(self)
        self.card_admin.setProperty('class', 'cardBox cardBoxActive')
        cadm_layout = QVBoxLayout(self.card_admin)
        cadm_layout.setContentsMargins(14, 12, 14, 12)
        cadm_layout.setSpacing(8)

        self.rb_admin = QRadioButton("2. Load Berdasarkan Batas Admin", self.card_admin)
        self.rb_admin.setChecked(True)
        self.btn_group.addButton(self.rb_admin, 2)
        cadm_layout.addWidget(self.rb_admin)

        desc_adm = QLabel("Filter fitur WFS berdasarkan hirarki wilayah administratif pemerintahan.", self.card_admin)
        desc_adm.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 22px;")
        desc_adm.setWordWrap(True)
        cadm_layout.addWidget(desc_adm)

        # Grid 2x2 Dropdowns: Provinsi, Kabupaten, Kecamatan, Desa
        self.admin_grid_widget = QWidget(self.card_admin)
        ag_layout = QGridLayout(self.admin_grid_widget)
        ag_layout.setContentsMargins(22, 6, 0, 0)
        ag_layout.setHorizontalSpacing(10)
        ag_layout.setVerticalSpacing(8)

        # 1. Provinsi
        l_prov = QLabel("PROVINSI", self.admin_grid_widget)
        l_prov.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569;")
        self.cb_prov = QComboBox(self.admin_grid_widget)
        ag_layout.addWidget(l_prov, 0, 0)
        ag_layout.addWidget(self.cb_prov, 1, 0)

        # 2. Kabupaten / Kota
        l_kab = QLabel("KABUPATEN / KOTA", self.admin_grid_widget)
        l_kab.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569;")
        self.cb_kab = QComboBox(self.admin_grid_widget)
        ag_layout.addWidget(l_kab, 0, 1)
        ag_layout.addWidget(self.cb_kab, 1, 1)

        # 3. Kecamatan
        l_kec = QLabel("KECAMATAN", self.admin_grid_widget)
        l_kec.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569;")
        self.cb_kec = QComboBox(self.admin_grid_widget)
        ag_layout.addWidget(l_kec, 2, 0)
        ag_layout.addWidget(self.cb_kec, 3, 0)

        # 4. Desa / Kelurahan
        l_desa = QLabel("DESA / KELURAHAN", self.admin_grid_widget)
        l_desa.setStyleSheet("font-size: 10px; font-weight: 700; color: #475569;")
        self.cb_desa = QComboBox(self.admin_grid_widget)
        ag_layout.addWidget(l_desa, 2, 1)
        ag_layout.addWidget(self.cb_desa, 3, 1)

        cadm_layout.addWidget(self.admin_grid_widget)
        main_layout.addWidget(self.card_admin)

        # =====================================================================
        # OPTION 3: AOI (AREA OF INTEREST)
        # =====================================================================
        self.card_aoi = QFrame(self)
        self.card_aoi.setProperty('class', 'cardBox')
        caoi_layout = QVBoxLayout(self.card_aoi)
        caoi_layout.setContentsMargins(14, 12, 14, 12)
        caoi_layout.setSpacing(8)

        self.rb_aoi = QRadioButton("3. Load Berdasarkan AOI (Area of Interest)", self.card_aoi)
        self.btn_group.addButton(self.rb_aoi, 3)
        caoi_layout.addWidget(self.rb_aoi)

        desc_aoi = QLabel("Batasi fitur spasial dengan poligon delineasi atau penggambaran area di kanvas.", self.card_aoi)
        desc_aoi.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 22px;")
        desc_aoi.setWordWrap(True)
        caoi_layout.addWidget(desc_aoi)

        # Sub panel AOI
        self.aoi_sub_widget = QWidget(self.card_aoi)
        aoi_sub_lay = QVBoxLayout(self.aoi_sub_widget)
        aoi_sub_lay.setContentsMargins(22, 6, 0, 0)
        aoi_sub_lay.setSpacing(8)

        # Sub-radio 1: Layer yang ada di QGIS
        self.rb_aoi_layer = QRadioButton("Pilih AOI yang ada di QGIS:", self.aoi_sub_widget)
        self.rb_aoi_layer.setChecked(True)
        aoi_sub_lay.addWidget(self.rb_aoi_layer)

        self.cb_aoi_layer = QComboBox(self.aoi_sub_widget)
        aoi_sub_lay.addWidget(self.cb_aoi_layer)

        # Sub-radio 2: Gambar AOI
        self.rb_aoi_draw = QRadioButton("Gambar AOI-nya:", self.aoi_sub_widget)
        aoi_sub_lay.addWidget(self.rb_aoi_draw)

        h_draw = QHBoxLayout()
        h_draw.setSpacing(8)
        self.btn_draw = QPushButton("🖌 Gambar Kotak Pembatas (BBOX) di Kanvas", self.aoi_sub_widget)
        self.btn_draw.setObjectName('btnDrawAoi')
        self.btn_draw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_draw.clicked.connect(self._on_draw_clicked)
        h_draw.addWidget(self.btn_draw)
        h_draw.addStretch()
        aoi_sub_lay.addLayout(h_draw)

        self.lbl_draw_hint = QLabel("Klik untuk mengaktifkan kursor gambar poligon/kotak pada kanvas peta QGIS.", self.aoi_sub_widget)
        self.lbl_draw_hint.setStyleSheet("font-size: 10px; color: #64748b;")
        aoi_sub_lay.addWidget(self.lbl_draw_hint)

        caoi_layout.addWidget(self.aoi_sub_widget)
        main_layout.addWidget(self.card_aoi)

        # Grouping sub-radios for AOI
        self.aoi_btn_group = QButtonGroup(self)
        self.aoi_btn_group.addButton(self.rb_aoi_layer, 1)
        self.aoi_btn_group.addButton(self.rb_aoi_draw, 2)

        # Action Buttons
        act_box = QHBoxLayout()
        act_box.addStretch()
        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setObjectName('btnCancel')
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        act_box.addWidget(self.btn_cancel)

        self.btn_confirm = QPushButton("Muat WFS ke Kanvas →", self)
        self.btn_confirm.setObjectName('btnConfirm')
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.clicked.connect(self._on_confirm_clicked)
        act_box.addWidget(self.btn_confirm)

        main_layout.addLayout(act_box)

        # Connect Radio Toggles
        self.rb_all.toggled.connect(self._update_cards_ui)
        self.rb_admin.toggled.connect(self._update_cards_ui)
        self.rb_aoi.toggled.connect(self._update_cards_ui)

        # Batasi tinggi dropdown popup agar tidak melebihi layar dan dapat di-scroll dengan mulus
        for cb in (self.cb_prov, self.cb_kab, self.cb_kec, self.cb_desa, self.cb_aoi_layer):
            cb.setMaxVisibleItems(8)
            v = cb.view()
            if v:
                v.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                v.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                v.setMaximumHeight(200)

        # Populate Administrative Dropdowns
        self._populate_admin_hierarchy()

        # Populate QGIS Polygon Layers
        self._populate_qgis_layers()

        self._update_cards_ui()

    # -------------------------------------------------------------------------
    # UI State & Toggles
    # -------------------------------------------------------------------------
    def _update_cards_ui(self):
        is_all = self.rb_all.isChecked()
        is_admin = self.rb_admin.isChecked()
        is_aoi = self.rb_aoi.isChecked()

        self.card_all.setStyleSheet("QFrame { background-color: #eff6ff; border: 1.5px solid #2563eb; border-radius: 10px; }"
                                    if is_all else
                                    "QFrame { background-color: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; }")

        self.card_admin.setStyleSheet("QFrame { background-color: #eff6ff; border: 1.5px solid #2563eb; border-radius: 10px; }"
                                      if is_admin else
                                      "QFrame { background-color: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; }")
        self.admin_grid_widget.setVisible(is_admin)

        self.card_aoi.setStyleSheet("QFrame { background-color: #eff6ff; border: 1.5px solid #2563eb; border-radius: 10px; }"
                                    if is_aoi else
                                    "QFrame { background-color: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; }")
        self.aoi_sub_widget.setVisible(is_aoi)

    # -------------------------------------------------------------------------
    # Administrative Dropdowns (Cascading)
    # -------------------------------------------------------------------------
    def _populate_admin_hierarchy(self):
        # Gabungkan daftar provinsi
        all_provs = sorted(list(set(list(ADMIN_HIERARCHY.keys()) + list(INDONESIA_REGIONS.keys()))))
        self.cb_prov.blockSignals(True)
        self.cb_prov.clear()
        self.cb_prov.addItems(all_provs)

        # Set default ke D.I. Yogyakarta jika ada
        default_idx = self.cb_prov.findText('D.I. Yogyakarta')
        if default_idx >= 0:
            self.cb_prov.setCurrentIndex(default_idx)
        else:
            default_diy = [i for i, p in enumerate(all_provs) if 'yogyakarta' in p.lower()]
            if default_diy:
                self.cb_prov.setCurrentIndex(default_diy[0])

        self.cb_prov.blockSignals(False)

        self.cb_prov.currentIndexChanged.connect(self._sync_kabupaten)
        self.cb_kab.currentIndexChanged.connect(self._sync_kecamatan)
        self.cb_kec.currentIndexChanged.connect(self._sync_desa)

        self._sync_kabupaten()

    def _sync_kabupaten(self):
        prov = self.cb_prov.currentText()
        kabs = []
        if prov in ADMIN_HIERARCHY:
            kabs = list(ADMIN_HIERARCHY[prov].keys())
        elif prov in INDONESIA_REGIONS:
            kabs = INDONESIA_REGIONS[prov]

        if not kabs:
            kabs = ['Kabupaten / Kota Utama', 'Kabupaten / Kota Sentral']

        self.cb_kab.blockSignals(True)
        self.cb_kab.clear()

        # Opsi 'Semua Kabupaten / Kota' selalu di urutan pertama dan menjadi default setelah provinsi dipilih
        all_kabs_label = 'Semua Kabupaten / Kota'
        kab_items = [all_kabs_label] + [k for k in kabs if k != all_kabs_label]
        self.cb_kab.addItems(kab_items)
        self.cb_kab.setCurrentIndex(0)

        self.cb_kab.blockSignals(False)
        self._sync_kecamatan()

    def _sync_kecamatan(self):
        prov = self.cb_prov.currentText()
        kab = self.cb_kab.currentText()
        is_all_kab = kab in ('Semua Kabupaten / Kota', 'Semua Kabupaten', '')

        kecs = ['Semua Kecamatan']
        if not is_all_kab:
            if prov in ADMIN_HIERARCHY and kab in ADMIN_HIERARCHY[prov]:
                kecs.extend(list(ADMIN_HIERARCHY[prov][kab].keys()))
            else:
                kecs.extend(['Kec. 01 (Pusat)', 'Kec. 02 (Barat)', 'Kec. 03 (Timur)', 'Kec. 04 (Utara)', 'Kec. 05 (Selatan)'])

        self.cb_kec.blockSignals(True)
        self.cb_kec.clear()
        self.cb_kec.addItems(kecs)
        self.cb_kec.setCurrentIndex(0)
        self.cb_kec.setEnabled(not is_all_kab)
        self.cb_kec.blockSignals(False)

        self._sync_desa()

    def _sync_desa(self):
        prov = self.cb_prov.currentText()
        kab = self.cb_kab.currentText()
        kec = self.cb_kec.currentText()
        is_all_kab = kab in ('Semua Kabupaten / Kota', 'Semua Kabupaten', '')
        is_all_kec = kec in ('Semua Kecamatan', '')

        desas = ['Semua Desa / Kelurahan']
        if not is_all_kab and not is_all_kec:
            if prov in ADMIN_HIERARCHY and kab in ADMIN_HIERARCHY[prov] and kec in ADMIN_HIERARCHY[prov][kab]:
                desas.extend(ADMIN_HIERARCHY[prov][kab][kec])
            else:
                desas.extend(['Kelurahan 01', 'Kelurahan 02', 'Desa 01', 'Desa 02'])

        self.cb_desa.blockSignals(True)
        self.cb_desa.clear()
        self.cb_desa.addItems(desas)
        self.cb_desa.setCurrentIndex(0)
        self.cb_desa.setEnabled(not is_all_kab and not is_all_kec)
        self.cb_desa.blockSignals(False)

    # -------------------------------------------------------------------------
    # QGIS Layers (Polygon AOI)
    # -------------------------------------------------------------------------
    def _populate_qgis_layers(self):
        self.cb_aoi_layer.clear()
        found_poly = False

        try:
            for l_id, layer in QgsProject.instance().mapLayers().items():
                if layer.type() == 0 and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                    self.cb_aoi_layer.addItem(f"Layer: {layer.name()}", l_id)
                    found_poly = True
        except Exception:
            pass

        # Tambahkan opsi bawaan jika tidak ada polygon atau untuk kemudahan
        self.cb_aoi_layer.addItem("Fitur Terpilih di Kanvas QGIS (Selected Features)", "selection")
        if not found_poly:
            self.cb_aoi_layer.addItem("Layer: Batas Kawasan Perencanaan DIY (Poligon)", "preset_diy")
            self.cb_aoi_layer.addItem("Layer: Delineasi Area Prioritas RDTR", "preset_rdtr")
            self.cb_aoi_layer.addItem("Layer: Buffer Koridor 500m Infrastruktur", "preset_buffer")

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def _on_draw_clicked(self):
        self.rb_aoi.setChecked(True)
        self.rb_aoi_draw.setChecked(True)
        self._on_confirm_clicked()

    def _on_confirm_clicked(self):
        if self.rb_all.isChecked():
            mode = 'all'
            aoi_sub = None
        elif self.rb_admin.isChecked():
            mode = 'admin'
            aoi_sub = None
        else:
            mode = 'aoi'
            aoi_sub = 'draw' if self.rb_aoi_draw.isChecked() else 'layer'

        result = {
            'mode': mode,
            'dataset': self.dataset,
            'sublayer': self.sublayer,
            'provinsi': self.cb_prov.currentText(),
            'kabupaten': self.cb_kab.currentText(),
            'kecamatan': self.cb_kec.currentText(),
            'desa': self.cb_desa.currentText(),
            'aoi_sub': aoi_sub,
            'aoi_layer': self.cb_aoi_layer.currentText(),
            'aoi_layer_data': self.cb_aoi_layer.currentData(),
        }

        self.loadWfsConfirmed.emit(result)
        self.accept()

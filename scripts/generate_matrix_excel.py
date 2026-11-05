import sys, os, time, subprocess, shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.awt import Size, Point

matrix_data = [
    # (Kategori, Fungsi, SA, AD, OP, UM, Keterangan)
    ("Autentikasi & Akun", "Login SSO Akun Geoportal IGT-PR", True, True, True, True, "Autentikasi akun pengguna ATR/BPN atau publik"),
    ("Autentikasi & Akun", "Pemilihan / Pergantian Peran (Role Switcher)", True, True, True, True, "Dialog interaktif pemilihan peran aktif (SA, AD, JH, UM)"),
    ("Autentikasi & Akun", "Logout / Keluar Sesi", True, True, True, True, "Keluar dari sesi plugin pada antarmuka QGIS"),
    ("Autentikasi & Akun", "Navigasi Breadcrumbs Topbar", True, True, True, True, "Jejak rekam halaman dengan tautan kembali ke Dashboard"),

    ("Dashboard / Beranda", "Akses Halaman Dashboard (Beranda)", True, True, True, True, "Beranda utama plugin dengan Card UI dan ringkasan data"),
    ("Dashboard / Beranda", "Filter Tahun Global (2026, 2025, 2024, 2023, Semua Tahun)", True, True, True, True, "Filter sinkronisasi data statistik dan katalog secara dinamis"),
    ("Dashboard / Beranda", "Statistik Ringkasan Data Terkompilasi", True, True, True, True, "Indikator jumlah pengajuan berstatus Terkompilasi"),
    ("Dashboard / Beranda", "Statistik Ringkasan Data Terintegrasi", True, True, True, True, "Indikator jumlah dataset resmi terintegrasi nasional"),
    ("Dashboard / Beranda", "Pintasan Hub Katalog IGT (4 Kategori)", True, True, True, True, "Pintasan ke IGT Pertanahan, Tata Ruang, Derivatif, Lainnya"),
    ("Dashboard / Beranda", "Pintasan Hub Unggah Data", True, True, True, True, "Pintasan membuka dialog unggah data geospasial"),
    ("Dashboard / Beranda", "Pintasan Hub Manajemen Data", True, True, True, False, "Tersedia untuk Superadmin, Admin, dan Operator"),
    ("Dashboard / Beranda", "Pintasan Hub Model Builder", True, True, True, True, "Pintasan ke katalog modul eksekusi pemodelan spasial"),

    ("Katalog Data IGT", "Akses Halaman Katalog IGT Terpadu", True, True, True, True, "Katalog pencarian dan visualisasi dataset terintegrasi"),
    ("Katalog Data IGT", "Katalog Tab IGT-PR (Terpadu Pertanahan & Tata Ruang)", True, True, True, True, "Katalog gabungan IGT Pertanahan dan IGT Tata Ruang"),
    ("Katalog Data IGT", "Katalog Tab IGT Pertanahan", True, True, True, True, "Dataset tematik berbasis bidang tanah terintegrasi"),
    ("Katalog Data IGT", "Katalog Tab IGT Tata Ruang", True, True, True, True, "Dataset rencana tata ruang berbasis kawasan terintegrasi"),
    ("Katalog Data IGT", "Katalog Tab IGT Derivatif Multiguna", True, True, True, True, "Layer tematik turunan analisis spasial yang telah disetujui"),
    ("Katalog Data IGT", "Katalog Tab IGT K/L Lainnya (Eksternal)", True, True, True, True, "Layer referensi kementerian dan lembaga eksternal"),
    ("Katalog Data IGT", "Pencarian Kata Kunci Dataset", True, True, True, True, "Cari berdasarkan nama IGT, ID, sublayer, atau wilayah"),
    ("Katalog Data IGT", "Filter Wilayah Hirarkis (Provinsi & Kab/Kota)", True, True, True, True, "Filter cakupan wilayah administrasi 38 provinsi di Indonesia"),
    ("Katalog Data IGT", "Paginasi Katalog (8 Dataset per Halaman)", True, True, True, True, "Navigasi halaman 1, 2, ..., nomor halaman, dan dropdown"),
    ("Katalog Data IGT", "Detail Informasi IGT & Metadata", True, True, True, True, "Dialog informasi lengkap: direktorat, satker, tanggal, CRS"),
    ("Katalog Data IGT", "Sub-Layer Hierarkis Multi-Year (Tahun Jamak)", True, True, True, True, "Accordion sublayer per tahun (LBS, ZNT, TTT)"),
    ("Katalog Data IGT", "Sub-Layer Hierarkis Multi-Skala", True, True, True, True, "Accordion sublayer per skala peta (RDTR 5K/10K/25K, RTRW)"),

    ("Integrasi Kanvas QGIS", "Muat Layer WMS (Gambar Peta) ke Kanvas QGIS", True, True, True, True, "Menambahkan layer WMS (gambar peta) ke kanvas QGIS"),
    ("Integrasi Kanvas QGIS", "Muat Layer WFS (Vektor Fitur) - Seluruh Satker Nasional", True, False, False, False, "Khusus Superadmin dapat mengakses fitur WFS seluruh Indonesia"),
    ("Integrasi Kanvas QGIS", "Muat Layer WFS (Vektor Fitur) - Sesuai Satker Penugasan", True, True, True, False, "Admin & Operator hanya untuk satker Sleman. Umum tidak diizinkan"),

    ("Unggah Data (Upload)", "Akses Formulir Dialog Unggah Data", True, True, True, True, "Dialog upload berkas dan entri metadata geospasial"),
    ("Unggah Data (Upload)", "Unggah Data IGT Pertanahan (IGT Utama)", False, False, True, False, "Khusus Operator Satker. Superadmin dan Admin tidak mengunggah IGT Utama"),
    ("Unggah Data (Upload)", "Unggah Data IGT Tata Ruang (IGT Utama)", False, False, True, False, "Khusus Operator Satker. Superadmin dan Admin tidak mengunggah IGT Utama"),
    ("Unggah Data (Upload)", "Unggah Data IGT Derivatif Multiguna", True, True, True, True, "Pengguna Umum dan internal dapat mengunggah derivatif"),
    ("Unggah Data (Upload)", "Unggah Data IGT K/L Lainnya (Eksternal)", True, False, False, False, "Khusus Superadmin untuk integrasi dataset rujukan K/L"),
    ("Unggah Data (Upload)", "Pilih Berkas Geospasial (.gpkg, .zip, .shp, .geojson)", True, True, True, True, "File picker lokal mendukung berbagai format spasial"),
    ("Unggah Data (Upload)", "Simpan & Kirim Pengajuan ke Antrean", True, True, True, True, "Menyimpan berkas pengajuan baru ke sistem"),

    ("Manajemen Data", "Akses Halaman Manajemen Data", True, True, True, False, "Pemantauan status pengajuan data internal"),
    ("Manajemen Data", "Manajemen Kategori IGT Utama", True, True, True, False, "Pengawasan proses kompilasi dan verifikasi IGT Utama"),
    ("Manajemen Data", "Manajemen Kategori IGT Derivatif", True, True, True, True, "Pengawasan persetujuan layer derivatif"),
    ("Manajemen Data", "Filter Tab Status (Revisi, Diajukan, Terkompilasi, Terintegrasi)", True, True, True, False, "Navigasi tab status tahapan pengajuan data"),
    ("Manajemen Data", "Cek / Verifikasi Topologi Spasial", True, True, False, False, "Superadmin & Admin verifikasi topologi pada status Terkompilasi"),
    ("Manajemen Data", "Persetujuan Integrasi Data Spasial", True, True, False, False, "Superadmin & Admin menyetujui integrasi ke Geoportal"),
    ("Manajemen Data", "Perbaiki Revisi Pengajuan", False, False, True, False, "Khusus Operator mengunggah perbaikan saat status Revisi"),
    ("Manajemen Data", "Hapus Layer / Pengajuan Eksternal", True, False, False, False, "Khusus Superadmin pada data eksternal K/L"),

    ("Model Builder Spasial", "Akses Modul Model Builder (Menjalankan Model)", True, True, True, True, "Menjalankan pemodelan spasial otomatis pada kanvas QGIS"),
    ("Model Builder Spasial", "Eksekusi Model Analisis Kesesuaian Lahan", True, True, True, True, "Menjalankan analisis multi-kriteria kesesuaian lahan langsung di kanvas QGIS"),
    ("Model Builder Spasial", "Eksekusi Model Buffer Kawasan Lindung", True, True, True, True, "Menjalankan analisis zona penyangga radius sempadan/kawasan lindung"),
    ("Model Builder Spasial", "Eksekusi Model Overlay RTRW vs Bidang Tanah", True, True, True, True, "Menjalankan tumpang susun bidang tanah terhadap zonasi pola ruang"),
    ("Model Builder Spasial", "Membangun / Merancang Model Spasial Baru", False, False, False, False, "Hanya dilakukan di Web Geoportal IGT-PR (QGIS hanya untuk eksekusi)"),

    ("Alur Derivatif Bidang", "Akses Alur 6-Langkah Derivatif Bidang", True, True, True, False, "Alur tematik pembuatan derivatif berbasis bidang tanah"),
    ("Alur Derivatif Bidang", "Langkah 1: Muat Baseline Bidang Tanah QGIS", True, True, True, False, "Memuat data persil dasar ke memori peta"),
    ("Alur Derivatif Bidang", "Langkah 2: Atur Struktur Atribut Baru", True, True, True, False, "Definisi kolom dan tipe data atribut tematik"),
    ("Alur Derivatif Bidang", "Langkah 3: Pilih Bidang Tanah pada Kanvas", True, True, True, False, "Interaksi klik persil bidang tanah di QGIS"),
    ("Alur Derivatif Bidang", "Langkah 4: Isi & Validasi Nilai Atribut", True, True, True, False, "Input data atribut tematik per persil"),
    ("Alur Derivatif Bidang", "Langkah 5: Simpan File GeoPackage / GeoJSON", True, True, True, False, "Ekspor layer tematik derivatif lokal"),
    ("Alur Derivatif Bidang", "Langkah 6: Join Atribut & Tampilkan Hasil di QGIS", True, True, True, False, "Penggabungan otomatis dan render visual kanvas"),
]

roles_info = [
    ("superadmin", "Superadmin", "SA", "Semua Satker", "1E40AF",
     "Akses WFS Seluruh Indonesia, Verifikasi Topologi, Persetujuan Integrasi Nasional, Manajemen Data Penuh. (Catatan: Superadmin tidak mengunggah IGT Utama).",
     "Bertanggung jawab penuh atas tata kelola data geospasial tematik nasional, validasi lintas sektor, dan persetujuan integrasi nasional. Pengunggahan data IGT Utama merupakan tugas Operator Satker."),
    ("admin", "Admin Satker", "AD", "Kantah Kab. Sleman", "6B21A8",
     "Akses WFS Satker Sleman, Unggah IGT Derivatif, Verifikasi Topologi, Persetujuan Derivatif, Menjalankan Model Spasial. (Catatan: Admin tidak mengunggah IGT Utama).",
     "Bertindak sebagai verifikator tingkat satuan kerja (Kantah), memvalidasi kelayakan geometri dan atribut data. Pengunggahan data IGT Utama merupakan tugas Operator Satker."),
    ("operator", "Operator Pusat", "JH", "Kantah Kab. Sleman", "166534",
     "Akses WFS Satker Sleman, Unggah Data IGT Utama (Pertanahan & Tata Ruang) & Derivatif, Perbaikan Revisi, Alur 6-Langkah Derivatif Bidang, Menjalankan Model Spasial.",
     "Pelaksana teknis pengolahan dan pengunggahan data spasial IGT Utama dan Derivatif, perbaikan revisi geometri/atribut, kompilasi data spasial per wilayah."),
    ("umum", "Pengguna Umum", "UM", "Non-Satker (Publik)", "334155",
     "Akses WMS Seluruh Katalog (Tanpa Akses WFS), Unggah Derivatif Multiguna, Menjalankan Model Spasial di QGIS.",
     "Pengguna publik / pemangku kepentingan eksternal yang memanfaatkan katalog peta terpadu untuk keperluan visualisasi, pengajuan derivatif mandiri, dan menjalankan model analisis spasial."),
]

def generate_base_file(base_path):
    wb = openpyxl.Workbook()
    
    # Styles
    font_title = Font(name="Segoe UI", size=14, bold=True, color="0F294D")
    font_sub = Font(name="Segoe UI", size=9.5, italic=True, color="64748B")
    font_tip = Font(name="Segoe UI", size=8.5, bold=True, color="0369A1")
    
    font_head = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    font_section = Font(name="Segoe UI", size=10.5, bold=True, color="0369A1")
    
    font_bold = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
    font_regular = Font(name="Segoe UI", size=10, color="1E293B")
    font_desc = Font(name="Segoe UI", size=9, italic=True, color="475569")
    
    fill_head_main = PatternFill(start_color="0F294D", end_color="0F294D", fill_type="solid")
    fill_head_sa = PatternFill(start_color="1E40AF", end_color="1E40AF", fill_type="solid")
    fill_head_ad = PatternFill(start_color="6B21A8", end_color="6B21A8", fill_type="solid")
    fill_head_op = PatternFill(start_color="166534", end_color="166534", fill_type="solid")
    fill_head_um = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    
    fill_section = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_checked = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
    
    thin_border_side = Side(style="thin", color="CBD5E1")
    border_cell = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_desc = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # SHEET 1: Matriks Hak Akses
    ws1 = wb.active
    ws1.title = "Matriks Hak Akses (Clickable)"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1["A1"] = "MATRIKS HAK AKSES PERAN (ROLE PERMISSION MATRIX) - PLUGIN QGIS IGT-PR"
    ws1["A1"].font = font_title
    ws1["A2"] = "Sistem Informasi Geospasial Tematik Pertanahan dan Tata Ruang (IGT-PR) · Kementerian ATR/BPN"
    ws1["A2"].font = font_sub
    ws1["A3"] = "💡 Tips: Kolom peran (B, C, D, E) berisi Kotak Centang (Checkbox). Klik langsung pada kotak checkbox untuk mengubah status centang."
    ws1["A3"].font = font_tip
    
    headers = [
        ("Fungsi / Fitur Plugin QGIS", fill_head_main, Alignment(horizontal="left", vertical="center")),
        ("superadmin", fill_head_sa, align_center),
        ("admin", fill_head_ad, align_center),
        ("operator", fill_head_op, align_center),
        ("umum", fill_head_um, align_center),
        ("Kategori / Modul", fill_head_main, Alignment(horizontal="left", vertical="center")),
        ("Keterangan & Catatan Hak Akses", fill_head_main, Alignment(horizontal="left", vertical="center")),
    ]
    
    ws1.row_dimensions[5].height = 28
    for col_idx, (h_title, h_fill, h_align) in enumerate(headers, 1):
        cell = ws1.cell(row=5, column=col_idx, value=h_title)
        cell.font = font_head
        cell.fill = h_fill
        cell.alignment = h_align
        cell.border = border_cell
        
    curr_row = 6
    last_group = None
    cb_positions = []
    
    for item in matrix_data:
        grp, func, sa, ad, op, um, note = item
        
        if grp != last_group:
            ws1.row_dimensions[curr_row].height = 24
            cell_sec = ws1.cell(row=curr_row, column=1, value=f"▶ MODUL {grp.upper()}")
            cell_sec.font = font_section
            cell_sec.fill = fill_section
            cell_sec.alignment = align_left
            cell_sec.border = border_cell
            for c in range(2, 8):
                c_cell = ws1.cell(row=curr_row, column=c)
                c_cell.fill = fill_section
                c_cell.border = border_cell
            curr_row += 1
            last_group = grp
            
        ws1.row_dimensions[curr_row].height = 22
        is_zebra = (curr_row % 2 == 0)
        base_fill = fill_zebra if is_zebra else fill_white
        
        c_fn = ws1.cell(row=curr_row, column=1, value=func)
        c_fn.font = font_bold if ("Akses" in func or "Upload" in func or "Unggah" in func) else font_regular
        c_fn.fill = base_fill
        c_fn.border = border_cell
        c_fn.alignment = align_left
        
        for c_idx, val in [(2, sa), (3, ad), (4, op), (5, um)]:
            c_chk = ws1.cell(row=curr_row, column=c_idx, value="")
            c_chk.fill = fill_checked if val else base_fill
            c_chk.border = border_cell
            c_chk.alignment = align_center
            cb_positions.append((c_idx - 1, curr_row - 1, 1 if val else 0))
            
        c_mod = ws1.cell(row=curr_row, column=6, value=grp)
        c_mod.font = font_regular
        c_mod.fill = base_fill
        c_mod.border = border_cell
        c_mod.alignment = align_left
        
        c_nt = ws1.cell(row=curr_row, column=7, value=note)
        c_nt.font = font_desc
        c_nt.fill = base_fill
        c_nt.border = border_cell
        c_nt.alignment = align_desc
        
        curr_row += 1

    ws1.column_dimensions['A'].width = 46
    ws1.column_dimensions['B'].width = 14
    ws1.column_dimensions['C'].width = 14
    ws1.column_dimensions['D'].width = 14
    ws1.column_dimensions['E'].width = 14
    ws1.column_dimensions['F'].width = 24
    ws1.column_dimensions['G'].width = 58
    
    ws1.freeze_panes = "A6"
    ws1.auto_filter.ref = f"A5:G{curr_row - 1}"
    ws1.print_title_rows = "5:5"

    # SHEET 2: Profil Peran
    ws2 = wb.create_sheet(title="Profil Peran (Role Info)")
    ws2.views.sheetView[0].showGridLines = True
    
    ws2["A1"] = "PROFIL DAN DESKRIPSI PERAN PENGGUNA (ROLES) - GEOPORTAL IGT-PR"
    ws2["A1"].font = font_title
    ws2["A2"] = "Tanggung jawab, satuan kerja (satker), dan cakupan wewenang pada Plugin QGIS Mockup V2"
    ws2["A2"].font = font_sub
    
    headers_s2 = ['Kode Peran', 'Nama Peran', 'Avatar', 'Satuan Kerja (Satker)', 'Warna Tema', 'Cakupan Hak Akses Utama', 'Deskripsi Tanggung Jawab & Operasional']
    ws2.row_dimensions[5].height = 26
    for c_idx, h in enumerate(headers_s2, 1):
        c = ws2.cell(row=5, column=c_idx, value=h)
        c.font = font_head
        c.fill = fill_head_main
        c.alignment = align_center if c_idx in [1, 3, 5] else align_left
        c.border = border_cell
        
    for r_idx, r_item in enumerate(roles_info, 6):
        code, name, av, satker, col_hex, hak, desc = r_item
        is_z = (r_idx % 2 == 0)
        b_fill = fill_zebra if is_z else fill_white
        ws2.row_dimensions[r_idx].height = 42
        
        c0 = ws2.cell(row=r_idx, column=1, value=code)
        c0.font = font_bold; c0.fill = b_fill; c0.border = border_cell; c0.alignment = align_center
        
        c1 = ws2.cell(row=r_idx, column=2, value=name)
        c1.font = font_bold; c1.fill = b_fill; c1.border = border_cell; c1.alignment = align_left
        
        c2 = ws2.cell(row=r_idx, column=3, value=av)
        c2.font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        c2.fill = PatternFill(start_color=col_hex, end_color=col_hex, fill_type="solid")
        c2.border = border_cell; c2.alignment = align_center
        
        c3 = ws2.cell(row=r_idx, column=4, value=satker)
        c3.font = font_regular; c3.fill = b_fill; c3.border = border_cell; c3.alignment = align_left
        
        c4 = ws2.cell(row=r_idx, column=5, value=f"#{col_hex}")
        c4.font = font_regular; c4.fill = b_fill; c4.border = border_cell; c4.alignment = align_center
        
        c5 = ws2.cell(row=r_idx, column=6, value=hak)
        c5.font = font_regular; c5.fill = b_fill; c5.border = border_cell; c5.alignment = align_left
        
        c6 = ws2.cell(row=r_idx, column=7, value=desc)
        c6.font = font_desc; c6.fill = b_fill; c6.border = border_cell; c6.alignment = align_desc
        
    ws2.column_dimensions['A'].width = 15
    ws2.column_dimensions['B'].width = 18
    ws2.column_dimensions['C'].width = 12
    ws2.column_dimensions['D'].width = 24
    ws2.column_dimensions['E'].width = 14
    ws2.column_dimensions['F'].width = 46
    ws2.column_dimensions['G'].width = 58
    ws2.freeze_panes = "A6"
    ws2.print_title_rows = "5:5"
    
    wb.save(base_path)
    return cb_positions

def main():
    base_tmp = "/tmp/matrix_base_clean.xlsx"
    cb_positions = generate_base_file(base_tmp)
    print(f"Base file created with {len(cb_positions)} checkboxes.")

    port = 2009
    proc = subprocess.Popen(['libreoffice', '--headless', f'--accept=socket,host=localhost,port={port};urp;'])
    time.sleep(2)
    
    output_single = "/tmp/matrix_with_form_controls.xlsx"
    try:
        localContext = uno.getComponentContext()
        resolver = localContext.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', localContext)
        ctx = resolver.resolve(f'uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext')
        smgr = ctx.ServiceManager
        desktop = smgr.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)

        prop_in = PropertyValue()
        prop_in.Name = 'Hidden'
        prop_in.Value = True
        doc = desktop.loadComponentFromURL(f'file://{base_tmp}', '_blank', 0, (prop_in,))
        
        # Sheet 0 (Matriks)
        sheet0 = doc.getSheets().getByIndex(0)
        draw_page = sheet0.getDrawPage()

        forms = draw_page.getForms()
        if forms.getCount() > 0:
            form = forms.getByIndex(0)
        else:
            form = smgr.createInstanceWithContext('com.sun.star.form.component.DataForm', ctx)
            forms.insertByName('Standard', form)

        sz = Size(420, 420)
        for col_idx, row_idx, state in cb_positions:
            cell = sheet0.getCellByPosition(col_idx, row_idx)
            cb_name = f"chk_{col_idx}_{row_idx}"
            
            cb = smgr.createInstanceWithContext('com.sun.star.form.component.CheckBox', ctx)
            cb.Name = cb_name
            cb.Label = ''
            cb.State = state
            form.insertByName(cb_name, cb)

            shape = doc.createInstance('com.sun.star.drawing.ControlShape')
            shape.setControl(cb)
            shape.setSize(sz)
            
            c_pos = cell.Position
            c_sz = cell.Size
            pt = Point()
            pt.X = c_pos.X + int((c_sz.Width - sz.Width) / 2)
            pt.Y = c_pos.Y + int((c_sz.Height - sz.Height) / 2)
            shape.setPosition(pt)
            
            draw_page.add(shape)
            shape.Anchor = cell

        # Page Styles: Set Landscape, A4, Fit to 1 page wide
        style_families = doc.getStyleFamilies()
        page_styles = style_families.getByName('PageStyles')
        for sheet_idx in range(doc.getSheets().getCount()):
            sh = doc.getSheets().getByIndex(sheet_idx)
            ps_name = sh.getPropertyValue('PageStyle')
            if page_styles.hasByName(ps_name):
                ps = page_styles.getByName(ps_name)
                ps.setPropertyValue('IsLandscape', True)
                ps.setPropertyValue('Width', 29700)
                ps.setPropertyValue('Height', 21000)
                ps.setPropertyValue('ScaleToPagesX', 1)
                ps.setPropertyValue('ScaleToPagesY', 0)

        # Set Design Mode to FALSE so user can immediately click checkboxes
        controller = doc.getCurrentController()
        if hasattr(controller, 'setFormDesignMode'):
            controller.setFormDesignMode(False)

        prop_out = PropertyValue()
        prop_out.Name = 'FilterName'
        prop_out.Value = 'Calc Office Open XML'
        doc.storeToURL(f'file://{output_single}', (prop_out,))
        doc.close(True)
        print("Generated master spreadsheet with native Form Control Checkboxes!")
    finally:
        proc.terminate()

    # Target destinations
    targets = [
        "/home/jhn/projects/SPPR/Mitraeka/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx",
        "/home/jhn/projects/SPPR/Mitraeka/igtpr-qgis-ui/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx",
        "/home/jhn/projects/SPPR/Mitraeka/igtpr-qgis-ui/qgis-plugin-example/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx"
    ]
    for t in targets:
        shutil.copyfile(output_single, t)
        print(f"✓ Copied to: {t}")

if __name__ == "__main__":
    main()

import xlsxwriter

def build_matrix_excel(output_path):
    wb = xlsxwriter.Workbook(output_path)
    
    # Formats
    fmt_title = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 14, 'bold': True, 'font_color': '#0F294D'
    })
    fmt_subtitle = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 9.5, 'italic': True, 'font_color': '#64748B'
    })
    
    # Headers
    fmt_head_main = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
        'bg_color': '#0F294D', 'align': 'left', 'valign': 'vcenter',
        'border': 1, 'border_color': '#475569'
    })
    fmt_head_sa = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
        'bg_color': '#1E40AF', 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#1E3A8A'
    })
    fmt_head_ad = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
        'bg_color': '#6B21A8', 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#581C87'
    })
    fmt_head_op = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
        'bg_color': '#166534', 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#14532D'
    })
    fmt_head_um = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
        'bg_color': '#334155', 'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#1E293B'
    })
    
    # Section Header
    fmt_section = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 10.5, 'bold': True, 'font_color': '#0369A1',
        'bg_color': '#E0F2FE', 'valign': 'vcenter',
        'border': 1, 'border_color': '#BAE6FD'
    })
    
    # Cell Data Formats
    fmt_cell_text = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 10, 'font_color': '#1E293B',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#FFFFFF'
    })
    fmt_cell_text_zebra = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 10, 'font_color': '#1E293B',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC'
    })
    fmt_cell_title = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 10, 'bold': True, 'font_color': '#0F172A',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#FFFFFF'
    })
    fmt_cell_title_zebra = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 10, 'bold': True, 'font_color': '#0F172A',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC'
    })
    
    # Checkbox cell format
    fmt_chk_cell = wb.add_format({
        'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#CBD5E1', 'bg_color': '#FFFFFF'
    })
    fmt_chk_cell_zebra = wb.add_format({
        'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#CBD5E1', 'bg_color': '#F8FAFC'
    })
    
    # Note / description
    fmt_cell_desc = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 9, 'italic': True, 'font_color': '#475569',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#FFFFFF', 'text_wrap': True
    })
    fmt_cell_desc_zebra = wb.add_format({
        'font_name': 'Segoe UI', 'font_size': 9, 'italic': True, 'font_color': '#475569',
        'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC', 'text_wrap': True
    })
    
    # Conditional formatting format for checked state (soft green highlight)
    fmt_cond_checked = wb.add_format({'bg_color': '#ECFDF5'})

    # =========================================================================
    # SHEET 1: Matriks Hak Akses (Checkbox Clickable)
    # =========================================================================
    ws1 = wb.add_worksheet('Matriks Hak Akses (Clickable)')
    ws1.hide_gridlines(0)
    ws1.set_landscape()
    ws1.set_paper(9) # A4
    ws1.fit_to_pages(1, 0)
    
    # Title Block
    ws1.write('A1', 'MATRIKS HAK AKSES PERAN (ROLE PERMISSION MATRIX) - PLUGIN QGIS IGT-PR', fmt_title)
    ws1.write('A2', 'Sistem Informasi Geospasial Tematik Pertanahan dan Tata Ruang (IGT-PR) · Kementerian ATR/BPN', fmt_subtitle)
    ws1.write('A3', '💡 Tips: Kolom peran (B, C, D, E) menggunakan Checkbox interaktif. Klik langsung pada kotak checkbox untuk mengubah status centang.', wb.add_format({'font_name': 'Segoe UI', 'font_size': 8.5, 'bold': True, 'font_color': '#0369A1'}))
    
    # Headers
    row_h = 4
    ws1.set_row(row_h, 28)
    ws1.write(row_h, 0, 'Fungsi / Fitur Plugin QGIS', fmt_head_main)
    ws1.write(row_h, 1, 'superadmin', fmt_head_sa)
    ws1.write(row_h, 2, 'admin', fmt_head_ad)
    ws1.write(row_h, 3, 'operator', fmt_head_op)
    ws1.write(row_h, 4, 'umum', fmt_head_um)
    ws1.write(row_h, 5, 'Kategori / Modul', fmt_head_main)
    ws1.write(row_h, 6, 'Keterangan & Catatan Hak Akses', fmt_head_main)
    
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
        ("Dashboard / Beranda", "Pintasan Hub Model Builder", True, True, True, True, "Pintasan ke katalog modul analisis pemodelan spasial"),

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
        ("Unggah Data (Upload)", "Unggah Data IGT Pertanahan", True, True, True, False, "Hanya internal pengelola data (Operator, Admin, Superadmin)"),
        ("Unggah Data (Upload)", "Unggah Data IGT Tata Ruang", True, True, True, False, "Hanya internal pengelola data (Operator, Admin, Superadmin)"),
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

        ("Model Builder Spasial", "Akses Modul Model Builder", True, True, True, True, "Katalog modul analisis geospasial otomatis"),
        ("Model Builder Spasial", "Eksekusi Model Analisis Kesesuaian Lahan", True, True, True, True, "Analisis multi-kriteria kesesuaian lahan langsung di kanvas"),
        ("Model Builder Spasial", "Eksekusi Model Buffer Kawasan Lindung", True, True, True, True, "Analisis zona penyangga radius sempadan/kawasan lindung"),
        ("Model Builder Spasial", "Eksekusi Model Overlay RTRW vs Bidang Tanah", True, True, True, True, "Tumpang susun bidang tanah terhadap zonasi pola ruang"),

        ("Alur Derivatif Bidang", "Akses Alur 6-Langkah Derivatif Bidang", True, True, True, False, "Alur tematik pembuatan derivatif berbasis bidang tanah"),
        ("Alur Derivatif Bidang", "Langkah 1: Muat Baseline Bidang Tanah QGIS", True, True, True, False, "Memuat data persil dasar ke memori peta"),
        ("Alur Derivatif Bidang", "Langkah 2: Atur Struktur Atribut Baru", True, True, True, False, "Definisi kolom dan tipe data atribut tematik"),
        ("Alur Derivatif Bidang", "Langkah 3: Pilih Bidang Tanah pada Kanvas", True, True, True, False, "Interaksi klik persil bidang tanah di QGIS"),
        ("Alur Derivatif Bidang", "Langkah 4: Isi & Validasi Nilai Atribut", True, True, True, False, "Input data atribut tematik per persil"),
        ("Alur Derivatif Bidang", "Langkah 5: Simpan File GeoPackage / GeoJSON", True, True, True, False, "Ekspor layer tematik derivatif lokal"),
        ("Alur Derivatif Bidang", "Langkah 6: Join Atribut & Tampilkan Hasil di QGIS", True, True, True, False, "Penggabungan otomatis dan render visual kanvas"),
    ]
    
    current_grp = None
    curr_row = 5
    start_data_row = curr_row
    
    for grp, func, sa, ad, op, um, note in matrix_data:
        if grp != current_grp:
            current_grp = grp
            ws1.merge_range(curr_row, 0, curr_row, 6, f"  ▶ MODUL {grp.upper()}", fmt_section)
            ws1.set_row(curr_row, 22)
            curr_row += 1
            
        is_zebra = (curr_row % 2 == 0)
        f_txt = fmt_cell_title_zebra if ("Akses" in func or "Upload" in func or "Unggah" in func) else (fmt_cell_text_zebra if is_zebra else fmt_cell_text)
        f_chk = fmt_chk_cell_zebra if is_zebra else fmt_chk_cell
        f_mod = fmt_cell_text_zebra if is_zebra else fmt_cell_text
        f_dsc = fmt_cell_desc_zebra if is_zebra else fmt_cell_desc
        
        ws1.set_row(curr_row, 21)
        ws1.write(curr_row, 0, func, f_txt)
        
        # INSERT NATIVE CELL CHECKBOXES (CLICKABLE IN EXCEL!)
        ws1.insert_checkbox(curr_row, 1, sa, f_chk)
        ws1.insert_checkbox(curr_row, 2, ad, f_chk)
        ws1.insert_checkbox(curr_row, 3, op, f_chk)
        ws1.insert_checkbox(curr_row, 4, um, f_chk)
        
        ws1.write(curr_row, 5, grp, f_mod)
        ws1.write(curr_row, 6, note, f_dsc)
        
        curr_row += 1
        
    end_data_row = curr_row - 1
    
    # Conditional formatting: saat checkbox bernilai TRUE, beri latar belakang hijau muda lembut
    ws1.conditional_format(start_data_row, 1, end_data_row, 4, {
        'type': 'cell',
        'criteria': '==',
        'value': True,
        'format': fmt_cond_checked
    })
    
    # Column Widths
    ws1.set_column('A:A', 46)
    ws1.set_column('B:E', 14)
    ws1.set_column('F:F', 24)
    ws1.set_column('G:G', 58)
    
    # Freeze Panes at row 5 (header persisten saat scrolling)
    ws1.freeze_panes(5, 0)
    
    # Autofilter
    ws1.autofilter(row_h, 0, end_data_row, 6)

    # =========================================================================
    # SHEET 2: Ringkasan & Profil Peran
    # =========================================================================
    ws2 = wb.add_worksheet('Profil Peran (Role Info)')
    ws2.hide_gridlines(0)
    ws2.set_landscape()
    ws2.set_paper(9)
    ws2.fit_to_pages(1, 0)
    
    ws2.write('A1', 'PROFIL DAN DESKRIPSI PERAN PENGGUNA (ROLES) - GEOPORTAL IGT-PR', fmt_title)
    ws2.write('A2', 'Tanggung jawab, satuan kerja (satker), dan cakupan wewenang pada Plugin QGIS Mockup V2', fmt_subtitle)
    
    headers_ws2 = ['Kode Peran', 'Nama Peran', 'Avatar', 'Satuan Kerja (Satker)', 'Warna Tema', 'Cakupan Hak Akses Utama', 'Deskripsi Tanggung Jawab & Operasional']
    ws2.set_row(4, 26)
    for c_idx, h in enumerate(headers_ws2):
        ws2.write(4, c_idx, h, fmt_head_main)
        
    roles_info = [
        ("superadmin", "Superadmin", "SA", "Semua Satker", "#1E40AF",
         "Akses WFS Seluruh Indonesia, Unggah Semua Kategori (termasuk K/L), Verifikasi Topologi, Persetujuan Integrasi Nasional.",
         "Bertanggung jawab penuh atas tata kelola data geospasial tematik nasional, validasi lintas sektor, persetujuan publikasi data IGT Utama dan eksternal ke Geoportal ATR/BPN."),
        ("admin", "Admin Satker", "AD", "Kantah Kab. Sleman", "#6B21A8",
         "Akses WFS Satker Sleman, Unggah IGT Utama & Derivatif, Verifikasi Topologi, Persetujuan Derivatif, Akses Model Builder.",
         "Bertindak sebagai verifikator tingkat satuan kerja (Kantah), memvalidasi kelayakan geometri dan atribut data sebelum dinaikkan ke tingkat integrasi pusat."),
        ("operator", "Operator Pusat", "JH", "Kantah Kab. Sleman", "#166534",
         "Akses WFS Satker Sleman, Unggah IGT Utama & Derivatif, Perbaikan Revisi Geometri/Atribut, Alur 6-Langkah Derivatif Bidang.",
         "Pelaksana teknis pengolahan data spasial, perbaikan overlap/gap saat revisi, kompilasi data spasial per wilayah, dan input atribut derivatif bidang tanah."),
        ("umum", "Pengguna Umum", "UM", "Non-Satker (Publik)", "#334155",
         "Akses WMS Seluruh Katalog (Tanpa Akses WFS), Unggah Derivatif Multiguna, Eksekusi Model Spasial Model Builder.",
         "Pengguna publik / pemangku kepentingan eksternal yang memanfaatkan katalog peta terpadu untuk keperluan visualisasi, analisis derivatif mandiri, dan pemodelan spasial."),
    ]
    
    for r_idx, r_item in enumerate(roles_info, 5):
        code, name, av, satker, col_hex, hak, desc = r_item
        is_z = (r_idx % 2 == 0)
        f_b = fmt_cell_text_zebra if is_z else fmt_cell_text
        f_d = fmt_cell_desc_zebra if is_z else fmt_cell_desc
        
        ws2.set_row(r_idx, 42)
        ws2.write(r_idx, 0, code, f_b)
        ws2.write(r_idx, 1, name, f_b)
        
        # Avatar with badge background color
        f_av = wb.add_format({
            'font_name': 'Segoe UI', 'font_size': 11, 'bold': True, 'font_color': '#FFFFFF',
            'bg_color': col_hex, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#CBD5E1'
        })
        ws2.write(r_idx, 2, av, f_av)
        ws2.write(r_idx, 3, satker, f_b)
        ws2.write(r_idx, 4, col_hex, f_b)
        ws2.write(r_idx, 5, hak, f_b)
        ws2.write(r_idx, 6, desc, f_d)
        
    ws2.set_column('A:A', 15)
    ws2.set_column('B:B', 18)
    ws2.set_column('C:C', 12)
    ws2.set_column('D:D', 24)
    ws2.set_column('E:E', 14)
    ws2.set_column('F:F', 46)
    ws2.set_column('G:G', 58)
    ws2.freeze_panes(5, 0)
    
    wb.close()
    print(f"✓ Berhasil membuat workbook: {output_path}")

targets = [
    "/home/jhn/projects/SPPR/Mitraeka/igtpr-qgis-ui/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx",
    "/home/jhn/projects/SPPR/Mitraeka/igtpr-qgis-ui/qgis-plugin-example/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx",
    "/home/jhn/projects/SPPR/Mitraeka/MATRIKS_HAK_AKSES_ROLE_QGIS.xlsx"
]

for t in targets:
    build_matrix_excel(t)


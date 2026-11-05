# -*- coding: utf-8 -*-
"""Model data, konfigurasi skema, dan abstraksi data source untuk plugin Geoportal IGT-PR.

=============================================================================
PETUNJUK PENERAPAN KE DATABASE LANGSUNG (UNTUK PENGEMBANG / DATABASE ADMIN)
=============================================================================
Semua data tabel dalam plugin ini dimuat dari satu berkas sumber data: `data.json`.
Arsitektur ini dirancang menggunakan LOOPING dinamis dan PEMETAAN SKEMA (schema mapping)
agar Anda dapat menghubungkan UI ini langsung ke Database (PostgreSQL/PostGIS, SQLite,
MySQL, atau REST API) dengan langkah mudah:

1. MENGGANTI SUMBER DATA KE DATABASE:
   - Ubah `DATA_SOURCE_MODE = 'json'` menjadi `DATA_SOURCE_MODE = 'database'`.
   - Sesuaikan konfigurasi koneksi pada dictionary `DB_CONFIG`.
   - Aktifkan salah satu blok kode koneksi pada fungsi `fetch_from_database()`.

2. MENGGANTI NAMA TABEL & KOLOM DATABASE:
   - Jika nama tabel di database Anda berbeda (misalnya: `tbl_katalog_igt`), ubah
     nilai `'table_name'` pada dictionary `TABLE_SCHEMAS`.
   - Jika nama kolom di database Anda berbeda (misalnya: `'name'` menjadi `'nama_layer'`),
     cukup ubah pemetaan pada `'columns'` di `TABLE_SCHEMAS`.
   - Sistem akan melakukan LOOPING otomatis untuk membaca setiap baris dan memetakan
     kolom database ke model UI tanpa perlu mengubah file antarmuka (UI).

3. PENAMBAHAN RECORD (INSERT):
   - Gunakan fungsi `insert_submission_record()` yang telah dilengkapi looping
     pemetaan terbalik (dari format UI ke kolom database).
=============================================================================
"""

import json
import os

# =============================================================================
# 1. KONFIGURASI SUMBER DATA (DATA SOURCE SETTINGS)
# =============================================================================

# Mode sumber data: 'json' (default mockup) atau 'database'
DATA_SOURCE_MODE = 'json'

# Lokasi berkas sumber data tunggal
DATA_JSON_PATH = os.path.join(os.path.dirname(__file__), 'data.json')

# Konfigurasi koneksi database relasional (PostgreSQL / SQLite / MySQL)
DB_CONFIG = {
    'driver': 'postgresql',  # 'postgresql', 'sqlite', 'mysql'
    'host': 'localhost',
    'port': 5432,
    'dbname': 'geoportal_igtpr',
    'user': 'postgres',
    'password': '',
    # Jika menggunakan SQLite, arahkan ke path berkas .db:
    # 'sqlite_path': os.path.join(os.path.dirname(__file__), 'geoportal.db'),
}


# =============================================================================
# 2. PEMETAAN TABEL & KOLOM (DATABASE SCHEMA MAPPING)
# Ganti nama tabel ('table_name') dan kolom ('columns') sesuai database Anda!
# Format mapping: 'nama_field_ui': 'nama_kolom_di_database'
# =============================================================================
TABLE_SCHEMAS = {
    'datasets': {
        'table_name': 'igt_datasets',  # Nama tabel di database
        'primary_key': 'id',
        'columns': {
            'id': 'id',
            'name': 'name',
            'category': 'category',
            'direktorat': 'direktorat',
            'satker': 'satker',
            'scope': 'scope',
            'prov': 'prov',
            'kab': 'kab',
            'date': 'date',
            'updated': 'updated',
            'status': 'status',
            'multiType': 'multi_type',
            'multiLabel': 'multi_label',
            'instansi': 'instansi',
            'keterangan': 'keterangan',
            'subLayers': 'sub_layers',
        }
    },
    'submissions': {
        'table_name': 'igt_submissions',  # Nama tabel di database
        'primary_key': 'id',
        'columns': {
            'id': 'id',
            'layer': 'layer',
            'name': 'name',
            'category': 'category',
            'satker': 'satker',
            'direktorat': 'direktorat',
            'date': 'date',
            'status': 'status',
            'note': 'note',
            'instansi': 'instansi',
            'scope': 'scope',
        }
    },
    'categories': {
        'table_name': 'igt_categories',
        'primary_key': 'id',
        'columns': {
            'id': 'id',
            'label': 'label',
            'shortLabel': 'short_label',
            'basis': 'basis',
            'icon': 'icon',
            'color': 'color',
            'bg': 'bg',
            'desc': 'description',
        }
    },
    'roles': {
        'table_name': 'igt_roles',
        'primary_key': 'id',
        'columns': {
            'id': 'id',
            'label': 'label',
            'avatar': 'avatar',
            'satker': 'satker',
            'color': 'color',
            'bg': 'bg',
            'desc': 'description',
        }
    }
}


# =============================================================================
# 3. FUNGSI PEMBACA SUMBER DATA & DATABASE ADAPTER (DENGAN LOOPING)
# =============================================================================

def load_raw_json_source():
    """Membaca satu berkas sumber data tunggal (data.json)."""
    if not os.path.exists(DATA_JSON_PATH):
        return {}
    try:
        with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as exc:
        print(f"[IGT-PR] Gagal membaca berkas sumber data {DATA_JSON_PATH}: {exc}")
        return {}


def get_raw_table_records(table_key, raw_data=None):
    """Mengambil raw records dari data.json (mendukung wrapper 'tables' maupun root)."""
    if raw_data is None:
        raw_data = load_raw_json_source()

    tables_dict = raw_data.get('tables', {})
    if table_key in tables_dict:
        data = tables_dict[table_key]
    else:
        data = raw_data.get(table_key, [])

    if isinstance(data, dict):
        return [dict(v, **{'_dict_key': k}) for k, v in data.items()]
    return list(data) if isinstance(data, list) else []


def fetch_from_database(table_name, column_list):
    """Template query langsung ke Database (PostgreSQL / SQLite / QtSql).
    
    Aktifkan dan sesuaikan blok kode di bawah ini jika menghubungkan ke database:
    -------------------------------------------------------------------------
    Contoh 1: PostgreSQL dengan psycopg2 (Direkomendasikan untuk QGIS/PostGIS)
    -------------------------------------------------------------------------
    # import psycopg2
    # from psycopg2.extras import RealDictCursor
    #
    # conn = psycopg2.connect(
    #     host=DB_CONFIG['host'],
    #     port=DB_CONFIG['port'],
    #     dbname=DB_CONFIG['dbname'],
    #     user=DB_CONFIG['user'],
    #     password=DB_CONFIG['password']
    # )
    # with conn.cursor(cursor_factory=RealDictCursor) as cur:
    #     cols_sql = ', '.join([f'"{c}"' for c in column_list]) if column_list else '*'
    #     cur.execute(f'SELECT {cols_sql} FROM "{table_name}"')
    #     rows = cur.fetchall()
    #     return [dict(r) for r in rows]

    -------------------------------------------------------------------------
    Contoh 2: SQLite3 (Berkas Database Lokal)
    -------------------------------------------------------------------------
    # import sqlite3
    # conn = sqlite3.connect(DB_CONFIG.get('sqlite_path', 'geoportal.db'))
    # conn.row_factory = sqlite3.Row
    # cur = conn.cursor()
    # cur.execute(f"SELECT * FROM {table_name}")
    # return [dict(r) for r in cur.fetchall()]
    -------------------------------------------------------------------------
    """
    print(f"[IGT-PR Data Adapter] Mengambil data dari tabel database '{table_name}'...")
    return []


def fetch_table_records(table_key):
    """Mengambil data tabel menggunakan LOOPING dinamis.
    
    Alur Looping:
    1. Ambil baris mentah dari Database atau data.json.
    2. LOOP setiap baris data (rows loop).
    3. Di dalam baris, LOOP setiap definisi kolom (columns loop) sesuai pemetaan
       pada TABLE_SCHEMAS[table_key]['columns'].
    4. Mengembalikan daftar dictionary yang dinormalisasi untuk komponen UI.
    """
    schema = TABLE_SCHEMAS.get(table_key, {})
    col_mapping = schema.get('columns', {})
    db_table_name = schema.get('table_name', table_key)

    # 1. Ambil data mentah
    if DATA_SOURCE_MODE == 'database':
        raw_rows = fetch_from_database(db_table_name, list(col_mapping.values()))
        if not raw_rows:
            # Fallback ke JSON jika database belum terhubung
            raw_rows = get_raw_table_records(table_key)
    else:
        raw_rows = get_raw_table_records(table_key)

    # 2. LOOPING DINAMIS: Pemetaan setiap baris dan kolom
    processed_records = []
    for row in raw_rows:
        mapped_row = {}
        # Loop setiap kolom sesuai schema mapping
        for ui_field, db_col in col_mapping.items():
            if db_col in row:
                mapped_row[ui_field] = row[db_col]
            elif ui_field in row:
                mapped_row[ui_field] = row[ui_field]

        # Salin juga atribut tambahan yang mungkin belum terdaftar di schema
        for key, val in row.items():
            if key not in mapped_row and key not in col_mapping.values() and not key.startswith('_'):
                mapped_row[key] = val

        processed_records.append(mapped_row)

    return processed_records


def load_categories():
    """Memuat data kategori dari berkas sumber data dengan looping pemetaan."""
    raw_data = load_raw_json_source()
    cats_raw = raw_data.get('tables', {}).get('categories', raw_data.get('categories', {}))
    schema = TABLE_SCHEMAS.get('categories', {})
    col_mapping = schema.get('columns', {})

    result = {}
    if isinstance(cats_raw, dict):
        for cat_id, cat_props in cats_raw.items():
            mapped = {}
            for ui_col, db_col in col_mapping.items():
                if db_col in cat_props:
                    mapped[ui_col] = cat_props[db_col]
                elif ui_col in cat_props:
                    mapped[ui_col] = cat_props[ui_col]
            for k, v in cat_props.items():
                if k not in mapped and k not in col_mapping.values():
                    mapped[k] = v
            result[cat_id] = mapped
    elif isinstance(cats_raw, list):
        for item in cats_raw:
            c_id = item.get('id')
            if c_id:
                result[c_id] = item
    return result


def load_roles():
    """Memuat data roles dari berkas sumber data dengan looping pemetaan."""
    raw_data = load_raw_json_source()
    roles_raw = raw_data.get('tables', {}).get('roles', raw_data.get('roles', {}))
    schema = TABLE_SCHEMAS.get('roles', {})
    col_mapping = schema.get('columns', {})

    result = {}
    if isinstance(roles_raw, dict):
        for role_id, role_props in roles_raw.items():
            mapped = {}
            for ui_col, db_col in col_mapping.items():
                if db_col in role_props:
                    mapped[ui_col] = role_props[db_col]
                elif ui_col in role_props:
                    mapped[ui_col] = role_props[ui_col]
            for k, v in role_props.items():
                if k not in mapped and k not in col_mapping.values():
                    mapped[k] = v
            result[role_id] = mapped
    elif isinstance(roles_raw, list):
        for item in roles_raw:
            r_id = item.get('id')
            if r_id:
                result[r_id] = item
    return result


def load_indonesia_regions():
    """Memuat lookup referensi wilayah provinsi & kabupaten/kota dari berkas sumber data."""
    raw_data = load_raw_json_source()
    return raw_data.get('tables', {}).get('indonesia_regions', raw_data.get('indonesia_regions', {}))


# =============================================================================
# 4. INISIALISASI DATA GLOBAL UNTUK SELURUH KOMPONEN PLUGIN
# =============================================================================

# Tabel Dataset Katalog IGT (IGT Pertanahan, Tata Ruang, Derivatif, Lainnya)
DATASETS = fetch_table_records('datasets')

# Tabel Pengajuan / Manajemen Data IGT
SUBMISSIONS = fetch_table_records('submissions')

# Metadata Kategori IGT
CATEGORIES = load_categories()

# Peran Pengguna & Hak Akses
ROLES = load_roles()

# Referensi Wilayah Administrasi Indonesia
INDONESIA_REGIONS = load_indonesia_regions()


def insert_submission_record(record):
    """Menyimpan pengajuan baru ke data source dengan looping pemetaan terbalik.
    
    Jika MODE_DATA_SOURCE == 'database', fungsi ini melakukan looping balik
    dari nama atribut UI ke nama kolom tabel database sebelum dieksekusi.
    """
    schema = TABLE_SCHEMAS.get('submissions', {})
    col_mapping = schema.get('columns', {})
    db_table_name = schema.get('table_name', 'igt_submissions')

    if DATA_SOURCE_MODE == 'database':
        # Looping pemetaan terbalik (UI field -> Kolom Database)
        db_record = {}
        for ui_field, db_col in col_mapping.items():
            if ui_field in record:
                db_record[db_col] = record[ui_field]
        print(f"[IGT-PR] Insert record ke database '{db_table_name}': {db_record}")
        # Masukkan query INSERT INTO ke database Anda di sini

    # Selalu tambahkan ke list lokal agar UI langsung responsif
    SUBMISSIONS.insert(0, record)
    return record


def reload_all_data():
    """Memuat ulang semua tabel data dari sumber data aktif."""
    global DATASETS, SUBMISSIONS, CATEGORIES, ROLES, INDONESIA_REGIONS
    DATASETS = fetch_table_records('datasets')
    SUBMISSIONS = fetch_table_records('submissions')
    CATEGORIES = load_categories()
    ROLES = load_roles()
    INDONESIA_REGIONS = load_indonesia_regions()
    return True


# =============================================================================
# 5. ATURAN HAK AKSES FITUR WFS
# =============================================================================

def can_access_wfs(role_id, dataset):
    """Cek apakah role yang aktif memiliki izin untuk mengakses layer fitur WFS:
    - Superadmin: Bisa akses semua WFS.
    - Admin: Bisa akses WFS sesuai satkernya (Kantah Kab. Sleman).
    - Operator: Bisa akses WFS sesuai satkernya (Kantah Kab. Sleman).
    - Umum: Hanya WMS (tidak dapat mengakses WFS).
    """
    if not role_id:
        return False
    r = str(role_id).replace('2', '').lower()
    if r == 'superadmin':
        return True
    if r == 'umum':
        return False
    # Layer IGT Derivatif Multiguna terintegrasi dapat diakses WFS oleh Admin dan Operator
    if dataset.get('category') == 'derivatif':
        return True
    role_cfg = ROLES.get(r, {})
    user_satker = role_cfg.get('satker') or 'Kantah Kab. Sleman'
    ds_satker = str(dataset.get('satker') or dataset.get('direktorat') or '').strip().lower()
    return 'sleman' in ds_satker or ds_satker == user_satker.lower()


def match_province_name(target, prov_list):
    """Mencocokkan nama provinsi dengan daftar provinsi menggunakan alias, singkatan, & pencarian cerdas."""
    if not target or not prov_list:
        return None
    t = target.strip().lower()
    if t in ('semua provinsi', '-- pilih provinsi terlebih dahulu --', ''):
        return None

    # 1. Exact match (case-insensitive)
    for p in prov_list:
        if p.lower() == t:
            return p

    # 2. Kamus alias & singkatan daerah Indonesia
    aliases_map = {
        'diy': 'daerah istimewa yogyakarta',
        'di yogyakarta': 'daerah istimewa yogyakarta',
        'd.i. yogyakarta': 'daerah istimewa yogyakarta',
        'yogyakarta': 'daerah istimewa yogyakarta',
        'jogja': 'daerah istimewa yogyakarta',
        'dki': 'daerah khusus ibukota jakarta',
        'dki jakarta': 'daerah khusus ibukota jakarta',
        'jakarta': 'daerah khusus ibukota jakarta',
        'babel': 'kepulauan bangka belitung',
        'bangka belitung': 'kepulauan bangka belitung',
        'kep. bangka belitung': 'kepulauan bangka belitung',
        'nad': 'aceh',
        'nanggroe aceh darussalam': 'aceh',
        'kepri': 'kepulauan riau',
        'kep. riau': 'kepulauan riau',
        'jabar': 'jawa barat',
        'jateng': 'jawa tengah',
        'jatim': 'jawa timur',
        'kalbar': 'kalimantan barat',
        'kalteng': 'kalimantan tengah',
        'kalsel': 'kalimantan selatan',
        'kaltim': 'kalimantan timur',
        'kaltara': 'kalimantan utara',
        'sulsel': 'sulawesi selatan',
        'sulut': 'sulawesi utara',
        'sulteng': 'sulawesi tengah',
        'sultra': 'sulawesi tenggara',
        'sulbar': 'sulawesi barat',
        'sumbar': 'sumatera barat',
        'sumsel': 'sumatera selatan',
        'sumut': 'sumatera utara',
        'ntb': 'nusa tenggara barat',
        'ntt': 'nusa tenggara timur',
        'malut': 'maluku utara',
    }

    # Cek apakah input adalah alias yang terdaftar
    canonical_alias = aliases_map.get(t)
    if canonical_alias:
        for p in prov_list:
            if p.lower() == canonical_alias:
                return p
            # Juga jika target dalam daftar provinsi adalah versi singkatnya (misal D.I. Yogyakarta)
            if canonical_alias == 'daerah istimewa yogyakarta' and 'yogyakarta' in p.lower():
                return p
            if canonical_alias == 'daerah khusus ibukota jakarta' and 'jakarta' in p.lower():
                return p
            if canonical_alias == 'aceh' and 'aceh' in p.lower():
                return p

    # 3. Prefix match (jika minimal 3 karakter untuk mencegah salah cocok)
    if len(t) >= 3:
        for p in prov_list:
            if p.lower().startswith(t):
                return p

    # 4. Keyword / Substring match (jika minimal 4 karakter)
    if len(t) >= 4:
        for p in prov_list:
            pl = p.lower()
            if t in pl:
                return p
        if 'yogyakarta' in t or 'jogja' in t:
            for p in prov_list:
                if 'yogyakarta' in p.lower():
                    return p
        if 'jakarta' in t:
            for p in prov_list:
                if 'jakarta' in p.lower():
                    return p
        if 'bangka' in t or 'belitung' in t:
            for p in prov_list:
                if 'bangka' in p.lower():
                    return p

    return None

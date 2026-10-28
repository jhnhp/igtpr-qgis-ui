# Contoh plugin QGIS: halaman login IGT-PR

Implementasi Qt dari mockup `shared/login/index.html` sebagai plugin QGIS kecil yang berdiri sendiri. Plugin ini hanya contoh tampilan: tombol **LOGIN** memancarkan sinyal `loginRequested` dan menampilkan pesan di message bar. Tidak ada autentikasi.

```text
igtpr_login_example/
├── __init__.py      # classFactory
├── metadata.txt
├── plugin.py        # tombol toolbar/menu, membuka dock di sisi kanan
├── login_page.py    # LoginPage (QWidget) dan LoginDockWidget
└── assets.py        # SVG: ilustrasi, ikon fitur, ikon Q, garis kontur
```

## Memasang

Salin atau symlink folder `igtpr_login_example` ke folder plugin profil QGIS, lalu aktifkan **IGT-PR Login (Contoh)** di *Plugins → Manage and Install Plugins* (centang *Show also experimental plugins*).

```bash
# Linux
ln -s "$PWD/igtpr_login_example" ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Windows: %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```

Tombol toolbar *Login IGT-PR (contoh)* membuka dan menutup dock.

Header login menggunakan `Examples/logo-bpn.png` dan `Examples/logo-igtpr.png` dengan judul **GEOPORTAL IGT-PR** dan pola garis latar mengikuti referensi visual. Saat dijalankan dari repository, plugin membaca kedua logo langsung dari folder `Examples/`. Untuk distribusi ZIP mandiri, salin kedua PNG itu ke folder `igtpr_login_example/` agar logo tersedia setelah plugin dipasang. Catatan: aset yang ada di `Examples/` saat ini berupa PNG, bukan SVG.

## Dari HTML ke Qt

| Mockup HTML | Implementasi Qt |
| --- | --- |
| CSS warna, font, sudut bulat, gradien tombol | Qt Style Sheet (`LOGIN_QSS`) |
| `box-shadow` tombol | `QGraphicsDropShadowEffect` |
| Ilustrasi QGIS dan tumpukan layer, ikon | SVG dirender `QSvgRenderer`. SVG ditulis ulang tanpa `filter`, `use` dan `clipPath` karena QtSvg hanya mendukung SVG Tiny 1.2 |
| Lingkaran, kontur, bukit dan pin di latar | Digambar `QPainter` di `LoginPage.paintEvent` |
| Media query | `LoginPage._relayout()` dari `resizeEvent`: ≥ 560 px berdampingan dan 3 kolom fitur, 360–559 px tombol di atas ilustrasi dan 2 kolom, < 360 px 1 kolom |
| `clamp()` ukuran font | Ukuran tetap; judul mengecil di dock sempit lewat property `compact` |

Enum Qt ditulis lengkap (`Qt.AlignmentFlag.AlignTop`, dst.) agar jalan di QGIS berbasis Qt5 maupun Qt6 (`supportsQt6=True`).

## Menyambungkan ke plugin IGT-PR

Plugin IGT-PR sudah punya alur SSO (`PluginIGRPR.login_sso_keycloak`, PKCE lewat `sso_auth.py`). Untuk memakai halaman ini di sana, tambahkan `LoginPage` sebagai halaman login di `stackedWidget` dock, lalu sambungkan sinyalnya:

```python
from .login_page import LoginPage

self.login_page = LoginPage(os.path.join(self.plugin_dir, 'logo-bpn.png'))
self.login_page.loginRequested.connect(self.login_sso_keycloak)
```

## Diuji

Dengan QGIS 3.44 / Qt 5.15 (offscreen): widget dirender di lebar dock 340, 420 dan 760 px, dan siklus plugin (initGui, buka dock, klik LOGIN, tutup, unload) dijalankan dengan `iface` tiruan. Belum diuji di QGIS berbasis Qt6 maupun di jendela QGIS sungguhan.

# -*- coding: utf-8 -*-
"""Gambar vektor untuk halaman login (ikon dan garis kontur).

Semua SVG di sini sengaja ditulis dalam subset yang didukung QtSvg (SVG Tiny 1.2): tanpa <filter>,
<use>, <clipPath> atau CSS. Ilustrasi jendela QGIS dan tumpukan layer berupa PNG (illustration.png),
karena perspektif, tekstur peta dan bayangannya tidak bisa dibuat dengan SVG Tiny.
"""

# Ikon garis 24x24; {color} diganti warna goresan.
_ICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" '
         'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%s</svg>')

ICONS = {
    'layers': _ICON % '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5"/><path d="M3 16.5l9 5 9-5"/>',
    'pin': _ICON % '<path d="M12 22s7-6.5 7-12a7 7 0 0 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.6"/>',
    'gear': _ICON % (
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83'
        'l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4'
        'a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1'
        'H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06'
        'a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0'
        ' 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1'
        ' 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'),
    'link': _ICON % '<path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/>',
    'shield': _ICON % '<path d="M12 2.5l8 3v6c0 5-3.4 8.6-8 10-4.6-1.4-8-5-8-10v-6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    'globe': _ICON % '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 7.5h14M5 16.5h14"/>',
    'upload': _ICON % '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    'database': _ICON % '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
    'map': _ICON % '<polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>',
    'arrow-left': _ICON % '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
    'node-tree': _ICON % '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><line x1="9" y1="6" x2="18" y2="6"/><line x1="6" y1="9" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/>',
    'check': _ICON % '<polyline points="20 6 9 17 4 12"/>',
    'search': _ICON % '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    'logout': _ICON % '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    'chevron-down': _ICON % '<polyline points="6 9 12 15 18 9"/>',
    'chevron-right': _ICON % '<polyline points="9 18 15 12 9 6"/>',
    'user': _ICON % '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    'time': _ICON % '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    'folder': _ICON % '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    'file': _ICON % '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
    'eye': _ICON % '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>',
    'alert': _ICON % '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    'edit': _ICON % '<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>',
    'play': _ICON % '<polygon points="6 4 20 12 6 20 6 4"/>',
    'check-circle': _ICON % '<circle cx="12" cy="12" r="9.5"/><polyline points="8 12.5 11 15.5 16.5 9.5"/>',
    'folder-plus': _ICON % ('<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
                            '<line x1="12" y1="11" x2="12" y2="17"/><line x1="9" y1="14" x2="15" y2="14"/>'),
    'cloud-upload': _ICON % ('<path d="M16 16l-4-4-4 4"/><line x1="12" y1="12" x2="12" y2="21"/>'
                             '<path d="M20.4 18.4A5 5 0 0 0 18 9h-1.3A8 8 0 1 0 3 16.3"/>'),
}

# Ikon "Q" pada tombol LOGIN.
Q_ICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40">'
          '<circle cx="18" cy="18" r="13" fill="none" stroke="{color}" stroke-width="6"/>'
          '<path d="M24 24l10 10" stroke="{color}" stroke-width="7" stroke-linecap="round"/></svg>')

# Garis kontur dekoratif di kanan atas; dirender meregang mengikuti area tujuan.
CONTOUR_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300"
 fill="none" stroke="#9db8d6" stroke-width="0.8" stroke-opacity="0.35">
 <path d="M60 300C80 210 150 170 230 160S390 110 400 40"/><path d="M90 300C110 225 170 192 240 182S395 140 400 75"/>
 <path d="M120 300C140 240 190 214 252 205S398 170 400 110"/><path d="M150 300C170 255 212 236 265 228S400 200 400 145"/>
 <path d="M180 300C198 270 234 258 278 251S400 230 400 180"/><path d="M30 300C50 195 128 148 218 138S385 80 392 0"/>
 <path d="M0 290C20 180 105 125 205 115S370 50 370 0"/><path d="M0 250C10 160 85 105 190 92S345 30 340 0"/>
</svg>"""

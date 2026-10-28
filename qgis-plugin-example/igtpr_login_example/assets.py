# -*- coding: utf-8 -*-
"""Gambar vektor untuk halaman login.

Semua SVG di sini sengaja ditulis dalam subset yang didukung QtSvg (SVG Tiny 1.2):
tanpa <filter>, <use>, <clipPath> atau CSS. Bayangan dibuat dengan bentuk transparan.
"""

# Garis batas bidang yang ditumpuk di atas setiap lapisan (pengganti <use> di versi HTML).
_PARCELS = """
<g fill="none" stroke="#ffffff" stroke-width="2" stroke-opacity="{op}">
 <path d="M0 40h400M0 95h400M0 150h400M0 190h400M55 0v220M120 0v220M170 0v220M240 0v220M300 0v220M350 0v220"/>
 <path d="M20 0l30 220M200 0l-25 220M280 0l40 220M0 120l400-30" stroke-width="1.2"/>
</g>"""

_SLAB_SHADOW = '<rect y="26" width="400" height="220" rx="10" fill="#1f4f8f" fill-opacity="0.10"/>'

ILLUSTRATION_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 470" width="520" height="470">
 <g transform="matrix(1,.07,.42,.24,20,402)">{SHADOW}<rect width="400" height="220" rx="10" fill="#2f9e44"/><rect x="40" y="30" width="120" height="70" fill="#6cc46a"/><rect x="230" y="120" width="150" height="80" fill="#1f7a34"/>{PARCELS_FAINT}</g>
 <g transform="matrix(1,.07,.42,.24,20,362)">{SHADOW}<rect width="400" height="220" rx="10" fill="#d4d8de"/><path d="M0 60C80 80 140 30 220 70S360 120 400 90M60 0l40 220M260 0l-30 220" fill="none" stroke="#7d8794" stroke-width="2.5" stroke-dasharray="7,6"/></g>
 <g transform="matrix(1,.07,.42,.24,20,322)">{SHADOW}<rect width="400" height="220" rx="10" fill="#b57de8"/><rect width="170" height="95" fill="#9b5fdb"/><rect x="240" y="150" width="160" height="70" fill="#d3a8f3"/>{PARCELS}</g>
 <g transform="matrix(1,.07,.42,.24,20,282)">{SHADOW}<rect width="400" height="220" rx="10" fill="#4f9be8"/><rect x="120" y="40" width="120" height="110" fill="#7fbaf5"/><rect x="300" width="100" height="95" fill="#2f7fd6"/>{PARCELS}</g>
 <g transform="matrix(1,.07,.42,.24,20,242)">{SHADOW}<rect width="400" height="220" rx="10" fill="#f5b82e"/><rect x="55" y="95" width="115" height="95" fill="#f7cf63"/><rect x="240" y="40" width="110" height="110" fill="#ec9f1c"/>{PARCELS}</g>

 <rect x="63" y="22" width="440" height="262" rx="9" fill="#1f4f8f" fill-opacity="0.12"/>
 <rect x="58" y="14" width="440" height="262" rx="8" fill="#ffffff" stroke="#c9d6e6"/>
 <rect x="80" y="62" width="250" height="196" fill="#8fd17a"/>
 <path d="M80 62h150l-30 90-120 20z" fill="#f6c440"/><path d="M200 62h130v80l-70 10z" fill="#f2e38f"/>
 <path d="M150 140l90-10 40 128H150z" fill="#f8e6a6"/><path d="M250 150l80-20v128h-40z" fill="#9cc3f2"/>
 <path d="M80 200l70-20 10 78H80z" fill="#59b458"/><path d="M285 205l45-5v58h-35z" fill="#b28be6"/>
 <path d="M255 66C250 120 280 160 300 200S320 240 326 254" fill="none" stroke="#3d8ee6" stroke-width="9"/>
 <path d="M130 62C140 130 160 190 150 258" fill="none" stroke="#1f6b43" stroke-width="3"/>
 <path d="M80 90h250M80 118h250M80 146h250M80 174h250M80 202h250M80 230h250M105 62v196M130 62v196M155 62v196M180 62v196M205 62v196M230 62v196M280 62v196M305 62v196" stroke="#ffffff" stroke-width="1" stroke-opacity="0.7"/>
 <rect x="58" y="14" width="440" height="20" rx="8" fill="#3f86de"/><rect x="58" y="26" width="440" height="8" fill="#3f86de"/>
 <text x="70" y="28" fill="#ffffff" font-family="Arial" font-size="10" font-weight="bold">QGIS</text>
 <rect x="58" y="34" width="440" height="24" fill="#f1f4f8"/>
 <g fill="#9fb0c5"><rect x="66" y="40" width="10" height="10" rx="2"/><rect x="80" y="40" width="10" height="10" rx="2"/><rect x="94" y="40" width="10" height="10" rx="2"/><rect x="140" y="40" width="10" height="10" rx="2"/><rect x="160" y="40" width="10" height="10" rx="2"/><rect x="188" y="40" width="10" height="10" rx="2"/></g>
 <rect x="112" y="40" width="10" height="10" rx="2" fill="#f2b84b"/><rect x="126" y="40" width="10" height="10" rx="2" fill="#6bb36f"/><rect x="174" y="40" width="10" height="10" rx="2" fill="#5d9be2"/>
 <rect x="58" y="58" width="22" height="200" fill="#ffffff"/>
 <g fill="#c5d0dd"><rect x="64" y="66" width="8" height="8" rx="2"/><rect x="64" y="82" width="8" height="8" rx="2"/><rect x="64" y="98" width="8" height="8" rx="2"/><rect x="64" y="114" width="8" height="8" rx="2"/><rect x="64" y="130" width="8" height="8" rx="2"/></g>
 <rect x="336" y="62" width="156" height="196" fill="#ffffff" stroke="#e1e8f1"/>
 <g font-family="Arial" font-size="11" fill="#22344f">
  <rect x="348" y="80" width="13" height="13" rx="2" fill="#f5b82e"/><text x="370" y="91">Bidang Tanah</text>
  <rect x="348" y="112" width="13" height="13" rx="2" fill="#7fbaf5"/><text x="370" y="123">Rencana Tata Ruang</text>
  <rect x="348" y="144" width="13" height="13" rx="2" fill="#b57de8"/><text x="370" y="155">Zona Nilai Tanah</text>
  <rect x="348" y="176" width="13" height="13" rx="2" fill="#c5cad1"/><text x="370" y="187">Batas Administrasi</text>
  <rect x="348" y="208" width="13" height="13" rx="2" fill="#2f9e44"/><text x="370" y="219">Kawasan Hutan</text>
 </g>
 <rect x="58" y="258" width="440" height="18" fill="#f1f4f8"/>
 <g fill="#c5d0dd"><rect x="120" y="264" width="40" height="6" rx="3"/><rect x="200" y="264" width="30" height="6" rx="3"/><rect x="300" y="264" width="50" height="6" rx="3"/><rect x="420" y="264" width="40" height="6" rx="3"/></g>
</svg>""".replace('{SHADOW}', _SLAB_SHADOW) \
    .replace('{PARCELS_FAINT}', _PARCELS.format(op='0.4')) \
    .replace('{PARCELS}', _PARCELS.format(op='0.85'))

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

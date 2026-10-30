#!/usr/bin/env python3
"""Render the login page illustration: a QGIS window floating above a stack of IGT map layers.

The picture follows the reference poster (Examples/WhatsApp Image 2026-10-28 at 10.25.23.jpeg).
It is generated instead of drawn by hand so it can be tuned and rendered again:

    python3 tools/make_login_illustration.py

The same PNG is written for the HTML mockup and for the example QGIS plugin.
Requires Pillow, numpy and scipy. The random seed is fixed, so the output is reproducible.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage
from scipy.spatial import Voronoi, cKDTree

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = [
    ROOT / 'shared/login/illustration.png',
    ROOT / 'qgis-plugin-example/igtpr_login_example/illustration.png',
]

# Positions are in "design units": the reference picture's illustration area, enlarged 2x.
DESIGN_SIZE = (1120, 1090)
SCALE = 1.6             # composite pixels per design unit
FINAL_DOWNSAMPLE = 2    # the composite is rendered at 2x and reduced at the end (anti-aliasing)
LANCZOS = Image.Resampling.LANCZOS
BICUBIC = Image.Resampling.BICUBIC

rng = np.random.default_rng(20261028)

# The QGIS window as a perspective quad: top-left, top-right, bottom-right, bottom-left.
WINDOW_QUAD = [(103, 28), (1087, 72), (1078, 585), (32, 515)]

# Map layers from top to bottom: left corner, front edge (left -> front corner), right edge (front -> right corner).
SLABS = [
    ('yellow', (35, 592), (795, 93), (227, -163)),
    ('blue', (35, 665), (775, 108), (235, -170)),
    ('purple', (35, 736), (763, 122), (243, -178)),
    ('gray', (34, 806), (752, 135), (252, -186)),
    ('green', (33, 877), (740, 146), (262, -194)),
]

LEGEND = [
    ((247, 192, 66), 'Bidang Tanah'),
    ((142, 197, 245), 'Rencana Tata Ruang'),
    ((185, 138, 240), 'Zona Nilai Tanah'),
    ((200, 203, 208), 'Batas Administrasi'),
    ((31, 154, 58), 'Kawasan Hutan'),
]


# ---------------------------------------------------------------------------------------------- helpers
def font(weight, size):
    candidates = {
        'regular': ['NotoSans-Regular.ttf', 'segoeui.ttf', 'DejaVuSans.ttf', 'Arial.ttf'],
        'medium': ['NotoSans-Medium.ttf', 'seguisb.ttf', 'NotoSans-Regular.ttf', 'DejaVuSans.ttf', 'Arial.ttf'],
        'bold': ['NotoSans-Bold.ttf', 'segoeuib.ttf', 'DejaVuSans-Bold.ttf', 'Arial Bold.ttf'],
    }[weight]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def design(x, y):
    """Design units -> composite pixels."""
    return (x * SCALE, y * SCALE)


def spline(points, samples=24):
    """Catmull-Rom curve through the points."""
    pts = [points[0], *points, points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = (np.asarray(p, float) for p in pts[i - 1:i + 3])
        for t in np.linspace(0, 1, samples, endpoint=False):
            out.append(tuple(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                    + (3 * p1 - p0 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(points[-1]))
    return out


def scaled(points, w, h):
    return [(u * w, v * h) for u, v in points]


def lattice(w, h, sx, sy, angle=0.0, jitter=0.0):
    """Seed points on a rotated, jittered grid: Voronoi cells of it look like land parcels."""
    a = math.radians(angle)
    r = math.hypot(w, h)
    i, j = np.meshgrid(np.arange(-r / sx, r / sx + 1), np.arange(-r / sy, r / sy + 1))
    x, y = i.ravel() * sx, j.ravel() * sy
    pts = np.column_stack([w / 2 + x * math.cos(a) - y * math.sin(a), h / 2 + x * math.sin(a) + y * math.cos(a)])
    pts += rng.uniform(-jitter, jitter, pts.shape)
    keep = (pts[:, 0] > -2 * sx) & (pts[:, 0] < w + 2 * sx) & (pts[:, 1] > -2 * sy) & (pts[:, 1] < h + 2 * sy)
    return pts[keep]


def noise(h, w, cell):
    """Smooth random field (unit variance) with features about `cell` pixels wide."""
    small = rng.normal(size=(int(h / cell) + 3, int(w / cell) + 3)).astype(np.float32)
    field = np.asarray(Image.fromarray(small, 'F').resize((w, h), BICUBIC))
    return field / (field.std() + 1e-6)


def parcels(h, w, seeds, mask=None, wavy=0.0, wavy_cell=100):
    """Index of the nearest seed for every pixel (optionally only inside `mask`), with wavy borders."""
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    if wavy:
        xs += noise(h, w, wavy_cell) * wavy
        ys += noise(h, w, wavy_cell) * wavy
    labels = np.full((h, w), -1, np.int64)
    sel = np.ones((h, w), bool) if mask is None else mask
    _, idx = cKDTree(seeds).query(np.column_stack([xs[sel], ys[sel]]), workers=-1)
    labels[sel] = idx
    return labels


def seed_colors(n, palette, weights=None, index=None, jitter=0.035):
    palette = np.asarray(palette, np.float32)
    if index is None:
        index = rng.choice(len(palette), size=n, p=weights)
    colors = palette[np.clip(index, 0, len(palette) - 1)]
    return np.clip(colors * (1 + rng.normal(0, jitter, (n, 1))), 0, 255)


def edges(labels, width=1):
    b = np.zeros(labels.shape, bool)
    b[:, 1:] |= labels[:, 1:] != labels[:, :-1]
    b[1:, :] |= labels[1:, :] != labels[:-1, :]
    if width > 1:
        b = ndimage.binary_dilation(b, iterations=width - 1)
    return b


def paint(img, mask, color, alpha=1.0):
    a = mask.astype(np.float32)[..., None] * alpha
    img *= 1 - a
    img += np.asarray(color, np.float32) * a


def to_image(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')


def stroke_distance(shape, polylines):
    """Distance (px) from every pixel to the nearest of the polylines."""
    h, w = shape
    centre = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(centre)
    for pts in polylines:
        draw.line(pts, fill=255, width=1)
    return ndimage.distance_transform_edt(np.asarray(centre) == 0)


def soft(dist, radius):
    """Anti-aliased disc mask around a stroke: 1 inside `radius`, fading over one pixel."""
    return np.clip(radius + 0.5 - dist, 0, 1)


def strokes(img, groups, casing=None, casing_width=5):
    """Paint (polylines, width, color) groups with round joins; optional casing under all of them."""
    dists = [(stroke_distance(img.shape[:2], polylines), width, color) for polylines, width, color in groups]
    if casing:
        for dist, width, _ in dists:
            paint(img, soft(dist, (width + casing_width) / 2), casing)
    for dist, width, color in dists:
        paint(img, soft(dist, width / 2), color)


def curves(points_list, w, h):
    return [spline(scaled(p, w, h)) for p in points_list]


def dashed(draw, pts, dash, gap, width, fill):
    pts = np.asarray(pts, float)
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    s = 0.0
    while s < cum[-1]:
        t = np.linspace(s, min(s + dash, cum[-1]), 6)
        draw.line(list(zip(np.interp(t, cum, pts[:, 0]), np.interp(t, cum, pts[:, 1]))), fill=fill, width=width)
        s += dash + gap


def aa_mask(size, draw_fn, factor=4):
    """Anti-aliased L mask: draw at `factor`x and reduce."""
    w, h = size
    big = Image.new('L', (w * factor, h * factor), 0)
    draw_fn(ImageDraw.Draw(big), factor)
    return big.resize(size, LANCZOS)


def perspective_coeffs(dst, src):
    """Image.transform(PERSPECTIVE) coefficients mapping output points `dst` to input points `src`."""
    rows, rhs = [], []
    for (x, y), (u, v) in zip(dst, src):
        rows += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        rhs += [u, v]
    return np.linalg.solve(np.array(rows, float), np.array(rhs, float)).tolist()


def warp(img, quad, canvas_size):
    """Place an RGBA image on the canvas so its corners land on `quad` (TL, TR, BR, BL)."""
    w, h = img.size
    coeffs = perspective_coeffs(quad, [(0, 0), (w, 0), (w, h), (0, h)])
    out = img.convert('RGBa').transform(canvas_size, Image.Transform.PERSPECTIVE, coeffs, BICUBIC)
    return out.convert('RGBA')


def shifted_alpha(alpha, dx, dy, opacity=1.0, blur=0):
    out = Image.new('L', alpha.size, 0)
    out.paste(alpha.point(lambda v: int(v * opacity)), (int(dx), int(dy)))
    return out.filter(ImageFilter.GaussianBlur(blur)) if blur else out


def flat_layer(size, color, alpha):
    layer = Image.new('RGBA', size, tuple(color) + (0,))
    layer.putalpha(alpha)
    return layer


# ---------------------------------------------------------------------------------------------- the map
def lots(h, w, spacing, angle=0.0, jitter=0.22, wavy=8, mask=None):
    """Land lots: Voronoi cells of a jittered, rotated grid; low jitter keeps them close to rectangles."""
    sx, sy = spacing
    seeds = lattice(w, h, sx, sy, angle, jitter * min(sx, sy))
    return seeds, parcels(h, w, seeds, mask, wavy=wavy, wavy_cell=max(sx, sy) * 1.5)


GREENS = [(146, 208, 100), (128, 200, 84), (112, 190, 70), (98, 180, 60), (86, 170, 54), (164, 216, 120)]

# zone: lot size, angle, jitter, wavy borders, palette, weights, border alpha, border width
MAP_ZONES = {
    0: ((150, 112), 8, 0.25, 10, GREENS, [0.2, 0.24, 0.22, 0.14, 0.08, 0.12], 0.8, 3),
    1: ((24, 17), -33, 0.08, 0, [(247, 236, 164), (245, 231, 152), (249, 241, 178), (243, 227, 144)],
        [0.35, 0.3, 0.2, 0.15], 0.75, 2),
    2: ((92, 68), -33, 0.15, 3, [(246, 182, 60), (248, 194, 76), (244, 170, 48), (250, 206, 100)],
        [0.35, 0.3, 0.2, 0.15], 0.9, 3),
    3: ((120, 96), 12, 0.25, 6, [(150, 190, 240), (126, 176, 236), (170, 206, 246), (110, 164, 232),
                                 (138, 184, 238)], None, 0.7, 3),
    4: ((100, 86), 12, 0.25, 6, [(188, 148, 234), (172, 128, 228), (204, 170, 240), (160, 116, 222)], None,
        0.7, 3),
    5: ((220, 220), 0, 0.3, 0, [(226, 237, 180), (220, 233, 170)], None, 0.6, 3),
    6: ((130, 100), -10, 0.25, 10, GREENS[:4], None, 0.8, 3),
}


def map_texture(w, h):
    """The map shown in the QGIS canvas: rural fields, a dense residential grid, rivers and roads."""
    zone_polygons = [  # zone id, polygon in normalized map coordinates (later zones are drawn on top)
        (1, [(0.06, 0.55), (0.18, 0.38), (0.33, 0.31), (0.47, 0.22), (0.60, 0.11), (0.69, 0.0), (0.88, 0.0),
             (0.83, 0.12), (0.78, 0.25), (0.73, 0.37), (0.66, 0.47), (0.58, 0.55), (0.51, 0.63), (0.45, 0.71),
             (0.38, 0.67), (0.29, 0.64), (0.19, 0.69), (0.09, 0.66)]),
        (2, [(0.26, 0.0), (0.70, 0.0), (0.63, 0.12), (0.55, 0.19), (0.47, 0.24), (0.41, 0.29), (0.35, 0.27),
             (0.30, 0.25), (0.25, 0.14)]),
        (6, [(0.86, 0.0), (1.0, 0.0), (1.0, 0.61), (0.92, 0.58), (0.86, 0.50), (0.80, 0.40), (0.80, 0.22)]),
        (3, [(0.55, 0.66), (0.63, 0.56), (0.72, 0.52), (0.80, 0.50), (0.88, 0.56), (0.86, 0.70), (0.85, 1.0),
             (0.57, 1.0)]),
        (4, [(0.85, 0.66), (0.92, 0.60), (1.0, 0.61), (1.0, 1.0), (0.85, 1.0)]),
        (5, [(0.59, 0.63), (0.66, 0.55), (0.73, 0.50), (0.70, 0.63), (0.67, 0.78), (0.655, 1.0), (0.58, 1.0),
             (0.59, 0.82)]),
    ]
    zone_img = Image.new('L', (w, h), 0)
    zd = ImageDraw.Draw(zone_img)
    for zone, poly in zone_polygons:
        zd.polygon(scaled(poly, w, h), fill=zone)
    zones = np.asarray(zone_img)

    img = np.zeros((h, w, 3), np.float32)
    labels = np.full((h, w), -1, np.int64)
    cream_seeds = None
    offset = 0
    for zone, (spacing, angle, jitter, wavy, palette, weights, border, width) in MAP_ZONES.items():
        mask = zones == zone
        seeds, lab = lots(h, w, spacing, angle, jitter, wavy, mask)
        colors = seed_colors(len(seeds), palette, weights)
        if zone == 0:  # a few cream fields between the green ones
            colors[rng.random(len(seeds)) < 0.06] = (246, 236, 176)
        if zone in (3, 4):  # a few peach lots
            colors[rng.random(len(seeds)) < 0.06] = (244, 188, 162)
        img[mask] = colors[lab[mask]]
        labels[mask] = lab[mask] + offset
        paint(img, edges(np.where(mask, labels, -1), width) & mask, (255, 255, 255), border)
        if zone == 1:
            cream_seeds = (seeds, offset)
        offset += len(seeds)

    # Streets between the residential blocks, and white lines between zones.
    cream = zones == 1
    _, blocks = lots(h, w, (176, 116), -33, 0.04, 0, cream)
    paint(img, edges(blocks, 5) & cream, (255, 255, 255), 0.95)
    paint(img, edges(zones, 5), (255, 255, 255), 0.95)

    # Lots just below the orange district: some filled light orange, the groups outlined in orange.
    seeds, off = cream_seeds
    area = Image.new('L', (w, h), 0)
    ImageDraw.Draw(area).polygon(scaled([(0.35, 0.29), (0.47, 0.25), (0.53, 0.31), (0.47, 0.43), (0.41, 0.49),
                                         (0.37, 0.41)], w, h), fill=1)
    area = np.asarray(area).astype(bool)
    inside = np.array([i for i, (x, y) in enumerate(seeds) if 0 <= x < w and 0 <= y < h and area[int(y), int(x)]])
    picked = np.isin(labels, inside + off) & cream
    filled = np.isin(labels, inside[rng.random(len(inside)) < 0.35] + off) & cream
    paint(img, filled, (250, 210, 128))
    outline = (edges(picked.astype(np.int8), 4) | edges(filled.astype(np.int8), 4)) & \
        ndimage.binary_dilation(picked, iterations=2)
    paint(img, outline, (238, 152, 40), 0.95)

    river = spline(scaled([(1.03, 0.03), (0.93, 0.20), (0.86, 0.33), (0.79, 0.44), (0.73, 0.55), (0.69, 0.70),
                           (0.665, 0.86), (0.655, 1.04)], w, h))
    dist = stroke_distance((h, w), [river])
    paint(img, soft(dist, h * 0.035 + 14), (255, 255, 255))
    paint(img, soft(dist, h * 0.035), (164, 204, 243))
    stream = spline(scaled([(0.30, 0.52), (0.335, 0.58), (0.368, 0.66), (0.392, 0.76), (0.407, 0.88),
                            (0.413, 1.04)], w, h))
    paint(img, soft(stroke_distance((h, w), [stream]), 8), (24, 88, 84))

    major = [
        [(0.0, 0.50), (0.10, 0.47), (0.20, 0.45), (0.27, 0.47), (0.33, 0.53), (0.40, 0.60), (0.47, 0.70),
         (0.52, 0.80)],
        [(0.0, 0.86), (0.10, 0.80), (0.22, 0.74), (0.33, 0.66)],
        [(0.18, 0.66), (0.32, 0.56), (0.45, 0.47), (0.57, 0.38), (0.66, 0.30), (0.74, 0.22), (0.80, 0.12),
         (0.84, 0.0)],
        [(0.60, 0.52), (0.67, 0.43), (0.72, 0.37), (0.76, 0.35), (0.80, 0.38), (0.83, 0.47), (0.90, 0.53),
         (1.0, 0.56)],
        [(0.87, 0.0), (0.875, 0.12), (0.86, 0.24), (0.81, 0.34)],
    ]
    minor = [
        [(0.05, 0.0), (0.08, 0.12), (0.12, 0.22), (0.18, 0.30)],
        [(0.16, 0.0), (0.17, 0.10), (0.15, 0.20)],
        [(0.0, 0.30), (0.07, 0.33), (0.14, 0.40)],
        [(0.10, 0.62), (0.14, 0.75), (0.16, 0.90), (0.20, 1.0)],
        [(0.24, 0.80), (0.30, 0.86), (0.33, 1.0)],
        [(0.62, 0.70), (0.66, 0.78), (0.72, 0.84), (0.80, 0.88), (0.90, 0.90), (1.0, 0.92)],
        [(0.88, 0.56), (0.86, 0.70), (0.86, 0.82), (0.88, 1.0)],
        [(0.92, 0.20), (0.96, 0.30), (1.0, 0.34)],
        [(0.0, 0.12), (0.06, 0.16), (0.12, 0.16), (0.22, 0.10), (0.26, 0.04)],
    ]
    strokes(img, [(curves(major, w, h), 15, (255, 255, 255)), (curves(minor, w, h), 8, (255, 255, 255))],
            casing=(206, 212, 221))
    strokes(img, [(curves([[(0.27, 0.60), (0.31, 0.70), (0.35, 0.82), (0.37, 1.0)],
                           [(0.04, 0.93), (0.16, 0.87), (0.26, 0.85)]], w, h), 6, (236, 152, 44))])
    return to_image(img)


# ---------------------------------------------------------------------------------------------- slab textures
def slab_texture(kind, w, h):
    if kind == 'green':
        field = noise(h, w, 150) * 0.65 + noise(h, w, 55) * 0.3 + noise(h, w, 18) * 0.2
        img = np.empty((h, w, 3), np.float32)
        img[:] = (18, 90, 36)
        for limit, color in ((-0.35, (28, 112, 44)), (0.15, (44, 136, 54)), (0.6, (74, 162, 64)),
                             (1.05, (122, 194, 92))):
            img[field > limit] = color
        _, lab = lots(h, w, (140, 110), 15, 0.3, 14)
        paint(img, edges(lab, 2), (16, 84, 32), 0.35)
        streams = [
            [(0.0, 0.70), (0.12, 0.62), (0.22, 0.58), (0.30, 0.48), (0.42, 0.42), (0.50, 0.30)],
            [(0.55, 1.0), (0.58, 0.80), (0.66, 0.66), (0.78, 0.58), (0.86, 0.40), (0.92, 0.20), (1.0, 0.12)],
            [(0.30, 1.0), (0.36, 0.86), (0.48, 0.80), (0.58, 0.80)],
        ]
        strokes(img, [(curves(streams, w, h), 6, (150, 212, 112))])
        return to_image(img)

    if kind == 'gray':
        seeds, lab = lots(h, w, (120, 90), 8, 0.3, 10)
        img = seed_colors(len(seeds), [(220, 223, 228), (212, 215, 221), (226, 228, 232), (204, 207, 214)],
                          [0.3, 0.3, 0.25, 0.15], jitter=0.01)[lab]
        paint(img, edges(lab, 2), (236, 238, 241), 0.45)
        strokes(img, [(curves([[(0.0, 0.30), (0.30, 0.36), (0.60, 0.30), (1.0, 0.36)],
                               [(0.45, 0.0), (0.42, 0.50), (0.50, 1.0)]], w, h), 6, (236, 238, 242))])
        image = to_image(img)
        draw = ImageDraw.Draw(image)
        vor = Voronoi(lattice(w, h, 290, 230, angle=14, jitter=90))
        for a, b in vor.ridge_vertices:
            if a < 0 or b < 0:
                continue
            p, q = vor.vertices[a], vor.vertices[b]
            if not any(-50 < x < w + 50 and -50 < y < h + 50 for x, y in (p, q)):
                continue
            t = np.linspace(0, 1, 9)[:, None]
            normal = np.array([q[1] - p[1], p[0] - q[0]]) / (np.hypot(*(q - p)) + 1e-6)
            bend = np.sin(np.pi * t) * rng.normal(0, 14) + np.sin(2 * np.pi * t) * rng.normal(0, 8)
            dashed(draw, spline([tuple(v) for v in p + t * (q - p) + bend * normal], 6), 16, 10, 5, (60, 68, 82))
        return image

    if kind == 'yellow':
        seeds, lab = lots(h, w, (96, 72), 22, 0.22, 8)
        palette = [(252, 226, 152), (250, 214, 120), (248, 201, 92), (246, 186, 64), (244, 170, 44), (240, 156, 36)]
        index = np.round(0.8 + 3.2 * seeds[:, 0] / w + rng.normal(0, 1.0, len(seeds))).astype(int)
        img = seed_colors(len(seeds), palette, index=index)[lab]
        paint(img, edges(lab, 3), (255, 255, 255), 0.55)
        _, blocks = lots(h, w, (330, 240), 22, 0.15, 10)
        paint(img, edges(blocks, 6), (255, 255, 255), 0.9)
        roads = [
            [(0.0, 0.55), (0.15, 0.50), (0.30, 0.42), (0.45, 0.40), (0.62, 0.30), (0.80, 0.24), (1.0, 0.20)],
            [(0.20, 1.0), (0.26, 0.80), (0.33, 0.62), (0.36, 0.42), (0.40, 0.20), (0.42, 0.0)],
            [(0.55, 1.0), (0.60, 0.80), (0.68, 0.62), (0.80, 0.50), (0.92, 0.44), (1.0, 0.43)],
        ]
        strokes(img, [(curves(roads, w, h), 11, (255, 255, 255)),
                      (curves([[(0.47, 1.0), (0.47, 0.6), (0.48, 0.2), (0.48, 0.0)]], w, h), 8, (236, 150, 40))])
        return to_image(img)

    if kind == 'blue':
        seeds, lab = lots(h, w, (96, 76), -15, 0.3, 14)
        palette = [(178, 212, 248), (150, 194, 244), (120, 174, 240), (92, 154, 234), (66, 134, 226), (46, 116, 216)]
        index = np.round(3.6 - 2.4 * seeds[:, 0] / w + rng.normal(0, 1.1, len(seeds))).astype(int)
        img = seed_colors(len(seeds), palette, index=index)[lab]
        paint(img, edges(lab, 3), (200, 222, 250), 0.4)
        roads = [
            [(0.0, 0.40), (0.20, 0.46), (0.40, 0.50), (0.52, 0.62), (0.58, 0.82), (0.60, 1.0)],
            [(0.38, 0.0), (0.44, 0.24), (0.52, 0.40), (0.70, 0.52), (0.86, 0.66), (1.0, 0.72)],
            [(0.75, 0.0), (0.78, 0.30), (0.86, 0.66)],
        ]
        strokes(img, [(curves(roads, w, h), 8, (240, 246, 253))])
        return to_image(img).filter(ImageFilter.GaussianBlur(0.8))

    # purple: soft lots, darker on the left
    seeds, lab = lots(h, w, (120, 90), 10, 0.3, 14)
    palette = [(222, 192, 248), (208, 172, 243), (194, 152, 238), (178, 132, 230), (162, 112, 222), (146, 94, 212)]
    index = np.round(4.2 - 3.6 * seeds[:, 0] / w + rng.normal(0, 0.9, len(seeds))).astype(int)
    img = seed_colors(len(seeds), palette, index=index)[lab]
    paint(img, edges(lab, 3), (222, 200, 246), 0.35)
    return to_image(img).filter(ImageFilter.GaussianBlur(2.0))


def slab_layers(kind, left, front, right, canvas_size):
    """Shadow, glow, edge and textured top of one map layer, in drawing order."""
    lx, ly = left
    bx, by = lx + front[0], ly + front[1]
    rx, ry = bx + right[0], by + right[1]
    tx, ty = lx + right[0], ly + right[1]
    quad = [design(tx, ty), design(rx, ry), design(bx, by), design(lx, ly)]
    pw = int(math.hypot(*front) * SCALE)
    ph = int(math.hypot(*right) * SCALE)

    # Texture in true proportions, then squeezed to the foreshortened size (cheap perspective + filtering).
    surface = slab_texture(kind, 1400, 1000).resize((pw, ph), LANCZOS).convert('RGBA')
    radius, rim = 22, 9
    shape = aa_mask((pw, ph), lambda d, f: d.rounded_rectangle([0, 0, pw * f - 1, ph * f - 1], radius * f, fill=255))
    border = aa_mask((pw, ph), lambda d, f: d.rounded_rectangle([0, 0, pw * f - 1, ph * f - 1], radius * f,
                                                                 outline=255, width=rim * f))
    surface.paste((255, 255, 255, 255), mask=border)
    surface.putalpha(shape)
    top = warp(surface, quad, canvas_size)

    alpha = top.getchannel('A')
    return [
        flat_layer(canvas_size, (34, 82, 160), shifted_alpha(alpha, 0, 26, 0.22, 16)),
        flat_layer(canvas_size, (255, 255, 255), shifted_alpha(alpha, 0, 12, 0.55, 7)),
        flat_layer(canvas_size, (204, 216, 233), shifted_alpha(alpha, 0, 12)),
        flat_layer(canvas_size, (242, 246, 251), shifted_alpha(alpha, 0, 6)),
        top,
    ]


# ---------------------------------------------------------------------------------------------- QGIS window
def toolbar_icon(draw, x, y, kind, s=22):
    blue, gray, yellow, green, red = (92, 142, 214), (138, 152, 172), (246, 196, 72), (106, 186, 92), (230, 112, 96)
    if kind == 'folder':
        draw.rounded_rectangle([x, y + 5, x + s, y + s - 2], 3, fill=yellow)
        draw.rectangle([x, y + 3, x + 9, y + 7], fill=yellow)
    elif kind == 'file':
        draw.rectangle([x + 3, y + 1, x + s - 4, y + s - 1], fill=(255, 255, 255), outline=blue, width=2)
    elif kind == 'save':
        draw.rounded_rectangle([x + 1, y + 1, x + s - 1, y + s - 1], 3, fill=blue)
        draw.rectangle([x + 6, y + 3, x + s - 6, y + 8], fill=(255, 255, 255))
    elif kind == 'layers':
        for dy, color in ((8, green), (3, yellow)):
            draw.polygon([(x + s / 2, y + dy), (x + s, y + dy + 6), (x + s / 2, y + dy + 12), (x, y + dy + 6)],
                         fill=color, outline=(255, 255, 255))
    elif kind == 'zoom':
        draw.ellipse([x + 1, y + 1, x + 15, y + 15], outline=gray, width=3)
        draw.line([x + 13, y + 13, x + s - 1, y + s - 1], fill=gray, width=4)
    elif kind == 'select':
        draw.rectangle([x + 2, y + 4, x + s - 2, y + s - 4], fill=(255, 236, 160), outline=yellow, width=2)
    elif kind == 'pencil':
        draw.line([x + 3, y + s - 3, x + s - 3, y + 3], fill=(236, 150, 40), width=5)
    elif kind == 'globe':
        draw.ellipse([x + 1, y + 1, x + s - 1, y + s - 1], fill=(120, 176, 236), outline=blue, width=2)
        draw.line([x + 1, y + s / 2, x + s - 1, y + s / 2], fill=(255, 255, 255), width=2)
    elif kind == 'chart':
        for i, (hgt, color) in enumerate(((10, blue), (16, green), (7, red))):
            draw.rectangle([x + 2 + i * 7, y + s - hgt, x + 7 + i * 7, y + s - 1], fill=color)
    elif kind == 'gear':
        draw.ellipse([x + 2, y + 2, x + s - 2, y + s - 2], outline=gray, width=4)
    else:  # 'box'
        draw.rounded_rectangle([x + 2, y + 2, x + s - 2, y + s - 2], 4, outline=blue, width=2)


def window_image():
    ww, wh = 1500, 780
    img = Image.new('RGB', (ww, wh), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    title = np.linspace([54, 136, 226], [100, 172, 241], ww, dtype=np.float32)
    img.paste(Image.fromarray(np.repeat(title[None], 50, axis=0).astype(np.uint8), 'RGB'), (0, 0))
    draw.ellipse([16, 12, 42, 38], outline=(150, 214, 92), width=5)
    draw.line([33, 30, 44, 41], fill=(250, 210, 60), width=5)
    draw.text((54, 9), 'QGIS', font=font('bold', 23), fill=(255, 255, 255))
    for i, glyph in enumerate(('min', 'max', 'close')):
        x = ww - 128 + i * 38
        if glyph == 'min':
            draw.line([x, 31, x + 16, 31], fill=(232, 242, 255), width=3)
        elif glyph == 'max':
            draw.rectangle([x, 17, x + 16, 33], outline=(232, 242, 255), width=3)
        else:
            draw.line([x, 17, x + 16, 33], fill=(232, 242, 255), width=3)
            draw.line([x, 33, x + 16, 17], fill=(232, 242, 255), width=3)

    chrome = (242, 245, 249)
    draw.rectangle([8, 50, ww - 8, 158], fill=chrome)
    x = 22
    for item in ('Project', 'Edit', 'View', 'Layer', 'Settings', 'Plugins', 'Vector', 'Raster', 'Database', 'Web',
                 'Mesh', 'Processing', 'Help'):
        draw.text((x, 58), item, font=font('regular', 16), fill=(104, 116, 134))
        x += draw.textlength(item, font=font('regular', 16)) + 30
    draw.line([8, 86, ww - 8, 86], fill=(226, 232, 240), width=2)
    kinds = ['folder', 'file', 'save', 'box', 'layers', 'zoom', 'select', 'pencil', 'globe', 'chart', 'gear']
    for row, y in enumerate((93, 128)):
        x = 20
        for i in range(30 if row == 0 else 24):
            toolbar_icon(draw, x, y, kinds[(i * 7 + row * 3 + i // 4) % len(kinds)])
            x += 38
            if i % 5 == 4:
                draw.line([x + 2, y, x + 2, y + 22], fill=(206, 214, 226), width=2)
                x += 14
            elif i % 7 == 3:
                draw.polygon([(x - 6, y + 11), (x + 2, y + 11), (x - 2, y + 16)], fill=(110, 124, 146))
                x += 8
            if x > ww - 70:
                break
    draw.line([8, 158, ww - 8, 158], fill=(226, 232, 240), width=2)
    draw.rectangle([8, 160, 56, 712], fill=chrome)
    for i in range(13):
        toolbar_icon(draw, 21, 176 + i * 40, ['zoom', 'select', 'box', 'pencil', 'layers', 'globe', 'gear'][i % 7])

    img.paste(map_texture(2000, 1104).resize((1000, 552), LANCZOS), (60, 160))
    draw.rectangle([59, 159, 1060, 712], outline=(214, 222, 232), width=2)

    draw.line([1064, 160, 1064, 712], fill=(222, 229, 238), width=2)
    label_font = font('medium', 30)
    for i, (color, label) in enumerate(LEGEND):
        y = 206 + i * 96
        draw.rounded_rectangle([1094, y, 1144, y + 50], 7, fill=color)
        draw.text((1166, y + 4), label, font=label_font, fill=(36, 50, 70))

    draw.rectangle([8, 714, ww - 8, wh - 8], fill=chrome)
    small = font('regular', 15)
    x = 24
    for label, box in (('Coordinate', '1004872,9273517'), ('Scale', '1:25000'), ('Magnifier', '100%'),
                       ('Rotation', '0,0 °'), ('Render', None), ('EPSG:4326', None)):
        draw.text((x, 731), label, font=small, fill=(84, 96, 116))
        x += draw.textlength(label, font=small) + 12
        if box:
            bw = draw.textlength(box, font=small) + 40
            draw.rounded_rectangle([x, 724, x + bw, 758], 6, fill=(255, 255, 255), outline=(208, 216, 228))
            draw.text((x + 10, 731), box, font=small, fill=(96, 108, 126))
            draw.polygon([(x + bw - 18, 738), (x + bw - 9, 738), (x + bw - 13.5, 744)], fill=(110, 124, 146))
            x += bw + 30
        else:
            x += 34

    radius = 22
    shape = aa_mask((ww, wh), lambda d, f: d.rounded_rectangle([0, 0, ww * f - 1, wh * f - 1], radius * f, fill=255))
    edge = aa_mask((ww, wh), lambda d, f: d.rounded_rectangle([0, 0, ww * f - 1, wh * f - 1], radius * f,
                                                               outline=255, width=3 * f))
    img.paste((205, 218, 235), mask=edge)
    out = img.convert('RGBA')
    out.putalpha(shape)
    return out


# ---------------------------------------------------------------------------------------------- composite
def main():
    canvas_size = (int(DESIGN_SIZE[0] * SCALE), int(DESIGN_SIZE[1] * SCALE))
    canvas = Image.new('RGBA', canvas_size, (255, 255, 255, 0))
    for kind, left, front, right in reversed(SLABS):
        for layer in slab_layers(kind, left, front, right, canvas_size):
            canvas = Image.alpha_composite(canvas, layer)

    window = warp(window_image(), [design(*p) for p in WINDOW_QUAD], canvas_size)
    alpha = window.getchannel('A')
    canvas = Image.alpha_composite(canvas, flat_layer(canvas_size, (28, 78, 156), shifted_alpha(alpha, 0, 30, 0.26, 24)))
    canvas = Image.alpha_composite(canvas, flat_layer(canvas_size, (28, 78, 156), shifted_alpha(alpha, 0, 6, 0.12, 6)))
    canvas = Image.alpha_composite(canvas, window)

    box = canvas.getchannel('A').point(lambda v: 255 if v > 6 else 0).getbbox()
    margin = 12
    box = (max(box[0] - margin, 0), max(box[1] - margin, 0),
           min(box[2] + margin, canvas_size[0]), min(box[3] + margin, canvas_size[1]))
    canvas = canvas.crop(box)
    size = (canvas.width // FINAL_DOWNSAMPLE, canvas.height // FINAL_DOWNSAMPLE)
    final = canvas.convert('RGBa').resize(size, LANCZOS).convert('RGBA')
    # 256 dithered colours look the same here and cut the file to about a sixth.
    final = final.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
    for path in OUTPUTS:
        final.save(path, optimize=True)
        print(f'{path.relative_to(ROOT)}  {final.width}x{final.height}  {path.stat().st_size // 1024} KB')


if __name__ == '__main__':
    main()

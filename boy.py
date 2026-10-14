# The boy, painted in code. Local units: ~400 tall, feet at y=0, faces right (3/4 view). flip=-1 faces left.
import numpy as np, math
from core import *
from rig import Rig

INK = '#4e3426'
SKIN = '#f6d6bd'; SKIN_LIT = '#fff0e2'; SKIN_SH = '#d39a86'
HAIR = '#f0be3c'; HAIR_LIT = '#ffe58a'; HAIR_SH = '#b9781d'
COAT = '#4f8a4c'; COAT_LIT = '#7fb46a'; COAT_SH = '#2c5236'
SCARF = '#f2b72e'; SCARF_LIT = '#ffe07a'; SCARF_SH = '#c27a17'
PANTS = '#5f9058'; BOOT = '#7a4b2e'; BOOT_LIT = '#a8714a'; BOOT_SH = '#4a2b1c'

RIG = Rig([
    ('pelvis', None, (0, -150)),
    ('chest', 'pelvis', (0, 0)),
    ('neck', 'chest', (6, -118)),
    ('head', 'neck', (0, -6)),
    ('armB', 'chest', (-20, -104)), ('foreB', 'armB', (0, 56)),
    ('armF', 'chest', (26, -104)), ('foreF', 'armF', (0, 56)),
    ('thighB', 'pelvis', (-14, 0)), ('shinB', 'thighB', (0, 72)),
    ('thighF', 'pelvis', (16, 0)), ('shinF', 'thighF', (0, 72)),
])

def limb(w0, w1, l, bulge=0.0):
    return catmull([(-w0, -4), (-w0 * (1 + bulge), l * 0.5), (-w1, l), (0, l + w1 * 0.6), (w1, l), (w0 * (1 + bulge), l * 0.5), (w0, -4), (0, -w0 * 0.7)])

def pose_walk(t, walk, ph=0.0):
    a = t * 7.0 + ph; sw = math.sin(a) * walk
    return {'thighF': -28 * sw, 'shinF': max(0, 35 * math.sin(a + 1.3)) * walk, 'thighB': 28 * sw, 'shinB': max(0, 35 * math.sin(a + 1.3 + math.pi)) * walk,
            'armF': 22 * sw, 'foreF': -18 * walk, 'armB': -22 * sw, 'foreB': -18 * walk}, abs(math.cos(a)) * -7 * walk

def draw_boy(frame, x, y, s=1.0, flip=1, t=0.0, pose=None, walk=0.0, blink=None, mouth='smile', talk=0.0, laugh=0.0,
             look=(0.0, 0.0), light=(-0.55, -0.7), rim='#ffd9a0', rim_w=0.5, wind=1.0, shadow=True, head_tilt=0.0, brows=0.0):
    pose = dict(pose or {})
    wp, bob = pose_walk(t, walk)
    for k, v in wp.items(): pose[k] = pose.get(k, 0) + v
    br = math.sin(t * 1.8) * 1.2
    pose['chest'] = pose.get('chest', 0) + br * 0.6 + laugh * math.sin(t * 13) * 2
    pose['head'] = pose.get('head', 0) + head_tilt + laugh * math.sin(t * 13 + 1) * 3
    bob += -laugh * abs(math.sin(t * 13)) * 5
    RIG.solve({k: v * flip if False else v for k, v in pose.items()}, (0, bob))
    pad = 60
    L = Layer(x - 230 * s - pad, y - 470 * s - pad, 460 * s + 2 * pad, 490 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def X(bone, pts):
        P = RIG.X(bone, pts); P[:, 0] *= flip; return P * s + [x, y]
    def part(bone, pts, base, lit, sh, **kw):
        P = X(bone, pts); m = L.mask(P, kw.pop('blur', 0.5))
        kw.setdefault('line', INK); kw.setdefault('line_w', 1.5 * s); kw.setdefault('line_a', 0.55)
        shade(L, m, base, lit=lit, shadow=sh, light=lt, rim=rim, rim_w=rim_w, poly=P, **kw)
        return P
    if shadow: ground_shadow(frame, x, y + 2, 85 * s, 14 * s, 0.45)
    # scarf tail behind everything, flowing in the wind
    nk = RIG.X('neck', [(0, 6)])[0]
    tail = []
    for i in range(9):
        u = i / 8
        tail.append(nk + [-20 - u * 150 * (0.6 + 0.4 * wind), u * 40 - u * u * 30 * wind + math.sin(t * 4 - u * 5) * 16 * u * wind])
    tail = np.array(tail)
    top = tail + [[0, -10 - 6 * (1 - i / 8)] for i in range(9)]; bot = tail + [[0, 12 + 4 * (1 - i / 8)] for i in range(9)]
    sc = catmull(np.concatenate([top, bot[::-1]]), n=6)
    P = sc.copy(); P[:, 0] *= flip; P = P * s + [x, y]
    shade(L, L.mask(P, 0.6), SCARF, lit=SCARF_LIT, shadow=SCARF_SH, light=lt, rim=rim, rim_w=rim_w, streak=0, tex_amt=0.08, line=INK, line_w=1.3 * s, line_a=0.5, poly=P)
    # back limbs
    part('thighB', limb(15, 13, 72), PANTS, '#7aa868', '#355a35', soft=0.9, streak=2)
    part('shinB', limb(13, 12, 64), PANTS, '#7aa868', '#355a35', soft=0.9, streak=2)
    part('shinB', catmull([(-15, 50), (14, 48), (30, 70), (30, 82), (-16, 82), (-17, 64)]), BOOT, BOOT_LIT, BOOT_SH, soft=0.9, spec=0.15)
    part('armB', limb(14, 12, 56, 0.1), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=2)
    part('foreB', limb(12, 11, 50), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=2)
    part('foreB', ellipse_pts(0, 58, 11, 12), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    # front leg
    part('thighF', limb(16, 14, 72), PANTS, '#86b674', '#3b6439', soft=0.9, streak=2)
    part('shinF', limb(14, 13, 64), PANTS, '#86b674', '#3b6439', soft=0.9, streak=2)
    part('shinF', catmull([(-16, 50), (15, 48), (32, 70), (32, 83), (-17, 83), (-18, 64)]), BOOT, BOOT_LIT, BOOT_SH, soft=0.9, spec=0.2)
    # coat: body with flared skirt, collar, buttons, belt
    coat = catmull([(-30, -112), (0, -122), (34, -112), (40, -60), (46, -6), (56, 34), (20, 42), (-14, 44), (-46, 34), (-40, -8), (-38, -60)])
    part('chest', coat, COAT, COAT_LIT, COAT_SH, soft=0.75, streak=1, tex_amt=0.08, ao=0.3)
    for yy in (-80, -50, -20):
        part('chest', ellipse_pts(16, yy, 4, 4), '#e2b64c', '#ffe08a', '#9c6d1f', line_a=0.4, line_w=1.0, spec=0.3)
    part('chest', catmull([(-38, -6), (44, -8), (45, 4), (-39, 6)]), '#6a4a2c', '#8f6a45', '#3e2a1a', line_a=0.4)
    # front arm
    part('armF', limb(15, 13, 56, 0.1), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=2)
    part('foreF', limb(13, 12, 50), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=2)
    part('foreF', catmull([(-11, 52), (10, 50), (13, 62), (6, 72), (-6, 72), (-12, 62)]), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    # scarf wrap around the neck
    part('neck', catmull([(-34, -8), (0, -16), (36, -8), (40, 12), (0, 20), (-36, 12)]), SCARF, SCARF_LIT, SCARF_SH, streak=0, tex_amt=0.08)
    # head
    hc = (8, -62)
    part('head', ellipse_pts(hc[0] - 34, hc[1] + 6, 12, 15), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)   # ear
    face = catmull([(hc[0] - 52, hc[1] - 30), (hc[0] - 10, hc[1] - 62), (hc[0] + 40, hc[1] - 50), (hc[0] + 62, hc[1] - 6), (hc[0] + 56, hc[1] + 36), (hc[0] + 22, hc[1] + 60), (hc[0] - 20, hc[1] + 56), (hc[0] - 50, hc[1] + 26)])
    part('head', face, SKIN, SKIN_LIT, SKIN_SH, soft=0.85, tex_amt=0.04, edge_dark=0.08)
    def HP(pts): return X('head', pts)
    for (cx, cy) in ((hc[0] + 40, hc[1] + 30), (hc[0] - 8, hc[1] + 30)):
        L.put(np.broadcast_to(hexc('#f2a091'), L.rgb.shape), L.mask(HP(ellipse_pts(cx, cy, 12, 7)), 5) * 0.55)
    # eyes
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    for (ex, ey, sc_) in ((hc[0] + 32, hc[1] + 4, 1.0), (hc[0] - 2, hc[1] + 4, 0.86)):
        ex += look[0] * 3; ey += look[1] * 3
        if bk > 0.15:
            P = HP(ellipse_pts(ex, ey, 8.5 * sc_, 12 * bk)); m = L.mask(P, 0.4)
            shade(L, m, '#3a2a22', lit='#6b4a32', shadow='#1e1410', light=(0.4, 0.8), tex_amt=0.02, edge_dark=0)
            L.put(np.broadcast_to(hexc('#7a5a33'), L.rgb.shape), L.mask(HP(ellipse_pts(ex, ey + 4 * bk, 6 * sc_, 5 * bk)), 2) * 0.7)
            for (dx, dy, rr) in ((-2.5, -5 * bk, 3.2), (3, 4 * bk, 1.5)):
                L.put(np.broadcast_to(np.array([1, .99, .95], np.float32), L.rgb.shape), L.mask(HP(ellipse_pts(ex + dx * sc_, ey + dy, rr * sc_, rr * sc_)), 0.5))
            pencil(L, HP([(ex - 10 * sc_, ey - 7 * bk), (ex - 3, ey - 13 * bk), (ex + 6 * sc_, ey - 12 * bk), (ex + 10 * sc_, ey - 6 * bk)]), '#3a2418', 2.3 * s, 0.85, lt, closed=False)
        else:
            lid = [(ex - 9, ey - 1), (ex - 3, ey - 6), (ex + 3, ey - 6), (ex + 9, ey - 1)] if laugh > 0.5 else [(ex - 9, ey), (ex - 3, ey + 4), (ex + 3, ey + 4), (ex + 9, ey)]
            pencil(L, HP(lid), '#3a2418', 2.4 * s, 0.9, lt, closed=False)
        pencil(L, HP([(ex - 9, ey - 22 - brows * 4), (ex, ey - 25 - brows * 5), (ex + 9, ey - 22 - brows * 3)]), '#b5832f', 2.4 * s, 0.7, lt, closed=False)
    pencil(L, HP([(hc[0] + 50, hc[1] + 14), (hc[0] + 54, hc[1] + 21), (hc[0] + 49, hc[1] + 23)]), '#b7806a', 1.6 * s, 0.7, lt, closed=False)
    mo = talk * abs(math.sin(t * 11)) + laugh * (0.7 + 0.3 * abs(math.sin(t * 13)))
    mx, my = hc[0] + 32, hc[1] + 38
    if mo > 0.15 or mouth == 'open':
        o = max(mo, 0.5 if mouth == 'open' else 0)
        P = HP(catmull([(mx - 10, my - 2), (mx + 10, my - 3), (mx + 7, my + 4 + 8 * o), (mx - 6, my + 4 + 8 * o)]))
        shade(L, L.mask(P), '#8d3b36', lit='#b8554c', light=lt, tex_amt=0.02, edge_dark=0.2, line=INK, line_w=1.3, line_a=0.6, poly=P)
        L.put(np.broadcast_to(hexc('#e0817a'), L.rgb.shape), L.mask(HP(ellipse_pts(mx, my + 2 + 6 * o, 5, 2.5 * o + 1)), 1) * 0.8)
    elif mouth == 'sad':
        pencil(L, HP([(mx - 8, my + 4), (mx, my), (mx + 8, my + 4)]), '#8a4c3e', 1.8 * s, 0.85, lt, closed=False)
    else:
        pencil(L, HP([(mx - 9, my - 1), (mx, my + 5), (mx + 9, my - 1)]), '#8a4c3e', 1.8 * s, 0.85, lt, closed=False)
    # hair: golden spiky clumps, tips moving in the wind
    r = np.random.default_rng(11)
    clumps = []
    for k in range(17):
        a = math.radians(-200 + k * 13 + r.random() * 6)
        base = np.array([hc[0] + 4 + math.cos(a) * 44, hc[1] - 6 + math.sin(a) * 50])
        ln = 40 + r.random() * 26 + (14 if 3 < k < 12 else 0)
        dirv = np.array([math.cos(a), math.sin(a)]) * 0.75 + np.array([-0.35, -0.5])
        dirv /= np.linalg.norm(dirv)
        sway = math.sin(t * 3.1 + k * 0.7) * 6 * wind + 8 * wind
        tip = base + dirv * ln + [-sway, math.cos(t * 2.7 + k) * 2]
        side = np.array([-dirv[1], dirv[0]]) * (14 + r.random() * 6)
        mid = base + dirv * ln * 0.55 + side * 0.15
        clumps.append((k, catmull([base - side, mid - side * 0.7, tip, mid + side * 0.6, base + side], n=7)))
    cap = catmull([(hc[0] - 56, hc[1] - 8), (hc[0] - 40, hc[1] - 52), (hc[0] + 6, hc[1] - 70), (hc[0] + 50, hc[1] - 54), (hc[0] + 64, hc[1] - 22), (hc[0] + 40, hc[1] - 30), (hc[0] + 10, hc[1] - 38), (hc[0] - 20, hc[1] - 26), (hc[0] - 40, hc[1] + 4)])
    order = sorted(clumps, key=lambda c: -abs(c[0] - 8))
    for k, poly in order[:9]:
        part('head', poly, '#d99d2a', HAIR_LIT, HAIR_SH, soft=0.7, streak=1, tex_amt=0.07, line_a=0.4, line_w=1.2 * s, edge_dark=0.15)
    part('head', cap, HAIR, HAIR_LIT, HAIR_SH, soft=0.75, streak=1, tex_amt=0.07, line_a=0.4, spec=0.12)
    for k, poly in order[9:]:
        part('head', poly, HAIR, HAIR_LIT, HAIR_SH, soft=0.7, streak=1, tex_amt=0.07, line_a=0.4, line_w=1.2 * s, edge_dark=0.15, spec=0.1)
    # fringe strands over the forehead
    for k in range(5):
        b = np.array([hc[0] + 2 + k * 11, hc[1] - 44 + k * 2]); tp = b + [10 + k * 3 - math.sin(t * 3 + k) * 3 * wind, 26 + (k % 2) * 8]
        P = catmull([b + [-9, 0], b + [9, -2], tp, ], n=6)
        part('head', P, HAIR, HAIR_LIT, HAIR_SH, soft=0.8, streak=1, tex_amt=0.06, line_a=0.35, line_w=1.0 * s)
    composite(frame, L)
    return L

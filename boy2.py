# The boy (3/4 front view), painted in code in the storybook gouache style. Units: ~400 tall, feet at y=0.
import numpy as np, math
from core import *
from rig import Rig

INK = '#5a3a26'
SKIN, SKIN_LIT, SKIN_SH = '#f7d7bf', '#fff1e4', '#d9a28a'
HAIR, HAIR_LIT, HAIR_SH = '#f0c443', '#fff09a', '#c08a22'
COAT, COAT_LIT, COAT_SH = '#5d8a45', '#8db86a', '#33552b'
TUNIC, TUNIC_LIT, TUNIC_SH = '#4f7a3b', '#7aa65a', '#2c4a24'
GOLD = '#e0b046'
SCARF, SCARF_LIT, SCARF_SH = '#f2c13e', '#ffe48a', '#c48a1d'
BOOT, BOOT_LIT, BOOT_SH = '#9a6a3f', '#c99766', '#5e3a20'

LAST = {}   # screen points from the last drawn boy (hands, head) for strings and effects
RIG = Rig([
    ('pelvis', None, (0, -150)),
    ('chest', 'pelvis', (0, 0)),
    ('head', 'chest', (2, -126)),
    ('armL', 'chest', (-42, -98)), ('foreL', 'armL', (0, 60)),
    ('armR', 'chest', (44, -98)), ('foreR', 'armR', (0, 60)),
    ('legL', 'pelvis', (-20, 0)), ('shinL', 'legL', (0, 68)),
    ('legR', 'pelvis', (20, 0)), ('shinR', 'legR', (0, 68)),
    ('bootL', 'shinL', (0, 64)), ('bootR', 'shinR', (0, 64)),
])

def walk_pose(t, walk):
    a = t * 6.5; sw = math.sin(a) * walk
    return ({'legL': 16 * sw, 'shinL': max(0, -22 * math.sin(a + 1.2)) * walk, 'legR': -16 * sw, 'shinR': max(0, 22 * math.sin(a + 1.2)) * walk,
             'armL': -14 * sw, 'armR': 14 * sw, 'chest': -2 * sw * 0.5}, -abs(math.cos(a)) * 6 * walk)

def draw_boy(frame, x, y, s=1.0, flip=1, t=0.0, pose=None, walk=0.0, blink=None, mouth='smile', talk=0.0, laugh=0.0,
             look=(0.0, 0.0), light=(-0.55, -0.7), rim='#ffd9a0', rim_w=0.45, wind=1.0, shadow=True, brows=0.0, turn=0.18, A=None, prop=None, prop_back=None):
    hb = np.zeros(2); scf = np.zeros(2); mo_override = None
    if A is not None:   # a full performance from boy_anim: angles, root, face
        P0 = dict(A['ang']); root = A['root']; look = A['look']; blink = A['blink']; laugh = A['laugh']; talk = A['talk']
        mouth = A.get('mouth', mouth); wind = A['wind']; hb = A['hair']; scf = A['scarf']; brows = A.get('brows', 0.0); mo_override = A.get('mo')
    else:
        P0 = dict(pose or {})
        wp, bob = walk_pose(t, walk)
        for k, v in wp.items(): P0[k] = P0.get(k, 0) + v
        P0['chest'] = P0.get('chest', 0) + math.sin(t * 1.8) * 0.5 + laugh * math.sin(t * 13) * 1.5
        P0['head'] = P0.get('head', 0) + laugh * math.sin(t * 13 + 1) * 3 + math.sin(t * 0.9) * 1.2
        P0.setdefault('armL', 0); P0.setdefault('armR', 0)
        P0['armL'] += 8; P0['armR'] -= 8
        bob += -laugh * abs(math.sin(t * 13)) * 4 + math.sin(t * 1.8) * 0.8
        root = (0, bob)
        for sd in 'LR': P0['boot' + sd] = -(P0.get('leg' + sd, 0) + P0.get('shin' + sd, 0))
    RIG.solve(P0, root)
    pad = 70
    L = Layer(x - 230 * s - pad, y - 450 * s - pad, 460 * s + 2 * pad, 470 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    pel = RIG.X('pelvis', [(0, 0)])[0]
    koff = {sd: RIG.X('shin' + sd, [(0, 0)])[0] - pel - [(-20 if sd == 'L' else 20), 68] for sd in 'LR'}
    def coat_deform(pts):
        # the coat skirt is pushed by the knees: the hem swings and lifts with each step
        P = np.asarray(pts, np.float32).reshape(-1, 2).copy()
        w = np.clip(P[:, 1] / 96, 0, 1) ** 1.3; sl = np.clip(0.5 - P[:, 0] / 80, 0, 1); sr = 1 - sl
        P[:, 0] += w * (sl * koff['L'][0] + sr * koff['R'][0]) * 0.9
        P[:, 1] += w * (sl * koff['L'][1] + sr * koff['R'][1]) * 0.6
        return P
    def X(bone, pts):
        if bone == 'chest': pts = coat_deform(pts)
        P = RIG.X(bone, pts); P[:, 0] *= flip; return P * s + [x, y]
    def part(bone, pts, base, lit, sh, **kw):
        P = X(bone, pts); m = L.mask(P, kw.pop('blur', 0.5))
        kw.setdefault('line', INK); kw.setdefault('line_w', 1.6 * s); kw.setdefault('line_a', 0.7)
        kw.setdefault('rim', rim); kw.setdefault('rim_w', rim_w); kw.setdefault('streak_amt', 0.14)
        shade(L, m, base, lit=lit, shadow=sh, light=lt, poly=P, **kw)
        return P
    def fill(P, color, a=1.0, blur=1.0):
        L.put(hexc(color), L.mask(P, blur) * a)
    if shadow: ground_shadow(frame, x, y + 3, 80 * s, 13 * s, 0.5)
    tx = turn * 30
    # ---- scarf tail (behind), hanging from the left shoulder and fluttering
    nk = RIG.X('chest', [(-24, -112)])[0]
    pts = []
    for i in range(10):
        u = i / 9
        pts.append(nk + [-10 - u * (20 + 100 * wind) + math.sin(t * 3.4 - u * 4) * 10 * u * wind + scf[0] * u * u, u * (150 - 70 * wind) + math.sin(t * 4.1 - u * 5) * 14 * u * wind + scf[1] * u * u])
    pts = np.array(pts)
    d = np.gradient(pts, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6
    wdt = np.linspace(18, 22, 10)[:, None]
    sc = catmull(np.concatenate([pts + nrm * wdt, (pts - nrm * wdt)[::-1]]), n=6)
    Psc = sc.copy(); Psc[:, 0] *= flip; Psc = Psc * s + [x, y]
    shade(L, L.mask(Psc, 0.6), SCARF, lit=SCARF_LIT, shadow=SCARF_SH, light=lt, rim=rim, rim_w=rim_w, streak=2, tex_amt=0.12, line=INK, line_w=1.4 * s, line_a=0.6, poly=Psc)
    end = pts[-1]; en = nrm[-1]
    for k in range(9):   # fringe
        b = end + en * (-20 + k * 5); tp = b + (pts[-1] - pts[-2]) / (np.linalg.norm(pts[-1] - pts[-2]) + 1e-6) * (14 + (k % 3) * 3)
        q = np.array([b, tp]); q[:, 0] *= flip; stroke(L, q * s + [x, y], '#d79a28', 2.6 * s, 0.9, taper=False)
    # ---- back arm (screen left)
    part('armL', catmull([(-15, -6), (16, -8), (20, 34), (16, 62), (-14, 64), (-19, 30)]), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=1, tex_amt=0.08)
    part('foreL', catmull([(-15, -4), (15, -4), (17, 40), (19, 56), (-17, 58), (-16, 30)]), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=1, tex_amt=0.08)
    part('foreL', catmull([(-18, 44), (19, 42), (20, 56), (-19, 58)]), GOLD, '#ffe08a', '#a07422', soft=0.9, line_a=0.5)
    part('foreL', catmull([(-11, 56), (10, 56), (13, 70), (8, 82), (-6, 84), (-13, 72)]), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    # ---- legs: wide trousers and boots
    for side in ('L', 'R'):
        sg = -1 if side == 'L' else 1
        part('leg' + side, catmull([(-20, -6), (20, -6), (22, 40), (19, 72), (-19, 72), (-22, 40)]), TUNIC, TUNIC_LIT, TUNIC_SH, soft=0.85, streak=2, tex_amt=0.08)
        part('shin' + side, catmull([(-19, -2), (19, -2), (21, 40), (20, 62), (-20, 62), (-21, 40)]), TUNIC, TUNIC_LIT, TUNIC_SH, soft=0.85, streak=2, tex_amt=0.08)
        part('boot' + side, catmull([(-18, -20), (18, -20), (20, -2), (28, 10), (24, 20), (-22, 20), (-21, 2)]), BOOT, BOOT_LIT, BOOT_SH, soft=0.85, spec=0.15, tex_amt=0.09)
        part('shin' + side, catmull([(-20, 54), (20, 54), (21, 60), (-21, 60)]), '#7d5230', '#a8774a', '#4f3018', line_a=0.4)
    # ---- coat: back panel, inner tunic, lapels, belt, buttons, pockets
    coat = catmull([(-46, -110), (-20, -124), (22, -124), (48, -110), (58, -60), (66, 10), (78, 92), (40, 100), (0, 96), (-40, 100), (-78, 92), (-64, 10), (-56, -60)])
    part('chest', coat, COAT, COAT_LIT, COAT_SH, soft=0.7, streak=1, tex_amt=0.1, ao=0.25)
    tunic = catmull([(-20, -118), (22, -118), (26, -40), (24, 40), (2, 46), (-22, 40), (-24, -40)])
    part('chest', tunic, TUNIC, TUNIC_LIT, TUNIC_SH, soft=0.8, streak=1, tex_amt=0.08, line_a=0.5)
    for side in (-1, 1):
        lap = [(side * 22, -116), (side * 40, -100), (side * 30, -50), (side * 30, 40), (side * 46, 96), (side * 36, 98), (side * 20, 40), (side * 18, -52)]
        part('chest', catmull(lap), COAT, COAT_LIT, COAT_SH, soft=0.85, streak=1, tex_amt=0.1, line_a=0.6)
        trim = X('chest', catmull([(side * 22, -116), (side * 19, -52), (side * 21, 40), (side * 37, 98)], closed=False, n=8))
        pencil(L, trim, GOLD, 3.2 * s, 0.85, lt, closed=False)
        pk = [(side * 40, 30), (side * 62, 28), (side * 64, 52), (side * 42, 54)]
        pencil(L, X('chest', catmull(pk, closed=False, n=5)), '#3d5f2c', 1.6 * s, 0.6, lt, closed=False)
        for yy in (-90, -70, -50):
            part('chest', ellipse_pts(side * 34, yy, 3.6, 3.6), GOLD, '#fff0a0', '#9c6d1f', line_a=0.5, line_w=1.0, spec=0.35, rim_w=0)
    part('chest', catmull([(-26, -24), (26, -24), (27, -12), (-27, -12)]), '#8a5a32', '#b07a4a', '#56351c', line_a=0.6)
    part('chest', catmull([(-7, -27), (7, -27), (8, -9), (-8, -9)]), GOLD, '#fff0a0', '#9c6d1f', line_a=0.7, spec=0.4, rim_w=0)
    fill(X('chest', catmull([(-4, -23), (4, -23), (4, -13), (-4, -13)])), '#8a5a32', 0.9, 0.5)
    def hand(side):
        P = X('fore' + side, [(0, 70)])[0]
        ang = sum(P0.get(j, 0) for j in ('pelvis', 'chest', 'arm' + side, 'fore' + side)) * flip
        return P, ang
    if prop_back is not None: prop_back(L, *hand('L'), s, lt, flip)
    # ---- front arm (screen right)
    part('armR', catmull([(-16, -8), (15, -6), (19, 30), (15, 62), (-15, 64), (-20, 34)]), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=1, tex_amt=0.08)
    part('foreR', catmull([(-15, -4), (15, -4), (16, 30), (17, 58), (-19, 56), (-17, 40)]), COAT, COAT_LIT, COAT_SH, soft=0.9, streak=1, tex_amt=0.08)
    part('foreR', catmull([(-19, 42), (18, 44), (19, 58), (-20, 56)]), GOLD, '#ffe08a', '#a07422', soft=0.9, line_a=0.5)
    part('foreR', catmull([(-12, 56), (11, 56), (14, 70), (7, 84), (-7, 82), (-13, 70)]), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    if prop is not None: prop(L, *hand('R'), s, lt, flip)
    LAST['handR'] = hand('R')[0]; LAST['handL'] = hand('L')[0]; LAST['head'] = X('head', [(0, -60)])[0]
    # ---- scarf wrap
    part('chest', catmull([(-50, -122), (-20, -142), (24, -144), (54, -124), (50, -100), (20, -94), (-20, -94), (-50, -102)]), SCARF, SCARF_LIT, SCARF_SH, streak=2, tex_amt=0.12, soft=0.7)
    part('chest', catmull([(-34, -112), (-12, -116), (-6, -96), (-22, -88), (-36, -98)]), SCARF, SCARF_LIT, SCARF_SH, streak=2, tex_amt=0.12, soft=0.8, line_a=0.45)
    for k in range(7):
        q = X('chest', [(-44 + k * 15, -136 + abs(k - 3) * 2), (-40 + k * 15, -102)]); stroke(L, q, '#d39a2a', 1.4 * s, 0.4, taper=False)
    # ---- head
    hc = np.array([tx * 0.3, -54]); HS = 1.2
    def H(pts): return X('head', np.asarray(pts, np.float32) * HS + hc * HS)
    for side in (-1, 1):   # ears
        ex = side * 47 + tx * 0.5
        P = H(catmull([(ex - 6, -10), (ex + side * 10, -14), (ex + side * 13, 6), (ex + side * 4, 16), (ex - side * 3, 8)]))
        shade(L, L.mask(P), SKIN, lit=SKIN_LIT, shadow=SKIN_SH, light=lt, rim=rim, rim_w=rim_w, poly=P, line=INK, line_w=1.4 * s, line_a=0.6)
        fill(H(ellipse_pts(ex + side * 5, 2, 4, 7)), '#e8a593', 0.6, 2)
    face = [(-46, -30), (-32, -52), (0, -58), (34, -52), (50, -28), (51, 4), (44, 28), (26, 44), (2, 49), (-22, 44), (-40, 28), (-48, 4)]
    face = [(px + tx * (0.3 if px > 0 else -0.1), py) for px, py in face]
    P = H(catmull(face)); shade(L, L.mask(P, 0.5), SKIN, lit=SKIN_LIT, shadow=SKIN_SH, light=lt, rim=rim, rim_w=rim_w, soft=0.9, tex_amt=0.04, edge_dark=0.06, poly=P, line=INK, line_w=1.6 * s, line_a=0.65)
    for cx in (-22 + tx, 24 + tx):
        fill(H(ellipse_pts(cx, 16, 12, 8)), '#f19c8c', 0.55, 5)
        for k in range(3): fill(H(ellipse_pts(cx - 5 + k * 5, 12 + (k % 2) * 3, 0.9, 0.9)), '#c47a62', 0.5, 0.3)
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    for ex, sc_ in ((-17 + tx, 0.92), (19 + tx, 1.0)):
        ex += look[0] * 3; ey = -6 + look[1] * 3
        if bk > 0.15:
            fill(H(ellipse_pts(ex, ey, 10 * sc_, 12 * bk + 1)), '#fffaf2', 0.9, 0.6)
            E = H(ellipse_pts(ex + 0.5, ey + 1, 8.8 * sc_, 11 * bk)); m = L.mask(E, 0.4)
            shade(L, m, '#4a301f', lit='#8a5a30', shadow='#24150d', light=(0.3, 0.9), tex_amt=0.02, edge_dark=0, weave=0)
            fill(H(ellipse_pts(ex, ey + 1, 4.2 * sc_, 5 * bk)), '#160d08', 0.9, 0.6)
            for dx, dy, rr in ((-3, -4.5 * bk, 3.0), (3.2, 4 * bk, 1.4)):
                fill(H(ellipse_pts(ex + dx * sc_, ey + dy, rr * sc_, rr * sc_)), '#fffdf6', 1.0, 0.4)
            pencil(L, H(catmull([(ex - 11 * sc_, ey - 2 * bk), (ex - 6, ey - 10.5 * bk), (ex + 5, ey - 11 * bk), (ex + 11 * sc_, ey - 3 * bk)], closed=False, n=5)), '#2e1a10', 1.8 * s, 0.85, lt, closed=False)
        else:
            lid = [(ex - 9, ey + 1), (ex - 3, ey - 5), (ex + 3, ey - 5), (ex + 9, ey + 1)] if laugh > 0.5 else [(ex - 9, ey), (ex - 3, ey + 4), (ex + 3, ey + 4), (ex + 9, ey)]
            pencil(L, H(lid), '#2e1a10', 2.4 * s, 0.9, lt, closed=False)
        pencil(L, H(catmull([(ex - 9, ey - 21 - brows * 4), (ex - 1, ey - 26 - brows * 5), (ex + 8, ey - 25 - brows * 3)], closed=False, n=5)), '#c99442', 2.0 * s, 0.6, lt, closed=False)
    pencil(L, H([(3 + tx * 1.2, 8), (6 + tx * 1.2, 14), (2 + tx * 1.2, 16)]), '#c48a72', 1.6 * s, 0.75, lt, closed=False)
    mo = talk * abs(math.sin(t * 11)) + laugh * (0.7 + 0.3 * abs(math.sin(t * 13))) if mo_override is None else mo_override
    mx, my = 2 + tx * 1.1, 29
    if mo > 0.15 or mouth == 'open':
        o = max(mo, 0.6 if mouth == 'open' else 0)
        M = H(catmull([(mx - 11, my - 2), (mx + 11, my - 2), (mx + 7, my + 4 + 8 * o), (mx - 7, my + 4 + 8 * o)]))
        shade(L, L.mask(M), '#93403a', lit='#b85a50', light=lt, tex_amt=0.02, edge_dark=0.2, line=INK, line_w=1.3 * s, line_a=0.7, poly=M, weave=0)
        fill(H(ellipse_pts(mx, my + 3 + 6 * o, 5, 2 * o + 1)), '#e8857c', 0.8, 1)
    elif mouth == 'sad':
        pencil(L, H([(mx - 8, my + 4), (mx, my + 1), (mx + 8, my + 4)]), '#93503e', 1.9 * s, 0.9, lt, closed=False)
    else:
        pencil(L, H([(mx - 11, my - 2), (mx - 4, my + 4), (mx + 4, my + 4), (mx + 11, my - 2)]), '#93503e', 2.0 * s, 0.9, lt, closed=False)
    # ---- hair: a fluffy mass of soft curls, tousled locks at the edge, a few bright strands
    r = np.random.default_rng(21)
    lk = HS * s
    def hp(px, py): return H([(px, py)])[0]
    def hpart(poly, *a, **k): return part('head', np.asarray(poly, np.float32) * HS + hc * HS, *a, **k)
    locks = []
    for k in range(15):   # edge locks, petal shapes pointing outward, swaying
        a = math.radians(165 + k * (210 / 14)); rr = 1.0 + 0.08 * math.sin(k * 3.1)
        b = np.array([tx * 0.4 + math.cos(a) * 50, -14 + math.sin(a) * 48])
        d = np.array([math.cos(a), math.sin(a)]); n_ = np.array([-d[1], d[0]])
        ln = 9 + (k % 3) * 3
        sw = (math.sin(t * 2.6 + k * 0.8) * 4 + 5) * wind
        tip = b + d * ln + [-sw, 0] + n_ * (6 if k % 2 else -6) + hb * 1.3
        locks.append(catmull([b - n_ * 14, b + d * ln * 0.7 - n_ * 12, tip - n_ * 5, tip + d * 4 + n_ * 3, b + d * ln * 0.6 + n_ * 11, b + n_ * 14], n=6))
    for poly in locks:
        hpart(poly, HAIR, HAIR_LIT, HAIR_SH, soft=0.75, streak=1, tex_amt=0.08, line_a=0.45, line_w=1.2 * s, edge_dark=0.12, rim_w=rim_w * 0.8)
    pts = []
    for k in range(70):
        a = math.radians(170 + r.random() * 200); d = math.sqrt(r.random())
        px, py = tx * 0.4 + math.cos(a) * 54 * d, -16 + math.sin(a) * 50 * d
        if py > -36 and abs(px - tx * 0.4) < 38: py = -36 - r.random() * 10
        pts.append((py, px, py, 13 + r.random() * 7))
    pts.sort(key=lambda p: -p[0])
    for _, px, py, rr in pts:
        c = hp(px + math.sin(t * 2.2 + px) * 0.8 * wind + hb[0] * (-py / 60), py + hb[1] * (-py / 60))
        puff(L, c[0], c[1], rr * lk, HAIR, HAIR_LIT, HAIR_SH, lt, soft=0.5, ao=0.35, rim=rim, rim_w=rim_w * 0.8, gx=int(px * 5), gy=int(py * 5))
    for k in range(5):   # a swept fringe
        side = (k - 2) / 2
        b = np.array([tx * 0.4 + side * 30 - 4, -40 + abs(side) * 3])
        sw = math.sin(t * 2.8 + k) * 2 * wind
        P = catmull([b + [-16, -8], b + [14, -10], b + [16 + sw, 4], b + [6 + sw + 6, 14 + (k % 2) * 5], b + [-6, 6]], n=6)
        hpart(P, HAIR, HAIR_LIT, HAIR_SH, soft=0.8, streak=1, tex_amt=0.08, edge_dark=0.12, line_a=0.4, line_w=1.0 * s, rim_w=rim_w * 0.5)
    for k in range(22):   # fine strands for sparkle
        a = math.radians(185 + r.random() * 170); d0 = 0.35 + r.random() * 0.3
        b = np.array([tx * 0.4 + math.cos(a) * 54 * d0, -16 + math.sin(a) * 50 * d0])
        tp = np.array([tx * 0.4 + math.cos(a + 0.25) * 56, -16 + math.sin(a + 0.25) * 52])
        stroke(L, H(catmull([b, (b + tp) / 2 + [2, -3], tp], closed=False, n=5)), HAIR_LIT, 1.4 * s, 0.6)
    composite(frame, L)
    return L

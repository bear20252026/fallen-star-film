# The Clockmaker: a tiny, hurried old man with round spectacles, a white beard and a big winding key. 3/4 view, painted.
# Units: about 300 tall, feet at y=0.
import numpy as np, math
from core import *
from rig import Rig

INK = '#3a2818'
SKIN, SKIN_LIT, SKIN_SH = '#f2c9a8', '#ffe6d2', '#c88e70'
COAT, COAT_LIT, COAT_SH = '#3f5f8e', '#7a9ac8', '#22344e'
VEST, VEST_LIT, VEST_SH = '#8a2f2a', '#c45a4a', '#4a1814'
TROU, TROU_LIT, TROU_SH = '#4a4038', '#7a6a5a', '#241e18'
BEARD, BEARD_LIT, BEARD_SH = '#eeeae4', '#ffffff', '#b4aca4'
GOLD = '#e0b046'

RIG = Rig([
    ('pelvis', None, (0, -100)),
    ('chest', 'pelvis', (0, 0)),
    ('head', 'chest', (6, -104)),
    ('armL', 'chest', (-30, -92)), ('foreL', 'armL', (0, 44)),
    ('armR', 'chest', (32, -92)), ('foreR', 'armR', (0, 44)),
    ('legL', 'pelvis', (-14, 0)), ('shinL', 'legL', (0, 48)),
    ('legR', 'pelvis', (14, 0)), ('shinR', 'legR', (0, 48)),
])

def draw_clockmaker(frame, x, y, s=1.0, flip=1, t=0.0, u=0.0, walk=0.0, crank=None, up=0.0, laugh=0.0, talk=0.0, frozen=0.0,
                    blink=None, light=(-0.5, -0.7), rim='#ffd9a0', rim_w=0.5, look=(0.0, 0.0), key=True, hold=0.0, smile=0.4, shadow=True):
    """u: gait phase (cycles); walk 0..1. crank: angle (rad) of the key-winding hand, or None.
    frozen: horror (eyes wide, mouth O). hold: right arm out offering something (0..1)."""
    a = 2 * math.pi * u
    sw = math.sin(a) * walk
    ch = laugh * abs(math.sin(t * 2 * math.pi * 3.4))
    ang = {'pelvis': 4 * walk, 'chest': 6 * walk - 6 * laugh - 2 * ch + 2 * math.sin(t * 2.0) * (1 - walk) - 4 * up,
           'head': -16 * up - 8 * laugh - 4 * ch + 4 * frozen,
           'legL': 26 * sw, 'shinL': max(0, -34 * math.sin(a + 1.3)) * walk, 'legR': -26 * sw, 'shinR': max(0, 34 * math.sin(a + 1.3)) * walk,
           'armL': -22 * sw + 10 - 40 * laugh - 60 * frozen, 'foreL': -20 - 30 * laugh - 40 * frozen,
           'armR': 22 * sw - 10 + 40 * laugh + 60 * frozen, 'foreR': -30 + 30 * laugh + 40 * frozen}
    if crank is not None:   # winding: the forearm turns the key in circles
        ang['armR'] = -70 + 10 * math.sin(crank); ang['foreR'] = -40 + 25 * math.cos(crank)
    if hold > 0:
        ang['armR'] += (-75 - ang['armR']) * hold; ang['foreR'] += (-15 - ang['foreR']) * hold
    bob = -abs(math.cos(a)) * 7 * walk - ch * 3
    RIG.solve(ang, (0, bob))
    pad = 50; L = Layer(x - 170 * s - pad, y - 340 * s - pad, 340 * s + 2 * pad, 350 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def X(bone, pts): P = RIG.X(bone, pts); P[:, 0] *= flip; return P * s + [x, y]
    def part(bone, pts, base, lit, sh, **kw):
        P = X(bone, pts); kw.setdefault('line', INK); kw.setdefault('line_w', 1.4 * s); kw.setdefault('line_a', 0.7)
        kw.setdefault('rim', rim); kw.setdefault('rim_w', rim_w)
        shade(L, L.mask(P, kw.pop('blur', 0.5)), base, lit=lit, shadow=sh, light=lt, poly=P, **kw); return P
    def fill(P, c, a_=1.0, b=1.0): L.put(hexc(c), L.mask(P, b) * a_)
    if shadow: ground_shadow(frame, x, y + 2, 60 * s, 10 * s, 0.45)
    # back arm
    part('armL', catmull([(-11, -4), (11, -4), (12, 26), (10, 46), (-10, 46), (-12, 24)]), COAT, COAT_LIT, COAT_SH, soft=0.85, streak=1, tex_amt=0.1)
    part('foreL', catmull([(-10, -2), (10, -2), (11, 30), (-11, 30)]), COAT, COAT_LIT, COAT_SH, soft=0.85, streak=1)
    part('foreL', catmull([(-8, 28), (8, 28), (10, 40), (0, 48), (-9, 40)]), SKIN, SKIN_LIT, SKIN_SH)
    # legs and big shoes
    for sd in 'LR':
        part('leg' + sd, catmull([(-12, -4), (12, -4), (13, 30), (10, 50), (-10, 50), (-13, 30)]), TROU, TROU_LIT, TROU_SH, soft=0.85, streak=2)
        part('shin' + sd, catmull([(-10, -2), (10, -2), (11, 26), (10, 42), (-10, 42), (-11, 24)]), TROU, TROU_LIT, TROU_SH, soft=0.85, streak=2)
        part('shin' + sd, catmull([(-12, 38), (12, 36), (30, 42), (32, 52), (-12, 52)]), '#2e2018', '#5a4434', '#140c08', spec=0.35)
    # long coat with tails
    coat = catmull([(-30, -100), (-14, -110), (18, -110), (34, -100), (38, -50), (44, 10), (50, 38), (20, 40), (0, 30), (-24, 40), (-48, 36), (-40, 8), (-36, -50)])
    part('chest', coat, COAT, COAT_LIT, COAT_SH, soft=0.75, streak=1, tex_amt=0.12, ao=0.15)
    part('chest', catmull([(-14, -104), (16, -104), (18, -40), (12, 0), (-10, 0), (-16, -40)]), VEST, VEST_LIT, VEST_SH, soft=0.8, tex_amt=0.1, line_a=0.5)
    for yy in (-80, -60, -40, -20):
        part('chest', ellipse_pts(2, yy, 2.6, 2.6), GOLD, '#fff0a0', '#9c6d1f', spec=0.5, line_a=0.3, line_w=0.6 * s, rim_w=0)
    stroke(L, X('chest', catmull([(2, -60), (14, -48), (22, -56)], closed=False, n=5)), GOLD, 1.6 * s, 0.9, taper=False)   # watch chain
    # head: big, bald on top, white tufts, spectacles, beard
    hc = (6, -40); HS = 1.0
    def H(pts): return X('head', np.asarray(pts, np.float32) + hc)
    for sx in (-1, 1):   # white hair tufts at the sides
        for k in range(4):
            P = H(ellipse_pts(sx * (40 + k * 2) - (4 if sx < 0 else 0), -10 + k * 9, 12 - k, 9))
            shade(L, L.mask(P, 0.6), BEARD, lit=BEARD_LIT, shadow=BEARD_SH, light=lt, soft=0.9, tex_amt=0.1, poly=P, rim=rim, rim_w=rim_w)
    P = H(catmull([(-40, -10), (-30, -44), (0, -56), (32, -44), (44, -8), (42, 20), (24, 40), (0, 44), (-24, 40), (-40, 20)]))
    shade(L, L.mask(P, 0.5), SKIN, lit=SKIN_LIT, shadow=SKIN_SH, light=lt, rim=rim, rim_w=rim_w, soft=0.9, tex_amt=0.05, spec=0.25, poly=P, line=INK, line_w=1.4 * s, line_a=0.6)
    fill(H(ellipse_pts(-6, -40, 14, 6, -0.2)), '#ffffff', 0.35, 4)   # shine on the bald head
    # beard and moustache
    bd = catmull([(-34, 8), (-20, 20), (0, 22), (24, 18), (38, 6), (36, 34), (20, 60), (2, 68), (-16, 60), (-32, 36)])
    P = H(bd); shade(L, L.mask(P, 0.6), BEARD, lit=BEARD_LIT, shadow=BEARD_SH, light=lt, soft=0.9, tex_amt=0.14, streak=2, poly=P, rim=rim, rim_w=rim_w, line=INK, line_w=1.0 * s, line_a=0.35)
    mo = talk * abs(math.sin(t * 12)) * 0.8 + laugh * (0.6 + 0.4 * abs(math.sin(t * 13))) + frozen * 0.9
    mx, my = 4, 22
    if mo > 0.12:
        wd = 7 if frozen > 0.5 else 10
        M = H(catmull([(mx - wd, my), (mx + wd, my), (mx + wd * 0.7, my + 4 + 12 * mo), (mx - wd * 0.7, my + 4 + 12 * mo)]) if frozen < 0.5 else ellipse_pts(mx, my + 7, 6, 9 * mo))
        shade(L, L.mask(M), '#6a2a24', lit='#8a4038', light=lt, tex_amt=0.02, edge_dark=0.2, line=INK, line_w=1.0 * s, line_a=0.6, poly=M, weave=0)
    for sx in (-1, 1):   # moustache wings
        P = H(catmull([(mx, my - 4), (mx + sx * 14, my - 8), (mx + sx * 26, my - 2), (mx + sx * 20, my + 2), (mx + sx * 6, my)]))
        shade(L, L.mask(P, 0.5), BEARD, lit=BEARD_LIT, shadow=BEARD_SH, light=lt, soft=0.9, tex_amt=0.1, poly=P, line=INK, line_w=0.9 * s, line_a=0.4)
    # nose
    P = H(catmull([(6, -8), (16, 4), (14, 14), (2, 14), (0, 4)])); shade(L, L.mask(P, 0.5), '#eab79a', lit='#ffd8c0', shadow='#c07a62', light=lt, spec=0.3, poly=P, line=INK, line_w=1.0 * s, line_a=0.45)
    fill(H(ellipse_pts(-20, 8, 7, 4)), '#ee9a88', 0.45, 3); fill(H(ellipse_pts(30, 8, 7, 4)), '#ee9a88', 0.45, 3)
    # eyes behind round spectacles
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    wide = 1 + 0.5 * frozen
    for ex in (-14, 22):
        ey = -10 - 3 * up
        if bk > 0.15:
            fill(H(ellipse_pts(ex, ey, 6 * wide, 6.5 * bk * wide + 0.5)), '#fffaf2', 0.95, 0.4)
            fill(H(ellipse_pts(ex + look[0] * 2, ey + look[1] * 2 - 2 * up, 3.6, 4.2 * bk)), '#2a1a10', 1.0, 0.4)
            fill(H(ellipse_pts(ex + look[0] * 2 - 1.2, ey - 1.8 - 2 * up, 1.2, 1.2)), '#ffffff', 1.0, 0.2)
        else:
            lid = [(ex - 6, ey + 1), (ex, ey - 4), (ex + 6, ey + 1)] if laugh > 0.5 else [(ex - 6, ey), (ex, ey + 3), (ex + 6, ey)]
            pencil(L, H(lid), '#2e1a10', 1.8 * s, 0.9, lt, closed=False)
        pencil(L, H(catmull([(ex - 10, ey - 13 - 4 * frozen), (ex, ey - 17 - 5 * frozen + 2 * laugh), (ex + 10, ey - 13 - 4 * frozen)], closed=False, n=5)), '#d8d4ce', 4.0 * s, 0.9, lt, closed=False)
        G = H(ellipse_pts(ex, ey, 12, 12)); pencil(L, G, '#8a6a2a', 1.8 * s, 0.9, lt)
        fill(H(ellipse_pts(ex - 4, ey - 5, 3, 2, 0.6)), '#ffffff', 0.5, 0.8)
    stroke(L, H([(-2, -10), (10, -10)]), '#8a6a2a', 1.6 * s, 0.9, taper=False)
    # front arm (+ the big key)
    part('armR', catmull([(-11, -4), (12, -4), (13, 26), (11, 46), (-11, 46), (-12, 24)]), COAT, COAT_LIT, COAT_SH, soft=0.85, streak=1, tex_amt=0.1)
    part('foreR', catmull([(-10, -2), (11, -2), (12, 30), (-11, 30)]), COAT, COAT_LIT, COAT_SH, soft=0.85, streak=1)
    hand = X('foreR', [(0, 42)])[0]
    if key:
        ka = sum(ang[j] for j in ('pelvis', 'chest', 'armR', 'foreR'))
        k_ = math.radians(ka) * flip
        def K(pts):
            P = np.asarray(pts, np.float32); c, s_ = math.cos(k_), math.sin(k_)
            return np.stack([P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c], 1) * s * [flip, 1] * [1, 1] + hand
        stroke(L, K([(0, 0), (0, 46)]), '#c9973a', 4 * s, 1, taper=False)
        P = K(catmull([(-12, -4), (0, -16), (12, -4), (0, 6)])); shade(L, L.mask(P, 0.5), '#c9973a', lit='#ffe08a', shadow='#7a5418', light=lt, spec=0.7, poly=P, line=INK, line_w=0.8 * s, line_a=0.5)
        P = K([(-2, 40), (12, 40), (12, 48), (-2, 48)]); shade(L, L.mask(P, 0.5), '#c9973a', lit='#ffe08a', shadow='#7a5418', light=lt, spec=0.7, poly=P)
    part('foreR', catmull([(-8, 28), (9, 28), (10, 40), (0, 48), (-9, 40)]), SKIN, SKIN_LIT, SKIN_SH)
    composite(frame, L)
    return hand

# Clocks for the Clockmaker's planet: grandfather clocks, round clocks on posts, the big gear clock. Hands and pendulums move.
import numpy as np, math
from core import *

def _rot(pts, ang, piv=(0, 0)):
    P = np.asarray(pts, np.float32).reshape(-1, 2) - piv; c, s_ = math.cos(ang), math.sin(ang)
    return np.stack([P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c], 1) + piv

def gear_pts(cx, cy, r, teeth, ang, depth=0.14):
    pts = []
    for k in range(teeth * 4):
        a = ang + k / (teeth * 4) * 2 * math.pi; rr = r * (1 + depth * (1 if (k % 4) in (1, 2) else -0.2))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return np.array(pts, np.float32)

def face(L, T, cx, cy, r, t, lt, rim, rim_w, s, run=1.0, tick=True, seed=0, numerals=True):
    """A clock face with hands. run: 0 stopped .. 1 running. The seconds hand ticks."""
    P = T(ellipse_pts(cx, cy, r * 1.08, r * 1.08))
    shade(L, L.mask(P, 0.5), '#b8862e', lit='#ffe08a', shadow='#6a4a14', light=lt, spec=0.6, poly=P, line='#3a2810', line_w=1.2 * s, line_a=0.7, rim=rim, rim_w=rim_w)
    P = T(ellipse_pts(cx, cy, r, r))
    shade(L, L.mask(P, 0.5), '#f3e9d2', lit='#fffaf0', shadow='#c9b896', light=lt, soft=0.9, tex_amt=0.05, poly=P, line='#3a2810', line_w=1.0 * s, line_a=0.5)
    for k in range(12):
        a = k / 12 * 2 * math.pi; r0 = r * (0.78 if k % 3 else 0.7)
        stroke(L, T([(cx + math.sin(a) * r0, cy - math.cos(a) * r0), (cx + math.sin(a) * r * 0.88, cy - math.cos(a) * r * 0.88)]), '#3a2810', (2.2 if k % 3 == 0 else 1.2) * s, 0.85, taper=False)
    tt = t * run
    sec = (math.floor(tt) if tick else tt) + seed * 7.3
    for (ln, w_, a) in ((0.5, 3.4, (sec / 43200 + seed * 0.13) * 2 * math.pi), (0.72, 2.4, (sec / 3600 * 8 + seed * 0.41) * 2 * math.pi), (0.82, 1.1, sec / 60 * 2 * math.pi)):
        stroke(L, T([(cx - math.sin(a) * r * 0.12, cy + math.cos(a) * r * 0.12), (cx + math.sin(a) * r * ln, cy - math.cos(a) * r * ln)]), '#241808', w_ * s, 0.95, taper=True)
    P = T(ellipse_pts(cx, cy, r * 0.06, r * 0.06)); L.put(hexc('#241808'), L.mask(P, 0.5))

def grandfather(frame, x, y, s, t, light=(-0.5, -0.7), rim='#ffd9a0', rim_w=0.5, run=1.0, seed=0, flip=1, chain=1.0):
    """A tall case clock (x, y = base centre) with a swinging pendulum and winding chains."""
    pad = 30; L = Layer(x - 90 * s - pad, y - 470 * s - pad, 180 * s + 2 * pad, 480 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = np.asarray(pts, np.float32).reshape(-1, 2).copy(); P[:, 0] *= flip; return P * s + [x, y]
    WOOD = ('#7a4422', '#b8743e', '#3e200e')
    P = T([(-56, 0), (56, 0), (50, -300), (62, -330), (62, -440), (40, -462), (-40, -462), (-62, -440), (-62, -330), (-50, -300)])
    shade(L, L.mask(P, 0.5), WOOD[0], lit=WOOD[1], shadow=WOOD[2], light=lt, soft=0.3, streak=2, tex_amt=0.15, spec=0.25, poly=P, line='#2a1408', line_w=1.4 * s, line_a=0.7, rim=rim, rim_w=rim_w)
    win = T([(-30, -40), (30, -40), (30, -280), (-30, -280)]); L.put(hexc('#1e120a'), L.mask(win, 0.6))
    sw = math.sin(t * run * math.pi + seed) * 0.32 * run + 0.0
    rod = _rot([(0, -270), (0, -100)], sw, (0, -270)); bob_ = _rot([(0, -96)], sw, (0, -270))[0]
    stroke(L, T(rod), '#c9973a', 3 * s, 1, taper=False)
    B = T(ellipse_pts(bob_[0], bob_[1], 17, 17)); shade(L, L.mask(B, 0.5), '#c9973a', lit='#ffe08a', shadow='#7a5418', light=lt, spec=0.8, poly=B)
    for cxw, ln in ((-14, 120 * chain + 60), (14, 180 - 120 * chain + 60)):   # chains with weights
        stroke(L, T([(cxw, -280), (cxw, -280 + ln)]), '#9a8a6a', 1.6 * s, 0.9, taper=False)
        Wt = T([(cxw - 6, -280 + ln), (cxw + 6, -280 + ln), (cxw + 6, -250 + ln), (cxw - 6, -250 + ln)])
        shade(L, L.mask(Wt, 0.5), '#b8862e', lit='#ffe08a', shadow='#6a4a14', light=lt, spec=0.6, poly=Wt)
    face(L, T, 0, -385, 46, t, lt, rim, rim_w, s, run=run, seed=seed)
    composite(frame, L)

def post_clock(frame, x, y, s, t, light=(-0.5, -0.7), rim='#ffd9a0', rim_w=0.5, run=1.0, seed=0, h=260, r=52, flip=1):
    pad = 30; L = Layer(x - r * 1.3 * s - pad, y - (h + r * 1.3) * s - pad, r * 2.6 * s + 2 * pad, (h + r * 1.4) * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = np.asarray(pts, np.float32).reshape(-1, 2).copy(); P[:, 0] *= flip; return P * s + [x, y]
    P = T([(-6, 0), (6, 0), (5, -h), (-5, -h)]); shade(L, L.mask(P, 0.5), '#4a3a2a', lit='#8a7050', shadow='#20160c', light=lt, spec=0.3, poly=P, line='#1a1008', line_w=1.0 * s, line_a=0.6)
    face(L, T, 0, -h - r * 0.9, r, t, lt, rim, rim_w, s, run=run, seed=seed)
    composite(frame, L)

def gear_clock(frame, x, y, s, t, light=(-0.5, -0.7), rim='#ffd9a0', rim_w=0.5, run=1.0, seed=0, flip=1, jam=0.0, out=None):
    """The big clock with its gears showing below the face. jam: a gear shakes, stuck. out['bite']: where the gears meet."""
    pad = 40; L = Layer(x - 200 * s - pad, y - 520 * s - pad, 400 * s + 2 * pad, 530 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = np.asarray(pts, np.float32).reshape(-1, 2).copy(); P[:, 0] *= flip; return P * s + [x, y]
    P = T([(-150, 0), (150, 0), (140, -520), (-140, -520)])
    shade(L, L.mask(P, 0.5), '#5a4632', lit='#9a7a56', shadow='#2a1e12', light=lt, soft=0.5, tex_amt=0.15, streak=2, poly=P, line='#1a1008', line_w=1.5 * s, line_a=0.7, rim=rim, rim_w=rim_w)
    P = T([(-120, -30), (120, -30), (120, -230), (-120, -230)]); L.put(hexc('#21160e'), L.mask(P, 0.8))
    ang = t * run * 0.8 + jam * 0.03 * math.sin(t * 60)
    for (cx, cy, r, n, d) in ((-58, -130, 70, 16, 1), (40, -110, 46, 11, -70 / 46), (78, -190, 30, 8, 70 / 30 * 0.7), (-20, -60, 26, 7, -1.8)):
        G = T(gear_pts(cx, cy, r, n, ang * d + cx))
        shade(L, L.mask(G, 0.5), '#b8862e', lit='#ffe08a', shadow='#5a3a10', light=lt, spec=0.7, soft=0.6, poly=G, line='#2a1808', line_w=1.0 * s, line_a=0.7)
        H_ = T(ellipse_pts(cx, cy, r * 0.25, r * 0.25)); L.put(hexc('#3a2410'), L.mask(H_, 0.5))
        for k in range(4):
            a = ang * d + cx + k * math.pi / 2
            stroke(L, T([(cx + math.cos(a) * r * 0.3, cy + math.sin(a) * r * 0.3), (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8)]), '#8a6020', 4 * s, 0.9, taper=False)
    if out is not None: out['bite'] = T([(-2, -118)])[0]
    face(L, T, 0, -380, 110, t, lt, rim, rim_w, s, run=run, seed=seed)
    composite(frame, L)

def pocket_watch(frame, x, y, s, t, light=(-0.5, -0.7), rim='#ffd9a0', open_=1.0, chain=True):
    pad = 20; L = Layer(x - 40 * s - pad, y - 60 * s - pad, 80 * s + 2 * pad, 110 * s + 2 * pad)
    def T(pts): return np.asarray(pts, np.float32).reshape(-1, 2) * s + [x, y]
    if chain: stroke(L, T(catmull([(0, -26), (8, -44), (-4, -56), (14, -58)], closed=False, n=6)), '#e0b046', 1.6 * s, 0.9, taper=False)
    face(L, T, 0, 0, 20, t, light, rim, 0.4, s, run=1.0, seed=3)
    P = T(ellipse_pts(0, -26, 4, 4)); shade(L, L.mask(P, 0.5), '#c9973a', lit='#ffe08a', shadow='#7a5418', light=light, spec=0.8)
    composite(frame, L)

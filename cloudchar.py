# The Cloud: a big soft cloud with a face. Sad = grey and raining; happy = white and bright. (x, y) = centre of the body.
import numpy as np, math, cv2
from core import *

def _lerp(a, b, u): return a + (b - a) * u

def draw_cloud_char(frame, x, y, s=1.0, t=0.0, mood=0.0, rain=0.0, blink=None, talk=0.0, laugh=0.0, look=(0.0, 0.0), wave=0.0, sob=0.0,
                    light=(-0.5, -0.7), rim='#ffffff', rim_w=0.5, rain_len=420, flip=1):
    """mood 0 sad .. 1 happy. sob: shaking sniffles. wave: 0..1 her right puff-arm waves. rain: drops falling from her."""
    m = ss(mood)
    base = _lerp(hexc('#a9b3c8'), hexc('#f2f5fb'), m); lit = _lerp(hexc('#dfe6f2'), hexc('#ffffff'), m); sh = _lerp(hexc('#646e88'), hexc('#a9b6d0'), m)
    sb = sob * math.sin(t * 22) * 4
    br = 1 + 0.02 * math.sin(t * 1.4) + 0.03 * laugh * abs(math.sin(t * 12))
    pad = 60; Wd, Hd = 260 * s, 150 * s
    L = Layer(x - Wd - pad, y - Hd - pad, 2 * Wd + 2 * pad, 2 * Hd + 2 * pad)
    # rain first (behind the body)
    if rain > 0.01:
        r = np.random.default_rng(5)
        for k in range(int(70 * rain)):
            u = r.random(); px = x + (u * 2 - 1) * 200 * s; ph = r.random()
            fall = ((t * (1.6 + r.random() * 0.6) + ph) % 1.0)
            py = y + 60 * s + fall * rain_len * s
            cv2.line(frame, (int(px * 8), int(py * 8)), (int((px - 3 * s) * 8), int((py + 22 * s) * 8)), (0.78, 0.84, 0.95), max(1, int(1.5 * s * 2)), cv2.LINE_AA, shift=3)
    lt = (light[0] * flip, light[1])
    r = np.random.default_rng(11)
    puffs = []
    for k in range(30):
        a = r.random() * 2 * math.pi; d = math.sqrt(r.random())
        px = math.cos(a) * 170 * d; py = math.sin(a) * 90 * d - 26 * (1 - abs(math.cos(a)))
        puffs.append((py, px, py, (50 + r.random() * 30) * (1.1 - 0.35 * d)))
    for k in range(18):   # silhouette
        a = k / 18 * 2 * math.pi
        puffs.append((math.sin(a) * 80 - 300, math.cos(a) * 185, math.sin(a) * 96 - (22 if math.sin(a) < 0 else -4), 46 + r.random() * 16))
    puffs.sort(key=lambda p: p[0])
    for _, px, py, rr in puffs:
        wob = math.sin(t * 1.3 + px * 0.05) * 3
        puff(L, x + (px * br + sb) * s, y + (py * br + wob) * s, rr * s, base, lit, sh, lt, soft=0.4, ao=0.35, rim=rim, rim_w=rim_w, gx=int(px * 3), gy=int(py * 3))
    # little puff arms
    for side in (-1, 1):
        wv = wave if side == 1 else 0.0
        ang = math.radians(-30 * side - 70 * wv * (0.7 + 0.3 * math.sin(t * 9))) if side == 1 else math.radians(30)
        ax, ay = x + side * 190 * s, y + 10 * s
        for j in range(3):
            d = 26 + j * 22
            cx, cy = ax + side * math.cos(ang) * d * s * (1 if side == 1 else 1), ay - math.sin(abs(ang)) * d * s * (1 if wv > 0 else -0.3)
            puff(L, cx, cy, (26 - j * 4) * s, base, lit, sh, lt, soft=0.4, ao=0.3, rim=rim, rim_w=rim_w)
    puff(L, x + sb * s, y + 4 * s, 108 * s, base, lit, sh, lt, soft=0.6, ao=0.1, rim=None, rim_w=0, alpha=0.85)   # a soft cheek for the face
    # face
    fx, fy = x + (look[0] * 6 + sb) * s, y + (-6 + look[1] * 4) * s
    def P(pts): return np.asarray(pts, np.float32) * s * 1.4 + [fx, fy]
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    for ex in (-42, 42):
        ey = -10
        if bk > 0.15:
            E = P(ellipse_pts(ex, ey, 15, 19 * bk + 0.5)); shade(L, L.mask(E, 0.5), '#2c2a3e', lit='#5a5878', shadow='#141220', light=(0.3, 0.9), tex_amt=0.02, edge_dark=0, weave=0)
            L.put(np.array([1, 1, 1], np.float32), L.mask(P(ellipse_pts(ex - 5, ey - 7 * bk, 5.5, 5.5)), 0.4))
            L.put(np.array([1, 1, 1], np.float32), L.mask(P(ellipse_pts(ex + 5, ey + 7 * bk, 2.4, 2.4)), 0.4))
        else:
            lid = [(ex - 14, ey + 2), (ex, ey - 8), (ex + 14, ey + 2)] if laugh > 0.5 else [(ex - 14, ey), (ex, ey + 6), (ex + 14, ey)]
            pencil(L, P(lid), '#2c2a3e', 3.0 * s, 0.9, lt, closed=False)
        # brows: sad = tilted up in the middle
        tilt = (1 - m) * 10
        pts = [(ex - 16, ey - 30), (ex + 14, ey - 30 - tilt)] if ex < 0 else [(ex - 14, ey - 30 - tilt), (ex + 16, ey - 30)]
        pencil(L, P(pts), '#6a6a86', 3.0 * s, 0.7, lt, closed=False)
        L.put(hexc('#f2a6b0'), L.mask(P(ellipse_pts(ex * 1.25, 18, 16, 8)), 6) * (0.25 + 0.4 * m))
    mo = talk * abs(math.sin(t * 10)) + laugh * (0.7 + 0.3 * abs(math.sin(t * 13)))
    if mo > 0.12:
        M = P(catmull([(-16, 24), (16, 24), (10, 32 + 16 * mo), (-10, 32 + 16 * mo)]))
        shade(L, L.mask(M), '#6a3a4a', lit='#8a4a5a', light=lt, tex_amt=0.02, edge_dark=0.2, line='#2c2a3e', line_w=1.2 * s, line_a=0.6, poly=M, weave=0)
    else:
        c = (m - 0.5) * 2
        pencil(L, P(catmull([(-14, 30 - c * 4), (0, 30 + c * 5), (14, 30 - c * 4)], closed=False, n=5)), '#2c2a3e', 2.6 * s, 0.85, lt, closed=False)
    if m < 0.5 and sob > 0:   # tears
        for ex in (-42, 42):
            u = (t * 0.8 + (0.5 if ex > 0 else 0)) % 1
            L.put(hexc('#cfe6ff'), L.mask(P(ellipse_pts(ex + 6, 6 + u * 40, 4, 6)), 0.5) * (1 - u))
    composite(frame, L)

# More painted props: watering can, broom, birds, a pulled baobab sprout, water drops, soot puffs.
import numpy as np, math
from core import *

def _rot(pts, ang_deg, piv=(0, 0)):
    P = np.asarray(pts, np.float32) - piv; a = math.radians(ang_deg); c, s_ = math.cos(a), math.sin(a)
    return np.stack([P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c], 1) + piv

def watering_can(L, hand, ang, s, lt, flip, tilt=0.0, out=None):
    """Held by its top handle. tilt: degrees forward (pouring). out: dict that receives the spout tip."""
    hx, hy = hand
    def T(pts): P = _rot(pts, -tilt); P[:, 0] *= flip; return P * s + [hx, hy]
    body = catmull([(-34, 18), (34, 18), (38, 40), (36, 78), (-36, 78), (-38, 40)])
    P = T(body); shade(L, L.mask(P, 0.5), '#6f9ab8', lit='#b5d6ea', shadow='#3a5a78', light=lt, soft=0.75, spec=0.35, tex_amt=0.06, line='#2f3f52', line_w=1.4 * s, line_a=0.7, poly=P)
    for yy in (34, 64):
        stroke(L, T([(-37, yy), (37, yy)]), '#4a6f8e', 2.2 * s, 0.7, taper=False)
    sp = catmull([(30, 66), (78, 22), (84, 14), (90, 18), (40, 76)])
    P = T(sp); shade(L, L.mask(P, 0.5), '#6f9ab8', lit='#b5d6ea', shadow='#3a5a78', light=lt, soft=0.8, spec=0.3, line='#2f3f52', line_w=1.2 * s, line_a=0.7, poly=P)
    rose = T(ellipse_pts(88, 15, 9, 5, -0.6)); shade(L, L.mask(rose, 0.5), '#58819f', lit='#a6c8de', light=lt, line='#2f3f52', line_w=1.0 * s, line_a=0.6, poly=rose)
    stroke(L, T(catmull([(-22, 18), (-14, -6), (14, -6), (22, 18)], closed=False, n=6)), '#4f7896', 5 * s, 1.0, taper=False)
    if out is not None: out['spout'] = T([(92, 16)])[0]

def broom(L, hand, ang, s, lt, flip):
    hx, hy = hand
    def T(pts): P = _rot(pts, ang * flip); P[:, 0] *= flip; return P * s + [hx, hy]
    stroke(L, T([(0, -40), (0, 120)]), '#8a5a32', 6 * s, 1.0, taper=False)
    br = catmull([(-8, 118), (8, 118), (26, 176), (-26, 176)])
    P = T(br); shade(L, L.mask(P, 0.5), '#d8b25a', lit='#f6dc8c', shadow='#9a7428', light=lt, streak=2, tex_amt=0.15, line='#6a4a20', line_w=1.2 * s, line_a=0.6, poly=P)
    for k in range(7):
        x0 = -20 + k * 6.6; stroke(L, T([(x0 * 0.4, 124), (x0, 176)]), '#a8832e', 1.2 * s, 0.5, taper=False)
    stroke(L, T([(-10, 128), (10, 128)]), '#b0563a', 3 * s, 0.9, taper=False)

def water_drops(f, spout, t, s, rate=1.0, gx=1.0):
    """A sparkling arc of water from the spout."""
    if spout is None: return
    x0, y0 = spout
    for k in range(int(26 * rate)):
        u = ((t * 2.2 + k / 26) % 1.0); g = 260 * s
        x = x0 + gx * 38 * s * u * 3; y = y0 + 0.5 * g * (u * 0.9) ** 2 * 3 + 10 * s * u
        r = (2.2 + (k % 3) * 0.6) * s
        glow(f, x, y, r * 1.1, '#e8f6ff', 0.25)
        cv2.circle(f, (int(x * 8), int(y * 8)), max(4, int(r * 8)), (0.82, 0.92, 1.0), -1, cv2.LINE_AA, shift=3)

def sprout_item(frame, x, y, s, t, light, ang=0.0, roots=True):
    """A baobab sprout held by its stalk (in a sheep's mouth), roots dangling."""
    pad = 20; L = Layer(x - 50 * s - pad, y - 60 * s - pad, 100 * s + 2 * pad, 120 * s + 2 * pad)
    def T(pts): return _rot(pts, ang) * s + [x, y]
    stroke(L, T([(0, 10), (0, -26)]), '#5d8a3e', 4 * s, 1, taper=False)
    for side in (-1, 1):
        b = np.array([0, -26]); tip = b + [side * 26, -14 + math.sin(t * 9 + side) * 3]
        n_ = np.array([-(tip - b)[1], (tip - b)[0]]) / (np.linalg.norm(tip - b) + 1e-6)
        P = T(catmull([b, (b + tip) / 2 + n_ * 9, tip, (b + tip) / 2 - n_ * 7], n=8))
        shade(L, L.mask(P, 0.5), '#6ea44c', lit='#b2d97c', shadow='#3b6a2e', light=light, soft=0.8, tex_amt=0.05, line='#3a4a24', line_w=1.0 * s, line_a=0.6, poly=P)
    if roots:
        for k in range(5):
            a = (k - 2) * 0.35 + math.sin(t * 6 + k) * 0.15
            P = T(catmull([(0, 10), (math.sin(a) * 10, 22), (math.sin(a) * 18, 36 + k % 2 * 6)], closed=False, n=5))
            stroke(L, P, '#a07a52', 1.8 * s, 0.9)
        P = T(ellipse_pts(0, 14, 7, 5)); L.put(hexc('#7a5a3a'), L.mask(P, 1.5) * 0.8)
    composite(frame, L)

def soot_puff(f, x, y, s, age, seed=0):
    """A soft cloud of volcano soot that billows out and fades (age in seconds)."""
    if age < 0 or age > 2.5: return
    r = np.random.default_rng(seed); a = max(0, 1 - age / 2.5)
    for k in range(12):
        ang = r.random() * 6.28; sp = 50 + r.random() * 90
        px = x + math.cos(ang) * sp * s * (1 - math.exp(-age * 2.5)); py = y + (math.sin(ang) * 0.5 - 0.6) * sp * s * (1 - math.exp(-age * 2.5)) - age * 20 * s
        rr = (26 + r.random() * 26) * s * (0.6 + age * 0.7)
        x0, x1 = int(max(0, px - rr * 2)), int(min(f.shape[1], px + rr * 2)); y0, y1 = int(max(0, py - rr * 2)), int(min(f.shape[0], py + rr * 2))
        if x1 <= x0 or y1 <= y0: continue
        yy, xx = np.mgrid[y0:y1, x0:x1]; d2 = ((xx - px) ** 2 + (yy - py) ** 2) / (rr * rr)
        m = np.exp(-d2 * 1.6) * 0.7 * a
        f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - m[..., None]) + np.array([0.24, 0.2, 0.22], np.float32) * m[..., None]

def bird(frame, x, y, s, t, flip=1, phase=0.0, color='#f4efe6', light=(-0.5, -0.7), glide=0.0):
    """A small white bird flapping (seen from the side)."""
    pad = 10; L = Layer(x - 60 * s - pad, y - 60 * s - pad, 120 * s + 2 * pad, 100 * s + 2 * pad)
    fl = math.sin(t * 13 + phase) * (1 - glide) + glide * 0.2
    def T(pts): P = np.asarray(pts, np.float32).copy(); P[:, 0] *= flip; return P * s + [x, y]
    body = T(catmull([(-30, 0), (-10, -8), (16, -8), (30, -4), (26, 4), (0, 8), (-24, 4)]))
    shade(L, L.mask(body, 0.5), color, lit='#ffffff', shadow='#b9b4c4', light=light, soft=0.8, tex_amt=0.04, line='#6a6070', line_w=1.0 * s, line_a=0.5, poly=body)
    tail = T([(-30, 0), (-44, -6), (-42, 6)]); L.put(hexc(color), L.mask(tail, 0.8))
    beak = T([(30, -4), (38, -1), (29, 2)]); L.put(hexc('#f0a040'), L.mask(beak, 0.5))
    L.put(hexc('#2a2026'), L.mask(T(ellipse_pts(22, -4, 1.8, 1.8)), 0.3))
    for side, dk in ((1, 0.8), (-1, 1.0)):
        tip_y = -40 * fl * dk; mid_y = -18 * fl * dk
        w = T(catmull([(-6, -4), (8, -6), (6 + side * 2, mid_y - 2), (-4 + side * 4, tip_y), (-12, mid_y + 4)]))
        c = color if side < 0 else '#e2dcd2'
        shade(L, L.mask(w, 0.5), c, lit='#ffffff', shadow='#a9a3b6', light=light, soft=0.8, tex_amt=0.04, line='#6a6070', line_w=0.9 * s, line_a=0.4, poly=w)
    composite(frame, L)

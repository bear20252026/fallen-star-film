# Moth: a big, soft, lonely night-moth. Grey-violet wings, fluffy cream collar, big dark eyes, feathery antennae.
# (x, y) = middle of his body; his feet are at y + 250*s. About twice as tall as the boy at the same s.
import numpy as np, math, cv2
from core import *

def _lerp(a, b, u): return a + (b - a) * u

FORE = [(0, 0), (50, -80), (150, -165), (270, -205), (345, -180), (350, -110), (300, -30), (210, 40), (110, 70), (40, 50)]
HIND = [(0, 0), (80, 30), (180, 95), (225, 175), (195, 245), (120, 240), (60, 170), (20, 80)]

def _wing(pts, side, ang, sx, piv):
    P = np.asarray(catmull(pts, closed=True, n=8), np.float32)
    P[:, 0] *= sx
    c, s_ = math.cos(ang), math.sin(ang)
    R = np.stack([P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c], 1)
    R[:, 0] *= side
    return R + piv

def _wpt(p, side, ang, sx, piv):
    x, y = p[0] * sx, p[1]; c, s_ = math.cos(ang), math.sin(ang)
    return (side * (x * c - y * s_) + piv[0], x * s_ + y * c + piv[1])

def draw_moth(frame, x, y, s=1.0, t=0.0, flip=1, open_=1.0, flap=0.0, flap_speed=2.2, mood=0.0, surprise=0.0, laugh=0.0, talk=0.0,
              blink=None, look=(0.0, 0.0), shiver=0.0, hold=None, reach=0.0, glow_amt=0.0, light=(-0.5, -0.7), rim='#d8c8ff', rim_w=0.5,
              tilt=0.0, out=None, dim=0.0, blur=0.0):
    """open_: 0 wings folded down by his sides .. 1 spread. flap: 0..1 how strongly the wings beat.
    mood 0 sad .. 1 happy. hold: (dx, dy) in his own units, where both hands meet (a hug, carrying). reach: arms up and out.
    glow_amt: a warm light in his arms lights him from below. out: dict filled with 'hand', 'head', 'chest' screen points."""
    m = ss(mood)
    jx = shiver * (math.sin(t * 41) * 3 + math.sin(t * 67) * 2)
    br = 1 + 0.025 * math.sin(t * 1.3) + 0.03 * laugh * abs(math.sin(t * 11))
    pad = 60
    L = Layer(x - 420 * s - pad, y - 420 * s - pad, 840 * s + 2 * pad, 720 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    ca, sa = math.cos(tilt), math.sin(tilt)
    def T(pts):
        P = np.asarray(pts, np.float32).reshape(-1, 2).copy()
        P = np.stack([P[:, 0] * ca - P[:, 1] * sa, P[:, 0] * sa + P[:, 1] * ca], 1)
        P[:, 0] *= flip; P[:, 0] += jx
        return P * s + [x, y]
    warm = hexc('#ffd27a')
    def W(c, k=1.0):   # warm the colour a little when the star glows in his arms
        c = hexc(c) if isinstance(c, str) else c
        return _lerp(c, c * 0.6 + warm * 0.55, min(1.0, glow_amt * 0.5 * k))

    # ---- wings: hind pair, then fore pair (behind the body)
    ph = t * flap_speed * 2 * math.pi
    beat = math.sin(ph)
    sx = 1 - flap * 0.55 * (0.5 + 0.5 * beat)
    ang_f = _lerp(1.95, 0.0, ss(open_)) + flap * 0.22 * beat
    ang_h = _lerp(0.75, 0.0, ss(open_)) + flap * 0.15 * beat
    sxo = _lerp(0.36, 1.0, ss(open_)) * sx
    for side in (-1, 1):
        piv = (side * 22, 28)
        P = T(_wing(HIND, side, ang_h, sxo, piv))
        shade(L, L.mask(P, 0.8), W('#7c6e98'), lit=W('#b4a8cc'), shadow='#3c3258', light=lt, soft=0.7, tex_amt=0.12, streak=2, streak_amt=0.2, weave=0.0,
              poly=P, line='#2a2238', line_w=1.2 * s, line_a=0.55, rim=rim, rim_w=rim_w * 0.6)
        e = _wpt((140, 160), side, ang_h, sxo, piv)
        L.put(hexc('#e9dcc6'), L.mask(T(ellipse_pts(e[0], e[1], 30 * sxo, 26)), 3) * 0.7)
        L.put(hexc('#4a3a66'), L.mask(T(ellipse_pts(e[0], e[1], 17 * sxo, 15)), 2) * 0.85)
    for side in (-1, 1):
        piv = (side * 30, -28)
        P = T(_wing(FORE, side, ang_f, sxo, piv))
        shade(L, L.mask(P, 0.8), W('#8a7caa'), lit=W('#c6badc'), shadow='#433860', light=lt, soft=0.7, tex_amt=0.12, streak=2, streak_amt=0.2, weave=0.0,
              poly=P, line='#2a2238', line_w=1.3 * s, line_a=0.55, rim=rim, rim_w=rim_w)
        # a pale band near the edge, soft veins, a big eye-spot
        band = [_wpt(p, side, ang_f, sxo, piv) for p in ((150, -150), (265, -185), (330, -160), (335, -105), (290, -40))]
        stroke(L, T(catmull(band, closed=False, n=6)), '#e6dac8', 16 * s * max(0.4, sxo), 0.45, blur=4, taper=True)
        for tip in ((270, -195), (340, -130), (280, -20), (180, 55)):
            v = [_wpt(p, side, ang_f, sxo, piv) for p in ((10, -5), (tip[0] * 0.5, tip[1] * 0.45), (tip[0] * 0.9, tip[1] * 0.9))]
            stroke(L, T(catmull(v, closed=False, n=5)), '#3e3458', 1.6 * s, 0.35, taper=True)
        e = _wpt((185, -90), side, ang_f, sxo, piv)
        L.put(hexc('#f0e4cc'), L.mask(T(ellipse_pts(e[0], e[1], 44 * sxo, 40)), 3) * 0.8)
        L.put(hexc('#5a4a7a'), L.mask(T(ellipse_pts(e[0], e[1], 30 * sxo, 27)), 2) * 0.9)
        L.put(hexc('#241c36'), L.mask(T(ellipse_pts(e[0], e[1], 16 * sxo, 15)), 2) * 0.9)
        L.put(hexc('#ffffff'), L.mask(T(ellipse_pts(e[0] - 6 * sxo, e[1] - 7, 5 * sxo, 5)), 1) * 0.6)

    # ---- abdomen: soft striped puffs going down
    for k in range(6):
        u = k / 5; cy = 40 + u * 175; r = (74 - 30 * u) * br
        col = '#8e82a8' if k % 2 == 0 else '#7a6e96'
        puff(L, *T([(0, cy)])[0], r * s, W(col), W('#c0b4d4'), '#3e3456', lt, soft=0.45, ao=0.3, rim=rim, rim_w=rim_w * 0.5, gx=k * 37, gy=k * 11)
    # little feet
    for side in (-1, 1):
        stroke(L, T([(side * 34, 200), (side * 44, 236), (side * 54, 248)]), '#3a3050', 7 * s, 0.9, taper=True)
    # thorax
    puff(L, *T([(0, -10)])[0], 92 * br * s, W('#9a8eb6'), W('#d0c6e2'), '#463c60', lt, soft=0.5, ao=0.25, rim=rim, rim_w=rim_w, gx=5, gy=9)
    # ---- arms (behind the collar)
    hands = []
    for side in (-1, 1):
        sh = (side * 72, -12)
        if hold is not None:
            hx, hy = hold; hd = (hx + side * 34, hy)
            el = (side * 105, (sh[1] + hy) * 0.5 + 25)
        else:
            rx = side * _lerp(95, 175, reach); ry = _lerp(70, -150, reach)
            hd = (rx, ry); el = (side * _lerp(110, 150, reach), _lerp(40, -40, reach))
        A = catmull([sh, el, hd], closed=False, n=6)
        stroke(L, T(A), W('#8a7ea6'), 30 * s, 1.0, taper=False)
        stroke(L, T(A), W('#b6aacc'), 14 * s, 0.45, taper=False)
        puff(L, *T([hd])[0], 22 * s, W('#a094bc'), W('#d6cce6'), '#4a4064', lt, soft=0.4, ao=0.2)
        hands.append(T([hd])[0])
    # ---- fluffy cream collar
    for k in range(11):
        u = k / 10; a = math.pi * (1.05 + 0.9 * u)
        cx, cy = math.cos(a) * 84, -80 - math.sin(a) * 26
        puff(L, *T([(cx, cy)])[0], (34 + 7 * math.sin(k * 2.1)) * br * s, W('#d6cede', 1.2), W('#f4eef6', 1.2), '#8a7ea4', lt, soft=0.4, ao=0.35,
             rim=rim, rim_w=rim_w * 0.6, gx=k * 13, gy=k * 7)
    # ---- antennae (feathery, swaying)
    hy0 = -158
    for side in (-1, 1):
        sw = math.sin(t * 1.1 + side) * 8 + surprise * 25
        base = (side * 26, hy0 - 52)
        mid = (side * (62 + sw * 0.3), hy0 - 150 - surprise * 20)
        tip = (side * (118 + sw), hy0 - 205 - surprise * 30 + (1 - m) * 25)
        A = np.asarray(catmull([base, mid, tip], closed=False, n=10), np.float32)
        for i in range(1, len(A) - 1, 1):
            d = A[i + 1] - A[i - 1]; nrm = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
            ln = 16 * math.sin(math.pi * i / len(A)) + 3
            for sg in (-1, 1):
                stroke(L, T([A[i], A[i] + nrm * ln * sg + d * 0.25]), '#6a5e86', 1.6 * s, 0.75, taper=True)
        stroke(L, T(A), '#4a3e66', 3.2 * s, 0.95, taper=True)
    # ---- head
    hx, hy = 0, hy0
    H_ = T(ellipse_pts(hx, hy, 82 * br, 72 * br))
    shade(L, L.mask(H_, 1.0), W('#a89cc2'), lit=W('#ddd4ec'), shadow='#4e4468', light=lt, soft=0.8, tex_amt=0.1, weave=0.0, poly=H_,
          line='#2a2238', line_w=1.1 * s, line_a=0.45, rim=rim, rim_w=rim_w)
    for k in range(7):   # fuzz on top of the head
        a = math.pi * (1.15 + 0.7 * k / 6)
        puff(L, *T([(math.cos(a) * 70, hy - 10 + math.sin(a) * 58)])[0], 15 * s, W('#a89cc2'), W('#ddd4ec'), '#5a5074', lt, soft=0.5, ao=0.1, gx=k * 9)
    # face
    fx, fy = look[0] * 8, look[1] * 6
    def P(pts): return T(np.asarray(pts, np.float32) + [hx + fx, hy + fy])
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    eyer = 1 + 0.25 * surprise
    for ex in (-34, 34):
        ey = -6
        if bk > 0.15:
            E = P(ellipse_pts(ex, ey, 25 * eyer, 30 * eyer * bk + 0.5))
            shade(L, L.mask(E, 0.6), '#1e1830', lit='#4a4268', shadow='#0c0a14', light=(0.3, 0.9), tex_amt=0.02, edge_dark=0, weave=0)
            L.put(np.array([1, 1, 1], np.float32), L.mask(P(ellipse_pts(ex - 8, ey - 11 * bk, 8, 8)), 0.5) * 0.95)
            L.put(np.array([1, 1, 1], np.float32), L.mask(P(ellipse_pts(ex + 8, ey + 10 * bk, 3.5, 3.5)), 0.5) * 0.8)
            if glow_amt > 0.05:
                L.put(warm, L.mask(P(ellipse_pts(ex + 2, ey + 14 * bk, 7, 4)), 1) * min(1, glow_amt))
        else:
            lid = [(ex - 18, ey + 4), (ex, ey - 9), (ex + 18, ey + 4)] if laugh > 0.5 else [(ex - 18, ey), (ex, ey + 7), (ex + 18, ey)]
            pencil(L, P(lid), '#241c36', 3.4 * s, 0.9, lt, closed=False)
        # soft brows: sad = up in the middle
        tilt_b = (1 - m) * 9 - surprise * 6
        bp = [(ex - 18, ey - 40), (ex + 16, ey - 40 - tilt_b)] if ex < 0 else [(ex - 16, ey - 40 - tilt_b), (ex + 18, ey - 40)]
        pencil(L, P(bp), '#5a4e78', 3.2 * s, 0.6, lt, closed=False)
        L.put(hexc('#f0a8c0'), L.mask(P(ellipse_pts(ex * 1.45, 26, 15, 8)), 5) * (0.2 + 0.4 * m))
    mo = talk * abs(math.sin(t * 9)) + laugh * (0.7 + 0.3 * abs(math.sin(t * 12)))
    if surprise > 0.4 and mo < 0.12:
        M = P(ellipse_pts(0, 36, 7, 9)); shade(L, L.mask(M, 0.5), '#5a3048', lit='#7a4060', light=lt, tex_amt=0, edge_dark=0.2, weave=0)
    elif mo > 0.12:
        M = P(catmull([(-15, 30), (15, 30), (9, 37 + 15 * mo), (-9, 37 + 15 * mo)]))
        shade(L, L.mask(M), '#5a3048', lit='#7a4060', light=lt, tex_amt=0.02, edge_dark=0.2, line='#241c36', line_w=1.2 * s, line_a=0.6, poly=M, weave=0)
    else:
        c = (m - 0.5) * 2
        pencil(L, P(catmull([(-12, 34 - c * 4), (0, 34 + c * 5), (12, 34 - c * 4)], closed=False, n=5)), '#241c36', 2.6 * s, 0.85, lt, closed=False)
    if dim > 0:   # half-seen in the dark: a deep violet silhouette with only a faint rim
        L.rgb *= (1 - 0.85 * dim); L.rgb += hexc('#140e22') * 0.6 * dim
    if blur > 0.5:   # out of focus (very close to the camera)
        k = int(blur) * 2 + 1; pa = cv2.GaussianBlur(L.rgb * L.a[..., None], (k, k), 0); L.a = cv2.GaussianBlur(L.a, (k, k), 0); L.rgb = pa / np.maximum(L.a, 1e-4)[..., None]
    composite(frame, L)
    if out is not None:
        out['hand'] = (hands[0] + hands[1]) * 0.5
        out['head'] = T([(hx, hy)])[0]
        out['chest'] = T([(0, 30)])[0]
    return (hands[0] + hands[1]) * 0.5

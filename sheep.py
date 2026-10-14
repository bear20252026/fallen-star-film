# The sheep, painted in code. Local units: body is ~200 wide, feet at y=0; scaled by s. Faces right (flip=-1 faces left).
import numpy as np, math
from core import *

WOOL = '#f4ece0'; WOOL_LIT = '#fffaf0'; WOOL_SH = '#b9b1c4'
FACE = '#f2dcc6'; FACE_LIT = '#fff0e0'; FACE_SH = '#c99f8f'
LEG = '#5b4337'; INK = '#5a3b2a'

def _xf(pts, x, y, s, flip, rot=0.0, piv=(0, 0)):
    P = np.asarray(pts, np.float32).copy()
    if rot:
        c, sn = math.cos(rot), math.sin(rot); q = P - piv
        P = np.stack([q[:, 0] * c - q[:, 1] * sn, q[:, 0] * sn + q[:, 1] * c], 1) + piv
    P[:, 0] *= flip
    return P * s + [x, y]

LAST = {}

def _rot(pts, deg, piv):
    P = np.asarray(pts, np.float32) - piv; a = math.radians(deg); c, sn = math.cos(a), math.sin(a)
    return np.stack([P[:, 0] * c - P[:, 1] * sn, P[:, 0] * sn + P[:, 1] * c], 1) + piv

def bumpy_outline(cx, cy, rx, ry, nb, amp, seed, start=0.0):
    r = np.random.default_rng(seed); a = np.linspace(0, 2 * np.pi, nb * 10, endpoint=False) + start
    ph = r.random(nb) * 0.4
    k = (a * nb / (2 * np.pi))
    bump = np.abs(np.sin(np.pi * (k + np.repeat(ph, 10)[: len(a)]))) ** 0.6
    rr = 1 + amp * (bump - 0.6)
    return np.stack([cx + rx * rr * np.cos(a), cy + ry * rr * np.sin(a)], 1)

def domes(L, centers, radii):
    """A height bump field made of little wool domes."""
    b = np.zeros((L.h, L.w), np.float32)
    yy, xx = np.mgrid[0:L.h, 0:L.w]
    for (cx, cy), r in zip(centers, radii):
        cx -= L.x0; cy -= L.y0
        x0, x1 = int(max(0, cx - r)), int(min(L.w, cx + r + 1)); y0, y1 = int(max(0, cy - r)), int(min(L.h, cy + r + 1))
        if x1 <= x0 or y1 <= y0: continue
        d2 = ((xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2) / (r * r)
        b[y0:y1, x0:x1] = np.maximum(b[y0:y1, x0:x1], np.sqrt(np.clip(1 - d2, 0, 1)))
    return b

def draw_sheep(frame, x, y, s=1.0, flip=1, t=0.0, head=0.0, walk=0.0, blink=None, mouth='smile',
               light=(-0.55, -0.7), rim='#ffd9a0', rim_w=0.45, squash=0.0, look=(0.0, 0.0), seed=3, tail=0.0, laugh=0.0, shadow=True, A=None):
    pad = 60
    L = Layer(x - 200 * s - pad, y - 300 * s - pad, 400 * s + 2 * pad, 320 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    jig = np.zeros(2); pitch = 0.0; ear_ang = 0.0; bx = 0.0; feet = None; air = 0.0; soot = 0.0
    if A is not None:   # a full performance from sheep_anim
        feet = A['feet']; bx, yb = A['body']; pitch = A['pitch']; head = A['head']; jig = A['jig']; ear_ang = A['ear']
        tail = A['tail']; squash = A['squash']; blink = A['blink']; look = A['look']; laugh = A['laugh']; mouth = A.get('mouth', mouth)
        air = A.get('air', 0.0); soot = A.get('soot', 0.0)
        br = math.sin(t * 1.9) * 0.012
    else:
        br = math.sin(t * 1.9) * 0.015 + laugh * abs(math.sin(t * 14)) * 0.03
        yb = walk * abs(math.sin(t * 7.5)) * -10 - laugh * abs(math.sin(t * 14)) * 6
    sy = 1 - squash + br; sx = 1 + squash * 0.6 - br * 0.5
    pc, ps = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    def X(pts, rot=0, piv=(0, 0)):
        P = np.asarray(pts, np.float32).reshape(-1, 2).copy()
        if rot:
            c, sn = math.cos(rot), math.sin(rot); q = P - piv
            P = np.stack([q[:, 0] * c - q[:, 1] * sn, q[:, 0] * sn + q[:, 1] * c], 1) + piv
        P[:, 1] = (P[:, 1] - yb) * sy + yb; P[:, 0] *= sx          # squash about the body
        q = P - [0, -110 + yb]; P = np.stack([q[:, 0] * pc - q[:, 1] * ps, q[:, 0] * ps + q[:, 1] * pc], 1) + [bx, -110 + yb]
        return _xf(P, x, y, s, flip)
    if shadow: ground_shadow(frame, x + bx * s * flip, y + 2, 120 * s * (1 - 0.4 * min(1, air / 60)), 16 * s, 0.45 * (1 - 0.5 * min(1, air / 60)))
    # stubby legs: from the body down to feet that are planted on the ground
    for i, (lx, ph, far) in enumerate([(-62, 0.0, True), (40, math.pi, True), (-40, math.pi, False), (62, 0.0, False)]):
        if feet is None:
            sw = math.sin(t * 7.5 + ph) * 0.5 * walk
            top = np.array([lx, -48 + yb]); foot = top + [math.sin(sw) * 46, math.cos(sw) * 46 - (6 * max(0, math.sin(t * 7.5 + ph)) * walk)]
            Ptop = X([top])[0]
        else:
            Ptop = X([[lx, -40 + yb]])[0]
        Pfoot = _xf([feet[i]], x, y, s, flip)[0] if feet is not None else X([foot])[0]
        d = Pfoot - Ptop; ln = np.linalg.norm(d) + 1e-6; dn = d / ln; nn = np.array([-dn[1], dn[0]])
        wd = 11 * s
        leg = catmull([Ptop - nn * wd, Ptop + nn * wd, Pfoot - dn * 12 * s + nn * 10 * s, Pfoot + nn * 9 * s, Pfoot - nn * 9 * s, Pfoot - dn * 12 * s - nn * 10 * s])
        P = leg; c = '#4a352b' if far else LEG
        shade(L, L.mask(P), c, lit='#86634f', shadow='#33241f', soft=0.9, light=lt, tex_amt=0.04, edge_dark=0.1, line=INK, line_w=1.1, line_a=0.35, poly=P)
        hoof = catmull([Pfoot + np.array([-10, -7]) * s, Pfoot + np.array([10, -7]) * s, Pfoot + np.array([11, 1]) * s, Pfoot + np.array([-11, 1]) * s])
        shade(L, L.mask(hoof), '#2f2420', lit='#57423a', light=lt, tex_amt=0.03, edge_dark=0.05)
    # tail
    tc = X([[-120, -105 + yb]], math.radians(tail), (-100, -100 + yb))[0]
    for k in range(4):
        puff(L, tc[0] + (k % 2 - 0.5) * 10 * s, tc[1] + (k // 2 - 0.5) * 10 * s, 13 * s, WOOL, WOOL_LIT, WOOL_SH, lt, rim=rim, rim_w=rim_w)
    # fleece: many painted puffs, back to front, bottom to top
    r = np.random.default_rng(seed); pts = []
    for k in range(95):
        a = r.random() * 2 * np.pi; d = math.sqrt(r.random())
        px, py = math.cos(a) * 112 * d, -118 + yb + math.sin(a) * 66 * d
        pts.append((py + r.random() * 6, px, py, (24 + r.random() * 12) * (1.05 - 0.25 * d)))
    for k in range(34):   # the silhouette
        a = k / 34 * 2 * np.pi
        pts.append((-118 + yb + math.sin(a) * 70 - 200, math.cos(a) * 118, -118 + yb + math.sin(a) * 70, 21 + r.random() * 6))
    pts.sort(key=lambda p: p[0])
    for _, px, py, rr in pts:
        hk = np.clip((-48 - (py - yb)) / 120, 0, 1)
        c = X([[px + jig[0] * hk, py + jig[1] * hk]])[0]
        puff(L, c[0], c[1], rr * s, WOOL, WOOL_LIT, WOOL_SH, lt, ao=0.45, rim=rim, rim_w=rim_w, gx=int(px * 3), gy=int(py * 3))
    # head
    hp = (82, -150 + yb); hr = math.radians(head)
    HX = lambda pts: X(pts, hr, hp)
    ear2 = HX(catmull([(118, -206 + yb), (146, -214 + yb), (162, -200 + yb), (146, -192 + yb)]))
    shade(L, L.mask(ear2), '#d9bfa9', lit='#ecd3bd', shadow='#a98471', light=lt, tex_amt=0.04, line=INK, line_w=1.0, line_a=0.4, poly=ear2)
    face = HX(catmull([(112, -228 + yb), (150, -222 + yb), (172, -192 + yb), (174, -158 + yb), (158, -128 + yb), (126, -118 + yb), (96, -128 + yb), (82, -160 + yb), (88, -204 + yb)]))
    shade(L, L.mask(face, 0.5), FACE, lit=FACE_LIT, shadow=FACE_SH, light=lt, rim=rim, rim_w=rim_w * 0.9, soft=0.8, tex_amt=0.045, edge_dark=0.08, line=INK, line_w=1.6, line_a=0.55, poly=face)
    # muzzle highlight
    mz = HX(ellipse_pts(150, -142 + yb, 22, 15, -0.2)); L.put(hexc('#fbe9da'), L.mask(mz, 5) * 0.5)
    if soot > 0.01:   # sooty face from the volcano
        sm = L.mask(face, 2.0); nz = tex(NOISE[2], 40, 40, sm.x1 - sm.x0, sm.y1 - sm.y0, 0.6)
        L.put(hexc('#3a3034'), Mask(sm.x0, sm.y0, sm.x1, sm.y1, sm.m * np.clip(0.75 + 0.35 * np.tanh(nz - nz.mean()), 0, 1) * 0.85 * soot))
    # head tuft of wool
    for k, (dx, dy, rr) in enumerate([(-22, 6, 16), (-6, -2, 19), (12, 2, 17), (26, 10, 13), (-30, 18, 12), (4, 12, 15)]):
        c = HX([[118 + dx, -224 + yb + dy]])[0]
        puff(L, c[0], c[1], rr * s, WOOL, WOOL_LIT, WOOL_SH, lt, ao=0.3, rim=rim, rim_w=rim_w)
    ear = HX(catmull(_rot([(96, -200 + yb), (70, -200 + yb), (46, -186 + yb), (50, -172 + yb), (76, -176 + yb), (96, -184 + yb)], ear_ang, (94, -192 + yb))))
    shade(L, L.mask(ear), '#ead2bd', lit='#fae6d2', shadow='#b9927e', light=lt, rim=rim, rim_w=rim_w, tex_amt=0.04, line=INK, line_w=1.3, line_a=0.5, poly=ear)
    inner = HX(catmull(_rot([(88, -192 + yb), (66, -191 + yb), (54, -182 + yb), (72, -181 + yb)], ear_ang, (94, -192 + yb))))
    L.put(hexc('#eba69c'), L.mask(inner, 1.5) * 0.85)
    bl = HX(ellipse_pts(146, -152 + yb, 11, 7)); L.put(hexc('#f29b8d'), L.mask(bl, 4.0) * 0.6)
    # big eye with sparkles
    ex, ey = 134 + look[0] * 3, -180 + yb + look[1] * 3
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    if bk > 0.15:
        eye = HX(ellipse_pts(ex, ey, 9, 12 * bk))
        shade(L, L.mask(eye, 0.4), '#2b1d1b', lit='#5a3f37', shadow='#1b1110', light=(0.4, 0.8), tex_amt=0.02, edge_dark=0)
        L.put(hexc('#6b4a3f'), L.mask(HX(ellipse_pts(ex, ey + 4 * bk, 6, 5 * bk)), 2) * 0.6)
        for (dx, dy, rr) in ((-2.5, -5 * bk, 3.4), (3, 4 * bk, 1.6)):
            L.put(np.array([1, 0.99, 0.95], np.float32), L.mask(HX(ellipse_pts(ex + dx, ey + dy, rr, rr)), 0.5))
        pencil(L, HX([(ex - 10, ey - 8 * bk), (ex - 3, ey - 13 * bk), (ex + 6, ey - 12 * bk), (ex + 11, ey - 6 * bk)]), '#2b1d1b', 2.2 * s, 0.85, lt, closed=False)
    else:
        lid = HX([(ex - 10, ey - 2), (ex - 4, ey - 7), (ex + 4, ey - 7), (ex + 10, ey - 2)]) if laugh > 0.5 else HX([(ex - 10, ey), (ex - 4, ey + 4), (ex + 4, ey + 4), (ex + 10, ey)])
        pencil(L, lid, '#2b1d1b', 2.4 * s, 0.9, lt, closed=False)
    pencil(L, HX([(ex - 10, ey - 22), (ex - 2, ey - 25), (ex + 8, ey - 22)]), '#9a7564', 1.6 * s, 0.55, lt, closed=False)
    nose = HX(ellipse_pts(166, -150 + yb, 4.5, 3.5)); L.put(hexc('#9b6a5c'), L.mask(nose, 0.6) * 0.9)
    if mouth == 'open' or laugh > 0.3:
        mo = HX(catmull([(146, -136 + yb), (162, -138 + yb), (158, -125 + yb), (149, -124 + yb)]))
        shade(L, L.mask(mo), '#9c4a45', lit='#c86a60', light=lt, tex_amt=0.02, edge_dark=0.2, line=INK, line_w=1.2, line_a=0.6, poly=mo)
        L.put(hexc('#e58c86'), L.mask(HX(ellipse_pts(153, -127 + yb, 4, 2.5)), 1) * 0.8)
    else:
        pencil(L, HX([(146, -138 + yb), (154, -133 + yb), (162, -138 + yb)]), '#6a4a3e', 1.6 * s, 0.85, lt, closed=False)
    LAST['mouth'] = HX([(156, -130 + yb)])[0]; LAST['head'] = HX([(130, -175 + yb)])[0]; LAST['tail'] = tc
    composite(frame, L)
    return L

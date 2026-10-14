# Props for the journey: the boy's telescope, the cardboard box (the lantern Pip rides in), the flock of birds on strings.
import numpy as np, math, cv2
from core import *
from props2 import bird

def _rot(pts, ang_deg, piv=(0, 0)):
    P = np.asarray(pts, np.float32).reshape(-1, 2) - piv; a = math.radians(ang_deg); c, s_ = math.cos(a), math.sin(a)
    return np.stack([P[:, 0] * c - P[:, 1] * s_, P[:, 0] * s_ + P[:, 1] * c], 1) + piv

def telescope(frame, x, y, s=1.0, light=(-0.5, -0.7), rim='#fff3d0', rim_w=0.4, ang=-26.0, flip=1):
    """A little brass telescope on a wooden tripod. (x, y) = feet. Returns the eyepiece point on screen."""
    pad = 30; L = Layer(x - 170 * s - pad, y - 330 * s - pad, 340 * s + 2 * pad, 340 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = np.asarray(pts, np.float32).reshape(-1, 2).copy(); P[:, 0] *= flip; return P * s + [x, y]
    def part(P, base, lit, sh, **kw):
        kw.setdefault('line', '#3a2616'); kw.setdefault('line_w', 1.3 * s); kw.setdefault('line_a', 0.7)
        shade(L, L.mask(P, 0.5), base, lit=lit, shadow=sh, light=lt, poly=P, rim=rim, rim_w=rim_w, **kw)
    head = (0, -200)
    for k, foot in enumerate(((-70, 0), (64, 2), (12, -22))):
        d = np.array(foot) - head; n_ = np.array([-d[1], d[0]]) / np.linalg.norm(d) * 4.5
        P = T([np.array(head) + n_, np.array(foot) + n_ * 0.7, np.array(foot) - n_ * 0.7, np.array(head) - n_])
        part(P, '#8a5a32' if k < 2 else '#6a4426', '#c08a58', '#4a2e18', soft=0.9, streak=2, tex_amt=0.15)
    part(T(ellipse_pts(0, -200, 12, 9)), '#6a5a48', '#a89070', '#3a2e22', spec=0.3)
    tube = _rot([(-90, -9), (60, -13), (60, 13), (-90, 9)], ang) + head
    part(T(tube), '#c9973a', '#ffe08a', '#7a5418', soft=0.8, spec=0.7, tex_amt=0.05)
    for xx, w_ in ((60, 16), (20, 14), (-40, 12)):   # brass rings
        part(T(_rot([(xx - 4, -w_), (xx + 4, -w_), (xx + 4, w_), (xx - 4, w_)], ang) + head), '#a8782a', '#f2d080', '#5a3c10', spec=0.6, line_a=0.4)
    lens = T(_rot(ellipse_pts(64, 0, 4, 13), ang) + head); part(lens, '#8fb6d8', '#eaf6ff', '#3a5670', spec=0.9, line_a=0.3)
    eye = T(_rot([(-96, 0)], ang) + head)[0]
    part(T(_rot([(-98, -6), (-88, -7), (-88, 7), (-98, 6)], ang) + head), '#2e2420', '#5a4a40', '#140e0a', line_a=0.4)
    composite(frame, L)
    return eye

def box(frame, x, y, s=1.0, light=(-0.5, -0.7), rim='#fff3d0', rim_w=0.4, glow_amt=0.0, t=0.0, handle=False, flip=1, tilt=0.0, grey=0.0):
    """The cardboard box with three air holes (from the first film). (x, y) = bottom centre. glow_amt: Pip's light inside.
    handle: a string loop on top for carrying; returns its top point on screen (or None)."""
    pad = 40; L = Layer(x - 120 * s - pad, y - 230 * s - pad, 240 * s + 2 * pad, 250 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = _rot(pts, tilt, (0, -50)); P[:, 0] *= flip; return P * s + [x, y]
    CB, CB_L, CB_S = '#c8965a', '#ecc488', '#7e5630'
    def part(P, base=CB, lit=CB_L, sh=CB_S, **kw):
        kw.setdefault('line', '#4a3018'); kw.setdefault('line_w', 1.4 * s); kw.setdefault('line_a', 0.75)
        shade(L, L.mask(P, 0.5), base, lit=lit, shadow=sh, light=lt, poly=P, rim=rim, rim_w=rim_w, **kw)
    g = glow_amt; gc = '#ffd060' if grey < 0.5 else '#d8d4c8'
    # back flap standing up, and the dark (or glowing) inside
    part(T([(-30, -106), (62, -106), (70, -152), (-22, -150)]), '#b4844c', '#dcb078', '#6e4a28', soft=0.25, tex_amt=0.2, streak=1)
    inside = T([(-58, -86), (36, -86), (64, -106), (-30, -106)])
    ic = mix(hexc('#3a2614'), hexc('#ffe7a0' if grey < 0.5 else '#e8e4dc'), min(1, g * 1.1))
    L.put(ic, L.mask(inside, 0.8))
    # side and front faces
    part(T([(36, -86), (64, -106), (64, -22), (36, 0)]), '#b07a42', '#d8a46a', '#6a4422', soft=0.3, tex_amt=0.2, streak=1)
    part(T([(-58, -86), (36, -86), (36, 0), (-58, 0)]), soft=0.3, tex_amt=0.22, streak=1, ao=0.15)
    stroke(L, T([(-58, -44), (36, -44)]), '#a8783e', 1.6 * s, 0.35, taper=False)   # tape line
    holes = [(-34, -58), (-8, -36), (14, -62)]
    for hx, hy in holes:
        H = T(ellipse_pts(hx, hy, 6.5, 6.5)); L.put(mix(hexc('#2a1a0c'), hexc('#fff2b8' if grey < 0.5 else '#eeeae2'), min(1, g * 1.3)), L.mask(H, 0.5))
        pencil(L, H, '#4a3018', 1.0 * s, 0.6, lt)
    # front flap folded down, left flap tipped out
    part(T([(-58, -86), (36, -86), (46, -120), (-48, -122)]), '#d4a468', '#f2cc94', '#8a6034', soft=0.25, tex_amt=0.2, streak=1, line_a=0.6)
    part(T([(-58, -86), (-30, -106), (-80, -132), (-100, -108)]), '#c08c50', '#e6ba80', '#76502c', soft=0.25, tex_amt=0.2, streak=1)
    top = None
    if handle:
        a, b = T([(-20, -100)])[0], T([(30, -100)])[0]; top = T([(5, -168)])[0]
        for p_ in (a, b): stroke(L, np.array([p_, (p_ + top) / 2 + [0, -6 * s], top]), '#e8dcc0', 2.0 * s, 0.9, taper=False)
    composite(frame, L)
    if g > 0.02:   # light pouring out of the holes and the open top
        for hx, hy in holes:
            p_ = T([(hx, hy)])[0]; glow(frame, p_[0], p_[1], 9 * s, gc, 0.7 * g)
        p_ = T([(4, -100)])[0]; glow(frame, p_[0], p_[1] - 20 * s, 60 * s, gc, 0.35 * g)
    return top

class Flock:
    """Migratory birds on strings: they circle loosely around a centre and pull the strings taut."""
    def __init__(self, n=11, seed=3, spread=(260, 120)):
        r = np.random.default_rng(seed)
        self.b = [dict(ph=r.random() * 6.28, sp=0.5 + r.random() * 0.4, ox=(r.random() * 2 - 1) * spread[0], oy=(r.random() * 2 - 1) * spread[1],
                       fp=r.random() * 6.28, sz=0.85 + r.random() * 0.3, tgt=k % 3) for k in range(n)]
    def positions(self, t, cx, cy, z, spread=1.0, panic=0.0):
        out = []
        for b in self.b:
            j = panic * 30 * math.sin(t * 7.1 + b['ph'] * 3)
            x = cx + (b['ox'] * spread + 40 * math.sin(t * b['sp'] + b['ph']) + j) * z
            y = cy + (b['oy'] * spread + 22 * math.sin(t * b['sp'] * 1.3 + b['ph'] * 2) + j * 0.6 * math.cos(t * 5.3 + b['ph'])) * z
            out.append((x, y, b))
        return out
    def draw(self, f, t, cx, cy, z, anchors=(), light=(-0.5, -0.7), flip=1, string_col=(0.93, 0.9, 0.82), arrive=1.0, spread=1.0, panic=0.0):
        """anchors: screen points the strings are tied to (hands, the sheep's harness). arrive 0..1 fades strings in."""
        P = self.positions(t, cx, cy, z, spread, panic)
        if anchors and arrive > 0:
            for (x, y, b) in P:
                ax, ay = anchors[b['tgt'] % len(anchors)]
                mid = ((x + ax) / 2 + 6 * z * math.sin(t * 2 + b['ph']), (y + ay) / 2 + 10 * z)
                pts = catmull([(x, y + 4 * z), mid, (ax, ay)], closed=False, n=8)
                stroke_frame(f, pts, string_col, max(1.0, 1.1 * z), 0.75 * arrive)
        for (x, y, b) in P:
            bird(f, x, y, 0.8 * z * b['sz'], t * b['sp'] * 1.6 + b['fp'], flip=flip, phase=b['fp'], light=light)
        return P

def stroke_frame(f, pts, col, w, a):
    """A thin antialiased line drawn straight on the frame."""
    P = np.asarray(pts, np.float32)
    x0, y0 = np.floor(P.min(0) - w - 2).astype(int); x1, y1 = np.ceil(P.max(0) + w + 2).astype(int)
    x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(f.shape[1], x1), min(f.shape[0], y1)
    if x1 <= x0 or y1 <= y0: return
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    q = ((P - [x0, y0]) * 16).astype(np.int32)
    cv2.polylines(m, [q], False, 1.0, max(1, int(round(w))), cv2.LINE_AA, shift=4)
    m = m[..., None] * a
    f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - m) + np.array(col, np.float32) * m

def space_rock(frame, x, y, s=1.0, light=(-0.6, -0.5), rim='#a8b8ff', rim_w=0.5, seed=0, w=420, depth=330):
    """A small floating rock to sit on. (x, y) = middle of its flat-ish top."""
    r = np.random.default_rng(seed)
    pad = 40; L = Layer(x - (w + 60) * s - pad, y - 60 * s - pad, (2 * w + 120) * s + 2 * pad, (depth + 120) * s + 2 * pad)
    def T(pts): return np.asarray(pts, np.float32).reshape(-1, 2) * s + [x, y]
    top = [(-w + 30, 10), (-w * 0.6, -8), (-w * 0.2, -2), (w * 0.15, -10), (w * 0.55, -4), (w - 20, 12)]
    bot = [(w + 20, 70), (w * 0.8, depth * 0.55), (w * 0.4, depth * 0.9), (0, depth), (-w * 0.45, depth * 0.85), (-w * 0.85, depth * 0.5), (-w - 30, 80)]
    P = T(catmull(top + bot, closed=True, n=6))
    shade(L, L.mask(P, 0.8), '#5a5266', lit='#968ea8', shadow='#221c2c', light=light, soft=0.5, tex_amt=0.25, streak=1, poly=P,
          line='#1a1420', line_w=1.5 * s, line_a=0.6, rim=rim, rim_w=rim_w, ao=0.2)
    Tp = T(catmull(top + [(w - 40, 40), (0, 46), (-w + 50, 38)], closed=True, n=6))   # the lit top face
    shade(L, L.mask(Tp, 1.5), '#7a7288', lit='#aaa2bc', shadow='#4a4258', light=(0.0, -1.0), soft=0.8, tex_amt=0.2, weave=0.02)
    for k in range(7):
        cx, cy = r.uniform(-w * 0.7, w * 0.7), r.uniform(70, depth * 0.7); rr = r.uniform(16, 40)
        C = T(ellipse_pts(cx, cy, rr, rr * 0.7)); L.put(hexc('#2e2838'), L.mask(C, 1.5) * 0.7)
        stroke(L, T(catmull([(cx - rr * 0.9, cy + rr * 0.1), (cx, cy + rr * 0.75), (cx + rr * 0.9, cy + rr * 0.1)], closed=False, n=5)), '#a49cb4', 2.0 * s, 0.5)
    for k in range(5):
        cx = r.uniform(-w * 0.6, w * 0.6); C = T(ellipse_pts(cx, r.uniform(8, 26), r.uniform(10, 22), 5)); L.put(hexc('#4a4258'), L.mask(C, 1) * 0.6)
    composite(frame, L)

def meteor(frame, x, y, r, ang, seed=0, light=(-0.6, -0.5), rim='#ffb08a', rim_w=0.6, dim=0.0, blur=0.0, hot=0.0):
    """A tumbling space rock. r: its radius on screen. ang: spin (radians). hot: a glowing ember edge."""
    rg = np.random.default_rng(seed)
    n = 13; rad = 1 + 0.22 * (rg.random(n) - 0.5) + 0.12 * np.sin(np.arange(n) * 2.1 + seed)
    pad = 20 + blur * 2; L = Layer(x - r * 1.4 - pad, y - r * 1.4 - pad, r * 2.8 + 2 * pad, r * 2.8 + 2 * pad)
    pts = [(math.cos(ang + k / n * 6.283) * r * rad[k], math.sin(ang + k / n * 6.283) * r * rad[k] * 0.86) for k in range(n)]
    P = np.asarray(catmull(pts, closed=True, n=4), np.float32) + [x, y]
    shade(L, L.mask(P, 0.8), '#4e4650', lit='#8a7e86', shadow='#1a1418', light=light, soft=0.55, tex_amt=0.3, streak=1, poly=P,
          line='#120c10', line_w=max(1.0, r * 0.02), line_a=0.5, rim=rim, rim_w=rim_w, ao=0.2)
    for k in range(4):
        a = ang + rg.random() * 6.283; d = rg.random() * 0.55 * r; cr = (0.1 + rg.random() * 0.14) * r
        cx, cy = x + math.cos(a) * d, y + math.sin(a) * d * 0.86
        L.put(hexc('#241c22'), L.mask(ellipse_pts(cx, cy, cr, cr * 0.75, rot=ang), 1.0) * 0.6)
        stroke(L, np.array([(cx - cr * 0.8, cy + cr * 0.3), (cx, cy + cr * 0.75), (cx + cr * 0.8, cy + cr * 0.3)], np.float32), '#a0949a', max(1.0, r * 0.025), 0.45)
    if dim > 0: L.rgb *= (1 - 0.8 * dim)
    if blur > 0.5:
        k = int(blur) * 2 + 1; pa = cv2.GaussianBlur(L.rgb * L.a[..., None], (k, k), 0); L.a = cv2.GaussianBlur(L.a, (k, k), 0); L.rgb = pa / np.maximum(L.a, 1e-4)[..., None]
    composite(frame, L)
    if hot > 0: glow(frame, x - r * 0.3, y - r * 0.2, r * 1.3, '#ff9a5a', 0.25 * hot)

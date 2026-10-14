# Painting engine: everything drawn in code. Float RGB canvases, soft "pillow" shading from distance fields,
# painterly texture from noise, watercolor edges, pencil lines, glow, paper.
import numpy as np, cv2, math
W, H = 1920, 804
RNG = np.random.default_rng(7)

def _vnoise(n, cells, seed):
    r = np.random.default_rng(seed).random((cells, cells)).astype(np.float32)
    r = np.tile(r, (3, 3))
    big = cv2.resize(r, (n * 3, n * 3), interpolation=cv2.INTER_CUBIC)
    return big[n:2 * n, n:2 * n]

def fbm_tex(n=1024, base=4, oct=6, seed=1, gain=0.55):
    t = np.zeros((n, n), np.float32); a = 1.0; s = 0.0
    for o in range(oct):
        t += a * _vnoise(n, base * 2 ** o, seed + o * 17); s += a; a *= gain
    t /= s; t = (t - t.mean()) / (t.std() + 1e-6)
    return t

NOISE = [fbm_tex(1024, 4, 6, s) for s in (1, 2, 3)]      # large-scale, normalised ~N(0,1)
FINE = fbm_tex(1024, 64, 3, 9, 0.6)                       # granulation
def streak_tex(angle_deg, seed=5):
    n = 1024; r = np.random.default_rng(seed).random((n, n)).astype(np.float32)
    k = np.zeros((41, 41), np.float32); c = 20
    a = math.radians(angle_deg); dx, dy = math.cos(a), math.sin(a)
    for i in range(-20, 21): k[int(round(c + dy * i)), int(round(c + dx * i))] = 1
    k /= k.sum(); s = cv2.filter2D(r, -1, k, borderType=cv2.BORDER_WRAP)
    return (s - s.mean()) / (s.std() + 1e-6)
STREAK = [streak_tex(a, 11 + i) for i, a in enumerate((0, 45, 90, 135))]
def _weave(n=1024, k=0.62):
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    w = np.sin((xx + yy) * k) * np.sin((xx - yy) * k)
    j = cv2.resize(np.random.default_rng(3).random((n // 3, n // 3)).astype(np.float32), (n, n))
    return (w * (0.6 + 0.8 * j)).astype(np.float32)
WEAVE = _weave()

def tex(t, x0, y0, w, h, scale=1.0):
    """Sample a tileable texture over a box (world-anchored by x0,y0) at a given scale."""
    n = t.shape[0]
    xs = ((np.arange(w) + x0) / scale).astype(np.int64) % n
    ys = ((np.arange(h) + y0) / scale).astype(np.int64) % n
    return t[np.ix_(ys, xs)]

def paper(w=W, h=H):
    p = 0.5 * tex(NOISE[2], 0, 0, w, h, 0.6) + 0.35 * tex(FINE, 0, 0, w, h, 0.5) + 0.25 * tex(STREAK[0], 0, 0, w, h, 1)
    return p

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)

def mix(a, b, t): return a + (b - a) * t
def ss(u): u = np.clip(u, 0, 1); return u * u * (3 - 2 * u)

# ---------------------------------------------------------------- shapes
def catmull(pts, closed=True, n=10):
    P = np.asarray(pts, np.float32); m = len(P); out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = P[(i - 1) % m] if closed or i > 0 else P[i]
        p1 = P[i]; p2 = P[(i + 1) % m]
        p3 = P[(i + 2) % m] if closed or i + 2 < m else P[(i + 1) % m]
        t = np.linspace(0, 1, n, endpoint=False)[:, None]
        t2, t3 = t * t, t * t * t
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed: out.append(P[-1:])
    return np.concatenate(out)

def ellipse_pts(cx, cy, rx, ry, rot=0, n=48):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False); c, s = math.cos(rot), math.sin(rot)
    x, y = rx * np.cos(a), ry * np.sin(a)
    return np.stack([cx + x * c - y * s, cy + x * s + y * c], 1)

def _over(L, sl, col, m):
    """Straight-alpha 'over' so soft edges never pick up black from empty pixels."""
    a0 = L.a[sl]; na = a0 + m * (1 - a0)
    w0 = (a0 * (1 - m) / np.maximum(na, 1e-5))[..., None]
    L.rgb[sl] = L.rgb[sl] * w0 + col * (1 - w0)
    L.a[sl] = na

class Layer:
    """A local float canvas covering a bounding box, for one character/prop. All painting works in small windows."""
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0, self.w, self.h = int(x0), int(y0), int(w), int(h)
        self.rgb = np.zeros((self.h, self.w, 3), np.float32); self.a = np.zeros((self.h, self.w), np.float32)
        self.cov = np.zeros((self.h, self.w), np.float32)
    def box(self, pts, pad):
        P = np.asarray(pts, np.float32)
        x0 = int(max(0, math.floor(P[:, 0].min() - self.x0 - pad))); x1 = int(min(self.w, math.ceil(P[:, 0].max() - self.x0 + pad)))
        y0 = int(max(0, math.floor(P[:, 1].min() - self.y0 - pad))); y1 = int(min(self.h, math.ceil(P[:, 1].max() - self.y0 + pad)))
        return x0, y0, x1, y1
    def mask(self, poly, blur=0.0, pad=8):
        """Returns a Mask (window + array) for a polygon."""
        x0, y0, x1, y1 = self.box(poly, pad + 3 * blur)
        if x1 <= x0 or y1 <= y0: return Mask(0, 0, 0, 0, np.zeros((0, 0), np.float32))
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        p = ((np.asarray(poly) - [self.x0 + x0, self.y0 + y0]) * 16).astype(np.int32)
        cv2.fillPoly(m, [p], 255, cv2.LINE_AA, shift=4)
        m = m.astype(np.float32) / 255
        if blur > 0: m = cv2.GaussianBlur(m, (0, 0), blur)
        return Mask(x0, y0, x1, y1, m)
    def put(self, col, m):
        if m.m.size == 0: return
        _over(self, m.sl, col, m.m)

class Mask:
    def __init__(self, x0, y0, x1, y1, m):
        self.x0, self.y0, self.x1, self.y1, self.m = x0, y0, x1, y1, m
        self.sl = (slice(y0, y1), slice(x0, x1))
    def __mul__(self, k): return Mask(self.x0, self.y0, self.x1, self.y1, self.m * k)
    __rmul__ = __mul__

def height_field(m, soft=0.5):
    mb = (m > 0.5).astype(np.uint8)
    if mb.sum() == 0: return np.zeros_like(m), 1.0
    d = cv2.distanceTransform(mb, cv2.DIST_L2, 5)
    dm = d.max() + 1e-6
    h = np.sqrt(np.clip(1 - (1 - np.clip(d / (dm * soft + 1e-6), 0, 1)) ** 2, 0, 1))
    h = cv2.GaussianBlur(h, (0, 0), max(1.0, dm * 0.08))
    return h, dm

def shade(L, M, base, *, light=(-0.55, -0.7), lit=None, shadow=None, rim=None, rim_w=0.0, spec=0.0,
          soft=0.6, bump=None, bump_amt=0.0, tex_amt=0.06, streak=None, edge_dark=0.18, line=None, line_w=1.6,
          line_a=0.65, gx=0, gy=0, poly=None, ao=0.0, glow_in=None, weave=0.045, streak_amt=0.35):
    """Paint one part: base colour shaded like a soft 3D form, with brush texture, edge pigment and pencil line."""
    if M.m.size == 0: return None
    m = M.m; h_, w_ = m.shape
    base = hexc(base) if isinstance(base, str) else base
    lit = hexc(lit) if isinstance(lit, str) else (base * 1.12 + 0.04 if lit is None else lit)
    shadow = hexc(shadow) if isinstance(shadow, str) else (base * np.array([0.62, 0.6, 0.75]) if shadow is None else shadow)
    hh, dm = height_field(m, soft)
    if bump is not None: hh = hh + bump[M.sl] * bump_amt
    gyy, gxx = np.gradient(hh * dm * 0.9)
    nrm = np.sqrt(gxx ** 2 + gyy ** 2 + 1)
    nx, ny, nz = -gxx / nrm, -gyy / nrm, 1 / nrm
    lx, ly = light; lz = 0.55; ln = math.sqrt(lx * lx + ly * ly + lz * lz); lx, ly, lz = lx / ln, ly / ln, lz / ln
    lam = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    t = ss((lam - 0.25) / 0.6)
    col = shadow * (1 - t[..., None]) + lit * t[..., None]
    mid = np.exp(-((lam - 0.45) ** 2) / 0.02)[..., None]
    col = col * (1 - 0.25 * mid) + base * 0.25 * mid
    X0, Y0 = L.x0 + M.x0 + gx, L.y0 + M.y0 + gy
    n = tex(NOISE[0], X0, Y0, w_, h_, 0.7) * 0.6 + tex(NOISE[1], X0, Y0, w_, h_, 0.25) * 0.4
    if streak is not None: n = n * 0.6 + tex(STREAK[streak], X0, Y0, w_, h_, 0.8) * streak_amt
    col = col * (1 + tex_amt * n[..., None])
    col = col * (1 - 0.05 * np.clip(tex(FINE, X0, Y0, w_, h_, 0.6), 0, 3)[..., None])
    if weave: col = col * (1 + weave * tex(WEAVE, X0, Y0, w_, h_, 1.0)[..., None])
    if ao > 0:
        cv_ = L.cov[M.sl]
        if cv_.any():
            occ = cv2.GaussianBlur(cv_, (0, 0), 6) * ao
            col = col * (1 - occ[..., None] * np.array([0.5, 0.55, 0.45]))
    if rim is not None and rim_w > 0:
        rimc = hexc(rim) if isinstance(rim, str) else rim
        edge = np.clip(1 - hh / 0.35, 0, 1) * np.clip(nx * lx + ny * ly, 0, 1)
        col = col + (rimc - col) * (edge * rim_w)[..., None]
    if spec > 0:
        hx, hy, hz = lx, ly, lz + 1; hn = math.sqrt(hx * hx + hy * hy + hz * hz)
        sp = np.clip(nx * hx / hn + ny * hy / hn + nz * hz / hn, 0, 1) ** 40
        col = col + spec * sp[..., None]
    if glow_in is not None:
        col = col + hexc(glow_in) * (hh ** 1.5)[..., None] * 0.6
    if edge_dark > 0:
        e = np.clip(m - cv2.GaussianBlur(m, (0, 0), 2.2), 0, 1) * 2
        col = col * (1 - edge_dark * e[..., None])
    sl = M.sl
    _over(L, sl, col, m)
    L.cov[sl] = np.maximum(L.cov[sl], m)
    if line is not None and poly is not None:
        pencil(L, poly, line, line_w, line_a, light)
    return hh

def _line_mask(L, P, widths, blur, closed):
    x0, y0, x1, y1 = L.box(P, max(widths) + 4)
    if x1 <= x0 or y1 <= y0: return None
    m = np.zeros((y1 - y0, x1 - x0), np.float32); Q = (P - [L.x0 + x0, L.y0 + y0]) * 16
    for i in range(len(Q) - 1):
        if widths[i] <= 0: continue
        cv2.line(m, tuple(Q[i].astype(int)), tuple(Q[i + 1].astype(int)), 1.0, max(1, int(round(widths[i]))), cv2.LINE_AA, shift=4)
    if blur: m = cv2.GaussianBlur(m, (0, 0), blur)
    return Mask(x0, y0, x1, y1, np.clip(m, 0, 1))

def pencil(L, poly, color, w=1.6, a=0.65, light=(-0.55, -0.7), closed=True, seed=0):
    col = hexc(color) if isinstance(color, str) else np.asarray(color, np.float32)
    P = np.asarray(poly, np.float32)
    if closed: P = np.concatenate([P, P[:1]])
    if len(P) < 2: return
    seg = np.diff(P, axis=0); nrm = np.stack([-seg[:, 1], seg[:, 0]], 1); nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6)
    facing = np.clip(-(nrm[:, 0] * light[0] + nrm[:, 1] * light[1]), -1, 1)
    gaps = np.random.default_rng(seed).random(len(seg)) < 0.03
    widths = np.where(gaps, 0, w * (0.55 + 0.6 * (0.5 + 0.5 * facing)))
    M = _line_mask(L, P, widths, 0.6, closed)
    if M is None: return
    m = M.m * a; sl = M.sl
    a0 = L.a[sl]; mm = m * np.clip(a0 * 1.5, 0, 1)   # pencil only where there is paint
    L.rgb[sl] = L.rgb[sl] * (1 - mm[..., None]) + col * mm[..., None]

def stroke(L, pts, color, w, a=1.0, blur=0.6, taper=True):
    col = hexc(color) if isinstance(color, str) else np.asarray(color, np.float32)
    P = np.asarray(pts, np.float32); n = len(P)
    if n < 2: return
    widths = [w * (math.sin(math.pi * min(1, (i / max(1, n - 2)) * 1.2 + 0.1)) if taper else 1) for i in range(n - 1)]
    M = _line_mask(L, P, widths, blur, False)
    if M is None: return
    m = M.m * a
    _over(L, M.sl, col, m)

# Scene lighting applied to every painted character as it lands in the frame (set per shot / per character):
#   tint: overall colour of the light; fill: colour the shadows pick up from the sky; bounce: light from the ground;
#   sun: screen position of the sun (back-light rim on the edges facing it); foot_y/height: where the character
#   stands and how tall it is on screen (for bounce light and the long cast shadow); cast: shadow strength.
ENV = {}

def _shift(a, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(a, M, (a.shape[1], a.shape[0]), borderMode=cv2.BORDER_CONSTANT)

def composite(frame, L, op=1.0):
    x0, y0 = L.x0, L.y0; x1, y1 = x0 + L.w, y0 + L.h
    cx0, cy0, cx1, cy1 = max(0, x0), max(0, y0), min(frame.shape[1], x1), min(frame.shape[0], y1)
    if cx1 <= cx0 or cy1 <= cy0: return
    E = ENV
    if E.get('cast', 0) > 0 and 'foot_y' in E:
        # long evening shadow: the silhouette laid down on the ground, away from the sun, softer with distance
        fy = E['foot_y']; shx, sq = E.get('shear', (0.9, 0.18))
        M = np.float32([[1, shx, x0 + shx * y0 - shx * fy], [0, -sq, (1 + sq) * fy - sq * y0]])
        sh = cv2.warpAffine(L.a, M, (frame.shape[1], frame.shape[0]), flags=cv2.INTER_LINEAR)
        sh = cv2.GaussianBlur(sh, (0, 0), max(1.5, E.get('height', 300) * 0.012))
        col = np.array(E.get('shadow_col', (0.42, 0.33, 0.52)), np.float32)
        frame *= 1 - (sh * E['cast'])[..., None] * (1 - col)
    a = (L.a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * op)
    rgb = L.rgb[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
    if E:
        rgb = rgb * np.array(E.get('tint', (1, 1, 1)), np.float32)
        lum = rgb.mean(axis=2, keepdims=True)
        fill = np.array(E.get('fill', (0, 0, 0)), np.float32)
        rgb = rgb + fill * np.clip(0.75 - lum, 0, 1) ** 1.5
        if 'foot_y' in E:
            yy = np.arange(cy0, cy1, dtype=np.float32)[:, None, None]
            hgt = E.get('height', 300); bw = np.clip((yy - (E['foot_y'] - hgt * 0.4)) / (hgt * 0.4), 0, 1) ** 1.5
            rgb = rgb + np.array(E.get('bounce', (0, 0, 0)), np.float32) * bw
        if 'sun' in E:
            sx, sy = E['sun']; mx, my = (cx0 + cx1) / 2, (cy0 + cy1) / 2
            dx, dy = sx - mx, sy - my; dn = math.hypot(dx, dy) + 1e-6
            d = E.get('rim_px', 5.0)
            inner = _shift(a, -dx / dn * d, -dy / dn * d)
            rim = np.clip(a - inner, 0, 1); rim = cv2.GaussianBlur(rim, (0, 0), 1.2) * a
            rgb = rgb + np.array(E.get('rim_col', (1.0, 0.85, 0.6)), np.float32) * (rim * E.get('rim', 0.6))[..., None]
    a = a[..., None]
    frame[cy0:cy1, cx0:cx1] = frame[cy0:cy1, cx0:cx1] * (1 - a) + rgb * a

def glow(frame, x, y, r, color, amt=1.0):
    h, w = frame.shape[:2]; x0, x1 = int(max(0, x - 7 * r)), int(min(w, x + 7 * r)); y0, y1 = int(max(0, y - 7 * r)), int(min(h, y + 7 * r))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]; d2 = ((xx - x) ** 2 + (yy - y) ** 2) / (r * r)
    g = (np.exp(-d2 * 1.2) * 0.8 + np.exp(-d2 * 0.18) * 0.35) * amt
    c = hexc(color) if isinstance(color, str) else color
    frame[y0:y1, x0:x1] = 1 - (1 - frame[y0:y1, x0:x1]) * (1 - np.clip(g[..., None] * c, 0, 1))

def finish(frame, pap=None, vign=0.35, grain_seed=0, bloom=0.35):
    f = np.clip(frame, 0, 1.5)
    if bloom > 0:
        hi = np.clip(f - 0.72, 0, None)
        small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
        b = cv2.GaussianBlur(small, (0, 0), 6) + cv2.GaussianBlur(small, (0, 0), 18) * 0.6
        f = f + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * bloom
    if pap is not None: f = f * (1 + 0.035 * pap[..., None]) 
    yy, xx = np.mgrid[0:H, 0:W]; d = ((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2
    f = f * (1 - vign * np.clip(d - 0.25, 0, 1)[..., None])
    g = np.random.default_rng(grain_seed).normal(0, 0.012, (H // 2, W // 2)).astype(np.float32)
    f = f + cv2.resize(g, (W, H))[..., None]
    f = np.clip(f, 0, 1)
    return (f[..., ::-1] * 255 + 0.5).astype(np.uint8)   # BGR for cv2

def puff(L, cx, cy, r, base, lit, shadow, light=(-0.55, -0.7), soft=0.35, ao=0.35, rim=None, rim_w=0.0, gx=0, gy=0, alpha=1.0):
    """A soft painted ball (wool, cloud, foliage): contact shadow under it, then a lit sphere with soft edges."""
    base, lit, shadow = [hexc(c) if isinstance(c, str) else c for c in (base, lit, shadow)]
    lx, ly = light; ln = math.hypot(lx, ly) + 1e-6; lx, ly = lx / ln, ly / ln
    R = r * 1.5; x0, x1 = int(max(0, cx - R - L.x0)), int(min(L.w, cx + R - L.x0 + 1)); y0, y1 = int(max(0, cy - R - L.y0)), int(min(L.h, cy + R - L.y0 + 1))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); xx += L.x0; yy += L.y0
    # wobbly edge from noise so puffs aren't perfect circles
    wob = tex(NOISE[1], int(L.x0 + x0 + gx), int(L.y0 + y0 + gy), x1 - x0, y1 - y0, 0.35) * 0.08 * r
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) + wob
    # contact shadow (ambient occlusion) pushed away from the light
    if ao > 0:
        ds = np.sqrt((xx - cx + lx * r * 0.25) ** 2 + (yy - cy + ly * r * 0.25) ** 2)
        sh = np.clip(1 - (ds - r * 0.9) / (r * 0.45), 0, 1) ** 2 * ao * alpha
        sh = sh * L.a[y0:y1, x0:x1]
        L.rgb[y0:y1, x0:x1] = L.rgb[y0:y1, x0:x1] * (1 - sh[..., None] * (1 - shadow * 0.8))
    m = np.clip((r - d) / (r * soft * 0.35 + 0.8), 0, 1) * alpha
    # sphere shading
    u = (xx - cx) / r; v = (yy - cy) / r; w2 = np.clip(1 - u * u - v * v, 0, 1); w = np.sqrt(w2)
    lam = np.clip(-(u * lx + v * ly) * 0.75 + w * 0.55, 0, 1)
    t = ss((lam - 0.15) / 0.7)[..., None]
    col = shadow * (1 - t) + lit * t
    col = col * 0.85 + base * 0.15
    n = tex(NOISE[0], int(L.x0 + x0 + gx), int(L.y0 + y0 + gy), x1 - x0, y1 - y0, 0.5)
    col = col * (1 + 0.035 * n[..., None])
    if rim is not None and rim_w > 0:
        rimc = hexc(rim) if isinstance(rim, str) else rim
        edge = np.clip((d / r - 0.72) / 0.28, 0, 1) * np.clip(-(u * lx + v * ly), 0, 1)
        col = col + (rimc - col) * (edge * rim_w)[..., None]
    _over(L, (slice(y0, y1), slice(x0, x1)), col, m)
    L.cov[y0:y1, x0:x1] = np.maximum(L.cov[y0:y1, x0:x1], m)

def ground_shadow(frame, x, y, rx, ry, amt=0.35, color=(0.35, 0.25, 0.35)):
    x0, x1 = int(max(0, x - rx * 1.6)), int(min(W, x + rx * 1.6)); y0, y1 = int(max(0, y - ry * 1.6)), int(min(H, y + ry * 1.6))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]; d = ((xx - x) / rx) ** 2 + ((yy - y) / ry) ** 2
    s = np.exp(-d * 1.6) * amt
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - s[..., None] * (1 - np.array(color, np.float32)))

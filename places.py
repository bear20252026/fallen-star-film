# Painted places other than B612. Each painter returns the same layers as bg.paint_b612(layers=True):
# (sky, [(cloud_rgb, cloud_a) x2], ground_rgb, ground_a, ground_y(x), light_source)
import numpy as np, math, cv2
from core import *
from bg import WW, WH, vgrad, soft_noise, cloud_layer

def _stars(img, n, ymax, seed, bright=1.0, big=0.04):
    r = np.random.default_rng(seed)
    for k in range(n):
        x, y = r.random() * WW, r.random() ** 1.6 * ymax
        a = (1 - 0.7 * y / ymax) * (0.35 + 0.65 * r.random()) * bright
        c = np.array([1, 0.96, 0.88]) if r.random() < 0.7 else np.array([0.85, 0.9, 1.0])
        rad = 2 if r.random() < big else 1
        cv2.circle(img, (int(x * 4), int(y * 4)), rad * 4 // 2 + 1, tuple((c * (0.5 + 0.5 * a)).tolist()), -1, cv2.LINE_AA, shift=2)
        if rad == 2:
            g = np.zeros((9, 9), np.float32); g[4, 4] = 1; g = cv2.GaussianBlur(g, (0, 0), 1.6); g /= g.max()
            x0, y0 = int(x) - 4, int(y) - 4
            if 0 <= x0 and x0 + 9 < WW and 0 <= y0 and y0 + 9 < WH: img[y0:y0 + 9, x0:x0 + 9] += g[..., None] * c * 0.35 * a

def _milky(img, seed, amt=0.22, angle=-0.35, y_mid=330, width=200, col='#c9c4ff'):
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    d = (yy - y_mid) * math.cos(angle) - (xx - WW / 2) * math.sin(angle)
    band = np.exp(-(d / width) ** 2)
    n = soft_noise(WW, WH, 90, seed) * 0.5 + soft_noise(WW, WH, 30, seed + 1) * 0.3
    m = np.clip(band * (0.6 + 0.5 * n), 0, 1.3) * amt
    img += m[..., None] * hexc(col)
    r = np.random.default_rng(seed + 9)   # dense small stars inside the band
    for k in range(1600):
        x = r.random() * WW; dd = (r.random() - 0.5) * width * 1.6
        y = y_mid + (x - WW / 2) * math.tan(angle) + dd / math.cos(angle)
        if 0 <= y < WH:
            a = 0.25 + 0.5 * r.random() * math.exp(-(dd / width) ** 2)
            cv2.circle(img, (int(x * 4), int(y * 4)), 2, (a, a * 0.97, a * 0.92), -1, cv2.LINE_AA, shift=2)

def desert_gy(x):
    return 842 + 26 * math.sin((x - 300) / 640) + 12 * math.sin(x / 270 + 1.3)

def paint_desert(tod='night', seed=0, quick=False):
    moon = (620, 210)
    if quick: return None, None, None, None, desert_gy, moon
    img = vgrad([(0, '#070b22'), (0.3, '#121a44'), (0.55, '#24306a'), (0.68, '#3a4580'), (0.74, '#56609a')])
    _milky(img, seed + 3)
    _stars(img, 1500, 760, seed + 4, big=0.05)
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    d = np.sqrt((xx - moon[0]) ** 2 + (yy - moon[1]) ** 2)
    img += np.exp(-d / 260)[..., None] * hexc('#9fb2ff') * 0.12
    # the crescent moon
    m1 = np.clip(1 - (d - 34), 0, 1); d2 = np.sqrt((xx - moon[0] - 14) ** 2 + (yy - moon[1] + 8) ** 2); m2 = np.clip(1 - (d2 - 30), 0, 1)
    cres = np.clip(m1 - m2, 0, 1)[..., None]; img = img * (1 - cres) + hexc('#fff6dc') * cres
    img += np.exp(-d / 60)[..., None] * hexc('#e8eeff') * 0.12
    zero = np.zeros((WH, WW, 1), np.float32)
    CL = [cloud_layer(img, [(2200, 260, 700, 40), (300, 420, 500, 30)], moon, '#1a2350', '#2a3566', '#4a5a90', '#7a88c0', 31, layer=True),
          (np.zeros_like(img), zero.copy())]
    CL[0] = (CL[0][0], CL[0][1] * 0.45)
    sky = img.copy()
    # dunes: far, middle and near ridges in cool moonlit sand
    ground = np.zeros((WH, WW), np.float32); g = img.copy()
    layers = [(lambda x: 790 + 22 * math.sin(x / 420 + 0.4) + 10 * math.sin(x / 150), '#3d4270', '#6e6e98', 0.75),
              (lambda x: 812 + 30 * math.sin(x / 520 + 2.0) + 8 * math.sin(x / 190 + 1), '#504c78', '#8a82a6', 0.85),
              (desert_gy, '#625a7e', '#a99cb4', 1.0)]
    for (fn, dark, lit, k) in layers:
        top = np.array([fn(x) for x in range(WW)], np.float32)
        m = np.clip(yy - top[None, :] + 0.5, 0, 1)
        slope = np.gradient(top)[None, :]
        lam = np.clip(0.5 - slope * 0.08 * (1 if moon[0] < WW / 2 else -1), 0, 1)   # faces toward the moon are lit
        depth = np.clip((yy - top[None, :]) / 260, 0, 1)
        c = mix(hexc(dark), hexc(lit), (lam * (1 - depth * 0.8))[..., None])
        c = c * (1 + 0.06 * soft_noise(WW, WH, 60, 11)[..., None]) * (1 + 0.05 * tex(STREAK[1], 0, 0, WW, WH, 1)[..., None])
        ridge = np.exp(-np.maximum(0, yy - top[None, :]) / 3) * m * lam
        c = c + hexc('#cfd6ff') * (ridge * 0.35)[..., None]
        haze = np.exp(-np.maximum(0, yy - top[None, :]) / 40) * (1 - k) * 0.6
        c = mix(c, hexc('#56609a'), haze[..., None])
        g = g * (1 - m[..., None]) + c * m[..., None]; ground = np.maximum(ground, m)
    # wind ripples on the near sand
    rip = np.sin(xx / 22 + soft_noise(WW, WH, 120, 5) * 3 + yy / 9) * 0.5 + 0.5
    near = np.clip((yy - np.array([desert_gy(x) for x in range(WW)], np.float32)[None, :]) / 200, 0, 1)
    g = g * (1 - (rip * 0.06 * near)[..., None])
    g = g * (1 + 0.025 * paper(WW, WH)[..., None])
    ga = ground[..., None].astype(np.float32)
    return np.clip(sky, 0, 1.4).astype(np.float32), CL, np.clip(g, 0, 1.4).astype(np.float32), ga, desert_gy, moon

PLACES = {'desert': paint_desert}

def _planet_disc(img, cx, cy, r, base, lit, dark, ring=None, light=(-0.6, -0.5)):
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2); m = np.clip(r - d + 0.5, 0, 1)
    nx, ny = (xx - cx) / r, (yy - cy) / r; lam = np.clip(-(nx * light[0] + ny * light[1]) * 0.9 + 0.35, 0, 1)
    c = mix(hexc(dark), hexc(base), ss(lam)[..., None]); c = mix(c, hexc(lit), ss(lam * 1.4 - 0.6)[..., None])
    c = c * (1 + 0.08 * soft_noise(WW, WH, max(8, r * 0.3), int(cx) % 7)[..., None])
    img[:] = img * (1 - m[..., None]) + c * m[..., None]
    img += (np.exp(-np.maximum(0, d - r) / (r * 0.12 + 2)) * (d > r))[..., None] * hexc(lit) * 0.25

def paint_space(tod='deep', seed=0, quick=False):
    """Deep space between the little planets: violet-blue dark, soft nebulae, dense stars, a few far worlds."""
    light = (300, 200)
    gy = lambda x: 5000.0
    if quick: return None, None, None, None, gy, light
    pal = {'deep': ('#04050f', '#0b1030', '#141a46', '#5a3c8a', '#2a6a8a', 0.30),
           'dark': ('#030308', '#07081a', '#0c0e26', '#3a2a5a', '#1a3040', 0.18),
           'storm': ('#080510', '#150c26', '#24163a', '#7a4a6a', '#5a3a2a', 0.32),
           'stairs': ('#01030e', '#071444', '#14307a', '#3a58b8', '#6a48b0', 0.28),
           'dawn': ('#0b1236', '#2a2f6a', '#6a5a9a', '#f0a080', '#ffd0a0', 0.35)}[tod]
    img = vgrad([(0, pal[0]), (0.5, pal[1]), (1.0, pal[2])])
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    for k, (col, sc, th) in enumerate(((pal[3], 260, 0.2), (pal[4], 180, 0.45))):   # nebulae
        n = soft_noise(WW, WH, sc, seed + 20 + k) + 0.5 * soft_noise(WW, WH, sc / 3, seed + 30 + k)
        m = np.clip((n - th) / 1.6, 0, 1) ** 1.6 * pal[5]
        img += m[..., None] * hexc(col)
    _milky(img, seed + 5, amt=0.12, angle=0.25, y_mid=560, width=260, col='#b9b0ff')
    _stars(img, 2600, WH, seed + 6, big=0.06)
    if tod == 'dawn':
        d = np.sqrt((xx - 2300) ** 2 + ((yy - 1100) * 1.4) ** 2); img += np.exp(-d / 500)[..., None] * hexc('#ffb88a') * 0.5
    zero = np.zeros((WH, WW, 1), np.float32)
    CL = [(np.zeros_like(img), zero.copy()), (np.zeros_like(img), zero.copy())]
    if tod in ('deep', 'dawn'):   # far little worlds
        _planet_disc(img, 2350, 300, 46, '#c98a6a', '#ffd2a8', '#3a2030')
        _planet_disc(img, 520, 880, 28, '#7a9ac8', '#d8ecff', '#1a2440')
    img *= (1 + 0.02 * paper(WW, WH)[..., None])
    sky = np.clip(img, 0, 1.4).astype(np.float32)
    return sky, CL, sky.copy(), zero.copy(), gy, light

PLACES['space'] = paint_space

from bg import paint_b612
PLACES['clock'] = lambda tod, **kw: paint_b612('clock_' + tod, layers=True, **kw)
PLACES['cloudp'] = lambda tod, **kw: paint_b612('cloudp_' + tod, layers=True, **kw)

def _limb(L, P, w0, w1, col, a=1.0):
    from core import _line_mask, _over
    n = len(P)
    widths = [w0 + (w1 - w0) * i / max(1, n - 2) for i in range(n - 1)]
    M = _line_mask(L, np.asarray(P, np.float32), widths, 0.7, False)
    if M is not None: _over(L, M.sl, hexc(col) if isinstance(col, str) else np.asarray(col, np.float32), M.m * a)

def dead_tree(frame, x, y, s, seed=0, light=(0.75, -0.45), rim='#9a88c8', col='#24202c', lit='#4a4458'):
    """A bare, crooked tree: no leaves, thin twisting branches that taper smoothly from trunk to twig."""
    r = np.random.default_rng(seed)
    pad = 20; L = Layer(x - 420 * s - pad, y - 600 * s - pad, 840 * s + 2 * pad, 620 * s + 2 * pad)
    segs = []
    def grow(x0, y0, ang, ln, w, d):
        pts = [(x0, y0)]; a = ang; px, py = x0, y0
        for k in range(5):
            a += r.normal(0, 0.14); px += math.sin(a) * ln / 5; py -= math.cos(a) * ln / 5; pts.append((px, py))
        wend = w * 0.6
        segs.append((pts, w, wend if d < 4 else 0.6))
        if d < 4:
            for k in range(2 if d > 0 else 3):
                grow(px, py, a + r.uniform(0.3, 0.75) * (1 if (k + d + seed) % 2 else -1), ln * r.uniform(0.55, 0.75), wend, d + 1)
    grow(0, 0, r.normal(0, 0.06), 210, 30, 0)
    segs[0] = (segs[0][0], 42, segs[0][2])   # a thicker foot
    for pts, w0, w1 in segs:
        P = np.asarray(catmull(pts, closed=False, n=5), np.float32) * s + [x, y]
        _limb(L, P, w0 * s, w1 * s, col)
        sh = np.array([light[0] * 0.3, light[1] * 0.2]) * w0 * s
        _limb(L, P + sh, w0 * 0.35 * s, w1 * 0.35 * s, lit, 0.55)
        if rim: _limb(L, P + [light[0] * w0 * 0.42 * s, 0], max(0.8, w0 * 0.1 * s), max(0.5, w1 * 0.1 * s), rim, 0.3)
    composite(frame, L)

def paint_dark(tod='night', seed=0, quick=False):
    """Moth's dark planet: indigo night, a violet glow on the horizon, grey dust and dead trees."""
    res = paint_b612('dark_' + tod, layers=True, quick=quick)
    if quick: return res
    sky, CL, ground, ga, gy, sun = res
    def bake(fn):
        nonlocal ground, ga
        b = np.zeros_like(ground); w_ = np.ones_like(ground); fn(b); fn(w_)
        a = np.clip(1 - (w_ - b).mean(axis=2, keepdims=True), 0, 1); col = b / np.maximum(a, 1e-3)
        ground = ground * (1 - a) + col * a; ga = np.maximum(ga, a)
    for (tx, sc, sd, k) in ((260, 1.25, 3, 0.75), (700, 0.75, 8, 0.6), (1080, 0.5, 11, 0.5), (2050, 0.62, 5, 0.55), (2420, 1.1, 2, 0.7), (2700, 0.8, 9, 0.6)):
        bake(lambda im, tx=tx, sc=sc, sd=sd, k=k: dead_tree(im, tx, gy(tx) + 14, sc, seed=sd, col=tuple((hexc('#24202c') * k / 0.75).tolist()),
                                                             lit=tuple((hexc('#4a4458') * k / 0.75).tolist())))
    return sky, CL, ground, ga, gy, sun
PLACES['dark'] = paint_dark

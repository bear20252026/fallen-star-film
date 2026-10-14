# Painted backgrounds, all in code. World images are 2880x1206; the camera crops/zooms them.
import numpy as np, math, cv2
from core import *

WW, WH = 2880, 1206

def vgrad(stops, h=WH, w=WW):
    ys = np.linspace(0, 1, h)
    cols = np.zeros((h, 3), np.float32)
    ps = [p for p, _ in stops]; cs = [hexc(c) for _, c in stops]
    for i in range(3): cols[:, i] = np.interp(ys, ps, [c[i] for c in cs])
    return np.repeat(cols[:, None, :], w, axis=1)

def soft_noise(w, h, scale, seed, oct=5):
    # scale ~ feature size in pixels
    t = NOISE[seed % 3]; out = tex(t, seed * 101, seed * 57, w, h, scale / 160.0)
    out = cv2.GaussianBlur(out, (0, 0), 2)
    return (out - out.mean()) / (out.std() + 1e-6)

def paint_clouds(img, y0, y1, seed, sun=(2300, 760), lit='#ffd3a0', body='#e7a6a6', shadow='#8d7ab0', amt=1.0, scale=260, thresh=0.25):
    h, w = img.shape[:2]
    n = soft_noise(w, y1 - y0, scale, seed)
    band = np.sin(np.linspace(0, np.pi, y1 - y0))[:, None] ** 0.8
    d = (n * band - thresh)
    m = np.clip(d / 0.5, 0, 1) ** 0.8
    # fake lighting: compare with the noise shifted toward the sun
    sx, sy = sun
    gx = cv2.Sobel(n, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(n, cv2.CV_32F, 0, 1, ksize=5)
    yy, xx = np.mgrid[y0:y1, 0:w].astype(np.float32)
    vx, vy = sx - xx, sy - yy; vn = np.sqrt(vx * vx + vy * vy) + 1
    lam = np.clip(-(gx * vx + gy * vy) / vn * 0.08 + 0.45, 0, 1)
    edge = np.clip(1 - d / 0.4, 0, 1) * np.clip(lam * 1.4 - 0.2, 0, 1)
    col = mix(hexc(shadow)[None, None], hexc(body)[None, None], ss(lam)[..., None])
    col = col + (hexc(lit) - col) * (edge * 0.9)[..., None]
    col = col * (1 + 0.04 * tex(FINE, 0, y0, w, y1 - y0, 0.7)[..., None])
    a = (m * amt)[..., None]
    img[y0:y1] = img[y0:y1] * (1 - a) + col * a

def cumulus(L, cx, cy, wdt, hgt, seed, light, base, lit, shadow, rim='#fff0c8', rim_w=0.6, alpha=0.95, soft=1.4):
    """A painted cumulus: puffs piled into a flat-bottomed dome."""
    r = np.random.default_rng(seed); pts = []
    for k in range(int(26 + wdt / 18)):
        u = r.random() * 2 - 1
        top = hgt * (1 - u * u) ** 0.7
        y = cy - r.random() * top * 0.8
        rad = (0.35 + 0.65 * (1 - abs(u))) * hgt * (0.45 + 0.3 * r.random())
        pts.append((y, cx + u * wdt * 0.5, y, rad))
    pts.sort(key=lambda p: p[0])   # higher puffs first? draw lower (front) puffs last
    for _, x, y, rad in pts[::-1][::-1]:
        puff(L, x, y, rad, base, lit, shadow, light, soft=soft, ao=0.18, rim=rim, rim_w=rim_w, gx=int(x), gy=int(y), alpha=alpha)

def cloud_layer(img, clouds, sun, top_col, mid_col, lit_col, rim_col, seed=0, layer=False):
    """Soft painted clouds: circles piled into shapes, then lit as one volume (sunlit edges glow)."""
    h, w = img.shape[:2]; m = np.zeros((h, w), np.float32); r = np.random.default_rng(seed)
    for (cx, cy, wd, ht) in clouds:
        for k in range(int(30 + wd / 12)):
            u = r.random() * 2 - 1; top = ht * (1 - u * u) ** 0.6
            y = cy - r.random() * top * 0.75; rad = (0.3 + 0.7 * (1 - abs(u))) * ht * (0.35 + 0.35 * r.random())
            cv2.circle(m, (int((cx + u * wd * 0.5) * 4), int(y * 4)), int(rad * 4), 1.0, -1, cv2.LINE_AA, shift=2)
        cv2.ellipse(m, (int(cx * 4), int(cy * 4)), (int(wd * 0.5 * 4), int(ht * 0.12 * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, shift=2)
    wob = soft_noise(w, h, 40, seed + 3) * 3
    mapx, mapy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    m = cv2.remap(m, mapx + wob, mapy + soft_noise(w, h, 40, seed + 4) * 3, cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(m, (0, 0), 2.5)
    hgt = cv2.GaussianBlur(m, (0, 0), 22)
    gx = cv2.Sobel(hgt, cv2.CV_32F, 1, 0, ksize=5); gy = cv2.Sobel(hgt, cv2.CV_32F, 0, 1, ksize=5)
    yy, xx = mapy, mapx
    vx, vy = sun[0] - xx, sun[1] - yy; vn = np.sqrt(vx * vx + vy * vy) + 1
    lam = np.clip(-(gx * vx + gy * vy) / vn * 5 + 0.3, 0, 1); lam = cv2.GaussianBlur(lam, (0, 0), 4)
    vert = np.clip((yy - (yy * 0 + 0)) / h, 0, 1)
    col = mix(hexc(top_col), hexc(mid_col), ss(lam * 1.3)[..., None])
    col = mix(col, hexc(lit_col), ss(lam * 1.3 - 0.35)[..., None])
    edge = np.clip((a - hgt * 1.2), 0, 1) * np.clip(lam * 2 - 0.3, 0, 1)
    col = col + (hexc(rim_col) - col) * np.clip(edge * 2.5, 0, 1)[..., None]
    col = col * (1 + 0.05 * soft_noise(w, h, 18, seed + 7)[..., None] * 0.6)
    a3 = (a * 0.93)[..., None]
    if layer: return col.astype(np.float32), a3.astype(np.float32)
    return img * (1 - a3) + col * a3


# Times of day for B612. Each one is a full palette: sky gradient, sun, clouds, ground, grass, haze.
PAL = {
 'dusk': dict(sky=[(0, '#3f4a86'), (0.3, '#8c78b4'), (0.52, '#e7a3a6'), (0.66, '#f6c59a'), (0.75, '#ffe1a8')], sun=(2240, 800),
              sun_core='#ffe7b0', sun_wide='#ffb88a', sun_amt=(0.35, 0.18), stars=160, star_y=380,
              cl1=('#7a6fa6', '#b993b5', '#ffc9a8', '#fff0cf'), cl2=('#a184ad', '#e3a5a8', '#ffd9b0', '#fff6dc'),
              g_dark='#7d9a58', g_lit='#c9c477', g_deep='#4c6b47', g_rim='#ffdca0', blade_dark='#5f8048', blade_lit='#e3d98a', haze='#ffd9b4'),
 'morning': dict(sky=[(0, '#5d93cf'), (0.32, '#8dbde6'), (0.55, '#c9e2ef'), (0.7, '#f4ead2'), (0.76, '#fff1d6')], sun=(520, 330),
              sun_core='#fffbe8', sun_wide='#fff0c0', sun_amt=(0.45, 0.16), stars=0, star_y=380,
              cl1=('#9fb4d6', '#e6eef6', '#ffffff', '#fffdf2'), cl2=('#aac0dc', '#eef3f8', '#ffffff', '#fffef6'),
              g_dark='#6f9e4f', g_lit='#bfd775', g_deep='#4f7a45', g_rim='#f4ffd0', blade_dark='#5c8a44', blade_lit='#d6e889', haze='#eef6f2'),
 'clock_sunset': dict(sky=[(0, '#40306e'), (0.28, '#9a5a8a'), (0.5, '#f08a6a'), (0.64, '#ffb46a'), (0.74, '#ffe0a0')], sun=(2150, 770),
              sun_core='#fff0b8', sun_wide='#ff9a5a', sun_amt=(0.6, 0.3), stars=60, star_y=260,
              cl1=('#6a4a7a', '#c07890', '#ffb890', '#ffe6c0'), cl2=('#8a5a7a', '#e88a80', '#ffc890', '#fff0d0'),
              g_dark='#8a7040', g_lit='#e0b860', g_deep='#5a4428', g_rim='#ffd890', blade_dark='#7a6232', blade_lit='#f0c870', haze='#ffc890', flower_mul=0.6),
 'cloudp_rain': dict(sky=[(0, '#4a5470'), (0.35, '#6a748e'), (0.6, '#8e98ae'), (0.72, '#a6aec0'), (0.76, '#b4bac8')], sun=(1500, 260),
              sun_core='#e8ecf4', sun_wide='#b8c0d4', sun_amt=(0.08, 0.06), stars=0, star_y=380,
              cl1=('#5a6480', '#7a849e', '#9aa4bc', '#b4bcd0'), cl2=('#68728e', '#8892aa', '#a6aec4', '#c0c6d6'),
              g_dark='#3e5e50', g_lit='#6a8a70', g_deep='#2a4238', g_rim='#a8b8c0', blade_dark='#3a5a4c', blade_lit='#7a9a80', haze='#a6aec0', flower_mul=0.5),
 'cloudp_after': dict(sky=[(0, '#4a86c8'), (0.32, '#7ab4e4'), (0.55, '#bfe0f0'), (0.7, '#f2f0dc'), (0.76, '#fff4d8')], sun=(700, 300),
              sun_core='#fffbe8', sun_wide='#fff0c0', sun_amt=(0.5, 0.2), stars=0, star_y=380,
              cl1=('#9fb4d6', '#e6eef6', '#ffffff', '#fffdf2'), cl2=('#aac0dc', '#eef3f8', '#ffffff', '#fffef6'),
              g_dark='#4f9a5a', g_lit='#b8e07a', g_deep='#3a7648', g_rim='#f4ffd0', blade_dark='#4a8a50', blade_lit='#cdea8a', haze='#e6f4f2'),
 'dark_night': dict(sky=[(0, '#05040c'), (0.35, '#0e0b1c'), (0.6, '#1a1430'), (0.72, '#2a1f44'), (0.76, '#32264e')], sun=(2250, 790),
              sun_core='#b898f0', sun_wide='#5a4098', sun_amt=(0.22, 0.16), stars=600, star_y=700,
              cl1=('#0c0a16', '#141024', '#1e1834', '#2a2244'), cl2=('#0e0c1a', '#18142a', '#221c38', '#2e284a'), flower_mul=0.25,
              g_dark='#18161e', g_lit='#302c3a', g_deep='#0e0c14', g_rim='#8a74c0', blade_dark='#1c1a24', blade_lit='#3a3646', haze='#241c38'),
 'night': dict(sky=[(0, '#0e1636'), (0.35, '#1f2b5c'), (0.6, '#34427a'), (0.72, '#4c5a8e'), (0.76, '#5a6698')], sun=(1900, 260),
              sun_core='#e8eeff', sun_wide='#9fb0e8', sun_amt=(0.18, 0.08), stars=700, star_y=760,
              cl1=('#1d2850', '#2c3866', '#46558a', '#6878a8'), cl2=('#26325c', '#33406e', '#4c5b90', '#6f7fb0'), flower_mul=0.35,
              g_dark='#2c4a4a', g_lit='#4f6e66', g_deep='#1d3438', g_rim='#a9bde8', blade_dark='#2a4646', blade_lit='#5e7e78', haze='#5e6c9e'),
}

def paint_b612(tod='dusk', seed=0, layers=False, quick=False):
    P = PAL[tod]
    if quick:   # only the planet's shape and the sun (the painting itself comes from the cache)
        R = 3600; cx, cy = 1440, 820 + R
        return None, None, None, None, (lambda x: cy - math.sqrt(max(0, R * R - (x - cx) ** 2))), P['sun']
    """B612 at dusk: a peach-violet sky, painted clouds, a low sun, the little curved planet with grass.
    layers=True returns (sky, [(cloud_rgb, cloud_a), ...], ground_rgb, ground_a, ground_y, sun) so clouds can drift."""
    img = vgrad(P['sky'])
    # sun glow on the horizon (right)
    sun = P['sun']
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    d = np.sqrt((xx - sun[0]) ** 2 + ((yy - sun[1]) * 1.3) ** 2)
    img = img + (np.exp(-d / 160)[..., None] * hexc(P['sun_core']) * P['sun_amt'][0] + np.exp(-d / 700)[..., None] * hexc(P['sun_wide']) * P['sun_amt'][1])
    # faint stars at the top
    r = np.random.default_rng(seed + 4)
    for k in range(P['stars']):
        x, y = r.random() * WW, r.random() ** 2 * P['star_y']
        a = (1 - y / P['star_y']) * (0.4 + 0.6 * r.random())
        cv2.circle(img, (int(x), int(y)), 1 if r.random() < 0.8 else 2, tuple((np.array([1, 0.97, 0.9]) * (0.6 + a * 0.4)).tolist()), -1, cv2.LINE_AA)
    CL = [cloud_layer(img, [(420, 300, 560, 120), (1180, 210, 400, 80), (2620, 330, 460, 100), (2100, 190, 320, 60), (3300, 260, 420, 90), (-300, 240, 380, 80)], sun, *P['cl1'], 1, layer=True),
          cloud_layer(img, [(1650, 540, 700, 130), (760, 630, 380, 70), (2900, 600, 420, 80)], sun, *P['cl2'], 2, layer=True)]
    sky = img.copy()
    if not layers:
        for c, a in CL: img = img * (1 - a) + c * a
    # far hills of the little planet's edge (haze)
    R = 3600; cx, cy = 1440, 820 + R
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ground = np.clip((R - dist) / 2.0 + 0.5, 0, 1)
    # ground colour: lit by the sun from the right, darker toward the left and the bottom
    lightx = np.clip((xx - 400) / 2400, 0, 1) if sun[0] > WW / 2 else np.clip((2480 - xx) / 2400, 0, 1)
    depth = np.clip((yy - 820) / 380, 0, 1)
    g = mix(hexc(P['g_dark']), hexc(P['g_lit']), lightx[..., None] * (1 - depth[..., None] * 0.6))
    g = mix(g, hexc(P['g_deep']), (depth ** 1.5)[..., None] * 0.7)
    rim_band = np.clip(1 - (R - dist) / 30, 0, 1) * ground
    g = g + hexc(P['g_rim']) * (rim_band * 0.5 * lightx)[..., None]
    n = soft_noise(WW, WH, 120, 5)
    g = g * (1 + 0.08 * n[..., None]) * (1 + 0.04 * tex(STREAK[2], 0, 0, WW, WH, 1)[..., None])
    img = img * (1 - ground[..., None]) + g * ground[..., None]
    # grass blades along the horizon rim and scattered tufts
    gl = np.zeros((WH, WW), np.float32); gc = np.zeros((WH, WW, 3), np.float32)
    for k in range(4200):
        x = r.random() * WW
        top = cy - math.sqrt(max(0, R * R - (x - cx) ** 2))
        y = top + (r.random() ** 2.2) * 380
        if y > WH: continue
        ln = (8 + r.random() * 14) * (0.6 + 0.8 * (y - top) / 380 + 0.4)
        lean = (r.random() - 0.5) * 0.6 + 0.2
        p0 = (int(x * 16), int(y * 16)); p1 = (int((x + lean * ln) * 16), int((y - ln) * 16))
        lx_ = min(1, max(0, (x - 400) / 2400)) if sun[0] > WW / 2 else min(1, max(0, (2480 - x) / 2400))
        c = mix(hexc(P['blade_dark']), hexc(P['blade_lit']), lx_ * (0.5 + 0.5 * r.random())) * (0.85 + 0.3 * r.random())
        cv2.line(gc, p0, p1, c.tolist(), 2, cv2.LINE_AA, shift=4)
        cv2.line(gl, p0, p1, 1.0, 2, cv2.LINE_AA, shift=4)
    gl = cv2.GaussianBlur(gl, (0, 0), 0.5)[..., None] * 0.8
    img = img * (1 - gl) + gc * gl / np.maximum(gl / 0.8, 1e-3) * 0 + gc * gl
    # little flowers
    for k in range(140):
        x = r.random() * WW; top = cy - math.sqrt(max(0, R * R - (x - cx) ** 2)); y = top + 20 + r.random() ** 1.5 * 350
        if y > WH - 5: continue
        c = [hexc('#f4d6e4'), hexc('#fff4c4'), hexc('#cbb6e8')][k % 3] * P.get('flower_mul', 1.0)
        cv2.circle(img, (int(x * 16), int(y * 16)), 3 * 16 // 2 * 2, c.tolist(), -1, cv2.LINE_AA, shift=4)
    # haze where sky meets planet
    hz = np.exp(-np.abs(dist - R) / 40)[..., None] * 0.25
    img = img * (1 - hz) + hexc(P['haze']) * hz
    img = img * (1 + 0.025 * paper(WW, WH)[..., None])
    def ground_y(x): return cy - math.sqrt(max(0, R * R - (x - cx) ** 2))
    if layers:
        ga = np.clip((R + 45 - dist) / 45, 0, 1).astype(np.float32)[..., None]   # ground + horizon haze + grass rim
        return np.clip(sky, 0, 1.4).astype(np.float32), CL, np.clip(img, 0, 1.4).astype(np.float32), ga, ground_y, sun
    return np.clip(img, 0, 1.4).astype(np.float32), ground_y, sun

if __name__ == '__main__':
    import time; t0 = time.time()
    img, gy, sun = paint_b612()
    print('painted in %.1fs' % (time.time() - t0))
    np.save('../bg_b612.npy', img)
    cv2.imwrite('../t_bg.jpg', (np.clip(cv2.resize(img, (1440, 603)), 0, 1)[..., ::-1] * 255).astype(np.uint8))

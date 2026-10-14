# Living environment: grass that moves in the wind, tufts in front of feet, pollen in the sunlight,
# and the sky composed from drifting cloud layers.
import numpy as np, cv2, math
from core import *

def wind(t, x):
    """Gusts that travel across the field from right to left."""
    return (0.55 + 0.45 * math.sin(t * 0.7 + x * 0.004)) * (0.6 + 0.4 * math.sin(t * 2.3 + x * 0.013)) + 0.15 * math.sin(t * 5.1 + x * 0.05)

class Field:
    """Tall blades and flowers standing on the planet's surface (world space), redrawn each frame with wind."""
    def __init__(self, gy, x0=300, x1=2700, n=1600, seed=11, depth=300, dark='#55773f', lit='#d9d283', lit_right=True, flower_mul=1.0):
        r = np.random.default_rng(seed); B = []
        for k in range(n):
            x = x0 + r.random() * (x1 - x0); d = r.random() ** 1.6 * depth
            y = gy(x) + 6 + d
            ln = (14 + r.random() * 22) * (0.7 + d / depth)
            lx = min(1, max(0, (x - 400) / 2400)) if lit_right else min(1, max(0, (2480 - x) / 2400))
            c = mix(hexc(dark), hexc(lit), lx * (0.35 + 0.55 * r.random())) * (0.8 + 0.35 * r.random())
            B.append((y, x, ln, (r.random() - 0.5) * 0.5 + 0.15, c, r.random() * 6.28, 1 + int(r.random() * 2)))
        B.sort(key=lambda b: b[0]); self.B = B
        self.F = [(gy(x) + 14 + d, x, [hexc('#f7dbe8'), hexc('#fff3c0'), hexc('#d6c2f0')][k % 3] * flower_mul, r.random() * 6.28)
                  for k, (x, d) in enumerate(zip(x0 + r.random(90) * (x1 - x0), r.random(90) ** 1.5 * depth))]

    def draw(self, f, C, t, ymin=-1e9, ymax=1e9):
        k = C.k
        for (y, x, ln, lean, c, ph, wd) in self.B:
            if y < ymin: continue
            if y > ymax: break
            X, Y = C.to_screen(x, y)
            if X < -40 or X > W + 40 or Y < -10 or Y > H + 60: continue
            sw = lean + 0.35 * wind(t, x) + 0.06 * math.sin(t * 3.7 + ph)
            L_ = ln * k; mx, my = X + sw * L_ * 0.45, Y - L_ * 0.55; tx, ty = X + sw * L_ * 1.05, Y - L_ * 0.95
            pts = np.array([[X, Y], [mx, my], [tx, ty]], np.float32)
            cv2.polylines(f, [np.round(pts * 16).astype(np.int32)], False, c.tolist(), max(1, int(wd * k * 0.9)), cv2.LINE_AA, shift=4)
        for (y, x, c, ph) in self.F:
            if not (ymin <= y <= ymax): continue
            X, Y = C.to_screen(x, y); sw = 0.3 * wind(t, x)
            X += sw * 10 * k; Y -= 10 * k
            if -10 < X < W + 10 and -10 < Y < H + 10:
                cv2.line(f, (int(X * 16), int(Y * 16)), (int((X - sw * 10 * k) * 16), int((Y + 12 * k) * 16)), (0.4, 0.55, 0.3), max(1, int(k)), cv2.LINE_AA, shift=4)
                for j in range(5):
                    a = ph + j * 1.2566
                    cv2.circle(f, (int((X + math.cos(a) * 2.6 * k) * 16), int((Y + math.sin(a) * 2.6 * k) * 16)), max(16, int(2.2 * k * 16)), c.tolist(), -1, cv2.LINE_AA, shift=4)
                cv2.circle(f, (int(X * 16), int(Y * 16)), max(12, int(1.5 * k * 16)), (1.0, 0.85, 0.4), -1, cv2.LINE_AA, shift=4)

def tufts(f, x, y, width, s, t, seed=0, n=26, sample_y=None):
    """Grass blades standing in front of a character's feet so it sits IN the meadow, not on it."""
    r = np.random.default_rng(seed)
    sy = int(min(H - 1, max(0, (sample_y or y) + 8 * s)))
    for k in range(n):
        bx = x + (r.random() - 0.5) * width; base = y + r.random() * 10 * s + 3 * s
        sxp = int(min(W - 1, max(0, bx)))
        c = f[sy, sxp].copy() * (0.85 + 0.35 * r.random())
        ln = (12 + r.random() * 16) * s * 1.4
        sw = (r.random() - 0.4) * 0.5 + 0.3 * wind(t, bx * 0.8) - 0.15
        pts = np.array([[bx, base], [bx + sw * ln * 0.4, base - ln * 0.55], [bx + sw * ln, base - ln]], np.float32)
        cv2.polylines(f, [np.round(pts * 16).astype(np.int32)], False, np.clip(c, 0, 1.2).tolist(), max(1, int(2.2 * s)), cv2.LINE_AA, shift=4)

class Motes:
    """Pollen and dust drifting in the low sun: tiny lights that glow brighter toward the sun."""
    def __init__(self, n=70, seed=5):
        r = np.random.default_rng(seed); self.P = r.random((n, 5))
    def draw(self, f, t, sun, amt=1.0, cam_dx=0.0):
        buf = np.zeros((H // 2, W // 2), np.float32)
        for (a, b, c, d, e) in self.P:
            x = (a * W * 1.3 - t * (12 + 20 * c) - cam_dx * (0.6 + c) + math.sin(t * (0.5 + d) + e * 6) * 30) % (W * 1.3) - W * 0.15
            y = (b * H + math.sin(t * (0.3 + c * 0.5) + e * 9) * 40 - t * 4 * d) % H
            dist = math.hypot(x - sun[0], y - sun[1]); br = (0.25 + 1.2 * math.exp(-dist / 700)) * (0.5 + 0.5 * math.sin(t * (2 + 3 * d) + e * 20)) ** 2
            cv2.circle(buf, (int(x * 8), int(y * 8)), int((1.0 + 2.0 * c) * 4), float(br), -1, cv2.LINE_AA, shift=3)
        buf = cv2.GaussianBlur(buf, (0, 0), 1.2)
        g = cv2.resize(buf, (W, H))[..., None] * amt
        f[:] = 1 - (1 - f) * (1 - np.clip(g * hexc('#ffe6b0'), 0, 1))

def compose_sky(C, sky, CL, ground, ga, t, drift=(5.0, 9.0), par=(0.82, 0.92), blur=0.0):
    """Sky + drifting clouds (with parallax: far clouds move less when the camera pans) + the ground."""
    from cam import Cam
    f = C.view(sky)
    for (col, a), dr, p in zip(CL, drift, par):
        Cp = Cam(C.x * p + 1440 * (1 - p) - t * dr, C.y * (p * 0.5 + 0.5) + 600 * (1 - (p * 0.5 + 0.5)), C.z)
        c = Cp.view(col); al = Cp.view(a[..., 0])[..., None]
        f = f * (1 - al) + c * al
    if blur > 0.3: f = cv2.GaussianBlur(f, (0, 0), blur * 1.3)
    g = C.view(ground); al = C.view(ga[..., 0])[..., None]
    if blur > 0.3:
        g = cv2.GaussianBlur(g, (0, 0), blur); al = cv2.GaussianBlur(al[..., 0], (0, 0), blur)[..., None]
    return f * (1 - al) + g * al

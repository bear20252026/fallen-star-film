# Camera over a painted world plate, plus helpers to place painted characters in world space.
import numpy as np, cv2, math
from core import *
BS = 1920 / 2400

def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)
def track(keys, t):
    """keys: [(t, value_or_tuple), ...] eased between."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = ease((t - t0) / (t1 - t0))
            if isinstance(v0, tuple): return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]

class Cam:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z
    @property
    def k(self): return BS * self.z
    def to_screen(self, wx, wy): return (wx - self.x) * self.k + 960, (wy - self.y) * self.k + 402
    def view(self, plate):
        """Crop + scale the world plate into a 1920x804 frame (sub-pixel accurate)."""
        k = self.k
        M = np.array([[k, 0, 960 - self.x * k], [0, k, 402 - self.y * k]], np.float32)
        return cv2.warpAffine(plate, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def grade(f, mul=(1, 1, 1), lift=(0, 0, 0), sat=1.0):
    g = f * np.array(mul, np.float32) + np.array(lift, np.float32)
    if sat != 1.0:
        l = g.mean(axis=2, keepdims=True); g = l + (g - l) * sat
    return g

def light_rays(f, x, y, amt=0.25, color='#ffe2b0', n=9, t=0.0):
    """Soft god-rays fanning from a point (the sun)."""
    yy, xx = np.mgrid[0:H:2, 0:W:2].astype(np.float32)
    a = np.arctan2(yy - y, xx - x); d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    r = (0.5 + 0.5 * np.sin(a * n + t * 0.15)) * (0.5 + 0.5 * np.sin(a * (n * 2.3) - t * 0.1))
    v = r * np.exp(-d / 900) * amt
    v = cv2.resize(cv2.GaussianBlur(v, (0, 0), 3), (W, H))
    c = hexc(color)
    return 1 - (1 - f) * (1 - np.clip(v[..., None] * c, 0, 1))

def dof_blur(f, amt):
    if amt <= 0.2: return f
    return cv2.GaussianBlur(f, (0, 0), amt)

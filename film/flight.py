# Flying between planets: actors that can turn in the air, streaming stars, the gold laughter trail, the box carried in the mouth.
import math, numpy as np, cv2
import core
from core import glow, ss
from base import Actor, Prop, W, H
from cast import steps
from sheep import LAST as SHEEP_LAST
from boy2 import LAST as BOY_LAST
from props3 import box, Flock

class RotActor(Actor):
    """Wraps an actor so it can rotate as a whole in the air (spins, swinging on a string)."""
    def __init__(self, inner, ang, piv_h=150.0, worlds=None):
        self.inner, self.ang, self.piv_h = inner, ang, piv_h
        self.height, self.tuft_w, self.tuft_n, self.cast = inner.height, 0, 0, getattr(inner, 'cast', None)
        if worlds is not None: self.worlds = worlds
    def foot(self, t): return self.inner.foot(t)
    def draw(self, f, X, Y, s, t, W_, C):
        a = float(self.ang(t))
        if abs(a) < 0.25: return self.inner.draw(f, X, Y, s, t, W_, C)
        R = int(520 * s) + 40; px, py = X, Y - self.piv_h * s
        x0, x1, y0, y1 = int(max(0, px - R)), int(min(W, px + R)), int(max(0, py - R)), int(min(H, py + R))
        if x1 <= x0 or y1 <= y0: return
        env = dict(core.ENV)
        b0 = np.zeros((H, W, 3), np.float32); b1 = np.ones((H, W, 3), np.float32)
        self.inner.draw(b0, X, Y, s, t, W_, C); core.ENV.clear(); core.ENV.update(env); self.inner.draw(b1, X, Y, s, t, W_, C)
        b0, b1 = b0[y0:y1, x0:x1], b1[y0:y1, x0:x1]
        al = np.clip(1 - (b1 - b0).mean(axis=2), 0, 1)
        M = cv2.getRotationMatrix2D((px - x0, py - y0), -a, 1.0)
        pre = cv2.warpAffine(b0, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)
        am = cv2.warpAffine(al, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR)[..., None]
        f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - am) + pre

class StarStream:
    """Near stars streaming past: the feeling of flight (screen space, three depths)."""
    def __init__(self, n=160, seed=4):
        r = np.random.default_rng(seed); self.p = [(r.random(), r.random(), 0.25 + r.random() ** 2 * 1.0, r.random()) for _ in range(n)]
    def draw(self, f, t, speed=1.0, dirx=-1.0, diry=0.12, amt=1.0, col=(1.0, 0.97, 0.9)):
        if amt <= 0: return
        for (u, v, d, b) in self.p:
            sp = 260 * d * speed
            x = (u * (W + 400) + dirx * sp * t) % (W + 400) - 200; y = (v * (H + 200) + diry * sp * t) % (H + 200) - 100
            ln = max(1.0, sp * 0.04); a = (0.25 + 0.75 * b) * amt * min(1, d * 1.4)
            p0 = (int(x * 16), int(y * 16)); p1 = (int((x - dirx * ln) * 16), int((y - diry * ln) * 16))
            c = tuple(float(ci * a) for ci in col)
            cv2.line(f, p0, p1, c, max(1, int(1 + d)), cv2.LINE_AA, shift=4)

class GoldTrail:
    """Little gold sparkles shed behind the lantern when Pip laughs; they drift back and fade."""
    def __init__(self): self.hist = []
    def draw(self, f, t, src, amt, z, drift=(-220, 30)):
        r = np.random.default_rng(int(t * 24) % 997)
        if src is None or amt <= 0.02: return
        for k in range(46):
            age = k * 0.06; a = amt * (1 - age / 2.8)
            if a <= 0: continue
            jx = (math.sin(k * 12.9898 + int(t * 6)) * 43758.5453) % 1 - 0.5; jy = (math.sin(k * 78.233 + int(t * 6)) * 12543.13) % 1 - 0.5
            x = src[0] + drift[0] * age * z + jx * 40 * z * age; y = src[1] + drift[1] * age * z + jy * 40 * z * age + 30 * age * age * z
            glow(f, x, y, (2.2 + 1.5 * ((k * 7) % 3)) * z, '#ffd56a', 0.7 * a * (0.6 + 0.4 * math.sin(t * 9 + k)))

def box_in_mouth(f, s, t, W_, facing, glow_amt, grey=0.0):
    """Draw the box hanging from the sheep's mouth (call right after the sheep is drawn)."""
    m = SHEEP_LAST.get('mouth')
    if m is None: return None
    sb = 0.85 * s
    X, Y = m[0] - 5 * sb * facing, m[1] + 168 * sb + 6 * s
    box(f, X, Y, sb, light=W_.light, rim=W_.rim, glow_amt=glow_amt, t=t, handle=True, tilt=5 * math.sin(t * 5), grey=grey)
    return (X, Y - 60 * sb)

def sheep_harness(z):
    if 'head' in SHEEP_LAST and 'tail' in SHEEP_LAST:
        hp, tp = np.array(SHEEP_LAST['head']), np.array(SHEEP_LAST['tail'])
        return tuple((hp + tp) / 2 + [0, -40 * z])
    return None

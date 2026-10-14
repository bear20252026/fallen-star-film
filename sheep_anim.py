# The sheep's performance: a real four-legged gait (walk = one leg at a time, trot = diagonal pairs) with
# planted hooves, a body that rides on the legs, wool that jiggles behind the body, floppy ears, hops with
# anticipation, squash on landing, sniffing, and laughing.
import numpy as np, math
from functools import lru_cache
from motion import keys, spring, foot_cycle, blink_amt, ss

LEGX = [-62, 40, -40, 62]                         # far back, far front, near back, near front
WALK_OFF = [0.0, 0.25, 0.5, 0.75]                 # lateral walk: LH, LF, RH, RF
TROT_OFF = [0.0, 0.5, 0.5, 0.0]                   # trot: diagonal pairs together

class SheepAnim:
    def __init__(self, path, k=1.6, head=None, hop=None, sniff=None, laugh=None, look=None, tail=None,
                 mouth=None, crouch=None, t_end=60.0, seed=9, pitch=None, soot=None, t_start=0.0, sleep=None, lift=None, paddle=None):
        self.path, self.k = path, k
        self.head = head or [(0, 0)]; self.hop = hop or []; self.sniff = sniff or [(0, 0)]
        self.laugh = laugh or [(0, 0)]; self.look = look or [(0, (0, 0))]; self.tail = tail or [(0, 0)]
        self.mouth = mouth or []; self.crouch = crouch or [(0, 0)]; self.seed = seed
        self.pitch = pitch or [(0, 0)]; self.soot = soot or [(0, 0)]; self.sleep = sleep or [(0, 0)]; self.lift = lift or [(0, 0)]; self.paddle = paddle or [(0, 0)]
        self.dt = 1 / 240; n = int((t_end - t_start + 4) / self.dt) + 2
        ts = np.arange(n) * self.dt - 2.0 + t_start
        xs = np.array([path(t) for t in ts]) * k
        v = np.gradient(xs, self.dt); self.ts, self.v = ts, v
        tf = np.clip((np.abs(v) - 70) / 50, 0, 1)                   # 0 walk .. 1 trot
        C = 80 + 40 * tf
        self.phase = np.cumsum(np.abs(v) / C) * self.dt; self.tf = tf
        self.w = np.array([ss(x) for x in np.clip(np.abs(v) / 30.0, 0, 1)])

    def _i(self, a, t): return float(np.interp(t, self.ts, a))

    def air(self, t):
        """Height of a hop: [(t_takeoff, duration, height)]; a parabola in the air."""
        lf = float(keys(self.lift, t))
        if lf > 0: return lf
        for t0, d, h in self.hop:
            if t0 <= t < t0 + d: u = (t - t0) / d; return 4 * h * u * (1 - u)
        return 0.0

    def crouch_amt(self, t):
        """Knees bend before take-off (anticipation) and after landing (absorbing the weight)."""
        c = float(keys(self.crouch, t))
        for t0, d, h in self.hop:
            a = t0 - t
            if 0 < a < 0.25: c += 14 * math.sin(math.pi * (1 - a / 0.25)) * 0.9 if a > 0.05 else 14 * (a / 0.05)
            b = t - (t0 + d)
            if 0 < b < 0.35: c += 16 * math.exp(-b * 9) * math.sin(min(math.pi, b * 22) + 0.2) if b > 0.02 else 16 * b / 0.02
        return c

    @lru_cache(maxsize=20000)
    def _base(self, tick):
        t = tick / 120.0
        u = self._i(self.phase, t); w = self._i(self.w, t); tf = self._i(self.tf, t)
        air = self.air(t); cr = self.crouch_amt(t)
        bob = w * ((1 - tf) * 1.6 * math.cos(8 * math.pi * u) + tf * 5.0 * math.cos(4 * math.pi * (u - 0.1)))
        laugh = float(keys(self.laugh, t))
        ch = laugh * (0.6 + 0.4 * math.sin(t * 2 * math.pi * 0.9)) * abs(math.sin(t * 2 * math.pi * 3.8))
        by = bob + cr * 0.6 - air + 5 * ch
        sl = float(keys(self.sleep, t)); by += 1.8 * sl * math.sin(t * 2 * math.pi / 3.6)
        sn = float(keys(self.sniff, t))
        head = float(keys(self.head, t)) + 8 * sl * (1 + 0.15 * math.sin(t * 2 * math.pi / 3.6)) + w * 3 * math.sin(4 * math.pi * u) + sn * (14 + 4 * math.sin(t * 2 * math.pi * 3.2)) - 10 * laugh - 5 * ch
        pitch = float(keys(self.pitch, t)) + w * tf * 2.0 * math.sin(2 * math.pi * u) + (-6 if air > 1 else 0) * min(1, air / 20)
        return np.array([by, head, pitch, ch])

    def base(self, t): return self._base(int(round(t * 120)))

    def at(self, t):
        u = self._i(self.phase, t); w = self._i(self.w, t); tf = self._i(self.tf, t)
        pd = float(keys(self.paddle, t))
        if pd > 0: u += pd * t * 2.2; w = max(w, pd)   # running in the air
        b = self.base(t)
        body = spring(lambda x: self.base(x)[[0, 2]], t, freq=5.0, zeta=0.7)
        head = spring(lambda x: self.base(x)[[1]], t, freq=3.0, zeta=0.5)[0]
        wool = spring(lambda x: self.base(x)[[0]], t, freq=3.2, zeta=0.28)[0]
        earl = spring(lambda x: self.base(x)[[1, 0]], t, freq=1.8, zeta=0.3)
        C = 80 + 40 * tf; duty = 0.65 - 0.2 * tf; lift = 9 + 6 * tf
        air = self.air(t)
        feet = []
        for i, lx in enumerate(LEGX):
            off = WALK_OFF[i] + (TROT_OFF[i] - WALK_OFF[i]) * tf
            rel, h, _ = foot_cycle(u + off, C, duty, lift)
            fx = lx * 0.95 + rel * w; fy = -h * w
            if air > 0.5 and pd < 0.5: fx = lx * 0.9 + (6 if lx > 0 else -6)   # legs tuck in the air
            fy = min(fy, body[0] + 2 - 12 * min(1, air / 20) + (3 if i % 2 else -3) * min(1, air / 20))   # legs never stretch: feet follow a rising body
            if pd >= 0.5: fx = lx * 0.95 + rel * 1.4; fy = body[0] + 6 - h * 1.6   # paddling: legs swing under the floating body
            feet.append((fx, fy))
        jig = np.array([0.0, (wool - body[0]) * 1.6])
        A = dict(feet=feet, body=(0.0, body[0]), pitch=body[1], head=head, jig=jig,
                 ear=(earl[0] - head) * 1.4 + (earl[1] - body[0]) * 1.2,
                 tail=float(keys(self.tail, t)) + 18 * math.sin(t * 2 * math.pi * 2.2) * (0.3 + 0.7 * float(keys(self.laugh, t))) * (1 - float(keys(self.sleep, t))),
                 squash=float(np.clip((body[0] - wool) * 0.006 + b[3] * 0.02, -0.08, 0.1)),
                 blink=min(blink_amt(t, self.seed), 1 - float(keys(self.sleep, t))), look=tuple(keys(self.look, t)), laugh=float(keys(self.laugh, t)), air=air, soot=float(keys(self.soot, t)))
        for (t0, t1, m) in self.mouth:
            if t0 <= t < t1: A['mouth'] = m
        return A

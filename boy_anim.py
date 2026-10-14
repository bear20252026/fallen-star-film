# The boy's performance: turns a few acting keys into a full body pose for any time t.
# Walk: feet stay planted (phase follows distance travelled), knees bend by IK, pelvis rises and falls,
# arms swing against the legs and drag behind them, the head steadies itself, hair and scarf follow through.
# Acting: pose keys go through springs with different stiffness, so the eyes lead, the head follows,
# then the chest, then the arms (successive breaking of joints), with overshoot and settle.
import numpy as np, math
from functools import lru_cache
from motion import keys, spring, foot_cycle, ik2, blink_amt, ss

L_THIGH, L_SHIN = 68.0, 64.0          # hip -> knee -> ankle (rig units)
HIP = {'L': (-20.0, 0.0), 'R': (20.0, 0.0)}
REST = {'L': -18.0, 'R': 24.0}         # where each foot stands when still (3/4 stance)
ANKLE_H = 20.0                          # ankle height above the sole
PELVIS_Y = -150.0
FX, FY = 0.62, 0.2      # forward axis of a 3/4-front character on screen (right and toward camera)
JOINTS = ['pelvis', 'chest', 'head', 'armL', 'foreL', 'armR', 'foreR']

class BoyAnim:
    def __init__(self, path, k=1.6, poses=None, crouch=None, lookup=None, look_x=None, laugh=None, talk=None,
                 mouth=None, brows=None, t_end=60.0, cycle=128.0, seed=4, sit=None, t_start=0.0, sleep=None, hang=None, wind=None):
        """path(t): world x of the boy's feet. k: rig units per world unit.
        poses: {joint: [(t, deg)]} acting keys (added on top of walk/idle). crouch: [(t, units)] knees bend.
        lookup / look_x: [(t, -1..1)] where the eyes/head aim. laugh/talk: [(t, 0..1)]."""
        self.path, self.k, self.C0 = path, k, cycle
        self.poses = poses or {}; self.crouch = crouch or [(0, 0)]
        self.lookup = lookup or [(0, 0)]; self.look_x = look_x or [(0, 0)]
        self.laugh = laugh or [(0, 0)]; self.talk = talk or [(0, 0)]; self.mouth = mouth or []
        self.brows = brows or [(0, 0)]; self.seed = seed; self.sit = sit or [(0, 0)]; self.sleep = sleep or [(0, 0)]; self.hang = hang or [(0, 0)]; self.windk = wind or [(0, 0)]
        # integrate the gait phase once (step length shrinks when walking slowly)
        self.dt = 1 / 240; n = int((t_end - t_start + 4) / self.dt) + 2
        ts = np.arange(n) * self.dt - 2.0 + t_start
        xs = np.array([path(t) for t in ts]) * k / FX
        v = np.gradient(xs, self.dt)
        self.ts, self.v = ts, v
        w = np.clip(np.abs(v) / 120.0, 0, 1)
        C = cycle * (0.6 + 0.4 * w)
        self.phase = np.cumsum(np.abs(v) / C) * self.dt; self.dist = np.cumsum(np.abs(v)) * self.dt; self.depth_scale = 1.0
        self.w = np.array([ss(x) for x in np.clip(np.abs(v) / 50.0, 0, 1)])

    def _i(self, arr, t): return float(np.interp(t, self.ts, arr))

    @lru_cache(maxsize=20000)
    def _base(self, tick):
        """The pose the body is reaching for at a moment (before springs). tick = t*120."""
        t = tick / 120.0
        u = self._i(self.phase, t); w = self._i(self.w, t); v = self._i(self.v, t)
        C = self.C0 * (0.6 + 0.4 * min(1, abs(v) / 120)); half = C * 0.6 / 2
        laugh = float(keys(self.laugh, t)); up = float(keys(self.lookup, t))
        a = {j: float(keys(self.poses[j], t)) if j in self.poses else 0.0 for j in JOINTS}
        # walk: arms swing against the legs; the body leans into the walk
        rL, _, _ = foot_cycle(u, C); rR, _, _ = foot_cycle(u + 0.5, C)
        a['armR'] += 17 * w * (rR / half) - 7; a['armL'] += 12 * w * (rL / half) + 7
        a['foreR'] += -10 - 14 * w * max(0, -rR / half); a['foreL'] += -8 - 12 * w * max(0, -rL / half)
        a['pelvis'] += 3.5 * w; a['chest'] += 1.5 * w * math.sin(2 * math.pi * u) * 0  # (twist reads poorly in 3/4)
        # idle life: breathing and slow weight shifts
        a['chest'] += 0.8 * math.sin(t * 2 * math.pi / 3.7) * (1 - w)
        a['armR'] += 1.2 * math.sin(t * 2 * math.pi / 3.7 + 0.6) * (1 - w); a['armL'] -= 1.0 * math.sin(t * 2 * math.pi / 3.7 + 0.8) * (1 - w)
        # looking up leans the head back first, chest a little
        a['head'] += -9 * up; a['chest'] += -3 * up
        # laughing: head tips back, chest opens, arms out and up with the giggles
        ch = laugh * (0.55 + 0.45 * math.sin(t * 2 * math.pi * 0.8)) * abs(math.sin(t * 2 * math.pi * 3.6))
        a['head'] += -7 * laugh - 4 * ch; a['chest'] += -4 * laugh - 2 * ch
        a['armR'] += -24 * laugh - 6 * ch; a['foreR'] += -38 * laugh; a['armL'] += 20 * laugh + 5 * ch; a['foreL'] += 30 * laugh
        sit = float(keys(self.sit, t))
        a['armR'] += -18 * sit; a['foreR'] += -45 * sit; a['armL'] += 10 * sit; a['foreL'] += -30 * sit; a['chest'] += 4 * sit
        sl = float(keys(self.sleep, t))   # asleep: head nods down, slow deep breaths
        a['head'] += 15 * sl + 2.0 * sl * math.sin(t * 2 * math.pi / 4.4 + 0.5); a['chest'] += 7 * sl + 1.6 * sl * math.sin(t * 2 * math.pi / 4.4)
        drop = float(keys(self.crouch, t)) + 5 * ch + 6 * w + 74 * sit
        sway = 3.0 * math.sin(t * 2 * math.pi / 4.6) * (1 - w)
        bob = 4.5 * w * math.cos(4 * math.pi * (u - 0.07))
        return np.array([a[j] for j in JOINTS] + [sway, drop + bob, laugh, up, ch])

    def depth(self, t, t0=0.0):
        """How far toward the camera (screen units, rig scale) the walk has carried him since t0."""
        return (self._i(self.dist, t) - self._i(self.dist, t0)) * FY * self.depth_scale

    def base(self, t): return self._base(int(round(t * 120)))

    def at(self, t):
        b0 = self.base(t)
        # each group chases the target with its own spring: core stiff, head softer, arms looser, forearms loosest
        core = spring(lambda x: self.base(x)[[0, 1, 7, 8]], t, freq=3.2, zeta=0.75)
        head = spring(lambda x: self.base(x)[[2, 8]], t, freq=2.4, zeta=0.6)
        arms = spring(lambda x: self.base(x)[[3, 5]], t, freq=2.0, zeta=0.45)
        fore = spring(lambda x: self.base(x)[[4, 6]], t, freq=1.7, zeta=0.38)
        ang = {'pelvis': core[0], 'chest': core[1], 'head': head[0] - 0.5 * (core[0] + core[1]) + 0.6 * (head[1] - core[3]),
               'armL': arms[0], 'foreL': fore[0], 'armR': arms[1], 'foreR': fore[1]}
        root = (core[2], core[3] + 4.0)
        # legs: planted feet + IK from the actual pelvis
        u = self._i(self.phase, t); w = self._i(self.w, t); v = self._i(self.v, t)
        C = self.C0 * (0.6 + 0.4 * min(1, abs(v) / 120))
        sitw = float(keys(self.sit, t))
        pel = np.array([root[0], PELVIS_Y + root[1]]); pa = math.radians(ang['pelvis'])
        cR, sR = math.cos(-pa), math.sin(-pa)
        for side, off in (('L', 0.0), ('R', 0.5)):
            rel, h, roll = foot_cycle(u + off, C, lift=14.0)
            fx = REST[side] + rel * w * FX; fy = -ANKLE_H - h * w + rel * w * FY
            hg = float(keys(self.hang, t))
            if hg > 0:   # hanging in the air from the strings: legs dangle and swing a little, knees soft
                fx += hg * (10 * math.sin(t * 1.9 + off * 2.6) - 4); fy -= hg * (8 + 6 * math.sin(t * 1.9 + off * 2.6 + 1.0))
            if sitw > 0:   # sitting on the ground: feet forward, knees up
                sx_, sy_ = (14.0, -16.0) if side == 'L' else (50.0, -12.0)
                fx += (sx_ - fx) * sitw; fy += (sy_ - fy) * sitw
            d = np.array([fx, fy]) - pel; loc = np.array([d[0] * cR - d[1] * sR, d[0] * sR + d[1] * cR])
            th1, th2 = ik2(HIP[side], loc, L_THIGH, L_SHIN, bend=1)
            ang['leg' + side] = th1; ang['shin' + side] = th2
            ang['boot' + side] = -(ang['pelvis'] + th1 + th2) - roll * w + 22 * hg
        # face
        up = float(keys(self.lookup, t)); lx = float(keys(self.look_x, t))
        eye = spring(lambda x: np.array([float(keys(self.look_x, x)), float(keys(self.lookup, x))]), t, freq=6.0, zeta=0.9)
        turn_speed = abs(spring(lambda x: self.base(x)[[2]], t, freq=6, zeta=1.0)[0] - head[0])
        extra = ()
        bl = blink_amt(t, self.seed)
        if turn_speed > 2.5: bl = min(bl, 0.1)          # we blink when the head turns quickly
        bl = min(bl, 1 - float(keys(self.sleep, t)))
        laugh = float(keys(self.laugh, t)); talk = float(keys(self.talk, t))
        # follow-through: hair and scarf are pushed by how the head and body actually moved
        hb = spring(lambda x: self.base(x)[[7, 8]], t, freq=2.8, zeta=0.3) - core[2:4]
        vel = self._i(self.v, t)
        scarf = np.array([-0.25 * vel / self.k * 0.0, 0.0]) + spring(lambda x: self.base(x)[[7, 8]], t, freq=1.4, zeta=0.35) - core[2:4]
        A = dict(ang=ang, root=root, look=(eye[0], -eye[1]), blink=bl, laugh=laugh, talk=talk,
                 wind=0.75 + 0.35 * w + float(keys(self.windk, t)), hair=np.array([hb[0] * 1.5, hb[1] * 2.0]), scarf=scarf * np.array([3.0, 3.0]),
                 brows=float(keys(self.brows, t)))
        if talk > 0.05:
            A['mo'] = talk * (0.25 + 0.75 * abs(math.sin(t * 9.0)) * (0.6 + 0.4 * math.sin(t * 3.1)))
        for (t0, t1, m) in self.mouth:
            if t0 <= t < t1: A['mouth'] = m
        return A

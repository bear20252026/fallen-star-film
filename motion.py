# Motion toolkit: springs (overlap and follow-through), planted-foot gaits, two-bone IK, smooth paths, blinks.
# Everything is a pure function of time so frames can be rendered in any order, in parallel.
import numpy as np, math

def ss(u): u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)
def ss5(u): u = min(1.0, max(0.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)

def keys(ks, t, ease=ss):
    """Eased keyframes [(t, value)] where each key is a held pose (ease in and out of every key)."""
    if t <= ks[0][0]: return np.asarray(ks[0][1], np.float64)
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = ease((t - t0) / max(1e-6, t1 - t0)); v0 = np.asarray(v0, np.float64); v1 = np.asarray(v1, np.float64)
            return v0 + (v1 - v0) * u
    return np.asarray(ks[-1][1], np.float64)

def flow(ks, t):
    """Keyframes passed THROUGH with continuous velocity (monotone cubic), easing only at the first and last key.
    Use for cameras and travel so nothing stops dead at a middle key."""
    T = np.array([k[0] for k in ks], np.float64); V = np.array([np.atleast_1d(k[1]) for k in ks], np.float64)
    if t <= T[0]: return V[0] if V.shape[1] > 1 else V[0, 0]
    if t >= T[-1]: return V[-1] if V.shape[1] > 1 else V[-1, 0]
    n = len(T); d = np.diff(V, axis=0) / np.diff(T)[:, None]
    m = np.zeros_like(V)
    for i in range(1, n - 1):
        a, b = d[i - 1], d[i]
        m[i] = np.where(a * b > 0, 2 / (1 / np.where(a == 0, 1e-9, a) + 1 / np.where(b == 0, 1e-9, b)), 0)
    i = int(np.searchsorted(T, t) - 1); h = T[i + 1] - T[i]; u = (t - T[i]) / h
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
    r = h00 * V[i] + h10 * h * m[i] + h01 * V[i + 1] + h11 * h * m[i + 1]
    return r if V.shape[1] > 1 else r[0]

def travel(t, t0, t1, x0, x1, acc=0.7, dec=0.9):
    """Distance along a move with a trapezoid speed profile: speeds up, cruises, slows down. Velocity is continuous."""
    if t <= t0: return x0
    if t >= t1: return x1
    D = t1 - t0; a, b = min(acc, D / 2), min(dec, D / 2)
    vmax = (x1 - x0) / (D - a / 2 - b / 2); u = t - t0
    if u < a: return x0 + vmax * (u * u / (2 * a))
    if u < D - b: return x0 + vmax * (a / 2 + (u - a))
    w = D - u; return x1 - vmax * (w * w / (2 * b))

def spring(fn, t, freq=2.5, zeta=0.55, T=None, dt=1 / 120):
    """Value of a damped spring that has been chasing fn(time) up to time t. Gives drag, overshoot and settle."""
    if T is None: T = min(3.0, 3.5 / (zeta * 2 * math.pi * freq) + 0.4)
    w = 2 * math.pi * freq; tt = t - T
    x = np.asarray(fn(tt), np.float64).copy(); v = np.zeros_like(x)
    n = int(T / dt)
    for i in range(n):
        tt += dt; g = np.asarray(fn(tt), np.float64)
        v += (w * w * (g - x) - 2 * zeta * w * v) * dt; x += v * dt
    return x

def deriv(fn, t, h=1 / 96):
    return (np.asarray(fn(t + h)) - np.asarray(fn(t - h))) / (2 * h)

def ik2(hip, foot, l1, l2, bend=1):
    """Two-bone IK in a space where a bone at angle 0 points down (+y) and positive angles swing the tip toward -x.
    bend=+1 puts the knee toward +x. Returns (thigh angle, shin angle relative to thigh) in degrees."""
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]
    D = max(1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    phi = math.atan2(-dx, dy)
    a1 = math.acos(max(-1, min(1, (l1 * l1 + D * D - l2 * l2) / (2 * l1 * D))))
    b = math.acos(max(-1, min(1, (l1 * l1 + l2 * l2 - D * D) / (2 * l1 * l2))))
    th1 = phi - bend * a1; th2 = bend * (math.pi - b)
    return math.degrees(th1), math.degrees(th2)

def foot_cycle(u, C, duty=0.6, lift=12.0):
    """One foot in a gait cycle of length C (body travel per full cycle). u in [0,1).
    Stance: foot is fixed on the ground (moves backward relative to the body at exactly body speed).
    Swing: foot lifts fast, travels forward, and reaches down to meet the ground. Returns (rel_x, height, roll)."""
    u = u % 1.0; half = C * duty / 2
    if u < duty:
        k = u / duty; rel = half - k * C * duty; h = 0.0
        roll = max(0.0, (k - 0.75) / 0.25) * 18          # heel peels off at the end of stance
        roll -= max(0.0, (0.12 - k) / 0.12) * 10          # toe still up just after heel strike
    else:
        v = (u - duty) / (1 - duty)
        rel = -half + ss(v) * 2 * half
        h = lift * math.sin(math.pi * min(1, v * 1.15)) ** 0.9 * (1 - 0.25 * v)
        roll = 18 * (1 - v) - 10 * ss((v - 0.6) / 0.4)
    return rel, h, roll

def blink_amt(t, seed=1, rate=0.28, extra=()):
    """1 = open, 0 = closed. Natural blinks (fast close, slower open) at irregular times plus forced ones."""
    r = np.random.default_rng(seed); times = []; tt = r.random() * 2
    while tt < 4000:
        times.append(tt); tt += 1.6 + r.exponential(1 / rate)
        if r.random() < 0.15: times.append(tt - 1.4 + 0.25)   # occasional double blink
    times = np.array(times + list(extra))
    d = t - times; d = d[(d > -0.01) & (d < 0.3)]
    if len(d) == 0: return 1.0
    x = d.min()
    if x < 0.06: return 1 - x / 0.06
    return min(1.0, (x - 0.06) / 0.16)

# S10 · The star stairs (300 s). Beyond the storm: a spiral staircase of stars rising into deep blue.
# Moth carries them up, step by step; every star they pass chimes hello and Pip chimes back.
# At the top, one empty gap. They put Pip in its place. It fits. But Pip is still faint. Nobody down there has seen it yet. They wait.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import RotActor, StarStream, GoldTrail, BOY_LAST, SHEEP_LAST
from props3 import box
from pip import draw_pip
from moth import draw_moth

class S10(Scene):
    DURATION = 300.0

SC = S10()
SPACE = World('stairs', place='space')
SC.worlds = [(0, 1e9, SPACE)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

T_ARRIVE, T_UP0, T_UP1, T_OPEN, T_LIFT, T_PLACE, T_FIT, T_WAIT = 14.0, 62.0, 178.0, 188.0, 196.0, 203.0, 209.0, 240.0
MS = 1.25
# the staircase: steps on a spiral, each one a little star
N_STEP, STEP_H, STEP_A, R_SP, CX, BASE_Y = 34, 60.0, 0.42, 560.0, 1440.0, 930.0
GAP_H = 2470.0                                   # where Pip's empty place is (virtual height)
def climb(t):
    pre = -380 * (1 - ss(t / 16))                 # the opening tilt up the stairs
    return pre + 1750 * ss((t - T_UP0) / (T_UP1 - T_UP0)) * 0.94 + 1750 * 0.06 * ((t - T_UP0) / (T_UP1 - T_UP0) if T_UP0 < t < T_UP1 else (1.0 if t >= T_UP1 else 0.0))
def vy(h, t): return BASE_Y - (h - climb(t))   # virtual height -> world y
GROUP_H0 = BASE_Y - 560 + 0.0                     # the group's height above the stairs' foot when climb = 0
def gpos(t):
    hg = climb(t) + GROUP_H0
    th = hg / STEP_H * STEP_A
    u = ss((t - T_UP0 + 6) / 8) * (1 - ss((t - T_UP1 + 4) / 8))
    xa = 1150 + 180 * ss((t - T_ARRIVE) / 18) - 900 * (1 - ss((t - T_ARRIVE + 2) / 16))
    xc = CX + 0.62 * R_SP * math.cos(th) - 120
    xt = 1260 + 60 * ss((t - T_LIFT) / 6)
    x = xa if t < T_UP0 else (xa * (1 - u) + xc * u if t < T_UP1 - 4 else xc * (1 - u) + xt * u)
    if t > T_UP1 + 4: x = xt
    y = 560 - 40 * ss((t - T_UP1) / 8) + 14 * math.sin(t * 1.2) - 18 * math.sin(math.pi * ((t - T_UP0) * 0.5 % 1.0)) * (T_UP0 < t < T_UP1)
    return x, y
def gtilt(t):
    a, b = gpos(t - 0.25), gpos(t + 0.25)
    return float(np.clip((b[0] - a[0]) * 0.003, -0.25, 0.25))
STEPS = [dict(k=k, h=k * STEP_H, th=k * STEP_A + 1.2) for k in range(N_STEP)]
# when the group passes each step (chime hello)
_tt = np.linspace(0, 300, 3001); _hh = np.array([climb(x) + GROUP_H0 for x in _tt])
for S_ in STEPS:
    i = np.argmax(_hh >= S_['h'] + 30); S_['tp'] = float(_tt[i]) if _hh[i] >= S_['h'] + 30 and _tt[i] > T_UP0 - 2 else 1e9

def pip_glow(t):   # in the box: a little warm; out: faint and small
    base = 0.55 + 0.05 * math.sin(t * 2)
    for S_ in STEPS:
        if 0 < t - S_['tp'] - 0.35 < 0.9: base += 0.3 * math.sin(math.pi * (t - S_['tp'] - 0.35) / 0.9)
    return base

# ---------------------------------------------------------------- the boy and the sheep, in Moth's arms
BOY = BoyAnim(segs([], 0), k=1.6, t_end=300, hang=[(0, 1)], wind=[(0, 0.35)],
    poses={'armR': [(0, -30), (40, -30), (41, -120), (47, -120), (48, -30), (T_OPEN, -30), (T_OPEN + 1, -50), (T_LIFT, -60), (T_LIFT + 2, -140), (T_PLACE + 2, -140),
                    (T_PLACE + 4, -30)],
           'foreR': [(0, -40), (40, -40), (41, -10), (47, -10), (48, -40), (T_OPEN + 1, -70), (T_LIFT + 2, -20), (T_PLACE + 4, -40)],
           'armL': [(0, 40), (T_LIFT, 40), (T_LIFT + 2, 130), (T_PLACE + 2, 130), (T_PLACE + 4, 40)], 'foreL': [(0, 30), (T_LIFT + 2, 20), (T_PLACE + 4, 30)],
           'chest': [(0, 0), (T_WAIT + 10, 0), (T_WAIT + 12, 6), (290, 6)]},
    look_x=[(0, 0.6), (30, 0.3), (T_UP0, 0.6), (100, 0.9), (140, 0.4), (T_UP1, 0.5), (T_OPEN, 0.2), (T_LIFT, 0.3), (T_FIT + 2, 0.5), (T_WAIT, 0.2), (300, 0.1)],
    lookup=[(0, 0.2), (25, 0.9), (55, 0.9), (T_UP0, 0.5), (100, 0.2), (140, 0.6), (T_UP1, 0.9), (T_OPEN, -0.6), (T_LIFT, 0.8), (T_FIT + 3, 0.7),
            (T_WAIT, -0.9), (300, -0.9)],
    brows=[(0, 0.2), (25, 0.8), (40, 0.2), (T_UP1, 0.3), (T_FIT + 4, 0.0), (T_WAIT, 0.8), (300, 1.0)],
    mouth=[(24, 27, 'open'), (T_FIT, T_FIT + 1.2, 'open')],
    laugh=[(0, 0), (75, 0), (76, 0.7), (82, 0.3), (110, 0.3), (111, 0.8), (118, 0.4), (150, 0.4), (151, 0.8), (158, 0.3), (T_FIT, 0.3), (T_FIT + 1.5, 0.9),
           (T_FIT + 8, 0.6), (T_WAIT - 4, 0.0)],
    talk=[(43.0, 0), (43.1, 1), (46.5, 1), (46.6, 0)])
boy = BoyActor(BOY, 0, facing=[(0, 1)]); boy.shadow = False; boy.cast = dict(cast=0.0)
boy.foot = lambda t: (gpos(t)[0] - 105, gpos(t)[1] + 245)
boyR = RotActor(boy, lambda t: math.degrees(gtilt(t)) * 0.5 + 2.5 * math.sin(t * 0.9), piv_h=380)
SHEEP = SheepAnim(segs([], 0), k=1.6, t_end=300, lift=[(0, 24)],
    head=[(0, 0), (25, -12), (55, -12), (T_UP0, 0)] + [(tt, v) for S_ in STEPS[3:30:4] if S_['tp'] < 300 for (tt, v) in ((S_['tp'], 0), (S_['tp'] + 0.3, 12), (S_['tp'] + 0.8, 0))]
         + [(T_OPEN, 10), (T_LIFT, -14), (T_FIT + 3, -10), (T_WAIT, 14), (300, 14)],
    look=[(0, (0.6, -0.3)), (25, (0.3, -1.0)), (55, (0.6, -0.8)), (T_UP0, (0.9, -0.2)), (120, (-0.6, -0.4)), (T_UP1, (0.4, -0.9)), (T_OPEN, (-0.6, 0.3)),
          (T_LIFT, (-0.3, -1.0)), (T_WAIT, (-0.3, 1.0)), (300, (-0.2, 1.0))],
    laugh=[(0, 0), (76, 0), (77, 0.8), (84, 0), (130, 0), (131, 0.8), (138, 0), (T_FIT, 0), (T_FIT + 1.5, 1), (T_FIT + 9, 0.7), (T_WAIT - 4, 0)],
    tail=[(0, 0)] + osc(T_FIT + 1, T_FIT + 9, 0.3, -24, 24) + [(T_FIT + 9.3, 0)], sleep=[(0, 0)])
sheep = SheepActor(SHEEP, 0, facing=[(0, 1)]); sheep.shadow = False; sheep.cast = dict(cast=0.0)
sheep.foot = lambda t: (gpos(t)[0] + 70, gpos(t)[1] + 262)
sheepR = RotActor(sheep, lambda t: math.degrees(gtilt(t)) * 0.6 + 3 * math.sin(t * 1.1 + 1), piv_h=120)

WATCH = {}
class MothActor(Actor):
    height = 600; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0)
    def foot(self, t): return gpos(t)
    def draw(self, f, X, Y, s, t, W_, C):
        out = {}
        draw_moth(f, X, Y, s * MS, t, flip=1, open_=1, flap=float(keys([(0, 0.8), (T_UP0, 1.0), (T_UP1, 1.0), (T_UP1 + 3, 0.5)], t)),
                  flap_speed=float(keys([(0, 1.2), (T_UP0, 1.6), (T_UP1, 1.6), (T_UP1 + 3, 0.7)], t)),
                  mood=float(keys([(0, 0.7), (25, 1.0), (T_WAIT, 0.5)], t)), surprise=float(keys([(0, 0), (22, 0), (24, 1), (34, 0.3), (40, 0)], t)),
                  laugh=float(keys([(0, 0), (90, 0), (91, 0.8), (98, 0), (T_FIT + 1, 0), (T_FIT + 2, 1), (T_FIT + 9, 0)], t)),
                  look=(float(keys([(0, 0.6), (25, 0.2), (T_UP0, 0.8), (T_UP1, 0.3), (T_LIFT, -0.5), (T_WAIT, 0.0)], t)),
                        float(keys([(0, 0.0), (25, -0.9), (55, -0.8), (T_UP0, -0.4), (T_UP1, -0.8), (T_OPEN, 0.7), (T_LIFT, -0.8), (T_WAIT, 1.0)], t))),
                  hold=(0, 120), glow_amt=0.4, light=W_.light, rim=W_.rim, rim_w=0.55, out=out, tilt=gtilt(t))
        WATCH['moth'] = out
moth = MothActor()
def box_fn(f, X, Y, s, t, W_, C):
    hr = BOY_LAST.get('handR')
    if hr is None: return
    sb = 0.85 * s; bx, by = hr[0] + 5 * sb, hr[1] + 168 * sb
    if t > T_LIFT: return
    box(f, bx, by, sb, light=W_.light, rim=W_.rim, glow_amt=pip_glow(t) if t < T_OPEN else max(0.1, 0.5 * (1 - ss((t - T_OPEN) / 3))), t=t, handle=True,
        tilt=3 * math.sin(t * 2), grey=0.35)
    WATCH['box'] = (bx, by - 70 * sb)
boxp = Prop(box_fn, lambda t: (gpos(t)[0], gpos(t)[1] + 300), height=150, tuft_w=0); boxp.shadow = False; boxp.cast = dict(cast=0.0)
SC.actors = [moth, boyR, sheepR, boxp]

# ---------------------------------------------------------------- the staircase, Pip, and the top
GAP_X = 1720
TOP = [(GAP_X - 330, GAP_H + 60, 30), (GAP_X - 170, GAP_H + 190, 26), (GAP_X + 180, GAP_H + 170, 32), (GAP_X + 360, GAP_H + 40, 28), (GAP_X + 120, GAP_H - 120, 22),
       (GAP_X - 210, GAP_H - 140, 24), (GAP_X + 10, GAP_H + 330, 20)]
def draw_step(f, C, t, S_, front):
    th = S_['th']; dep = math.sin(th)
    if (dep > 0.35) != front: return
    wx = CX + R_SP * math.cos(th); wy = vy(S_['h'], t)
    X, Y = C.to_screen(wx, wy)
    if not (-120 < X < W + 120 and -120 < Y < H + 160): return
    z = C.z; sz = 24 * z * (0.75 + 0.3 * dep)
    a = t - S_['tp']; hi = math.exp(-a * 1.6) if a > 0 else 0.0
    # a soft glowing tread under the star
    glow(f, X, Y + sz * 1.3, sz * 3.2, '#9ec4ff', 0.18 + 0.1 * hi)
    draw_pip(f, X, Y - 10 * hi * z, sz, t=t + S_['k'] * 1.3, light=0.7 + 0.25 * hi, face='laugh' if hi > 0.3 else 'open', laugh=hi, rot=0.15 * math.sin(t * 0.7 + S_['k']),
             squash=-0.18 * hi * math.sin(a * 9) if a > 0 else 0, glow_amt=0.6, look=(-0.6, -0.3))
def draw_top(f, C, t):
    z = C.z
    for (x, h, sz) in TOP:
        X, Y = C.to_screen(x, vy(h, t))
        if -80 < Y < H + 80:
            fit = math.exp(-max(0, t - T_FIT) * 1.2) if t > T_FIT else 0
            draw_pip(f, X, Y, sz * z * 1.0, t=t + x * 0.01, light=0.85, face='laugh' if fit > 0.3 else 'open', laugh=fit, glow_amt=0.5, look=((GAP_X - x) * 0.003, 0))
    X, Y = C.to_screen(GAP_X, vy(GAP_H, t))
    if t < T_FIT + 0.5 and -80 < Y < H + 80:   # the empty place: a faint dotted outline
        for k in range(10):
            a = k / 10 * 6.283 - 1.5708; rr = (26 if k % 2 == 0 else 12) * z
            glow(f, X + math.cos(a) * rr, Y + math.sin(a) * rr, 2.2 * z, '#cfe0ff', 0.5 * (0.6 + 0.4 * math.sin(t * 2 + k)))
def pip_state(t):
    """Pip out of the box: floats up to the boy's hands, then into its place."""
    if t < T_OPEN + 1: return None
    gx, gyv = GAP_X, vy(GAP_H, t)
    if t < T_LIFT + 2:
        b = WATCH.get('box_w') or (gpos(t)[0] - 40, gpos(t)[1] + 300)
        u = ss((t - T_OPEN - 1) / 6)
        hx, hy = gpos(t)[0] - 40, gpos(t)[1] + 120
        return (b[0] + (hx - b[0]) * u, b[1] + (hy - b[1]) * u)
    u = ss((t - T_LIFT - 2) / (T_FIT - T_LIFT - 2))
    hx, hy = gpos(t)[0] - 40, gpos(t)[1] + 120 - 60 * ss((t - T_LIFT) / 2)
    return (hx + (gx - hx) * u, hy + (gyv - hy) * u - 40 * math.sin(math.pi * u))
STREAM = StarStream(n=170, seed=23); TRAIL = GoldTrail()
def sky_fx(f, C, t, W_):
    sp = float(keys([(0, 0.4), (T_UP0, 0.4), (T_UP0 + 6, 0.9), (T_UP1 - 4, 0.9), (T_UP1 + 2, 0.08)], t))
    STREAM.draw(f, t, speed=sp, dirx=-0.15, diry=1.0, amt=0.7)
    if t > T_WAIT + 4:   # far below: the Earth, small and blue
        a = ss((t - T_WAIT - 4) / 10); X, Y = C.to_screen(760, 1150)
        glow(f, X, Y, 90 * C.z, '#6aa8ff', 0.35 * a)
        g = f.copy(); cv2.circle(g, (int(X * 4), int(Y * 4)), int(44 * C.z * 4), (0.23, 0.42, 0.72), -1, cv2.LINE_AA, shift=2)
        cv2.circle(g, (int((X - 8 * C.z) * 4), int((Y - 6 * C.z) * 4)), int(17 * C.z * 4), (0.35, 0.62, 0.42), -1, cv2.LINE_AA, shift=2)
        f[:] = f * (1 - a) + g * a
    for S_ in STEPS: draw_step(f, C, t, S_, False)
    draw_top(f, C, t)
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    for S_ in STEPS: draw_step(f, C, t, S_, True)
    p = pip_state(t)
    if p is not None:
        X, Y = C.to_screen(*p)
        placed = t > T_FIT
        lt = (0.5 if t < T_FIT else 0.32 + 0.3 * (1 - ss((t - T_FIT - 1) / 5))) + 0.05 * math.sin(t * 1.7)
        sz = (34 if not placed else 34 - 6 * ss((t - T_FIT) / 6)) * C.z
        draw_pip(f, X, Y, sz, t=t, light=lt, face='open' if t < T_WAIT else 'closed', laugh=0.0 if not (T_FIT < t < T_FIT + 3) else 0.6,
                 glow_amt=0.35, look=(0.0, 0.8 if t > T_WAIT else -0.4))
        if T_FIT - 0.2 < t < T_FIT + 1.5:
            glow(f, X, Y, 120 * z * (1 + (t - T_FIT)), '#fff2c0', 0.6 * (1 - abs(t - T_FIT - 0.3) / 1.2))
    for S_ in STEPS:   # Pip chimes back: a little ring of light from the box
        a = t - S_['tp'] - 0.35
        if 0 < a < 0.9 and 'box' in WATCH and t < T_OPEN:
            X, Y = WATCH['box']; glow(f, X, Y, 70 * z * (1 + a), '#ffd870', 0.4 * (1 - a / 0.9))
SC.sky_fx, SC.front_fx = sky_fx, front_fx

# ---------------------------------------------------------------- shots
def follow(ox, oy, z, k=0.7):
    return lambda t: (gpos(t)[0] * k + 1440 * (1 - k) + ox, gpos(t)[1] * k + 560 * (1 - k) + oy, z)
def gap_cam(z, oy=0):
    return lambda t: (GAP_X - 40, vy(GAP_H, t) + 40 + oy, z)
BOYH, SHEEPH, MOTHH = (-105, 80), (130, 130), (0, -40)
SC.shots = [
    (0,   [(0, (1440, 600, 0.72)), (14, (1440, 560, 0.75))], 0.0),
    (14,  follow(0, 60, 0.85, 0.4), 0.0),
    (30,  follow(*BOYH, 2.8), 0.0),
    (38,  follow(*MOTHH, 2.1), 0.0),
    (48,  [(48, (1440, 520, 0.72)), (T_UP0, (1440, 500, 0.75))], 0.0),
    (T_UP0, follow(80, 80, 1.0), 0.0),
    (74,  follow(*BOYH, 2.6), 0.0),
    (84,  follow(160, 40, 1.3), 0.0),
    (100, follow(0, 100, 0.8), 0.0),
    (112, follow(*SHEEPH, 2.6), 0.0),
    (122, follow(80, 80, 1.1), 0.0),
    (140, follow(*MOTHH, 2.1), 0.0),
    (150, follow(0, 100, 0.85), 0.0),
    (166, follow(80, 60, 1.2), 0.0),
    (T_UP1, follow(150, -40, 0.8), 0.0),
    (T_OPEN, follow(-60, 170, 2.0), 0.0),
    (T_LIFT + 1, follow(120, -80, 1.1), 0.0),
    (T_FIT - 2, gap_cam(2.2), 0.0),
    (T_FIT + 4, follow(*BOYH, 2.6), 0.0),
    (222, follow(150, -60, 0.95), 0.0),
    (T_WAIT, gap_cam(2.4), 0.0),
    (250, follow(-40, 40, 1.3), 0.0),
    (262, [(262, (1350, 640, 0.8)), (300, (1300, 700, 0.7))], 0.0),
]
SC.subs = [(43.0, 46.6, 'Look. They go all the way up.', '看。它们一直通到最上面。')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, T_UP0, 'wonder', 0.8), (T_UP0, T_UP1, 'playful', 0.8), (T_UP1, T_FIT, 'wonder', 0.75), (T_FIT, T_WAIT, 'warm', 0.75), (T_WAIT, 300, 'night', 0.6)]
SFX = [(0, 'wind', dict(dur=300, gain=0.2)), (24, 'shimmer', dict(dur=10, gain=0.5))]
NOTES = [1047, 1175, 1319, 1397, 1568, 1760, 1976, 2093]
for i, S_ in enumerate(STEPS):
    if S_['tp'] < 300:
        SFX.append((S_['tp'], 'chime', dict(notes=[NOTES[i % 8]], gain=0.35)))
        if i % 2 == 0: SFX.append((S_['tp'] + 0.35, 'chime', dict(notes=[NOTES[(i + 2) % 8] * 2], gain=0.18)))
SFX += [(T_OPEN + 1, 'twinkle', dict(gain=0.4)), (T_FIT, 'chime', dict(notes=[1568, 2093, 2637], gain=0.6)), (T_FIT + 0.2, 'sparkle'), (T_FIT + 1.5, 'giggle', dict(n=14)),
        (T_WAIT, 'shimmer', dict(dur=12, gain=0.25))]

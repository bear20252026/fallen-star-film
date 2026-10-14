# S09 · The meteor storm (300 s). Fast flight in Moth's arms. Rocks, small then big; Moth dodges; the sheep shields the lantern.
# A rock clips them: the lantern is knocked loose, the boy catches it, and Pip is grey and silent. In the quiet, drifting,
# they tell their happiest memories and laugh through tears. A tiny flicker. A chime. Pip is alive.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import RotActor, StarStream, GoldTrail, BOY_LAST, SHEEP_LAST
from props3 import box, meteor
from props import draw_rose
from boy2 import draw_boy
from sheep import draw_sheep
from moth import draw_moth

class S09(Scene):
    DURATION = 300.0

SC = S09()
SPACE = World('storm', place='space')
SC.worlds = [(0, 1e9, SPACE)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

T_STORM, HIT, CATCH, T_QUIET = 60.0, 165.0, 170.0, 176.0
T_B1, T_B2, T_B3, T_LAUGH, T_FLICK, T_ALIVE = 204.0, 221.0, 238.0, 253.0, 271.0, 280.0
MS = 1.25
DODGE = [(0, 0, 0), (60, 0, 0), (63, -70, -120), (67, -50, -105), (71, 90, 60), (75, 70, 45), (82, -40, -160), (86, -25, -140), (93, 100, 80), (97, 80, 60),
         (105, -90, -60), (109, -70, -45), (117, 50, -170), (121, 35, -150), (129, -70, 90), (133, -50, 70), (141, 70, -100), (145, 50, -80), (153, -20, 30),
         (157, 0, 0), (HIT, 0, 0)]
def jolt(t): return 70 * math.exp(-max(0, t - HIT) * 1.2) * math.sin(max(0, t - HIT) * 6) if t > HIT else 0.0
def gpos(t):
    dx = float(keys([(a, b) for a, b, c in DODGE], t)); dy = float(keys([(a, c) for a, b, c in DODGE], t))
    fl = 1 - 0.7 * ss((t - T_QUIET) / 10) + 0.7 * ss((t - T_ALIVE) / 10)
    return 1440 + dx + 30 * ss((t - 290) / 10), 560 + dy + jolt(t) + 14 * math.sin(t * 1.3) * fl + 8 * math.sin(t * 0.5)
def gtilt(t):
    a, b = gpos(t - 0.25), gpos(t + 0.25)
    return float(np.clip((b[0] - a[0]) * 0.0035 + (b[1] - a[1]) * 0.001, -0.35, 0.35)) + (0.25 * math.exp(-max(0, t - HIT) * 1.5) * math.sin((t - HIT) * 7) if t > HIT else 0)

def glow_pip(t):   # the lantern: warm, then nothing, then a flicker, then alive
    if t < HIT: return 0.45 + 0.06 * math.sin(t * 2) - 0.15 * ss((t - 140) / 20)
    g = 0.0
    for tf in (T_FLICK + 1.5, T_FLICK + 4, T_FLICK + 6.5):
        if tf - 0.3 < t < tf + 0.8: g = max(g, 0.35 * math.sin(math.pi * (t - tf + 0.3) / 1.1))
    return max(g, 0.85 * ss((t - T_ALIVE) / 3) * (0.85 + 0.15 * math.sin(t * 5)))
def grey(t): return 0.3 if t < HIT else 1 - min(1, glow_pip(t) * 1.3) if t > T_FLICK else 1.0

# ---------------------------------------------------------------- the boy, held in Moth's arm
BOY = BoyAnim(segs([], 0), k=1.6, t_end=300, hang=[(0, 1)], wind=[(0, 0.7), (T_QUIET, 0.7), (186, 0.15), (T_ALIVE, 0.15), (288, 0.5)],
    poses={'armR': [(0, -30), (HIT, -30), (HIT + 2, -90), (CATCH - 1, -60), (CATCH, -40), (300, -40)],
           'foreR': [(0, -40), (HIT, -40), (CATCH - 1, -10), (CATCH, -70), (300, -70)],
           'armL': [(0, 40), (HIT, 40), (HIT + 1, 70), (CATCH, 50), (300, 50)], 'foreL': [(0, 30), (300, 30)],
           'head': [(0, 0), (T_LAUGH, 0)] + osc(T_LAUGH + 1, T_LAUGH + 8, 0.6, -6, 6) + [(T_LAUGH + 8.4, 0)]},
    look_x=[(0, 0.8), (40, 0.6), (T_STORM, 0.9), (100, 0.4), (130, 1.0), (HIT, 0.3), (CATCH, 0.4), (T_QUIET, 0.4), (T_B1, -0.2), (215, 0.5),
            (T_B2, 0.2), (T_B3, 0.7), (T_LAUGH, 0.5), (T_FLICK, 0.5), (300, 0.8)],
    lookup=[(0, 0.0), (T_STORM, 0.2), (HIT, -0.6), (CATCH, -0.7), (T_QUIET, -0.6), (T_B1, 0.4), (215, 0.6), (T_B2, 0.6), (T_B3, 0.0), (T_LAUGH, 0.3),
            (T_FLICK, -0.7), (300, 0.3)],
    brows=[(0, 0.2), (T_STORM, 0.9), (HIT, 1.0), (T_QUIET, 1.0), (T_B1, 0.6), (T_LAUGH, 0.6), (T_FLICK, 1.0), (T_ALIVE + 1, 0.0)],
    mouth=[(HIT, HIT + 1.5, 'open'), (178, T_B1, 'sad'), (T_ALIVE, T_ALIVE + 1.2, 'open')],
    talk=[(T_B1 + 1.5, 0), (T_B1 + 1.6, 1), (T_B1 + 7, 1), (T_B1 + 7.1, 0), (T_B3 + 4, 0), (T_B3 + 4.1, 1), (T_B3 + 9.4, 1), (T_B3 + 9.5, 0)],
    laugh=[(0, 0), (40, 0), (41, 0.6), (45, 0), (T_LAUGH, 0), (T_LAUGH + 1, 0.9), (264, 0.8), (266, 0.2), (T_ALIVE, 0.2), (T_ALIVE + 1.2, 1), (300, 0.9)])
boy = BoyActor(BOY, lambda t: gpos(t)[1] + 245, facing=[(0, 1)]); boy.shadow = False; boy.cast = dict(cast=0.0)
boy.foot = lambda t: (gpos(t)[0] - 105, gpos(t)[1] + 245)
boyR = RotActor(boy, lambda t: math.degrees(gtilt(t)) * 0.5 + 3 * math.sin(t * 0.9), piv_h=380)

# ---------------------------------------------------------------- the sheep
SHEEP = SheepAnim(segs([], 0), k=1.6, t_end=300, lift=[(0, 24)],
    paddle=[(0, 0), (HIT, 0), (HIT + 0.2, 1), (HIT + 3, 1), (HIT + 4, 0)],
    head=[(0, 0), (T_STORM, 0), (T_STORM + 3, 16), (HIT, 16), (HIT + 0.5, -14), (CATCH, 10), (T_B3, 10), (T_B3 + 3, 0)],
    look=[(0, (0.6, -0.2)), (30, (0.8, -0.5)), (T_STORM, (0.4, 0.6)), (HIT, (0.0, 0.8)), (HIT + 1, (-0.6, 0.6)), (CATCH, (-0.8, 0.4)), (T_B1, (-0.8, -0.4)),
          (T_B2, (0.0, -0.8)), (T_B3, (-0.4, 0.0)), (T_FLICK, (-0.8, 0.5)), (300, (-0.6, 0.2))],
    laugh=[(0, 0), (T_B3 + 2, 0), (T_B3 + 3, 0.7), (T_LAUGH, 1), (266, 1), (267, 0), (T_ALIVE, 0), (T_ALIVE + 1, 1), (300, 1)],
    tail=[(0, 0)] + osc(T_LAUGH, 264, 0.3, -24, 24) + [(264.3, 0)] + osc(T_ALIVE + 1, 300, 0.3, -26, 26),
    mouth=[(HIT - 0.1, HIT + 1.6, 'open')], sleep=[(0, 0)])
sheep = SheepActor(SHEEP, lambda t: gpos(t)[1] + 262, facing=[(0, 1)]); sheep.shadow = False; sheep.cast = dict(cast=0.0)
sheep.foot = lambda t: (gpos(t)[0] + 70, gpos(t)[1] + 262)
sheepR = RotActor(sheep, lambda t: math.degrees(gtilt(t)) * 0.6 + 4 * math.sin(t * 1.1 + 1), piv_h=120)

# ---------------------------------------------------------------- Moth, carrying them
WATCH = {}
class MothActor(Actor):
    height = 600; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0)
    def foot(self, t): x, y = gpos(t); return (x, y)
    def draw(self, f, X, Y, s, t, W_, C):
        out = {}
        fs = float(keys([(0, 1.4), (T_STORM, 2.0), (HIT, 2.0), (HIT + 2, 0.5), (T_QUIET, 0.35), (T_ALIVE, 0.4), (T_ALIVE + 4, 1.4)], t))
        draw_moth(f, X, Y, s * MS, t, flip=1, open_=1, flap=float(keys([(0, 1), (T_QUIET, 0.7), (190, 0.35), (T_ALIVE, 0.4), (T_ALIVE + 3, 1)], t)), flap_speed=fs,
                  mood=float(keys([(0, 0.8), (T_STORM, 0.5), (HIT, 0.1), (T_B2, 0.4), (T_LAUGH, 0.8), (T_FLICK, 0.4), (T_ALIVE, 1)], t)),
                  surprise=float(keys([(0, 0), (HIT - 0.3, 0), (HIT, 1), (HIT + 2, 0.2), (T_FLICK + 1, 0.2), (T_FLICK + 2, 0.8), (T_ALIVE + 2, 0)], t)),
                  laugh=float(keys([(0, 0), (T_LAUGH + 1, 0), (T_LAUGH + 2, 1), (265, 1), (266.5, 0), (T_ALIVE + 1, 0), (T_ALIVE + 2, 1), (300, 1)], t)),
                  talk=float(keys([(T_B2 + 1, 0), (T_B2 + 1.1, 1), (T_B2 + 5.5, 1), (T_B2 + 5.6, 0)], t)),
                  look=(float(keys([(0, 0.7), (T_STORM, 0.9), (HIT, -0.3), (T_QUIET, -0.5), (T_B2, 0.3), (T_B3, -0.4), (300, 0.5)], t)),
                        float(keys([(0, 0.1), (HIT, 0.8), (T_QUIET, 0.9), (T_B2, -0.6), (T_B3, 0.6), (T_FLICK, 0.9), (300, 0.3)], t))),
                  hold=(0, 120), glow_amt=0.15 + 0.6 * glow_pip(t), light=W_.light, rim=W_.rim, rim_w=0.55, out=out, tilt=gtilt(t))
        WATCH['moth'] = out
moth = MothActor()

# the lantern: in the sheep's mouth, knocked loose, caught by the boy
def box_fn(f, X, Y, s, t, W_, C):
    sb = 0.85 * s
    if t < HIT:
        m = SHEEP_LAST.get('mouth')
        if m is None: return
        bx, by = m[0] - 5 * sb, m[1] + 168 * sb + 6 * s; tilt = 4 * math.sin(t * 5)
        WATCH['fall0'] = (bx, by)
    else:
        hr = BOY_LAST.get('handR')
        u = ss((t - HIT) / (CATCH - HIT))
        sx, sy = C.to_screen(*gpos(t)); f0 = (sx + 110 * s, sy + 330 * s)
        fx, fy = f0[0] - 60 * s * u, f0[1] + 140 * s * math.sin(math.pi * u * 0.9)
        if hr is not None and t > CATCH - 1.0:
            v = ss((t - CATCH + 1.0) / 1.0); hx, hy = hr[0] + 5 * sb, hr[1] + 168 * sb
            fx, fy = fx + (hx - fx) * v, fy + (hy - fy) * v
        bx, by = fx, fy; tilt = (1 - ss((t - CATCH + 0.6) / 0.8)) * 160 * math.sin((t - HIT) * 2.4) + 4 * math.sin(t * 2)
    box(f, bx, by, sb, light=W_.light, rim=W_.rim, glow_amt=glow_pip(t), t=t, handle=True, tilt=tilt, grey=grey(t))
    WATCH['box'] = (bx, by - 60 * sb)
boxp = Prop(box_fn, lambda t: (gpos(t)[0], gpos(t)[1] + 300), height=150, tuft_w=0)
boxp.shadow = False; boxp.cast = dict(cast=0.0)
SC.actors = [moth, boyR, sheepR, boxp]

# ---------------------------------------------------------------- the storm
def density(t):
    if t < 8: return 0
    if t < T_STORM: return 0.12 + 0.3 * (t - 8) / 52
    if t < 158: return 1.0
    return max(0.0, 1 - (t - 158) / 10)
_r = np.random.default_rng(77); ROCKS = []
while len(ROCKS) < 420:
    t0 = _r.uniform(0, 175)
    if _r.random() > density(t0): continue
    layer = _r.choice(['back', 'mid', 'front'], p=[0.55, 0.3, 0.15])
    big = min(1.0, (t0 - 8) / 70) if t0 > 8 else 0
    r = {'back': _r.uniform(6, 22) * (0.5 + big), 'mid': _r.uniform(24, 60) * (0.4 + big), 'front': _r.uniform(90, 200) * (0.3 + big)}[layer]
    sp = {'back': _r.uniform(260, 420), 'mid': _r.uniform(600, 900), 'front': _r.uniform(1300, 1900)}[layer]
    ROCKS.append(dict(t0=t0, layer=layer, r=r, sp=sp, y=_r.uniform(-100, H + 100), vy=_r.uniform(-120, 120), spin=_r.uniform(-1.5, 1.5), seed=int(_r.integers(0, 999)),
                      a0=_r.uniform(0, 6.28)))
DEBRIS = [dict(x=_r.uniform(0, W), y=_r.uniform(0, H), r=_r.uniform(5, 26), vx=_r.uniform(-12, 12), vy=_r.uniform(-8, 8), spin=_r.uniform(-0.3, 0.3),
               seed=int(_r.integers(0, 999)), a0=_r.uniform(0, 6.28)) for k in range(16)]
def draw_rocks(f, t, layers, W_):
    for R in ROCKS:
        if R['layer'] not in layers: continue
        age = t - R['t0']
        if age < 0: continue
        x = W + R['r'] * 2 + 100 - age * R['sp']
        if x < -R['r'] * 2 - 100: continue
        y = R['y'] + age * R['vy']
        blur = 0 if R['layer'] != 'front' else 6 + R['r'] * 0.05
        meteor(f, x, y, R['r'], R['a0'] + age * R['spin'], seed=R['seed'], light=W_.light, rim=W_.rim, dim=0.45 if R['layer'] == 'back' else 0.0, blur=blur,
               hot=0.6 if R['layer'] == 'mid' else 0.0)
STREAM = StarStream(n=200, seed=19)
def sky_fx(f, C, t, W_):
    sp = float(keys([(0, 0.9), (T_STORM, 1.5), (HIT, 1.5), (HIT + 2, 0.4), (T_QUIET, 0.12), (T_ALIVE, 0.12), (T_ALIVE + 6, 0.8)], t))
    STREAM.draw(f, t, speed=sp, amt=0.8)
    draw_rocks(f, t, ('back', 'mid'), W_)
    if t > HIT - 2:   # slow floating bits after the storm
        a = ss((t - HIT) / 6)
        for D in DEBRIS:
            x = (D['x'] + D['vx'] * t) % (W + 100) - 50; y = (D['y'] + D['vy'] * t) % (H + 100) - 50
            meteor(f, x, y, D['r'] * a + 0.1, D['a0'] + t * D['spin'], seed=D['seed'], light=W_.light, rim=W_.rim, dim=0.5)
SC.sky_fx = sky_fx

# ---------------------------------------------------------------- memory bubbles
def bubble(f, cx, cy, r, a, paint, tint='#fff1d6'):
    if a < 0.01: return
    g = f.copy()
    yy, xx = np.ogrid[0:H, 0:W]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    inside = np.clip((r - d) / (0.25 * r), 0, 1)
    g[:] = g * 0.35 + hexc(tint) * 0.65 * (0.7 + 0.3 * np.clip(1 - d / r, 0, 1))[..., None]
    paint(g)
    m = (inside * a * 0.92)[..., None]
    f[:] = f * (1 - m) + g * m
    ring = np.clip(1 - np.abs(d - r) / 3.0, 0, 1) * a * 0.5
    f[:] = f + hexc('#fff6e0') * ring[..., None]
    for k in range(3):   # a trail of little dots to whoever remembers
        pass
MEM_BOY = BoyAnim(segs([], 0), k=1.6, t_end=300, laugh=[(0, 1)], poses={'armR': [(0, 40)], 'foreR': [(0, 60)], 'armL': [(0, -40)], 'foreL': [(0, -60)]})
MEM_SHEEP = SheepAnim(segs([], 0), k=1.6, t_end=300, laugh=[(0, 1)], tail=[(0, 0)] + osc(0, 300, 0.3, -24, 24))
TRAIL = GoldTrail()
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    draw_rocks(f, t, ('front',), W_)
    # the rock that clips them
    if HIT - 2.6 < t < HIT + 2.6:
        u = (t - HIT) / 5.0
        gx, gy_ = gpos(HIT)
        X, Y = C.to_screen(gx + 140 + 1800 * -u, gy_ + 120 + 900 * -u * 0.0 + 900 * u)
        meteor(f, X, Y, 110 * C.k, t * 1.3, seed=5, light=W_.light, rim=W_.rim, hot=0.8)
        if abs(t - HIT) < 0.4:
            sx, sy = C.to_screen(gx + 100, gy_ + 150); glow(f, sx, sy, 260 * z, '#ffe8c0', (1 - abs(t - HIT) / 0.4) * 0.8)
    m = WATCH.get('moth', {})
    if 'box' in WATCH and glow_pip(t) > 0.5 and t > T_ALIVE: TRAIL.draw(f, t, WATCH['box'], (glow_pip(t) - 0.4) * 1.2, z, drift=(-200, 20))
    # the memories
    if T_B1 < t < T_B1 + 14 and 'head' in BOY_LAST:
        a = ss((t - T_B1) / 2) * (1 - ss((t - T_B1 - 12) / 2)); hx, hy = BOY_LAST['head']
        cx, cy, r = hx - 160 * z, hy - 330 * z, 190 * z
        u = ss((t - T_B1 - 2) / 6)
        bubble(f, cx, cy, r, a, lambda g: draw_rose(g, cx, cy + 150 * z, 0.75 * z, t, light=(-0.4, -0.8), dome=False, mood=u, rim='#fff0c0'), '#ffe6d2')
    if T_B2 < t < T_B2 + 14 and 'head' in m:
        a = ss((t - T_B2) / 2) * (1 - ss((t - T_B2 - 12) / 2)); hx, hy = m['head']
        cx, cy, r = hx + 360 * z, hy - 230 * z, 190 * z
        def paint2(g):
            g[:] = g * 0.25 + hexc('#1a1430') * 0.75 * np.ones_like(g)
            k = ss((t - T_B2 - 2) / 6)
            glow(g, cx, cy + 20 * z, 140 * z * k + 1, '#ffd070', 0.8 * k); glow(g, cx, cy + 20 * z, 20 * z * k + 1, '#fff6d0', k)
            draw_moth(g, cx - 90 * z, cy + 90 * z, 0.18 * z, t, flip=1, open_=0.2, mood=k, surprise=1 - k, laugh=0, light=(0.9, -0.2), rim='#ffd890', glow_amt=k)
        bubble(f, cx, cy, r, a, paint2, '#2a2040')
    if T_B3 < t < T_B3 + 15 and 'head' in SHEEP_LAST:
        a = ss((t - T_B3) / 2) * (1 - ss((t - T_B3 - 13) / 2)); hx, hy = SHEEP_LAST['head']
        cx, cy, r = hx + 160 * z, hy - 300 * z, 200 * z
        def paint3(g):
            draw_boy(g, cx - 60 * z, cy + 150 * z, 0.48 * z, 1, t=t, A=MEM_BOY.at(t), light=(-0.5, -0.7), rim='#fff0c0', shadow=False)
            draw_sheep(g, cx + 70 * z, cy + 160 * z, 0.48 * z, -1, t=t, A=MEM_SHEEP.at(t), light=(-0.5, -0.7), rim='#fff0c0', shadow=False)
        bubble(f, cx, cy, r, a, paint3, '#e8f0d8')
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
def follow(ox, oy, z):
    return lambda t: (gpos(t)[0] * 0.6 + 1440 * 0.4 + ox, gpos(t)[1] * 0.6 + 560 * 0.4 + oy, z)
BOYH = (-105, 80); SHEEPH = (130, 130); MOTHH = (0, -40)
SC.shots = [
    (0,   [(0, (1440, 640, 0.72)), (14, (1440, 650, 0.8))], 0.0),
    (14,  follow(0, 140, 1.25), 0.0),
    (28,  follow(*BOYH, 3.0), 0.0),
    (40,  follow(*MOTHH, 2.1), 0.0),
    (50,  follow(0, 120, 1.1), 0.0),
    (T_STORM, follow(0, 100, 0.95), 0.0),
    (84,  follow(*MOTHH, 2.0), 0.0),
    (92,  follow(0, 100, 0.85), 0.0),
    (102, follow(*SHEEPH, 2.8), 0.0),
    (112, follow(0, 100, 0.85), 0.0),
    (128, follow(*BOYH, 2.6), 0.0),
    (136, follow(0, 100, 0.95), 0.0),
    (150, follow(*MOTHH, 2.1), 0.0),
    (160, follow(0, 140, 1.15), 0.0),
    (CATCH - 1, follow(-60, 170, 1.8), 0.0),
    (T_QUIET, [(T_QUIET, (1440, 700, 0.8)), (T_B1 - 4, (1440, 690, 0.9))], 0.0),
    (T_B1 - 4, follow(-120, 0, 1.6), 0.0),
    (T_B2 - 1, follow(120, -140, 1.35), 0.0),
    (T_B3 - 1, follow(80, 40, 1.45), 0.0),
    (T_LAUGH, follow(0, 120, 1.25), 0.0),
    (T_FLICK, follow(10, 260, 2.6), 0.0),
    (T_ALIVE + 4, follow(0, 140, 1.1), 0.0),
    (290, [(290, (1450, 690, 1.0)), (300, (1600, 600, 0.75))], 0.0),
]
SC.subs = [(T_B1 + 1.5, T_B1 + 7.2, 'My happiest day? When the rose opened for the very first time.', '我最快乐的一天？是玫瑰第一次开花的时候。'),
           (T_B2 + 1.0, T_B2 + 5.7, 'Mine is the first time I ever saw a light.', '我的是我第一次看见光的时候。'),
           (T_B3 + 4.0, T_B3 + 9.6, "And you... 'That's exactly the sheep I wanted.'", '还有你……"这正是我想要的那只羊。"')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, T_STORM, 'adventure', 0.8), (T_STORM, HIT, 'tense', 1.0), (T_QUIET, T_B1, 'sad', 0.5), (T_B1, T_LAUGH, 'wonder', 0.7), (T_LAUGH, T_FLICK, 'warm', 0.75),
         (T_ALIVE, 300, 'triumph', 0.9)]
SFX = [(0, 'wind', dict(dur=HIT + 2, gain=1.0)), (HIT + 2, 'wind', dict(dur=120, gain=0.25))]
for R in ROCKS:
    if R['layer'] == 'front': SFX.append((R['t0'] + 0.6, 'whoosh', dict(dur=1.0, f=160, gain=0.6)))
SFX += [(HIT, 'thump', dict(gain=1.0)), (HIT + 0.1, 'baa', dict(f=360, dur=0.7)), (CATCH, 'tap', dict(gain=0.5)),
        (T_LAUGH + 1, 'giggle', dict(n=20, shift=-6)), (T_LAUGH + 2, 'giggle', dict(n=16, shift=-14)),
        (T_FLICK + 1.5, 'twinkle', dict(gain=0.3)), (T_FLICK + 4, 'twinkle', dict(gain=0.4)), (T_FLICK + 6.5, 'twinkle', dict(gain=0.5)),
        (T_ALIVE, 'chime', dict(notes=[1500, 1880, 2250, 3000])), (T_ALIVE + 0.3, 'sparkle'), (T_ALIVE + 1.2, 'giggle', dict(n=24)), (T_ALIVE + 3, 'shimmer', dict(dur=10, gain=0.6))]

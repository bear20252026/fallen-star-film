# S08 · The dark planet (300 s). The sheep walks alone across a dead, quiet planet and finds Moth curled under a tree,
# hugging the lantern like a hot-water bottle; Pip is grey. "It's so cold here. I just wanted some light."
# The sheep doesn't shout. It snuggles against him, wool on fur. It tickles: Moth giggles, then laughs, and Pip flickers gold.
# He gives the lantern back. "Can I come? I'll carry you." The boy arrives, out of breath; Moth carries them both away.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import GoldTrail, BOY_LAST, SHEEP_LAST
from props3 import box
from moth import draw_moth

class S08(Scene):
    DURATION = 300.0

SC = S08()
DARK = World('night', place='dark')
gy = DARK.gy
SC.worlds = [(0, 1e9, DARK)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

T_TALK, T_SNUG, T_GIG, T_LAUGH, T_GIVE, T_ASK, T_BOY, RISE0 = 128.0, 182.0, 196.0, 204.0, 242.0, 256.0, 262.0, 286.0
MX0, MX1 = 2050, 1880         # Moth sits here; then steps forward to pick them up
def rise(t, d=0.0):
    u = max(0.0, t - RISE0 - d); return 640 * ss(u / 14) * (0.4 + 0.6 * min(1, u / 5))
def gold(t):
    g = 0.0
    for (t0, t1) in ((T_GIG + 2, T_GIG + 4),):
        if t0 - 0.5 < t < t1 + 1.5: g = max(g, 0.5 * ss((t - t0) / 0.5) * (1 - ss((t - t1) / 1.5)))
    g = max(g, ss((t - T_LAUGH - 2) / 3) * (0.82 + 0.18 * math.sin(t * 5)))
    return g
def lantern(t): return 0.12 + 0.8 * gold(t)

# ---------------------------------------------------------------- the sheep
sheep_x = segs([(2, 22, 700, 0.5, 0.6), (26, 46, 1100, 0.5, 0.6), (50, 68, 1450, 0.5, 0.7), (96, 110, 1700, 0.6, 0.8), (T_SNUG - 4, T_SNUG + 1, 1870, 0.6, 0.8),
                (236, 240, 1800, 0.5, 0.6), (252, 255, 1860, 0.5, 0.6), (276, 280, 1950, 0.5, 0.6)], 300)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300, lift=[(0, 0), (RISE0 + 0.2, 0), (RISE0 + 1.2, 24)],
    crouch=[(0, 0), (T_SNUG + 1, 0), (T_SNUG + 3, 30), (234, 30), (236, 0)],
    head=[(0, 0), (12, 0), (14, 8), (20, 8), (22, 0), (34, -8), (40, 6), (46, 0), (60, 0), (64, 10), (70, 10), (72, -6), (96, -6), (100, 12), (112, 12), (118, 0),
          (140, 0), (142, 14), (150, 14), (152, 0), (T_SNUG + 3, 10)] + osc(T_SNUG + 4, 200, 0.7, 4, 16) + [(200.4, 10), (234, 10), (236, 0),
          (252, 0), (253, 18), (254.5, 0), (270, 0), (272, 8), (274, 0), (276, 8), (277, 0)],
    look=[(0, (0.6, -0.1)), (12, (0.2, -0.6)), (20, (0.8, 0.0)), (34, (-0.4, -0.4)), (46, (0.7, -0.2)), (64, (0.9, 0.0)), (96, (0.8, 0.1)), (120, (0.9, -0.3)),
          (140, (0.6, -0.2)), (T_SNUG, (0.8, -0.4)), (200, (0.6, -0.6)), (236, (0.8, -0.6)), (246, (0.4, 0.4)), (256, (0.8, -0.6)), (263, (-0.9, -0.1)), (274, (0.8, -0.5))],
    laugh=[(0, 0), (T_LAUGH, 0), (T_LAUGH + 1, 0.8), (226, 0.7), (228, 0), (258, 0), (259, 0.6), (300, 0.6)],
    tail=[(0, 0)] + osc(T_SNUG + 4, 200, 0.3, -20, 20) + [(200.3, 0)] + osc(274, 278, 0.3, -24, 24) + [(278.3, 0)],
    mouth=[(253.0, 254.6, 'open')], sleep=[(0, 0)])
sheep = SheepActor(SHEEP, lambda t: gy(sheep_x(t)) + 112 - rise(t, 0.3), facing=[(0, 1)])
sheep.shadow = lambda t: t < RISE0 + 0.6
sheep.cast = lambda t: dict(cast=0.0) if t > RISE0 + 0.6 else None

# ---------------------------------------------------------------- the boy (arrives at the end, out of breath)
boy_x = segs([(T_BOY, T_BOY + 7, 1640, 0.3, 0.8), (279, 282, 1760, 0.5, 0.6)], 700)
BOY = BoyAnim(boy_x, k=1.6, t_end=300, hang=[(0, 0), (RISE0 + 0.2, 0), (RISE0 + 1.4, 1)], wind=[(0, 0), (RISE0, 0), (RISE0 + 2, 0.4)],
    crouch=[(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, 34), (T_BOY + 14, 34), (T_BOY + 15, 0)],
    poses={'chest': [(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, 16)] + osc(T_BOY + 7.6, T_BOY + 14, 0.5, 13, 19) + [(T_BOY + 15, 0)],
           'armR': [(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, 30), (T_BOY + 14, 30), (T_BOY + 15, 0), (RISE0, 0), (RISE0 + 1.2, -40)],
           'foreR': [(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, 40), (T_BOY + 14, 40), (T_BOY + 15, 0)],
           'armL': [(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, -30), (T_BOY + 14, -30), (T_BOY + 15, 0), (RISE0, 0), (RISE0 + 1.2, 40)],
           'foreL': [(0, 0), (T_BOY + 7, 0), (T_BOY + 7.6, -40), (T_BOY + 14, -40), (T_BOY + 15, 0)]},
    look_x=[(0, 0.8), (T_BOY + 8, 0.2), (T_BOY + 11, 0.9), (280, 0.6), (RISE0, 0.0)],
    lookup=[(0, 0.2), (T_BOY + 8, -0.5), (T_BOY + 11, 0.6), (280, 0.3), (RISE0, -0.4), (RISE0 + 6, 0.2)],
    brows=[(0, 0.8), (T_BOY + 11, 1.0), (276, 0.0)],
    mouth=[(T_BOY + 7.6, T_BOY + 14, 'open'), (T_BOY + 11.2, T_BOY + 12.2, 'open')],
    laugh=[(0, 0), (276, 0), (277, 0.6), (281, 0.2), (RISE0 + 2, 0.2), (RISE0 + 3, 0.8), (300, 0.7)])
boy = BoyActor(BOY, lambda t: gy(boy_x(t)) + 70 - rise(t), facing=[(0, 1)], active=lambda t: t > T_BOY - 0.5)
boy.shadow = lambda t: t < RISE0 + 0.6
boy.cast = lambda t: dict(cast=0.0) if t > RISE0 + 0.6 else None

# ---------------------------------------------------------------- Moth, curled under the tree, hugging the lantern
moth_x = segs([(278, 283, MX1, 0.5, 0.6)], MX0)
BOXG = (1975, None)          # where he sets the lantern down
WATCH = {}
def hug_amt(t): return 1 - ss((t - T_GIVE) / 3)
class MothActor(Actor):
    height = 600; tuft_w = 60
    def __init__(self): self.shadow = True; self.cast = None
    def foot(self, t):
        x = moth_x(t); return (x, gy(x) + 40 - rise(t, -0.4))
    def draw(self, f, X, Y, s, t, W_, C):
        MS = 1.25; sm = s * MS
        g = gold(t); happy = ss((t - T_LAUGH) / 6)
        open_ = ss((RISE0 - 6 - t) / -4) if t > RISE0 - 6 else 0.0
        # sitting: his body rests low (feet at Y)
        cx, cy = X, Y - (190 + 46 * ss((t - T_GIVE - 8) / 4)) * sm
        hold = (float(keys([(0, -10), (T_GIVE, -10), (T_GIVE + 3, -70), (T_GIVE + 6, 0), (RISE0 - 6, 0)], t)),
                float(keys([(0, 70), (T_GIVE, 70), (T_GIVE + 3, 180), (T_GIVE + 6, 40), (RISE0 - 6, 40), (RISE0 - 3, 110)], t)))
        if T_GIVE + 6 < t < RISE0 - 6: hold = None
        shiver = 1 - ss((t - T_SNUG - 2) / 8)
        out = {}
        draw_moth(f, cx, cy, sm, t, flip=-1, open_=open_, flap=ss((t - RISE0 + 2) / 2), flap_speed=1.4,
                  mood=0.0 + 1.0 * happy, surprise=float(keys([(0, 0), (112, 0), (112.6, 1), (116, 0.3), (122, 0)], t)),
                  laugh=float(keys([(0, 0), (T_GIG, 0), (T_GIG + 0.4, 0.6), (T_GIG + 2.6, 0.6), (T_GIG + 3.2, 0), (T_LAUGH, 0), (T_LAUGH + 0.6, 1), (226, 1), (228, 0),
                                    (259, 0), (260, 0.6), (300, 0.7)], t)),
                  talk=float(keys([(T_TALK, 0), (T_TALK + 0.1, 1), (T_TALK + 5.4, 1), (T_TALK + 5.5, 0), (T_ASK, 0), (T_ASK + 0.1, 1), (T_ASK + 4.4, 1), (T_ASK + 4.5, 0)], t)),
                  blink=float(keys([(0, 0.05), (110, 0.05), (112, 1)], t)) if t < 113 else None,
                  look=(float(keys([(0, 0.3), (112, 0.9), (T_SNUG, 0.6), (T_LAUGH, 0.0), (T_GIVE, 0.8), (T_BOY + 8, 0.9), (RISE0, 0.2)], t)),
                        float(keys([(0, 0.8), (112, 0.5), (T_SNUG, 0.8), (T_LAUGH, -0.3), (T_GIVE, 0.6), (RISE0, 0.0)], t))),
                  shiver=shiver, hold=hold, glow_amt=0.25 + 0.9 * g, light=W_.light, rim=W_.rim, rim_w=0.55, out=out, dim=0.3 * (1 - ss((t - T_LAUGH) / 5)),
                  tilt=float(keys([(0, 0.08), (T_SNUG, 0.08), (T_SNUG + 4, -0.06), (T_LAUGH, 0.0)], t)))
        WATCH['moth'] = out
        sb = 0.85 * s
        if t < T_GIVE + 6:   # the lantern in his arms, then set down
            hx, hy = out['hand']
            gx_, gy_ = C.to_screen(BOXG[0], gy(BOXG[0]) + 100)
            u = ss((t - T_GIVE - 1) / 4)
            bx, by = hx + (gx_ - hx) * u, hy + 60 * sb + (gy_ - hy - 60 * sb) * u
            box(f, bx, by, sb, light=W_.light, rim=W_.rim, glow_amt=lantern(t), t=t, handle=True, grey=1 - min(1, g * 1.2))
            WATCH['box'] = (bx, by - 70 * sb)
moth = MothActor()

def box_fn(f, X, Y, s, t, W_, C):
    sb = 0.85 * s
    if t >= 253.6:
        m = SHEEP_LAST.get('mouth')
        if m is None: return
        X, Y = m[0] - 5 * sb, m[1] + 168 * sb + 6 * s
    box(f, X, Y, sb, light=W_.light, rim=W_.rim, glow_amt=lantern(t), t=t, handle=True, grey=1 - min(1, gold(t) * 1.2))
    WATCH['box'] = (X, Y - 70 * sb)
def box_foot(t):
    if t < T_GIVE + 6: return None
    if t >= 253.6: return (sheep_x(t), gy(sheep_x(t)) + 113 - rise(t, 0.3))
    return (BOXG[0], gy(BOXG[0]) + 100)
boxp = Prop(box_fn, box_foot, height=150, tuft_w=40)
SC.actors = [moth, sheep, boy, boxp]

# ---------------------------------------------------------------- effects: cold breath, the gold trail, wing dust when he lifts off
TRAIL = GoldTrail()
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    g = gold(t)
    if g > 0.05 and 'box' in WATCH: TRAIL.draw(f, t, WATCH['box'], g * 0.7, z, drift=(0, -150))
    m = WATCH.get('moth', {})
    if t < T_SNUG + 10 and 'head' in m:   # Moth's cold little breaths
        hx, hy = m['head']
        for k in range(3):
            age = ((t * 0.5 + k / 3) % 1.0)
            glow(f, hx - 20 * z + 40 * age * z, hy + 40 * z - 30 * age * z, (10 + 26 * age) * z, '#c8c0e8', 0.12 * (1 - age))
    if t > RISE0 - 2 and 'head' in m:
        hx, hy = m['head']; r = np.random.default_rng(int(t * 24))
        for k in range(18):
            a = r.random() * 6.28; d = (120 + r.random() * 260) * z
            glow(f, hx + math.cos(a) * d, hy + 200 * z + math.sin(a) * d * 0.6 + r.random() * 120 * z, 2.2 * z * 2, '#e0d4ff', 0.5)
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
G = lambda x, dy, z: (x, gy(x) + dy, z)
def track(t): x = sheep_x(t); return (x + 60, gy(x) - 90, 2.2)
def lift_cam(t):
    u = ss((t - RISE0) / 14); return (1820 + 80 * u, gy(1820) - 150 - rise(t) * 0.75, 1.15 - 0.35 * u)
SC.shots = [
    (0,   [(0, G(900, -260, 0.75)), (16, G(1000, -240, 0.8))], 0.0),
    (16,  track, 0.8),
    (30,  [(30, G(1200, -170, 1.15)), (46, G(1260, -160, 1.2))], 0.3),
    (46,  [(46, G(1250, -80, 2.6)), (60, G(1420, -80, 2.6))], 1.0),
    (60,  [(60, G(1650, -230, 0.95)), (72, G(1700, -220, 1.0))], 0.2),
    (72,  [(72, G(MX0 - 10, -150, 2.4)), (90, G(MX0 - 10, -150, 2.55))], 0.8),
    (90,  [(90, G(1520, -60, 2.8)), (100, G(1525, -60, 2.9))], 1.0),
    (100, [(100, G(1840, -140, 1.45)), (112, G(1850, -140, 1.5))], 0.3),
    (112, [(112, G(MX0 - 20, -205, 3.2)), (120, G(MX0 - 20, -205, 3.3))], 1.0),
    (120, [(120, G(1720, -70, 2.8)), (T_TALK, G(1720, -70, 2.9))], 1.0),
    (T_TALK, [(T_TALK, G(MX0 - 20, -200, 2.8)), (140, G(MX0 - 20, -200, 3.0))], 1.0),
    (140, [(140, G(1720, -70, 2.9)), (150, G(1720, -72, 3.0))], 1.0),
    (150, [(150, G(1880, -150, 1.4)), (T_SNUG, G(1890, -150, 1.6))], 0.3),
    (T_SNUG, [(T_SNUG, G(1930, -130, 1.9)), (T_LAUGH, G(1935, -132, 2.0))], 0.6),
    (T_LAUGH, [(T_LAUGH, G(MX0 - 20, -200, 2.6)), (215, G(MX0 - 20, -200, 2.75))], 0.8),
    (215, [(215, G(1960, -110, 3.2)), (225, G(1960, -110, 3.4))], 1.2),
    (225, [(225, G(1880, -200, 1.1)), (T_GIVE, G(1880, -200, 1.15))], 0.2),
    (T_GIVE, [(T_GIVE, G(1920, -120, 1.9)), (T_ASK, G(1920, -120, 2.0))], 0.6),
    (T_ASK, [(T_ASK, G(MX0 - 20, -200, 2.8)), (T_BOY, G(MX0 - 20, -200, 2.9))], 1.0),
    (T_BOY, [(T_BOY, G(1500, -200, 0.9)), (T_BOY + 8, G(1560, -190, 0.95))], 0.2),
    (T_BOY + 8, [(T_BOY + 8, G(1640, -150, 2.6)), (278, G(1640, -150, 2.7))], 1.0),
    (278, [(278, G(1840, -170, 1.3)), (RISE0, G(1840, -170, 1.35))], 0.3),
    (RISE0, lift_cam, 0.2),
]
SC.subs = [(T_TALK, T_TALK + 5.5, "It's so cold here. I just wanted some light.", '这里太冷了。我只是想要一点光。'),
           (T_ASK, T_ASK + 4.5, "Can I come? I'll carry you.", '我能一起去吗？我来驮你们。')]
SC.fade_in, SC.fade_out = 2.5, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 60, 'night', 0.6), (60, T_SNUG, 'sad', 0.75), (T_SNUG, T_LAUGH, 'wonder', 0.75), (T_LAUGH, T_GIVE, 'playful', 0.85), (T_GIVE, 300, 'warm', 0.85)]
SFX = [(0, 'wind', dict(dur=300, gain=0.35))]
for k in range(40): SFX.append((2 + k * 1.1, 'hoof', dict(gain=0.25)))
SFX += [(112.4, 'chime', dict(notes=[900], gain=0.3)), (T_GIG, 'giggle', dict(n=5, shift=-16, gain=0.6)), (T_GIG + 2, 'chime', dict(notes=[1500, 1880], gain=0.4)),
        (T_LAUGH, 'giggle', dict(n=26, shift=-12)), (T_LAUGH + 2, 'chime', dict(notes=[1500, 1880, 2250])), (T_LAUGH + 2.4, 'sparkle'),
        (214, 'giggle', dict(n=14, shift=-10)), (253.4, 'baa', dict(f=420, dur=0.5)), (T_BOY, 'step', dict(n=14, gain=0.5)),
        (277, 'giggle', dict(n=8)), (RISE0, 'whoosh', dict(dur=3, f=160, gain=0.6)), (RISE0 + 1, 'shimmer', dict(dur=8, gain=0.5)), (RISE0 + 3, 'giggle', dict(n=12))]

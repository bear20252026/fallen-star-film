# S04 · The Quiet (300 s). Flying out into the deep dark. Pip fades to grey; everyone is scared and quiet.
# The sheep does a silly upside-down dance on its string; the boy laughs, and Pip glows gold. "It's laughing that does it!"
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import RotActor, StarStream, GoldTrail, box_in_mouth, sheep_harness, BOY_LAST, SHEEP_LAST
from props3 import Flock
from sheep import draw_sheep

class S04(Scene):
    DURATION = 300.0

SC = S04()
SPACE = World('deep', place='space')
SC.worlds = [(0, 1e9, SPACE)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

BX, BY = 1360, 790          # the boy's feet (hanging)
SX, SY = 1560, 860          # the sheep's feet line
bob = lambda t, ph=0.0: 14 * math.sin(t * 0.7 + ph) + 5 * math.sin(t * 1.9 + ph * 2)

# when Pip glows: 0 grey .. 1 gold
def gold(t):
    g = 0.0
    for (t0, t1) in ((161.5, 169.0), (213.0, 220.0)):
        if t0 - 0.5 < t < t1 + 2.5: g = max(g, ss((t - t0) / 0.8) * (1 - ss((t - t1) / 2.5)))
    if t > 258: g = max(g, (0.55 + 0.35 * abs(math.sin((t - 258) * 1.3))) * ss((t - 258) / 2))
    return g
def lantern(t): return 0.32 - 0.16 * ss((t - 50) / 50) + 0.75 * gold(t)

# ---------------------------------------------------------------- the boy, hanging from the strings
BOY = BoyAnim(segs([], BX), k=1.6, t_end=300, hang=[(0, 1)], wind=[(0, 0.6)],
    poses={'armR': [(0, -128)], 'foreR': [(0, -6)],
           'armL': [(0, 0), (206, 0), (207, -20), (212, -20), (213, 0)],
           'head': [(0, 0), (205.8, 0)] + osc(206, 212, 0.5, -8, 8) + [(212.3, 0)]},
    look_x=[(0, 0.4), (60, 0.5), (70, 0.7), (120, 0.6), (128, 0.8), (200, 0.8), (205, -0.2), (212, 0.7), (230, 0.6)],
    lookup=[(0, -0.1), (60, -0.2), (70, -0.5), (118, -0.5), (128, -0.3), (200, -0.3), (220, -0.4), (232, -0.2)],
    brows=[(0, 0.3), (60, 0.4), (70, 1.0), (128, 0.8), (150, 0.2), (206, 1), (212, 0.2), (300, 0)],
    laugh=[(0, 0), (150.0, 0), (150.3, 0.3), (151.2, 0), (155.6, 0), (156.4, 1.0), (169, 0.9), (171, 0), (213, 0), (213.6, 0.3), (219, 0),
           (258, 0), (259, 0.9), (268, 0.6), (270, 0.2), (274, 0.8), (284, 0.7), (288, 0.3), (292, 0.8), (300, 0.7)],
    mouth=[(206, 212.2, 'open'), (64, 72, 'sad'), (90, 118, 'sad')],
    talk=[(222.0, 0), (222.1, 1), (226.0, 1), (226.1, 0)])
boy = BoyActor(BOY, lambda t: BY + bob(t)); boy.shadow = False; boy.cast = dict(cast=0.0)
boyR = RotActor(boy, lambda t: 3 * math.sin(t * 0.7 + 1.2), piv_h=380)

# ---------------------------------------------------------------- the sheep with the lantern in its mouth
SPIN = [(0, 0), (127.5, 0), (130.0, 180), (148.0, 180), (148.6, 170), (149.2, 190), (149.8, 175), (150.4, 180), (171.5, 180), (174.5, 360), (300, 360)]
SHEEP = SheepAnim(segs([], SX), k=1.6, t_end=300, lift=[(0, 24)],
    paddle=[(0, 0), (128, 0), (129, 1), (147.5, 1), (148, 0), (150.5, 0), (151, 1), (171, 1), (172, 0), (213, 0), (213.5, 0.6), (218, 0.6), (218.5, 0)],
    head=[(0, 0), (60, 0), (64, 10), (118, 10), (122, 0), (130, 0)] + osc(130, 147, 0.42, -14, 14) + [(147.5, 0)] + osc(151, 171, 0.42, -14, 14) + [(171.5, 0)],
    look=[(0, (0.4, -0.4)), (60, (-0.5, -0.8)), (118, (-0.6, -0.8)), (128, (0, 0)), (175, (-0.6, -0.6)), (205, (-0.8, -0.6)), (230, (-0.4, -0.5))],
    laugh=[(0, 0), (212.6, 0), (213.2, 1), (218.5, 1), (219.5, 0), (258.5, 0), (259.5, 1), (300, 0.8)],
    tail=[(0, 0)] + osc(130, 171, 0.3, -30, 30) + [(171.5, 0)],
    sleep=[(0, 0)])
class SheepBox(Actor):
    height = 260; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0); self.at_ = {}
    def foot(self, t): return (SX, SY + bob(t, 1.3))
    def draw(self, f, X, Y, s, t, W_, C):
        draw_sheep(f, X, Y, s, 1, t=t, A=SHEEP.at(t), light=W_.light, rim=W_.rim, rim_w=0.6, shadow=False)
        g = gold(t)
        p = box_in_mouth(f, s, t, W_, 1, lantern(t), grey=1 - g)
        self.at_[t] = p
sheepbox = SheepBox()
PIV_H = 120
sheepR = RotActor(sheepbox, lambda t: float(keys(SPIN, t)) % 360, piv_h=PIV_H)
SC.actors = [boyR, sheepR]

# ---------------------------------------------------------------- the sky: streaming stars, the birds, the gold trail
STREAM = StarStream(n=170, seed=8); FLOCK = Flock(n=12, seed=5, spread=(300, 110)); TRAIL = GoldTrail()
def sky_fx(f, C, t, W_):
    STREAM.draw(f, t, speed=0.8, amt=0.8)
SC.sky_fx = sky_fx
def rot_about(p, piv, ang):
    a = math.radians(ang); c, s_ = math.cos(a), math.sin(a); d = np.array(p) - piv
    return tuple(piv + [d[0] * c - d[1] * s_, d[0] * s_ + d[1] * c])
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    hx, hy = C.to_screen(BX, BY + bob(t) - 330)
    cx, cy = hx + 80 * z, hy - 300 * z
    anchors = []
    if 'handR' in BOY_LAST: anchors.append(tuple(BOY_LAST['handR']))
    h = sheep_harness(z)
    if h is not None:
        X, Y = C.to_screen(SX, SY + bob(t, 1.3)); piv = np.array([X, Y - PIV_H * z])
        anchors.append(rot_about(h, piv, float(keys(SPIN, t)) % 360))
    FLOCK.draw(f, t, cx, cy, z, anchors=anchors, light=W_.light, flip=-1)
    g = gold(t)
    if g > 0.05:
        X, Y = C.to_screen(SX + 120, SY + bob(t, 1.3) - 90)
        TRAIL.draw(f, t, (X, Y), g, z)
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
SC.shots = [
    (0,   [(0, (1440, 600, 0.72)), (16, (1440, 620, 0.8))], 0.0),
    (16,  [(16, (1380, 560, 2.0)), (30, (1385, 556, 2.1))], 0.0),
    (30,  [(30, (1460, 700, 1.2)), (46, (1470, 690, 1.3))], 0.0),
    (46,  [(46, (1440, 640, 0.9)), (60, (1450, 640, 0.95))], 0.0),
    (60,  [(60, (SX + 60, SY - 150, 3.2)), (72, (SX + 62, SY - 152, 3.4))], 0.0),
    (72,  [(72, (BX + 10, BY - 165, 3.0)), (86, (BX + 10, BY - 165, 3.15))], 0.0),
    (86,  [(86, (SX - 20, SY - 170, 2.6)), (100, (SX - 20, SY - 172, 2.7))], 0.0),
    (100, [(100, (1460, 700, 1.4)), (118, (1460, 690, 1.45))], 0.0),
    (118, [(118, (SX + 30, SY - 120, 2.2)), (128, (SX + 30, SY - 120, 2.3))], 0.0),
    (128, [(128, (1500, 720, 1.5)), (150, (1505, 715, 1.55))], 0.0),
    (150, [(150, (BX + 10, BY - 165, 3.0)), (156, (BX + 10, BY - 165, 3.1))], 0.0),
    (156, [(156, (1470, 700, 1.4)), (161, (1470, 700, 1.45))], 0.0),
    (161, [(161, (SX + 110, SY - 60, 3.4)), (170, (SX + 110, SY - 60, 3.6))], 0.0),
    (170, [(170, (1480, 700, 1.5)), (190, (1480, 690, 1.55))], 0.0),
    (190, [(190, (1440, 640, 1.0)), (205, (1440, 630, 1.05))], 0.0),
    (205, [(205, (BX + 10, BY - 165, 3.2)), (212.4, (BX + 10, BY - 165, 3.3))], 0.0),
    (212.4, [(212.4, (SX + 40, SY - 140, 2.6)), (220, (SX + 40, SY - 142, 2.7))], 0.0),
    (220, [(220, (BX + 10, BY - 165, 3.0)), (228, (BX + 10, BY - 165, 3.1))], 0.0),
    (228, [(228, (1470, 700, 1.4)), (258, (1480, 690, 1.45))], 0.0),
    (258, [(258, (1470, 690, 1.45)), (275, (1440, 640, 1.0))], 0.0),
    (275, [(275, (1440, 620, 0.85)), (300, (1300, 580, 0.72))], 0.0),
]
SC.subs = [(222.0, 226.0, "It's laughing that does it!", '是笑声！笑声让它亮起来！')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 60, 'night', 0.7), (60, 120, 'sad', 0.8), (120, 200, 'playful', 0.9), (200, 258, 'wonder', 0.8), (258, 300, 'triumph', 0.8)]
SFX = [(0, 'wind', dict(dur=300, gain=1.0))]
for k in range(0, 300, 9): SFX.append((k + 2.0, 'whoosh', dict(dur=1.6, f=420, gain=0.25)))
SFX += [(129.0, 'baa', dict(f=420, dur=0.5)), (150.0, 'giggle', dict(n=2, shift=-10, gain=0.5)), (156.4, 'giggle', dict(n=22)),
        (161.6, 'chime', dict(notes=[1500, 1880, 2250])), (162.2, 'giggle', dict(n=8, shift=14, gain=0.6)), (162, 'sparkle'),
        (213.2, 'baa', dict(f=380, dur=0.6)), (213.4, 'giggle', dict(n=10, shift=4)), (213.6, 'chime', dict(notes=[1600, 2000])),
        (259, 'giggle', dict(n=18)), (259.2, 'sparkle'), (266, 'giggle', dict(n=10, shift=8)), (274, 'giggle', dict(n=14)), (292, 'giggle', dict(n=10))]

# S05 · The Clockmaker (300 s). A sunset planet full of ticking clocks and a tiny man with no time.
# The sheep gets tangled in a chain and jams the big clock with its tail. Silence. He looks up: the sunset. He laughs; Pip glows.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import StarStream, GoldTrail, sheep_harness, BOY_LAST, SHEEP_LAST
from props3 import Flock, box
from clocks import grandfather, post_clock, gear_clock, pocket_watch
from clockmaker import draw_clockmaker

class S05(Scene):
    DURATION = 300.0

SC = S05()
CLK = World('sunset', place='clock')
gy = CLK.gy
SC.worlds = [(0, 1e9, CLK)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

T_STOP, T_FREE, T_RESTART = 152.0, 249.0, 272.0
LAND, RISE0 = 30.0, 280.0
def run(t):   # all clocks run, then stop when the tail jams the gears, then start again
    if t < T_STOP: return 1.0
    if t < T_RESTART: return 0.0
    return ss((t - T_RESTART) / 1.5)
def descend(t, d=0.0): return 560 * (1 - ss((t - 12 - d) / (LAND - 12)))
def rise(t, d=0.0):
    u = max(0.0, t - RISE0 - d); return 620 * ss(u / 18) * (0.4 + 0.6 * min(1, u / 6))
def gold(t):
    g = ss((t - 240.5) / 1.2) * (1 - ss((t - 262) / 4)) * (0.85 + 0.15 * math.sin(t * 6))
    return max(g, 0.5 * ss((t - 266) / 3))
def lantern(t): return 0.22 + 0.75 * gold(t)

# ---------------------------------------------------------------- the clocks
GF1, POST1, GEAR, GF2, POST2 = 700, 990, 1500, 1980, 2250
GEAROUT = {}
def clock_prop(kind, x, dy, seed, sc=1.0):
    def fn(f, X, Y, s, t, W_, C):
        kw = dict(light=W_.light, rim=W_.rim, run=run(t), seed=seed)
        if kind == 'gf': grandfather(f, X, Y, s * sc, t, chain=float(keys([(0, 1), (116, 1), (121, 0.2), (300, 0.2)], t)) if x == GF1 else 1.0, **kw)
        elif kind == 'post': post_clock(f, X, Y, s * sc, t, h=240 + seed * 13 % 60, **kw)
        else: gear_clock(f, X, Y, s * sc, t, jam=1.0 if T_STOP - 2.2 < t < T_STOP else 0.0, out=GEAROUT, **kw)
    return Prop(fn, (x, gy(x) + dy), height=480 * sc, tuft_w=70)
CLOCKS = [clock_prop('post', 420, 8, 1, 0.8), clock_prop('post', 1230, 6, 2, 0.75), clock_prop('post', 2480, 10, 3, 0.85), clock_prop('gf', 1760, 4, 9, 0.8),
          clock_prop('gf', GF1, 40, 4), clock_prop('post', POST1, 46, 5), clock_prop('gear', GEAR, 34, 6, 1.2), clock_prop('gf', GF2, 44, 7), clock_prop('post', POST2, 50, 8)]

# ---------------------------------------------------------------- the Clockmaker
cm_x = segs([(46, 50, 1920, 0.4, 0.5), (55, 60.5, 765, 0.4, 0.5), (66, 71, 1050, 0.4, 0.5), (80, 86, 1625, 0.4, 0.5), (104, 110, 1920, 0.4, 0.5),
             (118, 124, 2190, 0.4, 0.5), (172, 182, 1730, 0.7, 0.9), (268, 271.5, 1625, 0.5, 0.6)], 2190)
CM = Walker(cm_x, 300, stride=46)
CRANK = [(40, 46), (50.5, 55), (61, 66), (71.5, 80), (86.5, 104), (110.5, 118), (124.5, T_STOP), (272, 279)]
cm_facing = [(0, 1), (55, -1), (66, 1), (71, -1), (80, 1), (86, -1), (104, 1), (153, -1), (183.5, 1), (268, -1)]
def cm_state(t):
    crank = None
    for (a, b) in CRANK:
        if a <= t < b: crank = (t - a) * (11 if b - a < 20 else 8)
    return crank
class ClockmakerActor(Actor):
    height = 300; tuft_w = 80; tuft_n = 14
    def foot(self, t): return (cm_x(t), gy(cm_x(t)) + 66)
    def draw(self, f, X, Y, s, t, W_, C):
        u, w = CM.at(t)
        fr = float(keys([(0, 0), (T_STOP + 0.6, 0), (T_STOP + 1.0, 1), (168, 1), (171, 0)], t))
        hold = float(keys([(0, 0), (259, 0), (260.5, 1), (266.5, 1), (267.5, 0)], t))
        p = draw_clockmaker(f, X, Y, s * 1.0, steps(cm_facing, t), t=t, u=u, walk=w, crank=cm_state(t), light=W_.light, rim=W_.rim, rim_w=0.6,
                            up=float(keys([(0, 0), (184, 0), (186.5, 0.9), (238, 0.9), (241, 0.4), (300, 0.2)], t)),
                            laugh=float(keys([(0, 0), (240.5, 0), (241.2, 1), (256, 1), (258, 0.3), (300, 0.3)], t)),
                            talk=float(keys([(72.0, 0), (72.1, 1), (77.0, 1), (77.1, 0), (195.0, 0), (195.1, 1), (199.8, 1), (199.9, 0),
                                             (262.0, 0), (262.1, 1), (265.8, 1), (265.9, 0)], t)),
                            frozen=fr, hold=hold, key=hold < 0.5, look=(0.6 if t < 150 else -0.4, 0), smile=0.2 if t < 186 else 0.6)
        if hold > 0.5 and t < 266.6: pocket_watch(f, p[0], p[1] + 18 * s, 1.2 * s, t, light=W_.light, rim=W_.rim)
cm = ClockmakerActor()

# ---------------------------------------------------------------- the boy and the sheep come down, watch, help, leave
boy_x = segs([(66, 68, 1090, 0.6, 0.7), (201, 209, 1840, 0.8, 0.9)], 1150)
BOY = BoyAnim(boy_x, k=1.6, t_end=300,
    hang=[(0, 1), (LAND - 1.2, 1), (LAND, 0), (RISE0 - 0.3, 0), (RISE0 + 1.2, 1)], wind=[(0, 0.5), (LAND, 0.1)],
    crouch=[(0, 0), (LAND, 0), (LAND + 0.15, 16), (LAND + 0.8, 0)],
    poses={'armR': [(0, -128), (LAND, -128), (LAND + 0.8, 0), (66.5, 0), (67.2, -50), (69.5, -50), (70.5, 0), (262, 0), (263.5, -62), (267, -60), (268, -20),
                    (276, -20), (277.5, -128), (300, -128)],
           'foreR': [(0, -6), (LAND, -6), (LAND + 0.8, 0), (66.5, 0), (67.2, -40), (69.5, -40), (70.5, 0), (262, 0), (263.5, -30), (267, -30), (268, -60),
                     (276, -60), (277.5, -6), (300, -6)]},
    look_x=[(0, 0.4), (LAND, 0.6)] + [(40 + k * 6, 0.8 if k % 2 == 0 else -0.6) for k in range(12)] + [(115, -0.6), (130, -0.8), (152, -0.3), (165, 0.6), (210, 0.7), (262, -0.6), (280, 0.4)],
    lookup=[(0, -0.3), (LAND, 0.0), (186, 0.0), (188, 0.8), (238, 0.8), (241, 0.2), (276, 0.7), (300, 0.8)],
    brows=[(0, 0.2), (40, 0.6), (66, 1.0), (80, 0.6), (152, 1.0), (186, 0.2)],
    laugh=[(0, 0), (126, 0), (126.6, 0.5), (131, 0.4), (132, 0), (241.5, 0), (242.3, 1), (256, 0.9), (258, 0.2), (282, 0.2), (283, 0.7), (300, 0.6)],
    talk=[(66.6, 0), (66.7, 1), (68.2, 1), (68.3, 0)],
    mouth=[(T_STOP + 0.3, T_STOP + 3, 'open')])
boy = BoyActor(BOY, lambda t: gy(boy_x(t)) + 70 - descend(t) - rise(t), facing=[(0, 1), (66, -1), (71, 1), (240, -1), (276, 1)])
boy.shadow = lambda t: LAND - 2 < t < RISE0 + 0.5
boy.cast = lambda t: dict(cast=0.0) if (t < LAND - 0.5 or t > RISE0 + 0.3) else None
def watch_prop(t):
    if not (266.6 <= t < 276.5): return None
    return lambda L, hand, ang, s, lt, flip: None
WATCH = {}

sheep_x = segs([(108, 116, 790, 0.6, 0.8), (131.5, 138, 1360, 0.5, 0.7), (142, 148.5, 1428, 0.5, 0.8), (T_FREE, T_FREE + 0.5, 1395, 0.1, 0.2),
                (252, 262, 1640, 0.6, 0.8), (276, 279, 1700, 0.5, 0.6)], 1300)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300, lift=[(0, 24), (LAND - 0.6, 24), (LAND + 0.4, 0), (RISE0 + 0.4, 0), (RISE0 + 1.2, 24)],
    head=[(0, 0), (LAND + 3, 0), (LAND + 4, 16), (LAND + 6, 0)] + [(116, 0)] + [(116.5 + k * 0.6, -14 if k % 2 == 0 else 4) for k in range(8)] + [(121.5, 0),
          (T_STOP - 2.2, 0), (T_STOP - 1.9, -20), (T_STOP - 0.8, -8), (T_STOP + 3, -4), (T_FREE, 0)] + [(276, 0), (277, 16), (278.4, 0)],
    sniff=[(0, 0), (114.5, 0), (115.5, 0.8), (116.4, 0)],
    hop=[(122.2, 0.3, 16), (123.0, 0.3, 14), (123.9, 0.3, 12), (124.8, 0.35, 10), (T_STOP - 2.2, 0.25, 12), (T_FREE, 0.35, 22)],
    pitch=[(0, 0), (125.1, 0), (125.4, -26), (129.5, -24), (130.2, 0), (T_STOP - 2.2, 0), (T_STOP - 2.0, 8), (T_FREE, 6), (T_FREE + 0.3, 0)],
    crouch=[(0, 0), (125.1, 0), (125.4, 18), (129.5, 18), (130.2, 0)],
    look=[(0, (0, 0)), (LAND, (0.4, 0)), (110, (-0.6, 0)), (125, (0.8, -0.8)), (131, (0, 0)), (T_STOP - 2, (0.9, -0.4)), (T_STOP + 2, (0.3, 0.3)),
          (186, (0.4, -0.8)), (245, (0.3, -0.5))],
    tail=[(0, 0), (T_STOP - 2.3, 0), (T_STOP - 2.0, 40), (T_FREE, 40), (T_FREE + 0.3, 0)],
    laugh=[(0, 0), (242, 0), (242.6, 1), (257, 1), (258, 0), (283, 0), (283.6, 0.8), (300, 0.7)],
    mouth=[(116.3, 121.4, 'open'), (T_STOP - 2.1, T_STOP - 0.6, 'open'), (276.8, 278.6, 'open')])
sheep_y = lambda t: gy(sheep_x(t)) + 112 - descend(t, 0.4) - rise(t, 0.5)
sheep = SheepActor(SHEEP, sheep_y, facing=[(0, 1), (107.5, -1), (131.5, 1), (139, -1), (251.5, 1)])
sheep.shadow = lambda t: LAND - 1.5 < t < RISE0 + 1.0
sheep.cast = lambda t: dict(cast=0.0) if (t < LAND - 0.3 or t > RISE0 + 0.8) else None

# the lantern box: in the mouth while flying, set down while they stay
BOXX = 1236
def box_fn(f, X, Y, s, t, W_, C):
    sb = 0.85 * s
    if t < LAND + 4.5 or t >= 277.6:
        m = SHEEP_LAST.get('mouth')
        if m is None: return
        fl = steps(sheep.facing, t); X, Y = m[0] - 5 * sb * fl, m[1] + 168 * sb + 6 * s
    box(f, X, Y, sb, light=W_.light, rim=W_.rim, glow_amt=lantern(t), t=t, handle=True, grey=1 - gold(t))
    WATCH['box'] = (X, Y - 60 * sb)
def box_foot(t):
    if t < LAND + 4.5 or t >= 277.6: return (sheep_x(t), sheep_y(t) + 1)
    return (BOXX, gy(BOXX) + 104)
boxp = Prop(box_fn, box_foot, height=150, tuft_w=50)

# the pocket watch, given to the boy
def watch_fn(f, X, Y, s, t, W_, C):
    h = BOY_LAST.get('handR')
    if h is not None: pocket_watch(f, h[0], h[1] + 16 * s, 1.2 * s, t, light=W_.light, rim=W_.rim)
watchp = Prop(watch_fn, lambda t: (boy_x(t), gy(boy_x(t)) + 71), height=40, active=lambda t: 266.6 <= t < 276.5)
SC.actors = CLOCKS + [cm, boy, sheep, boxp, watchp]

# ---------------------------------------------------------------- chain tangle, birds, gold
FLOCK = Flock(n=12, seed=5, spread=(300, 110)); TRAIL = GoldTrail()
def chain_wrap(f, t, z):
    a = float(keys([(0, 0), (121.3, 0), (122.0, 1), (130.4, 1), (131.2, 0)], t))
    if a <= 0 or 'head' not in SHEEP_LAST: return
    hp, tp = np.array(SHEEP_LAST['head']), np.array(SHEEP_LAST['tail']); c = (hp + tp) / 2 + [0, 12 * z]
    rx = abs(hp[0] - tp[0]) * 0.5; ry = rx * 0.55
    for ring in range(3):
        for k in range(26):
            u = k / 26 * 2 * math.pi + ring * 0.7 + t * 0.4
            x = c[0] + math.cos(u) * rx * (0.55 + ring * 0.18); y = c[1] + math.sin(u) * ry * 0.35 + (ring - 1) * ry * 0.45 + math.sin(u * 2) * 4 * z
            if math.sin(u) > -0.2:
                cv2.ellipse(f, (int(x * 8), int(y * 8)), (int(8 * z * 8), int(5 * z * 8)), math.degrees(u) + 90, 0, 360,
                            (0.95 * a, 0.78 * a, 0.35 * a), max(2, int(3 * z)), cv2.LINE_AA, shift=3)
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    chain_wrap(f, t, z)
    # birds: with them in the sky, away while they stay, back for the leaving
    if t < LAND + 6 or t > RISE0 - 5:
        bx = boy_x(t); hx, hy = C.to_screen(bx, gy(bx) + 70 - descend(t) - rise(t) - 330)
        away = ss((t - LAND) / 6) if t < LAND + 6 else 1 - ss((t - RISE0 + 5) / 5)
        cx, cy = hx + 80 * z + away * 400 * z, hy - 300 * z - away * 900 * z
        anchors = []
        if away < 0.3:
            if 'handR' in BOY_LAST: anchors.append(tuple(BOY_LAST['handR']))
            h = sheep_harness(z)
            if h is not None: anchors.append(h)
        FLOCK.draw(f, t, cx, cy, z, anchors=anchors, light=W_.light, flip=-1, arrive=1 - away / 0.3 if away < 0.3 else 0)
    g = gold(t)
    if g > 0.05 and 'box' in WATCH: TRAIL.draw(f, t, WATCH['box'], g * 0.8, z, drift=(0, -160))
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
def lift_cam(t):
    u = ss((t - RISE0) / 18)
    return (1720 - 60 * u, gy(1720) - 110 - rise(t) * 0.72, 1.3 - 0.45 * u)
G = lambda x, dy, z: (x, gy(x) + dy, z)
SC.shots = [
    (0, [(0, (1440, 560, 0.95)), (14, (1400, 600, 1.0))], 0.0),
    (14, [(14, G(1200, -260, 1.3)), (LAND + 2, G(1220, -60, 1.45))], 0.3),
    (LAND + 2, [(LAND + 2, G(1440, -140, 1.0)), (40, G(1460, -140, 1.05))], 0.0),
    (40, [(40, G(POST2 - 30, -10, 2.6)), (46, G(POST2 - 30, -10, 2.7))], 1.0),
    (46, [(46, G(2050, -60, 1.6)), (55, G(1950, -60, 1.7))], 0.6),
    (55, [(55, G(1500, -80, 1.0)), (61, G(900, -60, 1.2))], 0.3),
    (61, [(61, G(GF1 + 60, -20, 2.6)), (66, G(GF1 + 70, -20, 2.7))], 1.0),
    (66, [(66, G(1070, -30, 2.2)), (80, G(1072, -32, 2.3))], 1.0),
    (80, [(80, G(1300, -60, 1.15)), (86, G(1550, -60, 1.25))], 0.3),
    (86, [(86, G(1580, -60, 2.0)), (104, G(1590, -64, 2.1))], 0.8),
    (104, [(104, G(1440, -140, 0.95)), (116, G(1300, -120, 1.0))], 0.0),
    (116, [(116, G(GF1 + 70, -10, 2.6)), (122, G(GF1 + 70, -12, 2.7))], 1.0),
    (122, [(122, G(800, -10, 2.2)), (131.5, G(805, -12, 2.3))], 0.8),
    (131.5, [(131.5, G(1000, -60, 1.3)), (142, G(1300, -60, 1.4))], 0.3),
    (142, [(142, G(1460, -50, 1.9)), (T_STOP - 2.5, G(1470, -52, 2.0))], 0.8),
    (T_STOP - 2.5, [(T_STOP - 2.5, G(GEAR - 30, -10, 3.0)), (T_STOP, G(GEAR - 30, -10, 3.1))], 2.0),
    (T_STOP, [(T_STOP, (1440, 640, 0.95)), (T_STOP + 6, (1440, 640, 0.97))], 0.0),
    (T_STOP + 6, [(T_STOP + 6, G(2185, 0, 3.4)), (170, G(2185, 0, 3.55))], 2.0),
    (170, [(170, G(1900, -60, 1.5)), (184, G(1800, -60, 1.6))], 0.5),
    (184, [(184, G(1735, -10, 3.0)), (194, G(1735, -16, 3.1))], 1.5),
    (194, [(194, (2150, 600, 1.1)), (201, (2140, 590, 1.15))], 0.0),
    (201, [(201, G(1738, -10, 3.2)), (210, G(1738, -12, 3.3))], 2.0),
    (210, [(210, G(1760, -100, 1.3)), (240, G(1790, -110, 1.4))], 0.3),
    (240, [(240, G(1760, -30, 2.6)), (247, G(1762, -32, 2.7))], 1.5),
    (247, [(247, (BOXX, gy(BOXX) + 30, 3.0)), (252, (BOXX, gy(BOXX) + 26, 3.1))], 2.0),
    (252, [(252, G(1720, -50, 1.6)), (259, G(1725, -52, 1.65))], 0.6),
    (259, [(259, G(1785, -30, 2.6)), (270, G(1788, -32, 2.7))], 1.5),
    (270, [(270, G(1700, -90, 1.2)), (RISE0, G(1720, -90, 1.3))], 0.3),
    (RISE0, lift_cam, 0.2),
]
SC.subs = [(72.0, 77.0, 'No time, no time! If I stop, they stop!', '没时间，没时间！我一停，它们就停了！'),
           (195.0, 199.9, 'Oh. I forgot it was so pretty.', '哦。我都忘了，它这么美。'),
           (262.0, 265.9, 'For when you need a minute.', '等你需要一分钟的时候用。')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 36, 'wonder', 0.8), (36, 110, 'playful', 0.75), (110, T_STOP, 'playful', 0.9), (T_STOP + 4, 186, 'sad', 0.5), (186, 240, 'dusk', 0.9),
         (240, 300, 'triumph', 0.85)]
SFX = [(0, 'wind', dict(dur=LAND + 3, gain=0.8)), (LAND, 'thump', dict(gain=0.5)), (LAND + 0.5, 'birds', dict(n=12))]
for k in range(int((T_STOP - LAND) * 2)):   # the ticking of all the clocks
    SFX.append((LAND + k / 2, 'tap', dict(gain=0.32 if k % 2 == 0 else 0.22)))
for k in range(int((300 - T_RESTART) * 2)): SFX.append((T_RESTART + 1.5 + k / 2, 'tap', dict(gain=0.22 if k % 2 == 0 else 0.15)))
for (a, b) in CRANK:
    for k in range(int((b - a) / 0.6)): SFX.append((a + k * 0.6, 'sweep', dict(dur=0.18, gain=0.35)))
for (a, b) in ((46, 50), (55, 60.5), (66, 71), (80, 86), (104, 110), (118, 124)):
    for k in range(int((b - a) * 3.2)): SFX.append((a + k / 3.2, 'step', dict(gain=0.5)))
SFX += [(116.5, 'chime', dict(notes=[700, 900], gain=0.3)), (122.2, 'tap', dict(gain=0.6)), (123.0, 'tap', dict(gain=0.6)), (125.3, 'thump'), (125.5, 'baa', dict(f=300, dur=0.6)),
        (126.6, 'giggle', dict(n=6, shift=-6, gain=0.6)), (T_STOP - 2.2, 'baa', dict(f=460, dur=0.4)), (T_STOP - 2.0, 'thump', dict(gain=0.8)),
        (T_STOP - 0.4, 'chime', dict(notes=[300, 260], gain=0.6)), (195, 'shimmer', dict(dur=6, gain=0.5)), (241.2, 'giggle', dict(n=24)),
        (241.6, 'chime', dict(notes=[1500, 1880, 2250])), (242, 'sparkle'), (T_FREE, 'pop'), (263, 'chime', dict(notes=[2600, 3100], gain=0.5)),
        (T_RESTART, 'chime', dict(notes=[1200, 1500, 1800], gain=0.6)), (RISE0 - 4, 'birds', dict(n=16)), (RISE0, 'whoosh', dict(dur=4, f=500)),
        (RISE0 + 3, 'giggle', dict(n=10))]

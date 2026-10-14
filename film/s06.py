# S06 · The Cloud (300 s). A planet of endless soft rain and a sad Cloud. She thinks the sheep is a lost baby cloud;
# the sheep plays along, puffs up and plays tag with her on the birds. She laughs, the rain stops, a rainbow. Pip blazes gold.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import GoldTrail, sheep_harness, BOY_LAST, SHEEP_LAST
from props3 import Flock, box
from cloudchar import draw_cloud_char

class S06(Scene):
    DURATION = 300.0

SC = S06()
RAIN = World('rain', place='cloudp'); AFTER = World('after', place='cloudp')
gy = RAIN.gy
T_DIS0, T_DIS1 = 188.0, 198.0
SC.worlds = [(0, T_DIS0, RAIN), (T_DIS0, T_DIS1, (RAIN, AFTER)), (T_DIS1, 1e9, AFTER)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

LAND, RISE0 = 30.0, 274.0
def descend(t, d=0.0): return 560 * (1 - ss((t - 12 - d) / (LAND - 12)))
def rise(t, d=0.0):
    u = max(0.0, t - RISE0 - d); return 620 * ss(u / 18) * (0.4 + 0.6 * min(1, u / 6))
def rain_amt(t): return 1.0 - 0.45 * ss((t - 140) / 25) - 0.55 * ss((t - 182) / 5)
def gold(t):
    g = ss((t - 240) / 1.5) * (1 - 0.35 * ss((t - 262) / 4)) * (0.88 + 0.12 * math.sin(t * 5))
    return g
def lantern(t): return 0.2 + 0.1 * ss((t - 186) / 6) + 0.75 * gold(t)

# ---------------------------------------------------------------- the boy
boy_x = segs([], 1150)
BOY = BoyAnim(boy_x, k=1.6, t_end=300,
    hang=[(0, 1), (LAND - 1.2, 1), (LAND, 0), (RISE0 - 0.3, 0), (RISE0 + 1.2, 1)], wind=[(0, 0.5), (LAND, 0.0)],
    crouch=[(0, 0), (LAND, 0), (LAND + 0.15, 16), (LAND + 0.8, 0)],
    poses={'armR': [(0, -128), (LAND, -128), (LAND + 0.8, 0), (31, 0), (32, 30), (52, 30), (53, 0), (268, 0), (270, -128), (300, -128)],
           'foreR': [(0, -6), (LAND, -6), (LAND + 0.8, 0), (31, 0), (32, 70), (52, 70), (53, 0), (268, 0), (270, -6), (300, -6)],
           'armL': [(0, 0), (31, 0), (32, -30), (52, -30), (53, 0)], 'foreL': [(0, 0), (31, 0), (32, -70), (52, -70), (53, 0)],
           'chest': [(0, 0)] + osc(32, 52, 0.12, -1.5, 1.5) + [(52.2, 0)],
           'head': [(0, 0), (112, 0), (112.4, 8), (112.8, 0), (113.2, 8), (113.6, 0)]},
    look_x=[(0, 0.4), (LAND, 0.4), (55, 0.9), (110, 0.9), (111, 0.5), (124, 0.6), (180, 0.8), (240, 0.3)],
    lookup=[(0, -0.3), (LAND, 0.0), (55, 0.5), (110, 0.3), (124, 0.7), (180, 0.5), (200, 0.9), (238, 0.8), (240, 0.0), (270, 0.8)],
    brows=[(0, 0.6), (55, 1.0), (82, 0.5), (130, 0.0)],
    laugh=[(0, 0), (138, 0), (139, 0.6), (176, 0.5), (178, 0), (181, 0), (182, 0.9), (192, 0.7), (194, 0), (240.5, 0), (241.3, 1), (256, 0.8), (258, 0.3), (284, 0.3), (285, 0.7), (300, 0.6)],
    mouth=[(200, 204, 'open')])
boy = BoyActor(BOY, lambda t: gy(boy_x(t)) + 70 - descend(t) - rise(t), facing=[(0, 1)])
boy.shadow = lambda t: LAND - 2 < t < RISE0 + 0.5
boy.cast = lambda t: dict(cast=0.0) if (t < LAND - 0.5 or t > RISE0 + 0.3) else None

# ---------------------------------------------------------------- the sheep (puffs up, flies on the birds, plays tag)
TAG0, TAG1 = 124.0, 180.0
sheep_x = segs([(127, 133, 1650, 0.5, 0.5), (134, 140, 1150, 0.5, 0.5), (141, 147, 1750, 0.5, 0.5), (148.5, 155, 1050, 0.5, 0.5),
                (156, 163, 1680, 0.5, 0.5), (164, 171, 1250, 0.5, 0.5), (172, 178, 1320, 0.6, 0.7), (276, 279, 1360, 0.5, 0.6)], 1300)
def fly(t):
    u = ss((t - TAG0) / 4) * (1 - ss((t - (TAG1 - 4)) / 4))
    return u * (260 + 70 * math.sin((t - TAG0) * 1.1))
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300,
    lift=[(0, 24), (LAND - 0.6, 24), (LAND + 0.4, 0), (TAG0, 0), (TAG0 + 1, 24), (TAG1 - 1, 24), (TAG1, 0), (RISE0 + 0.4, 0), (RISE0 + 1.2, 24)],
    paddle=[(0, 0), (TAG0 + 1, 0), (TAG0 + 2, 1), (TAG1 - 1.5, 1), (TAG1 - 1, 0)],
    head=[(0, 0)] + osc(40, 43, 0.14, -16, 16) + [(43.2, 0), (276, 0), (277, 16), (278.4, 0)],
    look=[(0, (0, 0)), (LAND, (0.4, -0.3)), (80, (0.8, -0.6)), (110, (-0.5, -0.4)), (TAG0, (0.6, -0.5)), (TAG1, (0.5, -0.6)), (200, (0.3, -0.9)), (240, (-0.4, 0))],
    tail=[(0, 0)] + osc(40, 43, 0.14, -30, 30) + [(43.2, 0)] + osc(TAG0 + 2, TAG1 - 2, 0.3, -24, 24) + [(TAG1 - 1.5, 0)],
    laugh=[(0, 0), (138, 0), (138.6, 1), (176, 1), (177, 0), (182, 0), (182.6, 1), (192, 0.8), (193, 0), (241, 0), (241.6, 1), (257, 1), (258, 0), (284, 0), (284.6, 0.8), (300, 0.7)],
    mouth=[(113.5, 114.6, 'open'), (276.8, 278.6, 'open')])
sheep_y = lambda t: gy(sheep_x(t)) + 112 - descend(t, 0.4) - rise(t, 0.5) - fly(t)
sheep = SheepActor(SHEEP, sheep_y, facing=[(0, 1), (133.5, -1), (140.5, 1), (148, -1), (155.5, 1), (163.5, -1), (171.5, 1)])
flying = lambda t: t < LAND - 0.3 or TAG0 + 0.5 < t < TAG1 - 0.5 or t > RISE0 + 0.8
sheep.shadow = lambda t: not flying(t)
sheep.cast = lambda t: dict(cast=0.0) if flying(t) else None
sheep.scale = lambda t: 1 + 0.22 * ss((t - 112) / 1.6) * (1 - ss((t - 181) / 2.5))

BOXX = 1236; WATCH = {}
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

# ---------------------------------------------------------------- the Cloud
def cloud_pos(t):
    if t < 82: x, h = 1880, 250
    elif t < TAG0: u = ss((t - 82) / 8); x, h = 1880 + (1600 - 1880) * u, 250 - 20 * u
    elif t < TAG1 + 2:   # chasing the sheep
        u = ss((t - TAG0) / 3) * (1 - ss((t - TAG1 + 1) / 3)); td = t - 1.4
        x = 1600 * (1 - u) + (sheep_x(td) + 150 * math.sin(t * 0.7)) * u; h = 230 * (1 - u) + (fly(td) + 210) * u
    elif t < 262: x, h = 1600, 230
    else: x, h = 1600 + 40 * ss((t - 262) / 6), 230 + 40 * ss((t - 262) / 6)
    return x, gy(x) - h + 10 * math.sin(t * 0.9)
class CloudActor(Actor):
    height = 300; tuft_w = 0
    def __init__(self): self.cast = dict(cast=0.0)
    def foot(self, t): x, _ = cloud_pos(t); return (x, gy(x) + 30)
    def draw(self, f, X, Y, s, t, W_, C):
        x, y = cloud_pos(t); X2, Y2 = C.to_screen(x, y)
        mood = float(keys([(0, 0), (80, 0), (90, 0.35), (TAG0, 0.4), (150, 0.75), (181, 0.85), (183, 1.0)], t))
        draw_cloud_char(
                        f, X2, Y2, 0.95 * s, t, mood=mood, rain=max(0, rain_amt(t) * (1 - mood * 0.6)), sob=float(keys([(0, 1), (78, 1), (81, 0)], t)),
                        talk=float(keys([(92, 0), (92.1, 1), (96.9, 1), (97.0, 0)], t)),
                        laugh=float(keys([(0, 0), (TAG0 + 8, 0), (TAG0 + 9, 0.6), (TAG1 - 6, 0.6), (TAG1 - 5, 0), (181.5, 0), (182.2, 1), (195, 1), (197, 0.3),
                                          (241, 0.3), (242, 0.9), (256, 0.8), (258, 0.3)], t)),
                        wave=float(keys([(0, 0), (268, 0), (269, 1), (296, 1)], t)),
                        look=(float(keys([(0, 0), (55, 0), (60, -0.8), (TAG0, -0.6), (TAG1, -0.5), (200, 0.0), (270, -0.6)], t)),
                              float(keys([(0, 0.6), (60, 0.5), (TAG0, 0.3), (200, -0.8), (238, -0.6), (240, 0.4)], t))),
                        light=W_.light, rain_len=(gy(x) - y) / 0.95 / 0.5 + 40)
cloud = CloudActor()
SC.actors = [cloud, boy, sheep, boxp]

# ---------------------------------------------------------------- rain, rainbow, birds, gold
FLOCK = Flock(n=12, seed=5, spread=(300, 110)); TRAIL = GoldTrail()
RAINR = np.random.default_rng(21).random((420, 4))
def rainbow(f, cx, cy, r, w, a):
    if a <= 0.01: return
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    cols = [hexc(c) for c in ('#ff6a6a', '#ffb05a', '#fff07a', '#8ae07a', '#7ab8ff', '#a88aff')]
    u = (r - d) / w
    m = np.clip(1 - np.abs(u - 0.5) * 2, 0, 1) ** 0.8 * a * np.clip((cy - yy) / (0.45 * r), 0, 1)   # an arc, fading out toward its feet
    idx = np.clip(u * 6, 0, 5.999); i0 = idx.astype(int)
    c = np.stack(cols)[i0]
    f[:] = f * (1 - 0.55 * m[..., None]) + c * 0.55 * m[..., None]
def sky_fx(f, C, t, W_):
    if W_ is AFTER:
        a = ss((t - 200) / 14) * 0.85
        cx, cy = C.to_screen(1500, 1250); rainbow(f, cx, cy, 1150 * C.z * 0.5 * 1.4, 130 * C.z * 0.5 * 1.4, a)
SC.sky_fx = sky_fx
def front_fx(f, C, t, W_):
    z = C.z * 0.5
    ra = rain_amt(t) if W_ is RAIN else 0.0
    if ra > 0.01:   # rain over everything
        n = int(420 * ra)
        for k in range(n):
            u, v, sp, ph = RAINR[k]
            if t > 140 and math.sin(u * 13 + t * 0.3) > 1.6 - 2 * ra: continue   # patches of dry
            fall = (t * (1.3 + sp * 0.6) + ph) % 1.0
            x = u * (W + 200) - 100 - fall * 40; y = fall * (H + 100) - 50
            ln = (16 + 26 * sp) * (0.6 + 0.4 * z)
            cv2.line(f, (int(x * 8), int(y * 8)), (int((x - ln * 0.12) * 8), int((y + ln) * 8)), (0.82 * 0.6, 0.86 * 0.6, 0.95 * 0.6), 1, cv2.LINE_AA, shift=3)
            f[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))] = (0.9, 0.93, 1.0)
    if 40 < t < 43.5 and 'head' in SHEEP_LAST:   # the sheep shakes the water off
        hp, tp = np.array(SHEEP_LAST['head']), np.array(SHEEP_LAST['tail']); c = (hp + tp) / 2
        r = np.random.default_rng(int(t * 24))
        for k in range(30):
            a = r.random() * 6.28; d = (40 + r.random() * 120) * z * 2
            glow(f, c[0] + math.cos(a) * d, c[1] + math.sin(a) * d * 0.6, 2.4 * z * 2, '#dfefff', 0.7)
    if 112 < t < 116 and 'head' in SHEEP_LAST:   # puffing up: a little burst of sparkle
        hp, tp = np.array(SHEEP_LAST['head']), np.array(SHEEP_LAST['tail']); c = (hp + tp) / 2; b = t - 112
        for k in range(16):
            a = k / 16 * 6.28; d = (90 + 120 * b) * z * 2
            glow(f, c[0] + math.cos(a) * d, c[1] + math.sin(a) * d * 0.6, 2.4 * z * 2, '#ffffff', 0.8 * (1 - b / 4))
    # birds: arrive with them, carry the sheep in the tag, take them away at the end
    show = t < LAND + 6 or TAG0 - 7 < t < TAG1 + 6 or t > RISE0 - 6
    if show:
        if t < LAND + 6 or t > RISE0 - 6:
            bx = boy_x(t); hx, hy = C.to_screen(bx, gy(bx) + 70 - descend(t) - rise(t) - 330)
            away = ss((t - LAND) / 6) if t < LAND + 6 else 1 - ss((t - RISE0 + 6) / 5)
            anchors_fn = lambda: [tuple(BOY_LAST['handR'])] if 'handR' in BOY_LAST else []
        else:
            sx = sheep_x(t); hx, hy = C.to_screen(sx, sheep_y(t) - 220)
            away = 1 - ss((t - TAG0 + 7) / 6) if t < TAG0 else ss((t - TAG1) / 6)
            anchors_fn = lambda: []
        cx, cy = hx + 80 * z + away * 400 * z, hy - 300 * z - away * 900 * z
        anchors = []
        if away < 0.3:
            anchors = anchors_fn(); h = sheep_harness(z)
            if h is not None: anchors.append(h)
        FLOCK.draw(f, t, cx, cy, z, anchors=anchors, light=W_.light, flip=-1, arrive=1 - away / 0.3 if away < 0.3 else 0)
    g = gold(t)
    if g > 0.05 and 'box' in WATCH: TRAIL.draw(f, t, WATCH['box'], g * 0.8, z, drift=(0, -160))
    if t > RISE0 + 6 and W_ is AFTER:   # a small rainbow follows them up
        bx = boy_x(t); X, Y = C.to_screen(bx + 120, gy(bx) + 70 - rise(t) + 200)
        rainbow(f, X, Y, 300 * z * 2, 40 * z * 2, 0.6 * ss((t - RISE0 - 6) / 4))
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
G = lambda x, dy, z: (x, gy(x) + dy, z)
def lift_cam(t):
    u = ss((t - RISE0) / 18)
    return (1300 + 60 * u, gy(1300) - 110 - rise(t) * 0.72, 1.3 - 0.45 * u)
def tag_cam(t):
    sx = 0.5 * (sheep_x(t) + cloud_pos(t)[0]); return (0.7 * sx + 0.3 * 1440, gy(1440) - 120 - 0.6 * fly(t), 1.1)
SC.shots = [
    (0, [(0, (1440, 560, 0.95)), (14, (1400, 600, 1.0))], 0.0),
    (14, [(14, G(1200, -260, 1.3)), (LAND + 2, G(1220, -60, 1.45))], 0.3),
    (LAND + 2, [(LAND + 2, G(1150, -40, 2.6)), (40, G(1152, -42, 2.7))], 1.0),
    (40, [(40, G(1300, -20, 2.4)), (44, G(1302, -22, 2.5))], 1.0),
    (44, [(44, G(1440, -140, 1.0)), (55, G(1460, -140, 1.05))], 0.0),
    (55, [(55, G(1150, -40, 2.6)), (60, G(1152, -42, 2.7))], 1.0),
    (60, [(60, G(1880, -250, 2.0)), (80, G(1880, -250, 2.15))], 0.6),
    (80, [(80, G(1500, -140, 1.2)), (92, G(1520, -150, 1.3))], 0.3),
    (92, [(92, G(1600, -230, 2.4)), (98, G(1600, -230, 2.5))], 0.8),
    (98, [(98, G(1300, -20, 2.6)), (104, G(1302, -22, 2.7))], 1.0),
    (104, [(104, G(1450, -140, 1.2)), (112, G(1450, -140, 1.25))], 0.3),
    (112, [(112, G(1300, -30, 2.2)), (118, G(1300, -40, 2.3))], 0.8),
    (118, [(118, G(1400, -200, 1.0)), (TAG0 + 4, G(1400, -260, 1.05))], 0.0),
    (TAG0 + 4, tag_cam, 0.0),
    (150, [(150, G(1150, -40, 2.6)), (155, G(1152, -42, 2.7))], 1.0),
    (155, tag_cam, 0.0),
    (TAG1, [(TAG1, G(1450, -160, 1.1)), (186, G(1460, -160, 1.15))], 0.0),
    (186, [(186, G(1600, -230, 2.4)), (194, G(1600, -230, 2.5))], 0.8),
    (194, [(194, G(1440, -200, 0.95)), (214, G(1440, -240, 1.0))], 0.0),
    (214, [(214, G(1200, -40, 1.8)), (228, G(1210, -44, 1.85))], 0.6),
    (228, [(228, G(1440, -180, 1.0)), (240, G(1440, -180, 1.02))], 0.0),
    (240, [(240, (BOXX, gy(BOXX) + 30, 3.0)), (246, (BOXX, gy(BOXX) + 26, 3.1))], 2.0),
    (246, [(246, G(1250, -40, 2.2)), (256, G(1255, -42, 2.3))], 0.8),
    (256, [(256, G(1620, -240, 2.2)), (264, G(1620, -240, 2.3))], 0.8),
    (264, [(264, G(1420, -150, 1.1)), (RISE0, G(1400, -150, 1.2))], 0.3),
    (RISE0, lift_cam, 0.2),
]
SC.subs = [(92.0, 97.0, 'A little cloud! Are you lost too?', '一朵小云！你也迷路了吗？')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 80, 'sad', 0.7), (80, TAG0, 'wonder', 0.75), (TAG0, TAG1, 'playful', 0.95), (TAG1, 240, 'wonder', 0.9), (240, 300, 'triumph', 0.9)]
SFX = [(0, 'wind', dict(dur=LAND + 3, gain=0.7)), (0, 'pour', dict(dur=40, gain=0.7)), (40, 'pour', dict(dur=40, gain=0.7)), (80, 'pour', dict(dur=40, gain=0.7)),
       (120, 'pour', dict(dur=40, gain=0.6)), (160, 'pour', dict(dur=26, gain=0.4)), (LAND, 'thump', dict(gain=0.4)), (LAND + 0.5, 'birds', dict(n=10)),
       (40, 'sneeze', dict(gain=0.4)), (41, 'sweep', dict(dur=1.5, gain=0.5)), (62, 'giggle', dict(n=3, shift=-14, gain=0.3)), (70, 'giggle', dict(n=3, shift=-14, gain=0.3)),
       (113.6, 'baa', dict(f=360, dur=0.6)), (114, 'sparkle'), (TAG0 - 6, 'birds', dict(n=14)), (TAG0 + 1, 'whoosh', dict(dur=2, f=600))]
for k in range(8): SFX.append((TAG0 + 8 + k * 6.5, 'giggle', dict(n=6, shift=6 * (k % 2))))
SFX += [(182.2, 'giggle', dict(n=24, shift=-4)), (186, 'shimmer', dict(dur=8, gain=0.7)), (200, 'chime', dict(notes=[1000, 1250, 1500, 2000], gain=0.6)),
        (240, 'chime', dict(notes=[1500, 1880, 2250])), (240.5, 'sparkle'), (241.3, 'giggle', dict(n=20)), (RISE0 - 6, 'birds', dict(n=16)),
        (RISE0, 'whoosh', dict(dur=4, f=500)), (RISE0 + 3, 'giggle', dict(n=10)), (RISE0 + 6, 'shimmer', dict(dur=8, gain=0.5))]

# S03 · Grey by tomorrow (300 s). Morning: Pip is fading. Through the telescope: the pilot in the desert, searching the sky.
# "We have to take it home." The sheep brings the old box; Pip hops in and it glows. The birds come. Goodbye to the rose. Lift off.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys, travel
from boy2 import LAST as BOY_LAST
from pilot import draw_pilot, draw_plane
from props3 import telescope, box, Flock

class S03(Scene):
    DURATION = 300.0

SC = S03()
MORN = World('morning'); DES = World('night', place='desert')
gy = MORN.gy; dgy = DES.gy
T_IN, T_OUT = 75.0, 117.0                       # through the telescope
SC.worlds = [(0, T_IN, MORN), (T_IN, T_OUT, DES), (T_OUT, 1e9, MORN)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

PIPX = 1700; NEST = (PIPX, gy(PIPX) + 98)
TX = 860                                         # the telescope
BOXX = 640; BOX_DOWN = 1662
RISE0 = 274.0
def rise(t, d=0.0):
    u = max(0.0, t - RISE0 - d); return 620 * ss(u / 18) * (0.4 + 0.6 * min(1, u / 6))

# ---------------------------------------------------------------- the boy
boy_x = segs([(56, 68, TX + 128, 0.8, 0.9), (120.5, 130.5, 1600, 0.8, 1.0)], 1600)
BOY = BoyAnim(boy_x, k=1.6, t_end=300,
    crouch=[(0, 34), (52, 34), (54, 0), (69, 0), (70.5, 26), (118.5, 26), (119.8, 0), (130.5, 0), (132, 34), (158, 34), (160, 0)],
    poses={'chest': [(0, 6), (52, 6), (54, 0), (69, 0), (70.5, 9), (118.5, 9), (119.8, 0), (129, 0), (131, 6), (158, 6), (160, 0)],
           'head': [(0, 6), (52, 6), (54, 0), (69, 0), (70.5, 8), (118.5, 8), (119.8, 0)],
           'armR': [(0, 0), (69, 0), (70.5, -48), (118.5, -46), (119.5, 0), (162, 0), (163.2, -132), (167.5, -130), (168.5, 0),
                    (258, 0), (259.5, -128), (300, -128)],
           'foreR': [(0, 0), (69, 0), (70.5, -60), (118.5, -60), (119.5, 0), (162, 0), (163.2, -70), (167.5, -70), (168.5, 0),
                     (258, 0), (259.5, -6), (300, -6)],
           'armL': [(0, 0), (31.5, 0), (32.5, -30), (40, -30), (41, 0)], 'foreL': [(0, 0), (31.5, 0), (32.5, -40), (40, -40), (41, 0)]},
    look_x=[(0, 0.6), (50, 0.6), (52, -0.2), (56, -0.6), (70, -0.6), (120, 0.0), (129, 0.6), (160, 0.3), (176, -0.6), (196, 0.4), (206, 0.6), (250, 0.4)],
    lookup=[(0, -0.45), (52, -0.4), (54, 0.0), (130, 0), (131, -0.45), (152, -0.3), (154.5, 0.6), (158, 0.5), (160, 0.0), (175, 0.0),
            (250, 0.0), (252, 0.8), (300, 0.8)],
    brows=[(0, 1), (54, 0.6), (120, 1), (150, 0.2), (204, 0), (300, 0)],
    talk=[(147.0, 0), (147.1, 1), (153.4, 1), (153.5, 0)],
    laugh=[(0, 0), (204.3, 0), (205, 0.6), (209, 0.4), (210, 0), (222, 0), (223, 0.35), (230, 0.3), (231, 0), (252, 0), (253, 0.5), (300, 0.5)],
    mouth=[(119.6, 121.0, 'sad')],
    hang=[(0, 0), (RISE0 - 0.3, 0), (RISE0 + 1.2, 1)])
boy = BoyActor(BOY, lambda t: gy(boy_x(t)) + 70 - rise(t), facing=[(0, 1), (55.5, -1), (120.2, 1)])

# ---------------------------------------------------------------- the sheep
sheep_x = segs([(175.5, 185, BOXX + 150, 0.6, 0.8), (189.5, 203, 1770, 0.6, 0.9)], 1770)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300,
    crouch=[(0, 60), (34, 60), (35.5, 20), (44.5, 20), (46, 60), (171, 60), (174, 0), (185.5, 0), (186.5, 12), (188.2, 12), (189, 0)],
    head=[(0, 14), (34, 14), (35.5, 18), (44.5, 18), (46, 14), (171, 14), (174, 0), (185.5, 0), (186.5, 16), (188.2, 16), (189.2, 0),
          (259, 0), (260, 14), (261.5, 0)],
    sniff=[(0, 0), (35.6, 0), (36.4, 0.9), (38, 0.6), (39, 0.9), (44, 0.9), (44.5, 0)],
    look=[(0, (-0.4, 0.8)), (46, (-0.6, 0.5)), (150, (-0.7, 0.2)), (172, (-0.8, 0)), (190, (0.6, 0)), (204, (-0.3, 0.6)), (250, (0, -0.8))],
    tail=[(0, 0), (184.5, 0)] + osc(185, 188, 0.3, -20, 20) + [(188.5, 0), (204, 0)] + osc(204.5, 208, 0.3, -24, 24) + [(208.5, 0)],
    mouth=[(186.6, 188.4, 'open'), (259.8, 261.4, 'open')],
    sleep=[(0, 0)], lift=[(0, 0), (RISE0 + 0.4, 0), (RISE0 + 1.2, 24)])
sheep_y = lambda t: gy(sheep_x(t)) + 112 - rise(t, 0.5)
sheep = SheepActor(SHEEP, sheep_y, facing=[(0, -1), (175, -1), (189.2, 1), (203, -1), (262, 1)])

# ---------------------------------------------------------------- the rose (morning: no dome)
ROSE = (1440, gy(1440) + 40)
rose = RoseActor(ROSE, dome=[(0, 0)], lean=[(0, 0), (264, 0), (265, -8), (270, -8), (271.5, -14), (278, -12)],
                 talk=[(265.6, 0), (265.8, 1), (269.4, 1), (269.6, 0)])

# ---------------------------------------------------------------- Pip (greyer every minute), then into the box
def pip_light(t): return 0.40 - 0.16 * ss(t / 70) - 0.06 * ss((t - 120) / 60)
HOP0 = 216.0
def pip_state(t):
    if t >= HOP0 + 0.9: return None
    x, y = NEST; sq = 0.02 * math.sin(t * 2 * math.pi / 3.6); rot = 0.0
    face = 'sad' if t < 200 else 'open'
    if 36.5 < t < 44: rot = 0.07 * math.sin((t - 36.5) * 9) * math.exp(-(t - 36.5) * 0.4)   # nudged by the nose
    if t >= HOP0:   # one hop up and into the box
        u = (t - HOP0) / 0.9; bx, by = BOX_DOWN, gy(BOX_DOWN) + 100 - 150
        x = NEST[0] + (bx - NEST[0]) * u; y = NEST[1] + (by - NEST[1]) * u - 4 * 120 * u * (1 - u); rot = -0.6 * u
    lt = pip_light(t) + (0.08 * math.exp(-((t - 38.5) / 0.4) ** 2))
    return dict(x=x, y=y, ground_y=y + 30, light=lt, size=26, face=face, squash=sq, rot=rot, look=(-0.6, -0.4) if t > 205 else (0, 0.5))
pip = PipActor(pip_state)

# ---------------------------------------------------------------- the telescope and the box
EYE = {}
def tel_fn(f, X, Y, s, t, W_, C):
    EYE['p'] = telescope(f, X, Y, 1.8 * s, light=W_.light, rim=W_.rim, flip=-1, ang=-19)
tel = Prop(tel_fn, (TX, gy(TX) + 40), height=330, tuft_w=80)
def box_glow(t): return 0.0 if t < HOP0 + 0.8 else 0.75 * ss((t - HOP0 - 0.8) / 2.5) + 0.06 * math.sin(t * 3.1)
def box_mode(t):
    if t < 188.3: return 'ground0'
    if t < 203.5: return 'mouth'
    if t < 260.6: return 'ground1'
    return 'mouth'
def box_fn(f, X, Y, s, t, W_, C):
    sb = 0.85 * s; md = box_mode(t)
    if md == 'mouth':
        m = SHEEP_LAST.get('mouth')
        if m is None: return
        fl = steps(sheep.facing, t)
        X, Y = m[0] - 5 * sb * fl, m[1] + 168 * sb + 6 * s
        tilt = 5 * math.sin(t * 5)
    else: tilt = 0.0
    box(f, X, Y, sb, light=W_.light, rim=W_.rim, glow_amt=box_glow(t), t=t, handle=True, tilt=tilt)
def box_foot(t):
    md = box_mode(t)
    if md == 'ground0': return (BOXX, gy(BOXX) + 92)
    if md == 'ground1': return (BOX_DOWN, gy(BOX_DOWN) + 100)
    return (sheep_x(t), sheep_y(t) + 1)
boxp = Prop(box_fn, box_foot, height=150, tuft_w=60)
SC.actors = [boy, sheep, rose, pip, tel, boxp]
for a_ in SC.actors: a_.worlds = (MORN,)
boy.shadow = lambda t: t < RISE0 + 0.5; sheep.shadow = lambda t: t < RISE0 + 1.0

# ---------------------------------------------------------------- the desert, seen through the telescope
PX = 1500
def plane_fn(f, X, Y, s, t, W_, C): draw_plane(f, X, Y, 1.42 * s, light=W_.light, rim=W_.rim)
def pilot_fn(f, X, Y, s, t, W_, C):
    draw_pilot(f, X, Y, 0.95 * s, 1, t=t, light=W_.light, rim=W_.rim,
               up=float(keys([(0, 0.75), (104, 0.75), (108.5, 0.25), (117, 0.2)], t)),
               look=(float(keys([(0, 0)] + osc(80, 101, 5.0, -0.8, 0.8) + [(102, 0)], t)), 0),
               talk=float(keys([(100.4, 0), (100.5, 1), (103.8, 1), (103.9, 0)], t)),
               slump=float(keys([(0, 0), (104.5, 0), (109, 1)], t)), smile=0.15)
on_desert = lambda t: T_IN <= t < T_OUT
SC.actors += [Prop(plane_fn, (PX, dgy(PX) + 20), height=300, active=on_desert), Prop(pilot_fn, (PX - 60, dgy(PX) + 21), height=400, active=on_desert)]

def eye_iris_close(t0, t1):
    def fn(t):
        p = EYE.get('p', (W / 2, H / 2)); u = ss((t - t0) / (t1 - t0)); return p[0], p[1], 1500 * (1 - u) + 1
    return fn
def eye_iris_open(t0, t1, r1=1500):
    def fn(t):
        p = EYE.get('p', (W / 2, H / 2)); u = ss((t - t0) / (t1 - t0)); return p[0], p[1], r1 * u + 1
    return fn
def scope(t):   # the round telescope view over the desert
    if t < T_IN + 2.0: r = 720 * ss((t - T_IN) / 2.0)
    elif t > T_OUT - 2.0: r = 720 * ss((T_OUT - t) / 2.0)
    else: r = 720
    return W / 2, H / 2, r + 1
SC.iris = [(72.5, T_IN, eye_iris_close(72.5, T_IN)), (T_IN, T_OUT, scope), (T_OUT, T_OUT + 2.5, eye_iris_open(T_OUT, T_OUT + 2.5))]

# ---------------------------------------------------------------- the birds
FLOCK = Flock(n=12, seed=5, spread=(300, 110))
def flock_center(t, C):
    # they arrive from the right, circle above the boy, then climb with him
    hx, hy = C.to_screen(boy_x(t), gy(boy_x(t)) - 330 - rise(t))
    u = ss((t - 250) / 8)
    return hx + (1 - u) * 1500 * C.z * 0.5 + 60 * C.z * 0.5, hy - 120 * C.z * 0.5 - (1 - u) * 160 * C.z * 0.5
def front_fx(f, C, t, W_):
    if W_ is MORN and t >= 250:
        cx, cy = flock_center(t, C)
        anchors = []
        arrive = ss((t - 258) / 3)
        if arrive > 0:
            if 'handR' in BOY_LAST: anchors.append(tuple(BOY_LAST['handR']))
            if t > 260.5 and 'head' in SHEEP_LAST and 'tail' in SHEEP_LAST:
                hp, tp = np.array(SHEEP_LAST['head']), np.array(SHEEP_LAST['tail'])
                anchors.append(tuple((hp + tp) / 2 + [0, -40 * C.z * 0.5]))
        FLOCK.draw(f, t, cx, cy, C.z * 0.5, anchors=anchors, light=W_.light, flip=-1, arrive=arrive)
    if W_ is MORN and 270.2 < t < 272.5:   # a tear she pretends isn't there
        X, Y = C.to_screen(ROSE[0] - 14, ROSE[1] - 175 + 60 * (t - 270.2)); glow(f, X, Y, 4 * C.z * 0.5, '#e8f6ff', 0.8)
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
def lift_cam(t):
    u = ss((t - RISE0) / 18)
    return (1640 - 100 * u, gy(1640) - 110 - rise(t) * 0.72, 1.35 - 0.5 * u)
SC.shots = [
    (0, [(0, (1350, 660, 1.0)), (10, (1380, 690, 1.12))], 0.0),
    (10, [(10, (NEST[0], NEST[1] - 18, 4.0)), (22, (NEST[0], NEST[1] - 20, 4.3))], 3.0),
    (22, [(22, (1615, 760, 3.0)), (34, (1620, 756, 3.1))], 2.5),
    (34, [(34, (1720, 830, 2.6)), (46, (1725, 826, 2.7))], 1.5),
    (46, [(46, (1680, 780, 1.8)), (56, (1680, 776, 1.85))], 0.8),
    (56, [(56, (1450, 700, 1.15)), (68, (1060, 720, 1.25))], 0.3),
    (68, [(68, (TX + 60, 720, 2.4)), (T_IN, (TX + 75, 715, 2.7))], 1.0),
    (T_IN, [(T_IN, (1440, 650, 1.0)), (86, (1460, 655, 1.08))], 0.0),
    (86, [(86, (PX - 60, dgy(PX) - 80, 2.6)), (100, (PX - 60, dgy(PX) - 84, 2.8))], 1.0),
    (100, [(100, (PX - 50, dgy(PX) - 160, 4.6)), (106, (PX - 50, dgy(PX) - 160, 4.8))], 2.0),
    (106, [(106, (PX - 80, dgy(PX) - 70, 2.2)), (T_OUT, (PX - 80, dgy(PX) - 66, 2.05))], 0.5),
    (T_OUT, [(T_OUT, (TX + 75, 715, 2.7)), (122, (TX + 90, 720, 2.6))], 1.0),
    (122, [(122, (1100, 700, 1.15)), (130.5, (1560, 720, 1.25))], 0.3),
    (130.5, [(130.5, (NEST[0], NEST[1] - 18, 4.2)), (140, (NEST[0], NEST[1] - 20, 4.4))], 3.0),
    (140, [(140, (1615, 750, 3.0)), (158, (1619, 744, 3.2))], 2.5),
    (158, [(158, (1660, 760, 1.7)), (174, (1665, 758, 1.75))], 0.6),
    (174, [(174, (1500, 720, 1.1)), (186, (900, 720, 1.2))], 0.3),
    (186, [(186, (BOXX + 90, 840, 2.6)), (190, (BOXX + 100, 836, 2.7))], 1.5),
    (190, [(190, (900, 720, 1.2)), (203, (1600, 720, 1.25))], 0.3),
    (203, [(203, (1680, 780, 2.0)), (214, (1685, 778, 2.05))], 1.0),
    (214, [(214, (1690, 840, 2.8)), (222, (1680, 836, 2.9))], 1.5),
    (222, [(222, (BOX_DOWN, gy(BOX_DOWN) + 30, 3.4)), (236, (BOX_DOWN, gy(BOX_DOWN) + 26, 3.6))], 2.5),
    (236, [(236, (1660, 760, 1.9)), (250, (1665, 755, 1.95))], 0.8),
    (250, [(250, (1600, 560, 1.0)), (258, (1600, 580, 1.05))], 0.0),
    (258, [(258, (1660, 740, 1.6)), (264, (1665, 735, 1.65))], 0.6),
    (264, [(264, (ROSE[0], ROSE[1] - 120, 3.6)), (272, (ROSE[0], ROSE[1] - 120, 3.8))], 2.5),
    (272, [(272, (1640, 700, 1.35)), (RISE0, (1640, 690, 1.35))], 0.3),
    (RISE0, lift_cam, 0.2),
]
SC.subs = [
    (100.5, 104.0, '...Where did you go?', '……你去哪儿了？'),
    (147.0, 153.5, 'We have to take it home. Before its light goes out.', '我们得送它回家。在它的光熄灭之前。'),
    (265.6, 269.6, 'Go. And come back.', '去吧。要回来。'),
]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 60, 'sad', 0.8), (60, 118, 'night', 0.8), (118, 160, 'sad', 0.75), (160, 250, 'playful', 0.8), (250, 300, 'adventure', 0.9)]
SFX = [(0, 'birds', dict(n=4)), (0, 'wind', dict(dur=75, gain=0.6)), (T_IN, 'wind', dict(dur=42, gain=0.9)), (T_OUT, 'wind', dict(dur=183, gain=0.6))]
for k in range(int((66 - 56) * 1.9)): SFX.append((56.2 + k / 1.9, 'step', dict(pan=0.3)))
for k in range(int((128.5 - 120.5) * 1.9)): SFX.append((120.7 + k / 1.9, 'step', dict(pan=0.6)))
SFX += [(36.6, 'chime', dict(notes=[900], gain=0.4)), (72.8, 'whoosh', dict(dur=2.0, f=300, gain=0.6)), (T_OUT, 'whoosh', dict(dur=2.0, f=300, gain=0.6))]
for k in range(int((184 - 175.5) * 2.6)): SFX.append((175.6 + k / 2.6, 'hoof', dict(gain=0.4)))
for k in range(int((202 - 189.5) * 2.6)): SFX.append((189.6 + k / 2.6, 'hoof', dict(gain=0.4)))
SFX += [(188.0, 'pop', dict(gain=0.4)), (203.6, 'thump', dict(gain=0.7)), (205, 'giggle', dict(n=5)), (HOP0, 'tap', dict(gain=0.4)),
        (HOP0 + 0.9, 'chime', dict(notes=[1500, 1900, 2250])), (HOP0 + 1.2, 'sparkle', dict(gain=0.6)), (250, 'birds', dict(n=14)),
        (256, 'birds', dict(n=10)), (258.5, 'whoosh', dict(dur=1.5, f=700, gain=0.5)), (265.8, 'chime', dict(notes=[1400, 1760], gain=0.5)),
        (RISE0, 'whoosh', dict(dur=4, f=500)), (RISE0 + 1, 'birds', dict(n=16)), (RISE0 + 6, 'shimmer', dict(dur=8, gain=0.6))]
boy.cast = lambda t: dict(cast=0.0) if t > RISE0 + 0.3 else None
sheep.cast = lambda t: dict(cast=0.0) if t > RISE0 + 0.8 else None

# S02 · The star falls (300 s). Night. The friend's star hiccups and falls into the rose's garden; the sheep finds Pip,
# Pip hides behind the dome, the rose shelters it, the sheep curls around it. The boy wakes: a gap in the sky.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys, travel

class S02(Scene):
    DURATION = 300.0

SC = S02()
NIGHT = World('night')
gy = NIGHT.gy
SC.worlds = [(0, 1e9, NIGHT)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

# ---------------------------------------------------------------- the boy: asleep sitting on the hill, wakes at the end
BX = 1180
BOY = BoyAnim(segs([], BX), k=1.6, t_end=300, sit=[(0, 1)],
    sleep=[(0, 1), (262.0, 1), (263.6, 0)],
    poses={'armR': [(0, 0), (263.4, 0), (264.4, -95), (266.2, -92), (267.4, 0)], 'foreR': [(0, 0), (263.4, 0), (264.4, -40), (266.2, -40), (267.4, 0)],
           'head': [(0, 0), (262.5, 0), (263.5, 6), (264.5, -4), (266, 0)],
           'chest': [(0, 0), (263.4, 0), (264.4, -5), (266.2, -5), (267.4, 0)]},
    look_x=[(0, 0.2), (267, 0.2), (268.5, 0.9), (273, 0.9), (275, 0.7)],
    lookup=[(0, 0), (267, 0), (268.5, -0.3), (273, -0.3), (275, 0.9), (285, 0.85), (287, 0.3), (300, 0.25)],
    laugh=[(0, 0), (269.5, 0), (270.3, 0.35), (272.5, 0.3), (273.5, 0)],
    talk=[(287.5, 0), (287.6, 1), (292.0, 1), (292.1, 0)],
    brows=[(0, 0), (276.5, 0), (277.5, 1), (300, 1)],
    mouth=[(276.6, 278.0, 'open'), (263.6, 264.8, 'open')])
boy = BoyActor(BOY, lambda t: gy(BX) + 70)

# ---------------------------------------------------------------- the sheep: asleep, wakes, creeps, finds Pip, curls round it
PIPX = 1690                    # where the star lands
sheep_x = segs([(86, 111, 1560, 0.3, 0.5),          # creeping up to the light
                (136.2, 136.6, 1585, 0.1, 0.2),     # startled backwards hop
                (178, 193, 1555, 0.4, 0.6),         # tiptoes back toward the dome
                (196.5, 199, 1540, 0.4, 0.5)], 1060)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300,
    sleep=[(0, 1), (77.6, 1), (78.4, 0), (226, 0), (232, 1)],
    crouch=[(0, 60), (81.5, 60), (84.0, 0), (86, 7), (111, 7), (112, 2), (199, 2), (204, 60)],
    head=[(0, 0), (57.6, 0), (57.8, -6), (58.0, 4), (58.3, -3), (58.6, 0), (78.4, 0), (79.0, -10), (80.5, -6), (81.5, 0),
          (86, 10), (111, 10), (112, 0), (131.8, 0), (132.0, -18), (133.5, -10), (137, 0),
          (145, 0), (145.6, 14), (148, 12), (150, 0), (204, 0), (210, 0), (214, 14), (300, 16)],
    sniff=[(0, 0), (112, 0), (113, 0.9), (122, 0.8), (124, 0.3), (125, 0.9), (130.5, 0.9), (131.2, 0), (186, 0), (187, 0.6), (192, 0.6), (193, 0)],
    hop=[(132.0, 0.35, 14)],
    look=[(0, (0, 0)), (78.4, (0, 0)), (80.5, (0.6, 0)), (86, (0.8, 0.6)), (111, (0.6, 0.8)), (132, (0, -0.3)), (137, (-0.3, 0)),
          (150, (-0.6, 0.2)), (176, (-0.5, 0.1)), (205, (-0.3, 0.6)), (226, (-0.2, 0.8))],
    tail=[(0, 0), (79, 0)] + osc(79.5, 81.5, 0.3, -18, 18) + [(82, 0), (214, 0)] + osc(214.5, 218, 0.35, -22, 22) + [(218.5, 0)],
    mouth=[(132.0, 133.0, 'open')])
sheep_y = lambda t: gy(sheep_x(t)) + 112
sheep = SheepActor(SHEEP, sheep_y, facing=[(0, 1), (138.5, -1)])

# ---------------------------------------------------------------- the rose
ROSE = (1440, gy(1440) + 40)
rose = RoseActor(ROSE, dome=[(0, 1)],
                 lean=[(0, 0), (52.2, 0), (52.5, -10), (54.5, -4), (57, 0), (152, 0), (156, 7), (176, 7), (182, 3), (300, 3)],
                 talk=[(168.0, 0), (168.2, 1), (172.8, 1), (173.0, 0)])

# ---------------------------------------------------------------- Pip: the friend's star
FRIEND = (1960, 250)
LAND = (PIPX, gy(PIPX) + 46)                        # Pip's centre when sitting in the grass
HIDE = (1405, gy(1405) + 6)                          # behind the dome (far side from the sheep)
NEST = (1470, gy(1470) + 98)                         # in front of the sheep's chest, in the wool
T_FALL0, T_LAND = 47.6, 52.2

def hop_path(t, pts):
    """Pip hopping between points: pts = [(t0, dur, (x0,y0), (x1,y1), h)]; returns (x, y, squash, rot) or None."""
    for (t0, d, a, b, h) in pts:
        if t0 <= t < t0 + d:
            u = (t - t0) / d; e = u * u * (3 - 2 * u) * 0.3 + u * 0.7
            x = a[0] + (b[0] - a[0]) * e; y = a[1] + (b[1] - a[1]) * e - 4 * h * u * (1 - u)
            return x, y, -0.12 * math.sin(math.pi * u), 0.25 * math.sin(math.pi * u) * (1 if b[0] > a[0] else -1)
        if t0 + d <= t < t0 + d + 0.3:   # landing squash, settles
            b_ = t - t0 - d; return b[0], b[1], 0.22 * math.exp(-b_ * 14) * math.cos(b_ * 30), 0.0
    return None

HOPS = [(133.0, 0.5, LAND, (1615, gy(1615) + 26), 46), (133.7, 0.45, (1615, gy(1615) + 26), (1540, gy(1540) + 14), 36),
        (134.35, 0.5, (1540, gy(1540) + 14), HIDE, 30),
        (205.5, 0.55, HIDE, (1445, gy(1445) + 60), 30), (206.4, 0.5, (1445, gy(1445) + 60), NEST, 26)]

def pip_light(t):
    if t < T_LAND: return 1.0
    l = 0.48 - 0.16 * ss((t - T_LAND) / 20)                     # pale after the fall
    l += 0.30 * ss((t - 212) / 26) - 0.06 * ss((t - 262) / 30)   # warmed by the wool
    return l

def pip_state(t):
    if t < T_FALL0: return None
    if t < T_LAND:   # the fall: a long arc, accelerating, tumbling
        u = ((t - T_FALL0) / (T_LAND - T_FALL0)) ** 1.6
        x = FRIEND[0] + (LAND[0] - FRIEND[0]) * u + 160 * math.sin(math.pi * u) ; y = FRIEND[1] + (LAND[1] - FRIEND[1]) * u ** 1.2
        return dict(x=x, y=y, ground_y=LAND[1] + 30, rot=(t - T_FALL0) * 6.5, face='closed', light=1.0, size=24, squash=-0.15)
    st = dict(light=pip_light(t), size=26, face='closed', look=(0, 0), rot=0.0, squash=0.0)
    p = hop_path(t, HOPS)
    if p is not None: x, y, sq, rot = p
    elif t < 133.0: x, y = LAND
    elif t < 205.5: x, y = HIDE
    else: x, y = NEST
    if p is None:
        sq, rot = 0.0, 0.0
        if t < 133.0:   # just landed: a few bounces, then trembling in the grass
            b = t - T_LAND
            if b < 1.2: y -= 34 * abs(math.sin(b * math.pi / 0.6)) * math.exp(-b * 2.5); sq = 0.2 * math.exp(-b * 4) * math.cos(b * 10.5)
            rot = 0.045 * math.sin(t * 31) * (1 - ss((t - 128) / 4)) if b > 1.2 else 0.0
        elif t < 205.5:   # hiding: peeks out to the left and right of the dome's glass
            peek = float(keys([(0, 0), (140, 0), (141, 1), (144, 1), (144.6, 0), (152, 0), (153, 1), (160, 1), (161, 0.4), (182, 0.4), (183, 1), (204, 1)], t))
            x += 34 * peek; rot = 0.12 * peek; sq = 0.03 * math.sin(t * 20) * (1 - peek)
        else:
            sq = 0.025 * math.sin(t * 2 * math.pi / 3.6)    # breathing with the sheep
    st.update(x=x, y=y, ground_y=y + 30, squash=sq, rot=rot)
    if t >= 131.0 and t < 238: st['face'] = 'open'
    if 131.0 <= t < 205.5: st['look'] = (-0.8, 0.2) if t < 140 else (0.7, 0.3)
    if 208 <= t < 238: st['look'] = (0.4, -0.6)
    if 214 < t < 238: st['laugh'] = 0.0
    return st
pip = PipActor(pip_state)
SC.actors = [boy, sheep, rose, pip]

# ---------------------------------------------------------------- the sky: the friend's star, its flickers, the gap it leaves
def friend_amt(t):
    if t >= T_FALL0: return 0.0
    a = 0.95
    for (t0, d) in ((26.0, 0.25), (29.0, 0.18), (29.5, 0.2), (32.5, 0.3), (33.3, 0.15), (34.0, 0.4), (42.0, 0.3), (43.0, 0.25), (44.2, 0.5)):
        if t0 <= t < t0 + d: a *= 0.15 + 0.85 * abs(math.cos(math.pi * (t - t0) / d * 1.5))
    return a
def friend_pos(t):
    x, y = FRIEND
    if 41.0 <= t < T_FALL0:   # wobbles, then slips
        w = ss((t - 41) / 5); x += 7 * w * math.sin(t * 17); y += 4 * w * math.sin(t * 23)
        if t > 46.6: y += 30 * ((t - 46.6) / 1.0) ** 2
    return x, y
def sky_fx(f, C, t, W_):
    a = friend_amt(t)
    if a > 0.01:
        X, Y = C.to_screen(*friend_pos(t)); glow(f, X, Y, 5 * C.z, '#fff1c4', a)
        for ang in (0, math.pi / 2):
            L_ = (13 + 16 * a) * C.z
            cv2.line(f, (int((X - math.cos(ang) * L_) * 16), int((Y - math.sin(ang) * L_) * 16)), (int((X + math.cos(ang) * L_) * 16), int((Y + math.sin(ang) * L_) * 16)),
                     (a, 0.96 * a, 0.85 * a), max(1, int(1.2 * C.z)), cv2.LINE_AA, shift=4)
    if t >= T_FALL0:   # the gap: a little hollow of darkness where the star was
        X, Y = C.to_screen(*FRIEND); r = 70 * C.z
        x0, x1, y0, y1 = int(max(0, X - 2 * r)), int(min(W, X + 2 * r)), int(max(0, Y - 2 * r)), int(min(H, Y + 2 * r))
        if x1 > x0 and y1 > y0:
            yy, xx = np.mgrid[y0:y1, x0:x1]; m = np.exp(-((xx - X) ** 2 + (yy - Y) ** 2) / (r * r)) * 0.55 * ss((t - T_FALL0) / 6)
            f[y0:y1, x0:x1] *= (1 - m[..., None])
        e = max(0, 1 - (t - T_FALL0) / 5)   # an ember fading where it hung
        if e > 0: glow(f, X, Y, 2.5 * C.z, '#ffe2a0', 0.4 * e)
SC.sky_fx = sky_fx

def front_fx(f, C, t, W_):
    if T_FALL0 <= t < T_LAND + 0.6:   # the streak
        for k in range(34):
            tt = min(t, T_LAND) - k * 0.03
            if tt < T_FALL0: break
            q = pip_state(tt); X, Y = C.to_screen(q['x'], q['y']); u = k / 34
            glow(f, X, Y, 15 * C.z * 0.5 * (1 - u * 0.7), '#ffe6a0', 0.7 * (1 - u) * (1 if t < T_LAND else max(0, 1 - (t - T_LAND) / 0.6)))
    if T_LAND <= t < T_LAND + 3.0:   # the soft landing: a puff of light and sparks
        b = t - T_LAND; X, Y = C.to_screen(*LAND)
        glow(f, X, Y, (40 + 160 * b) * C.z * 0.5, '#ffe2a0', 0.8 * math.exp(-b * 2.2))
        r = np.random.default_rng(7)
        for k in range(18):
            a = r.random() * math.pi - math.pi; sp = (60 + r.random() * 120) * C.z * 0.5
            glow(f, X + math.cos(a) * sp * b, Y + math.sin(a) * sp * b + 60 * b * b * C.z * 0.5, 2.4 * C.z * 0.5, '#fff2b0', 0.9 * max(0, 1 - b / 2.2))
    if 52.3 <= t < 54.5:   # the glass dome rings: a shimmer runs round it
        b = t - 52.3; X, Y = C.to_screen(ROSE[0], ROSE[1] - 120)
        glow(f, X, Y, 90 * C.z * 0.5, '#dfe8ff', 0.35 * math.exp(-b * 2) * (0.6 + 0.4 * math.sin(b * 40)))
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
def follow_sheep(dx, dy, z):
    return lambda t: (sheep_x(t) + dx, gy(sheep_x(t)) + dy, z)
SC.shots = [
    (0,     [(0, (1300, 600, 0.95)), (14, (1290, 640, 1.04))], 0.0),
    (14,    [(14, (1120, 810, 1.8)), (24, (1130, 805, 1.9))], 0.8),
    (24,    [(24, (1800, 380, 1.3)), (36, (1850, 360, 1.42))], 0.0),
    (36,    [(36, (1185, 720, 3.0)), (41, (1188, 716, 3.1))], 2.5),
    (41,    [(41, (1960, 285, 2.4)), (47.4, (1960, 280, 2.6))], 0.0),
    (47.4,  [(47.4, (1800, 470, 1.0)), (52.2, (1720, 600, 1.1)), (56, (1700, 640, 1.15))], 0.0),
    (56,    [(56, (1580, 790, 2.4)), (62, (1590, 788, 2.5))], 1.5),
    (62,    [(62, (PIPX, LAND[1] + 10, 4.0)), (72, (PIPX, LAND[1] + 8, 4.3))], 3.0),
    (72,    [(72, (1060, 840, 2.6)), (82, (1066, 836, 2.7))], 1.5),
    (82,    follow_sheep(120, 50, 1.6), 0.6),
    (112,   [(112, (1640, 800, 3.0)), (131, (1645, 798, 3.2))], 2.0),
    (131,   [(131, (PIPX, LAND[1] + 6, 4.4)), (133, (PIPX, LAND[1] + 6, 4.5))], 3.0),
    (133,   [(133, (1570, 780, 1.9)), (150, (1560, 778, 1.95))], 0.8),
    (150,   [(150, (1470, 740, 3.2)), (160, (1474, 738, 3.3))], 2.5),
    (160,   [(160, (1500, 770, 2.2)), (180, (1505, 768, 2.3))], 1.0),
    (180,   [(180, (1530, 790, 2.0)), (200, (1515, 790, 2.05))], 0.8),
    (200,   [(200, (1500, 810, 2.4)), (215, (1495, 808, 2.5))], 1.2),
    (215,   [(215, (NEST[0], NEST[1] - 10, 3.6)), (232, (NEST[0], NEST[1] - 12, 3.8))], 2.5),
    (232,   [(232, (1350, 700, 1.3)), (260, (1380, 690, 1.36))], 0.3),
    (260,   [(260, (1250, 780, 2.2)), (274, (1255, 776, 2.25))], 1.0),
    (274,   [(274, (1960, 300, 1.6)), (284, (1960, 290, 1.8))], 0.0),
    (284,   [(284, (1185, 720, 3.0)), (300, (1188, 712, 3.15))], 2.5),
]
SC.subs = [
    (168.0, 173.0, "Well? Don't just stand there. It's cold.", '愣着干嘛？它冷着呢。'),
    (287.5, 292.5, "Oh no. That's his star.", '糟了。那是他的星星。'),
]
SC.fade_in, SC.fade_out = 2.0, 2.5
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 40, 'night', 0.8), (40, 56, 'tense', 0.8), (56, 130, 'wonder', 0.7), (130, 200, 'playful', 0.6), (200, 262, 'warm', 0.8), (262, 300, 'sad', 0.9)]
SFX = [(0, 'crickets', dict(dur=300, gain=0.9)), (0, 'wind', dict(dur=300, gain=0.4))]
for t0 in (26.0, 29.0, 29.5, 32.5, 34.0, 42.0, 44.2): SFX.append((t0, 'twinkle', dict(m=92, gain=0.5)))
SFX += [(46.8, 'whoosh', dict(dur=5.2, f=900)), (T_LAND, 'pop', dict(gain=0.6)), (T_LAND + 0.1, 'chime', dict(notes=[2100, 2640, 3150])),
        (52.3, 'shimmer', dict(dur=2.5, gain=0.5)), (78.5, 'baa', dict(f=330, dur=0.35, gain=0.4))]
for k in range(int((111 - 86) * 1.2)): SFX.append((86 + k / 1.2, 'hoof', dict(gain=0.25)))
SFX += [(131.2, 'chime', dict(notes=[1900, 2400])), (132.0, 'baa', dict(f=420, dur=0.3)), (133.0, 'tap', dict(gain=0.4)), (133.7, 'tap', dict(gain=0.35)),
        (134.4, 'tap', dict(gain=0.3)), (141, 'twinkle', dict(m=100, gain=0.3)), (153, 'twinkle', dict(m=103, gain=0.3)),
        (205.5, 'tap', dict(gain=0.3)), (206.4, 'tap', dict(gain=0.3)), (212, 'sparkle', dict(gain=0.4)), (228, 'giggle', dict(n=3, shift=14, gain=0.4))]

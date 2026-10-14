# S07 · Moth takes Pip (300 s). A calm night flight; the boy dozes, the sheep keeps watch with the lantern.
# A huge soft shadow passes. The birds panic. Moth swoops down and takes the lantern; the sheep holds on and is shaken off.
# The birds scatter. The boy and the sheep drift down onto a small rock. The light fades towards a dark planet. The sheep decides.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import RotActor, StarStream, sheep_harness, BOY_LAST, SHEEP_LAST
from props3 import Flock, box, space_rock
from sheep import draw_sheep
from moth import draw_moth

class S07(Scene):
    DURATION = 300.0

SC = S07()
SPACE = World('dark', place='space')
SC.worlds = [(0, 1e9, SPACE)]

def rot_about(p, piv, ang):
    a = math.radians(ang); c, s_ = math.cos(a), math.sin(a); d = np.array(p) - piv
    return tuple(piv + [d[0] * c - d[1] * s_, d[0] * s_ + d[1] * c])
def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

BX, BY = 1360, 790          # the boy's feet (hanging)
SX, SY = 1560, 860          # the sheep's feet line
T_PASS1, T_PASS2, T_COME, T_GRAB, T_SNAP, T_REL = 62.0, 92.0, 120.0, 138.0, 146.0, 152.0
LANDB, LANDS = 211.0, 212.0
ROCK_X, ROCK_TOP = 1460, 880
def bob(t, ph=0.0): return (14 * math.sin(t * 0.7 + ph) + 5 * math.sin(t * 1.9 + ph * 2)) * (1 - ss((t - 192) / 14))
def sink(t, d=0.0): return 90 * ss((t - 170 - d) / (41 - d))
def rock_y(t): return ROCK_TOP + 900 * (1 - ss((t - 176) / 36))
def pull(t): return (70 * ss((t - T_GRAB - 1) / 2.5) + 14 * math.sin(t * 5.3)) * (1 - ss((t - T_REL) / 0.7)) * ss((t - T_GRAB) / 0.5)
def shake(t):
    e = ss((t - T_GRAB - 0.5) / 1.2) * (1 - ss((t - T_REL) / 0.5))
    tumble = -38 * math.exp(-max(0, t - T_REL) * 0.9) * math.cos((t - T_REL) * 3.2) if t > T_REL else 0.0
    return e * (16 * math.sin(t * 7.3) + 7 * math.sin(t * 12.7)) + tumble
def lantern(t): return 0.55 + 0.06 * math.sin(t * 1.7) + 0.15 * ss((t - T_COME) / 6) * abs(math.sin(t * 6))

# ---------------------------------------------------------------- the boy
boy_x = segs([(278, 284, BX + 110, 0.5, 0.5)], BX)
BOY = BoyAnim(boy_x, k=1.6, t_end=300, hang=[(0, 1), (LANDB - 1.5, 1), (LANDB, 0)], wind=[(0, 0.6), (T_SNAP, 0.6), (160, 0.25), (LANDB, 0)],
    sleep=[(0, 1), (72.5, 1), (73.6, 0)], sit=[(0, 0), (216, 0), (218.5, 1), (265, 1), (267.5, 0)],
    crouch=[(0, 0), (LANDB, 0), (LANDB + 0.2, 18), (LANDB + 0.9, 0)],
    poses={'armR': [(0, -128), (T_SNAP, -128), (T_SNAP + 0.8, -75), (165, -70), (205, -45), (LANDB, -20), (LANDB + 1, 0)],
           'foreR': [(0, -6), (T_SNAP, -6), (T_SNAP + 0.8, -10), (LANDB, 0)],
           'armL': [(0, 0), (139, 0), (140, 75), (T_SNAP, 75), (T_SNAP + 0.8, 70), (165, 70), (205, 45), (LANDB, 20), (LANDB + 1, 0)],
           'foreL': [(0, 0), (139, 0), (140, 10), (T_SNAP + 0.8, 10), (LANDB, 0)],
           'head': [(0, 0), (73.6, 0), (74.4, -10), (76, 8), (78, 0), (220, 0), (222, 12), (238, 12), (241, 0), (285, 0), (285.5, 9), (286, 0), (286.5, 9), (287, 0)]},
    look_x=[(0, 0.2), (73.6, 0.2), (74.4, -0.7), (76, 0.8), (79, 0.3), (T_COME, 0.6), (T_GRAB, 0.9), (T_REL, 0.9), (160, 1.0), (176, 0.6), (220, 0.2),
            (241, 0.8), (250, 1.0), (262, 0.9), (275, 1.0)],
    lookup=[(0, -0.2), (73.6, -0.1), (80, 0.2), (T_COME, 0.8), (130, 0.6), (T_GRAB, 0.3), (T_REL, 0.8), (165, 0.9), (190, 0.5), (220, -0.4), (238, -0.4),
            (241, 0.0), (250, 0.4), (275, 0.5)],
    brows=[(0, 0.2), (73.6, 0.6), (75, 1.0), (85, 0.6), (T_COME, 1.0), (175, 1.0), (215, 0.8), (240, 0.9), (262, 0.4), (275, 0.0)],
    mouth=[(121.0, 123.2, 'open'), (141, 145, 'open'), (165, 205, 'sad'), (215, 240, 'sad')],
    talk=[(153.0, 0), (153.1, 1), (155.6, 1), (155.7, 0)])
boy = BoyActor(BOY, lambda t: BY + bob(t) + sink(t), facing=[(0, 1)])
boy.shadow = lambda t: t > LANDB - 0.5
boy.cast = dict(cast=0.0)
boyR = RotActor(boy, lambda t: 3 * math.sin(t * 0.7 + 1.2) * (1 - ss((t - 195) / 12)), piv_h=380)

# ---------------------------------------------------------------- the sheep with the lantern in its mouth
sheep_x = segs([(272, 280, SX + 130, 0.5, 0.6)], SX)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=300, lift=[(0, 24), (LANDS - 0.8, 24), (LANDS + 0.3, 0)],
    paddle=[(0, 0), (T_GRAB + 0.5, 0), (T_GRAB + 1, 1), (T_REL + 4, 1), (T_REL + 5, 0)],
    crouch=[(0, 0), (216, 0), (219, 48), (255, 48), (258, 0)],
    head=[(0, 0), (20, 0), (22, 8), (34, 8), (36, -6), (50, -6), (52, 0), (64, 0), (64.4, -14), (70, -14), (72, 0), (104, 0), (106, 10), (118, 10), (121, -12)]
         + [(T_GRAB, -12)] + osc(T_GRAB + 0.3, T_REL, 0.36, -18, 18) + [(T_REL + 0.3, -16), (175, -10), (216, 0), (219, 14), (244, 14), (246, -6),
         (262, -6), (262.4, 10), (262.8, -6), (263.2, 10), (263.6, 0), (282, 0), (283, -8)],
    look=[(0, (0.3, -0.3)), (14, (-0.6, -0.4)), (22, (0.7, -0.2)), (36, (0.2, -0.8)), (52, (-0.4, -0.3)), (64.4, (0.0, -1.0)), (72, (-0.7, -0.6)),
          (82, (0.6, -0.8)), (104, (0.2, 0.2)), (T_COME, (-0.3, -1.0)), (T_GRAB, (0.0, -1.0)), (T_REL + 0.5, (0.6, -1.0)), (176, (0.8, -0.8)),
          (216, (-0.3, 0.3)), (244, (-0.2, 0.2)), (246, (0.8, -0.5)), (300, (0.9, -0.5))],
    tail=[(0, 0)] + osc(T_GRAB + 0.5, T_REL + 3, 0.3, -26, 26) + [(T_REL + 3.3, 0)],
    mouth=[(T_REL - 0.2, T_REL + 1.8, 'open'), (262.2, 263.0, 'open')], sleep=[(0, 0)])
def sheep_y(t): return SY + bob(t, 1.3) + sink(t, 1.0) * (ROCK_TOP - SY) / 90 - pull(t)
WATCH = {}
class SheepBox(Actor):
    height = 260; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0)
    def foot(self, t): return (sheep_x(t), sheep_y(t))
    def draw(self, f, X, Y, s, t, W_, C):
        draw_sheep(f, X, Y, s, 1, t=t, A=SHEEP.at(t), light=W_.light, rim=W_.rim, rim_w=0.6, shadow=t > LANDS - 0.3)
        if t < T_REL:
            m = SHEEP_LAST.get('mouth')
            if m is None: return
            sb = 0.85 * s; bx, by = m[0] - 5 * sb, m[1] + 168 * sb + 6 * s
            if t > T_GRAB: by -= 18 * sb * ss((t - T_GRAB) / 1.0)
            top = box(f, bx, by, sb, light=W_.light, rim=W_.rim, glow_amt=lantern(t), t=t, handle=True, tilt=5 * math.sin(t * 5) * (1 - ss((t - T_COME) / 4)), grey=0.25)
            WATCH['handle'] = (t, top, s); WATCH['box'] = (bx, by - 60 * sb)
sheepbox = SheepBox()
PIV_H = 120
sheepR = RotActor(sheepbox, shake, piv_h=PIV_H)

# ---------------------------------------------------------------- the rock they land on
def rock_fn(f, X, Y, s, t, W_, C):
    space_rock(f, X, Y, s * 1.3, light=W_.light, rim=W_.rim, seed=4)
rock = Prop(rock_fn, lambda t: (ROCK_X, rock_y(t) - 40), height=200, tuft_w=0, active=lambda t: t > 176)
rock.shadow = False; rock.cast = dict(cast=0.0)

# ---------------------------------------------------------------- Moth
HOV = (1760, 470)            # where he hovers, staring at the light
FAR = (2330, 240)            # where he vanishes
HOLD = (0, 150)              # his hands, in his own units, below his chest
MS = 1.25                    # his size
HANDLE_OFF = (93, -105)      # the lantern's handle, from the sheep's feet (measured)
def handle_world(t):
    sx, sy = sheep_x(t), sheep_y(t)
    return rot_about((sx + HANDLE_OFF[0], sy + HANDLE_OFF[1]), np.array([sx, sy - PIV_H * 0.625]), shake(t))
def moth_free(t):
    if t < 128:
        u = ss((t - T_COME) / 8); x = 820 + (HOV[0] - 820) * u; y = 120 + (HOV[1] - 120) * u - 60 * math.sin(math.pi * u)
    else: x, y = HOV
    return x + 12 * math.sin(t * 1.1), y + 16 * math.sin(t * 1.6)
class MothActor(Actor):
    height = 600; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0); self.rel = None
    def foot(self, t):
        if not (T_COME - 1 < t < 178): return None
        if t < T_REL + 0.5: return (HOV[0], sheep_y(t) - 40)   # just behind the sheep while he reaches for the lantern
        return (FAR[0], 0)
    def draw(self, f, X, Y, s, t, W_, C):
        z = C.z; sm = 0.5 * z * MS
        hold = (float(keys([(0, 60), (128, 60), (134, -30), (T_GRAB, 0)], t)), float(keys([(0, 130), (128, 130), (134, 170), (T_GRAB, HOLD[1])], t)))
        fx, fy = C.to_screen(*moth_free(t))
        if 133 < t < T_REL:
            hw = handle_world(t); wx, wy = hw[0] - hold[0] * 0.625 * MS, hw[1] - hold[1] * 0.625 * MS - 6 * math.sin(t * 4.2)
            gx, gy_ = C.to_screen(wx, wy); u = ss((t - 133) / 5)
            cx, cy = fx + (gx - fx) * u, fy + (gy_ - fy) * u
        elif t >= T_REL:
            hw = handle_world(T_REL); rx, ry = hw[0] - HOLD[0] * 0.625 * MS, hw[1] - HOLD[1] * 0.625 * MS; u = ss((t - T_REL) / 24)
            wx = rx + (FAR[0] - rx) * u - 120 * math.sin(math.pi * u); wy = ry + (FAR[1] - ry) * u
            cx, cy = C.to_screen(wx, wy); sm *= 1 - 0.8 * ss((t - T_REL - 2) / 22)
        else:
            cx, cy = fx, fy
        dim = float(keys([(0, 0.85), (124, 0.85), (132, 0.25), (T_REL, 0.3), (166, 0.8)], t))
        flap = float(keys([(0, 1), (128, 0.6), (T_GRAB, 0.7), (T_GRAB + 1, 1)], t))
        fs = float(keys([(0, 1.0), (128, 0.8), (T_GRAB, 1.0), (T_GRAB + 1, 2.2), (T_REL, 2.2), (T_REL + 3, 1.3)], t))
        out = {}
        draw_moth(f, cx, cy, sm, t, flip=1, open_=1.0, flap=flap, flap_speed=fs, mood=0.0, surprise=float(keys([(0, 0), (128, 0), (129, 0.7), (133, 0.2), (T_REL, 0)], t)),
                  look=(-0.4, 0.9), hold=hold, glow_amt=float(keys([(0, 0.2), (128, 0.6), (T_REL, 0.9)], t)), light=(0.2, 0.9), rim='#ffd890',
                  rim_w=0.4, dim=dim, out=out, tilt=0.12 * math.sin(t * 2.3) * (1 - ss((t - 128) / 3)))
        if t >= T_REL:   # the lantern in his arms
            sb = 0.85 * 0.5 * z * MS / 1.25 * (sm / (0.5 * z * MS)); hx, hy = out['hand']
            box(f, hx - 5 * sb, hy + 168 * sb, sb, light=(0.2, -0.9), rim='#ffd890', glow_amt=lantern(t) + 0.2, t=t, handle=True, grey=0.25)
            WATCH['moth_box'] = (hx, hy + 100 * sb, sb)
moth = MothActor()
SC.actors = [rock, boyR, sheepR, moth]

# ---------------------------------------------------------------- sky: streaming stars, Moth far away, the lantern dot, the dark planet
STREAM = StarStream(n=170, seed=12); FLOCK = Flock(n=12, seed=5, spread=(300, 110))
PLANET = (2480, 330)
def stream_speed(t): return 0.8 - 0.62 * ss((t - T_SNAP) / 22)
def sky_fx(f, C, t, W_):
    STREAM.draw(f, t, speed=stream_speed(t), amt=0.8)
    z = C.z
    a = ss((t - 222) / 16)
    if a > 0.01:   # the dark planet, a faint violet glow on its rim
        X, Y = C.to_screen(*PLANET); r = 150 * C.k
        glow(f, X, Y, r * 1.7, '#7a58c0', 0.5 * a)
        yy, xx = np.ogrid[0:H, 0:W]
        d = np.sqrt((xx - X) ** 2 + (yy - Y) ** 2)
        m = np.clip((r - d) / 2.5, 0, 1)[..., None] * a
        lit = np.clip(((xx - X) * -0.5 + (yy - Y) * -0.4) / r * 0.9 + 0.35, 0, 1)[..., None] ** 1.3
        col = hexc('#1a1228') * (1 - lit) + hexc('#5e4888') * lit
        col = col * (1 + 0.12 * np.sin(xx * 0.05 + yy * 0.03)[..., None] * np.sin(yy * 0.07 - xx * 0.02)[..., None])
        f[:] = f * (1 - m) + col * m
        rim = np.clip(1 - np.abs(d - r) / (3 + 0.02 * r), 0, 1)[..., None] * a * 0.6
        f[:] = f + hexc('#a888ff') * rim
    if T_PASS2 < t < T_PASS2 + 7:   # far behind them, something huge crosses the stars
        u = (t - T_PASS2) / 7
        wx, wy = 2500 - 1900 * u, 260 + 60 * math.sin(u * 3.14)
        X, Y = C.to_screen(wx, wy)
        draw_moth(f, X, Y, 0.16 * z, t, flip=-1, open_=1, flap=1, flap_speed=0.9, dim=0.95, light=(-0.6, -0.5), rim='#a8b8ff', rim_w=0.3)
    if t > 170:   # the lantern light, going away, fading into the dark
        u = ss((t - 170) / 60)
        wx, wy = FAR[0] + (PLANET[0] - FAR[0]) * u, FAR[1] + (PLANET[1] - 40 - FAR[1]) * u
        X, Y = C.to_screen(wx, wy); a2 = (1 - ss((t - 214) / 22)) * ss((t - 170) / 4)
        if a2 > 0.01:
            glow(f, X, Y, 26 * z * (1 - 0.6 * u), '#ffd060', 0.6 * a2); glow(f, X, Y, 6 * z, '#fff2c0', 0.9 * a2)
SC.sky_fx = sky_fx

DUST = np.random.default_rng(31).random((90, 4))
def wing_dust(f, t, t0, x0, z, amt=1.0):
    """Silver-violet scales falling from his wings after he passes."""
    age = t - t0
    if age < 0 or age > 16: return
    for k in range(len(DUST)):
        u, v, sp, ph = DUST[k]
        x = x0 + (u - 0.5) * 1900 + 30 * math.sin(t * (0.8 + sp) + ph * 6); y = -40 + v * 300 + age * (30 + 40 * sp) * z
        a = amt * (1 - age / 16) * (0.5 + 0.5 * math.sin(t * (3 + sp * 4) + ph * 6))
        if 0 < x < W and 0 < y < H: glow(f, x, y, (2.0 + 2.5 * sp) * z, '#cfc4ff', 0.7 * a)

def front_fx(f, C, t, W_):
    z = C.z * 0.5
    # the birds: calm, then panicking, then the strings snap and they scatter
    away = ss((t - T_SNAP) / 5)
    if away < 0.999:
        hx, hy = C.to_screen(BX, BY + bob(t) - 330)
        panic = float(keys([(0, 0), (T_PASS1 + 0.5, 0), (T_PASS1 + 1.5, 1), (80, 0.5), (110, 0.3), (T_COME, 1)], t))
        cx, cy = hx + 80 * z - away * 900 * z, hy - 300 * z - away * 900 * z
        anchors = []
        if t < T_SNAP:
            if 'handR' in BOY_LAST: anchors.append(tuple(BOY_LAST['handR']))
            h = sheep_harness(z)
            if h is not None:
                X, Y = C.to_screen(sheep_x(t), sheep_y(t)); piv = np.array([X, Y - PIV_H * z])
                anchors.append(rot_about(h, piv, shake(t)))
        FLOCK.draw(f, t, cx, cy, z, anchors=anchors, light=W_.light, flip=-1, spread=1 + 2.5 * away, panic=panic)
    # the first pass: a huge soft shape brushes past, right in front of the camera
    if T_PASS1 < t < T_PASS1 + 3.2:
        u = (t - T_PASS1) / 3.2
        draw_moth(f, -900 + 3800 * u, 330 - 140 * u, 3.0, t, flip=1, open_=1, flap=1, flap_speed=0.8, dim=1.0, blur=14, light=(-0.6, -0.5), rim='#a8b8ff', rim_w=0.2)
    wing_dust(f, t, T_PASS1 + 0.8, W / 2, 1.0)
    wing_dust(f, t, T_COME + 4, W / 2 + 200, 0.8, 0.6)
    # gold light spilling from the lantern in his arms
    if T_REL < t < 178 and 'moth_box' in WATCH:
        X, Y, sb = WATCH['moth_box']; glow(f, X, Y, 90 * sb, '#ffd060', 0.25)
SC.front_fx = front_fx

# ---------------------------------------------------------------- shots
SC.shots = [
    (0,   [(0, (1440, 600, 0.72)), (14, (1450, 620, 0.8))], 0.0),
    (14,  [(14, (BX + 10, BY - 165, 3.0)), (28, (BX + 10, BY - 166, 3.15))], 0.0),
    (28,  [(28, (SX + 60, SY - 150, 3.0)), (40, (SX + 62, SY - 152, 3.15))], 0.0),
    (40,  [(40, (1460, 700, 1.4)), (T_PASS1 + 4, (1465, 695, 1.5))], 0.0),
    (T_PASS1 + 4, [(T_PASS1 + 4, (SX + 50, SY - 160, 2.8)), (73, (SX + 50, SY - 162, 2.9))], 0.0),
    (73,  [(73, (BX + 10, BY - 165, 3.0)), (80, (BX + 10, BY - 165, 3.1))], 0.0),
    (80,  [(80, (1440, 640, 0.95)), (T_PASS2, (1440, 630, 1.0))], 0.0),
    (T_PASS2, [(T_PASS2, (1500, 560, 0.8)), (100, (1500, 560, 0.82))], 0.0),
    (100, [(100, (SX + 40, SY - 140, 2.0)), (T_COME, (SX + 40, SY - 140, 2.6))], 0.0),
    (T_COME, [(T_COME, (1480, 560, 0.85)), (128, (1560, 600, 1.0))], 0.0),
    (128, [(128, (BX + 10, BY - 160, 2.8)), (131, (BX + 10, BY - 160, 2.9))], 0.0),
    (131, [(131, (1620, 560, 1.3)), (T_GRAB + 1, (1620, 540, 1.45))], 0.0),
    (T_GRAB + 1, [(T_GRAB + 1, (1560, 560, 1.1)), (T_REL, (1560, 540, 1.15))], 0.0),
    (T_REL, [(T_REL, (BX + 30, BY - 170, 2.4)), (156, (BX + 30, BY - 170, 2.5))], 0.0),
    (156, [(156, (1700, 520, 0.9)), (176, (1800, 440, 0.8))], 0.0),
    (176, [(176, (BX + 60, BY - 140, 2.2)), (192, (BX + 60, BY - 130, 2.3))], 0.0),
    (192, [(192, (1460, 660, 0.85)), (LANDB + 3, (1460, 720, 0.95))], 0.0),
    (LANDB + 3, [(LANDB + 3, (1460, 780, 1.5)), (240, (1460, 790, 1.6))], 0.0),
    (240, [(240, (SX - 20, ROCK_TOP - 120, 2.6)), (248, (SX - 10, ROCK_TOP - 120, 2.7))], 0.0),
    (248, [(248, (1750, 660, 0.85)), (258, (1820, 620, 0.9))], 0.0),
    (258, [(258, (SX + 20, ROCK_TOP - 130, 2.6)), (266, (SX + 20, ROCK_TOP - 130, 2.7))], 0.0),
    (266, [(266, (1500, 780, 1.4)), (286, (1560, 770, 1.5))], 0.0),
    (286, [(286, (1600, 720, 1.1)), (300, (1900, 560, 0.7))], 0.0),
]
SC.subs = [(153.0, 155.8, 'No! Come back!', '不！回来！')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, 60, 'night', 0.7), (60, 120, 'tense', 0.7), (120, 176, 'tense', 0.95), (176, 240, 'sad', 0.8), (240, 300, 'adventure', 0.75)]
SFX = [(0, 'wind', dict(dur=176, gain=0.9)), (176, 'wind', dict(dur=124, gain=0.4))]
for k in range(0, 146, 9): SFX.append((k + 2.0, 'whoosh', dict(dur=1.6, f=420, gain=0.22)))
SFX += [(T_PASS1, 'whoosh', dict(dur=3.2, f=140, gain=1.0)), (T_PASS1 + 1.0, 'birds', dict(n=16)), (73.6, 'baa', dict(f=330, dur=0.4, gain=0.5)),
        (T_PASS2, 'whoosh', dict(dur=6, f=110, gain=0.4))]
for k in range(16): SFX.append((T_COME + k * 0.9, 'whoosh', dict(dur=0.8, f=160, gain=0.45)))
for k in range(14): SFX.append((T_GRAB + k * 0.45, 'whoosh', dict(dur=0.4, f=200, gain=0.5)))
SFX += [(T_GRAB, 'baa', dict(f=300, dur=0.9)), (T_SNAP, 'pop', dict(gain=0.5)), (T_SNAP + 0.2, 'birds', dict(n=24)), (T_REL - 0.1, 'baa', dict(f=380, dur=1.0)),
        (LANDB, 'thump', dict(gain=0.5)), (LANDS, 'thump', dict(gain=0.4)), (262.3, 'baa', dict(f=420, dur=0.5))]

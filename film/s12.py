# S12 · Home (250 s). Moth flies them home in the dawn; B612 appears. The rose, pretending she wasn't waiting: "You're late."
# Moth hangs the empty lantern by the rose and curls up by the warm volcano. Evening: the boy, the sheep and Moth in the grass.
# Pip winks from the sky. "Every time you laugh, a star gets brighter." The sheep falls asleep, smiling. The End.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import StarStream, BOY_LAST, SHEEP_LAST
from props3 import box
from pip import draw_pip
from moth import draw_moth

class S12(Scene):
    DURATION = 250.0

SC = S12()
SPACE = World('dawn', place='space'); MORN = World('morning'); DUSK = World('dusk'); NIGHT = World('night')
gy = MORN.gy
SC.worlds = [(0, 24, SPACE), (24, 29, (SPACE, MORN)), (29, 176, MORN), (176, 186, (MORN, DUSK)), (186, 204, DUSK), (204, 212, (DUSK, NIGHT)), (212, 1e9, NIGHT)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

LAND, T_LATE, T_HANG, T_CURL, T_LIE, T_WINK, T_SAY, T_SLEEP = 48.0, 76.0, 136.0, 160.0, 196.0, 214.0, 219.0, 232.0
ROSE = (1440, gy(1440) + 40); POST = 1650; VOLC = 700
BX0, SX0, MX0 = 1045, 1220, 1150
def gpos(t):
    """The flying group (Moth's middle) before they land."""
    if t < 26:
        u = ss(t / 26); return 2500 - 1300 * u, 520 + 40 * math.sin(t * 1.1)
    u = ss((t - 26) / (LAND - 26)); gl = gy(BX0) + 70 - 245
    return 1500 + (MX0 - 1500) * u, -260 + (gl + 260) * u + 10 * math.sin(t * 1.2) * (1 - u)
flying = lambda t: t < LAND

# ---------------------------------------------------------------- the boy
boy_x = segs([(58, 66, 1290, 0.5, 0.7), (118, 121, 1240, 0.5, 0.6), (184, 194, 860, 0.5, 0.7)], BX0)
BOY = BoyAnim(boy_x, k=1.6, t_end=260, hang=[(0, 1), (LAND - 1, 1), (LAND, 0)], wind=[(0, 0.4), (LAND, 0)],
    crouch=[(0, 0), (LAND, 0), (LAND + 0.2, 16), (LAND + 0.9, 0)], sit=[(0, 0), (T_LIE, 0), (T_LIE + 2.5, 1)],
    poses={'armR': [(0, -30), (LAND - 1, -30), (LAND, 0), (80, 0), (81, -40), (84, -40), (85, 0), (100, 0), (101, -60), (106, -60), (107, 0),
                    (T_LIE + 3, 0), (T_LIE + 4, -100), (T_SAY - 1, -100), (T_SAY, -110), (T_SAY + 4, -110), (T_SAY + 5, 0)],
           'foreR': [(0, -40), (LAND, 0), (81, 60), (84, 60), (85, 0), (101, 20), (106, 20), (107, 0), (T_LIE + 4, 10), (T_SAY + 5, 0)],
           'armL': [(0, 40), (LAND, 0)], 'foreL': [(0, 30), (LAND, 0)],
           'chest': [(0, 0), (T_LIE + 3, 0), (T_LIE + 5, -8), (250, -8)]},
    look_x=[(0, -0.5), (LAND, 0.6), (70, 1.0), (88, 0.8), (98, -0.8), (110, 0.8), (130, 0.6), (T_HANG, 0.9), (T_CURL, -0.8), (184, -0.9), (T_LIE + 3, 0.2), (T_SAY, 0.5)],
    lookup=[(0, 0.3), (LAND, 0.0), (70, -0.1), (98, 0.1), (T_CURL, 0.0), (T_LIE + 3, 0.9), (T_SAY + 6, 0.6), (240, 0.4)],
    brows=[(0, 0.3), (T_LATE, 0.6), (T_LATE + 4, 0.0)],
    laugh=[(0, 0.4), (LAND, 0.6), (60, 0.3), (T_LATE + 3, 0.3), (T_LATE + 4, 0.9), (90, 0.4), (T_CURL + 4, 0.3), (T_WINK + 1, 0.3), (T_WINK + 2, 0.8), (T_WINK + 4, 0.3),
           (T_SAY + 5, 0.5), (250, 0.4)],
    talk=[(T_SAY, 0), (T_SAY + 0.1, 1), (T_SAY + 4.4, 1), (T_SAY + 4.5, 0)])
boy = BoyActor(BOY, lambda t: gy(boy_x(t)) + 70, facing=[(0, 1), (183.5, -1), (195, 1)])
_bf = boy.foot
boy.foot = lambda t: (gpos(t)[0] - 105, gpos(t)[1] + 245) if flying(t) else _bf(t)
boy.shadow = lambda t: t > LAND - 1
boy.cast = lambda t: dict(cast=0.0) if flying(t) else None

# ---------------------------------------------------------------- the sheep
sheep_x = segs([(59, 67, 1360, 0.5, 0.7), (186, 195, 980, 0.5, 0.7)], SX0)
SHEEP = SheepAnim(sheep_x, k=1.6, t_end=260, lift=[(0, 24), (LAND - 0.6, 24), (LAND + 0.3, 0)],
    crouch=[(0, 0), (T_LIE - 1, 0), (T_LIE + 2, 60)],
    head=[(0, 0), (70, 0), (72, 10), (74, 0)] + osc(88, 92, 0.5, -6, 12) + [(92.3, 0), (T_SLEEP, 0), (T_SLEEP + 4, 14)],
    look=[(0, (-0.5, 0.3)), (LAND, (0.7, -0.2)), (T_LATE, (0.9, -0.4)), (98, (-0.6, -0.4)), (T_HANG, (0.7, -0.3)), (T_CURL, (-0.8, -0.2)), (T_LIE, (0.4, -0.6)),
          (T_WINK, (0.3, -1.0)), (T_SLEEP, (0.2, -0.4))],
    laugh=[(0, 0.5), (LAND, 0.8), (60, 0.2), (T_LATE + 4, 0.2), (T_LATE + 5, 1), (88, 0.3), (T_WINK + 1, 0.3), (T_WINK + 2, 1), (T_WINK + 5, 0.4), (T_SLEEP, 0.4)],
    tail=[(0, 0)] + osc(LAND, LAND + 4, 0.3, -24, 24) + [(LAND + 4.3, 0)] + osc(T_LATE + 5, T_LATE + 10, 0.3, -24, 24) + [(T_LATE + 10.3, 0)],
    sleep=[(0, 0), (T_SLEEP, 0), (T_SLEEP + 6, 1)])
sheep = SheepActor(SHEEP, lambda t: gy(sheep_x(t)) + 112, facing=[(0, 1), (185.5, -1)])
_sf = sheep.foot
sheep.foot = lambda t: (gpos(t)[0] + 70, gpos(t)[1] + 262) if flying(t) else _sf(t)
sheep.shadow = lambda t: t > LAND - 1
sheep.cast = lambda t: dict(cast=0.0) if flying(t) else None

# ---------------------------------------------------------------- the rose
rose = RoseActor(ROSE, dome=[(0, 1)], lean=[(0, 0), (66, 0), (68, -12), (T_LATE + 3, -12), (T_LATE + 5, 0)],
                 talk=[(T_LATE, 0), (T_LATE + 0.1, 1), (T_LATE + 2.4, 1), (T_LATE + 2.5, 0)],
                 mood=[(0, 0), (T_LATE + 4, 0), (T_LATE + 6, 1), (130, 1), (140, 0.5), (250, 0.5)])
rose.worlds = (MORN, DUSK, NIGHT)

# ---------------------------------------------------------------- Moth
def moth_ground(t):
    if t < T_HANG - 8: return MX0, 0.0
    if t < T_HANG: u = ss((t - T_HANG + 8) / 7); return MX0 + (POST - 80 - MX0) * u, 120 * math.sin(math.pi * u)
    if t < T_CURL - 10: return POST - 80, 0.0
    u = ss((t - T_CURL + 10) / 9); return POST - 80 + (VOLC + 60 - POST + 80) * u, 220 * math.sin(math.pi * u)
WATCH = {}
class MothActor(Actor):
    height = 600; tuft_w = 60
    def __init__(self): self.shadow = True; self.cast = None
    def foot(self, t):
        if flying(t): return gpos(t)
        x, h = moth_ground(t); return (x, gy(x) + 30 - h)
    def draw(self, f, X, Y, s, t, W_, C):
        sm = s * 1.25
        if flying(t):
            cx, cy = X, Y; open_ = 1.0; flap = 1.0
        else:
            x, h = moth_ground(t)
            air = h > 3 or (T_HANG - 8 < t < T_HANG) or (T_CURL - 10 < t < T_CURL - 1)
            sitting = t > T_CURL - 1
            cx, cy = X, Y - (190 if sitting else 230) * sm
            open_ = 1.0 if air else (0.0 if sitting else float(keys([(LAND, 1), (LAND + 3, 0.3)], t)))
            flap = 1.0 if air else 0.0
        night = ss((t - 200) / 12)
        if night > 0.01: glow(f, cx, cy, 300 * sm, '#ffcf80', 0.32 * night)   # warm at last: a soft night lamp
        out = {}
        holding = T_HANG - 9 < t < T_HANG + 1
        draw_moth(f, cx, cy, sm, t, flip=1 if t < T_CURL - 10 else -1, open_=open_, flap=flap, flap_speed=1.3,
                  mood=1.0, laugh=float(keys([(0, 0.6), (LAND, 0.6), (LAND + 2, 0), (T_LATE + 4, 0), (T_LATE + 5, 0.8), (90, 0)], t)),
                  surprise=float(keys([(0, 0), (T_LATE, 0), (T_LATE + 0.5, 0.6), (T_LATE + 3, 0)], t)),
                  blink=(0.0 if t > T_CURL + 6 and not (T_WINK + 1 < t < T_SAY + 6) else None),
                  look=(float(keys([(0, 0.5), (LAND, 0.6), (98, -0.6), (T_HANG, 0.4), (T_CURL, 0.2)], t)), float(keys([(0, 0.3), (T_LIE, -0.5), (T_WINK, -0.9)], t))),
                  hold=(0, 120) if flying(t) else ((0, 90) if holding else ((0, 70) if t > T_CURL else None)), reach=float(keys([(0, 0), (100, 0), (101, 0.6), (106, 0.6), (107, 0)], t)),
                  glow_amt=0.3 + 0.5 * night, light=W_.light, rim=W_.rim, rim_w=0.55, out=out, tilt=0.06 if t > T_CURL else 0.0)
        WATCH['moth'] = out
        if holding and 'hand' in out:
            hx, hy = out['hand']; sb = 0.85 * s
            box(f, hx - 5 * sb, hy + 168 * sb, sb, light=W_.light, rim=W_.rim, glow_amt=0.0, t=t, handle=True, grey=0.6)
moth = MothActor()
def post_fn(f, X, Y, s, t, W_, C):
    L = Layer(X - 140 * s - 20, Y - 420 * s - 20, 280 * s + 40, 440 * s + 40)
    stroke(L, np.array([(X, Y), (X + 3 * s, Y - 380 * s)], np.float32), '#6a4a2a', 10 * s, 1, taper=False)
    stroke(L, np.array([(X + 3 * s, Y - 370 * s), (X - 90 * s, Y - 372 * s)], np.float32), '#6a4a2a', 7 * s, 1, taper=False)
    composite(f, L)
    if t > T_HANG:
        sb = 0.85 * s; hx, hy = X - 80 * s, Y - 370 * s
        box(f, hx - 5 * sb, hy + 168 * sb + 8 * s, sb, light=W_.light, rim=W_.rim, glow_amt=0.12 * ss((t - 205) / 8), t=t, handle=True, tilt=2 * math.sin(t * 0.8), grey=0.6)
post = Prop(post_fn, (POST, gy(POST) + 30), height=380, tuft_w=40); post.worlds = (MORN, DUSK, NIGHT)
SC.actors = [boy, sheep, rose, moth, post]

# ---------------------------------------------------------------- sky: B612 ahead at dawn, Pip winking at night
STREAM = StarStream(n=120, seed=41)
PIPS = (1880, 230)
def sky_fx(f, C, t, W_):
    z = C.z
    if W_ is SPACE:
        STREAM.draw(f, t, speed=0.5, amt=0.6)
        X, Y = C.to_screen(700, 640); r = (60 + 160 * ss(t / 26)) * z
        glow(f, X, Y, r * 2.2, '#ffd8b0', 0.45)
        x0, x1, y0, y1 = int(max(0, X - r - 4)), int(min(W, X + r + 4)), int(max(0, Y - r - 4)), int(min(H, Y + r + 4))
        if x1 > x0 and y1 > y0:   # the little planet, painted round: lit from the dawn, grass, a soft rim of air
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); dx, dy = (xx - X) / r, (yy - Y) / r; d = np.sqrt(dx * dx + dy * dy)
            m = np.clip((1 - d) * r / 2.0, 0, 1)[..., None]
            nz = np.sqrt(np.clip(1 - d * d, 0, 1)); lit = np.clip(-0.55 * dx - 0.5 * dy + 0.65 * nz, 0, 1)[..., None]
            col = hexc('#2c5a3a') * (1 - lit) + hexc('#9cd27a') * lit
            col = col * (1 + 0.06 * np.sin(xx * 0.09 + yy * 0.05)[..., None] * np.sin(yy * 0.11)[..., None])
            rim = np.clip(1 - np.abs(d - 0.97) / 0.06, 0, 1)[..., None] * 0.6
            f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - m) + col * m + hexc('#ffe0c0') * rim * m
            for (vx, vy_) in ((-0.55, -0.62), (-0.2, -0.86)):   # two tiny volcanoes on the rim
                glow(f, X + vx * r, Y + vy_ * r, r * 0.05, '#8a5a3a', 0.8)
        glow(f, X - r * 0.45, Y - r * 0.85, r * 0.12, '#ff8a9a', 0.9)   # the rose, a pink speck
    if W_ is NIGHT or W_ is DUSK:
        a = ss((t - 206) / 6)
        if a > 0.01:
            X, Y = C.to_screen(*PIPS)
            wink = (T_WINK < t < T_WINK + 0.5) or (T_SAY + 5 < t < T_SAY + 5.4) or (240 < t < 240.4)
            draw_pip(f, X, Y, 16 * z, t=t, light=1.0 * a, face='closed' if wink else 'open', laugh=0.6 if wink else 0.2, glow_amt=1.0 * a)
SC.sky_fx = sky_fx

# ---------------------------------------------------------------- shots
G = lambda x, dy, z: (x, gy(x) + dy, z)
def fly_cam(t): x, y = gpos(t); return (x * 0.5 + 1440 * 0.5, y * 0.5 + 560 * 0.5 + 60, 0.85)
def land_cam(t): x, y = gpos(t); u = ss((t - 30) / (LAND - 30)); return (x + 40, y + 120 * u + 80, 1.0 + 0.2 * u)
SC.shots = [
    (0,   fly_cam, 0.0),
    (14,  [(14, (1300, 600, 2.0)), (24, (1250, 600, 2.1))], 0.0),
    (24,  [(24, G(1300, -520, 0.75)), (30, G(1300, -480, 0.78))], 0.0),
    (30,  land_cam, 0.0),
    (LAND + 2, [(LAND + 2, G(1150, -40, 2.4)), (58, G(1150, -40, 2.5))], 0.8),
    (58,  [(58, G(1330, -150, 1.3)), (T_LATE, G(1350, -150, 1.4))], 0.3),
    (T_LATE, [(T_LATE, (ROSE[0], ROSE[1] - 150, 3.2)), (T_LATE + 8, (ROSE[0], ROSE[1] - 150, 3.4))], 1.2),
    (T_LATE + 8, [(T_LATE + 8, G(1300, -40, 2.4)), (96, G(1300, -40, 2.5))], 0.8),
    (96,  [(96, G(1300, -200, 1.1)), (112, G(1320, -200, 1.15))], 0.3),
    (112, [(112, G(MX0 + 20, -230, 2.2)), (122, G(MX0 + 20, -230, 2.3))], 0.8),
    (122, [(122, G(1440, -160, 0.9)), (T_HANG + 4, G(1500, -170, 0.95))], 0.2),
    (T_HANG + 4, [(T_HANG + 4, (POST - 80, gy(POST) - 160, 2.6)), (150, (POST - 80, gy(POST) - 160, 2.7))], 1.0),
    (150, [(150, G(1200, -260, 0.8)), (T_CURL, G(1100, -250, 0.85))], 0.0),
    (T_CURL, [(T_CURL, G(VOLC + 60, -160, 1.7)), (176, G(VOLC + 60, -160, 1.8))], 0.6),
    (176, [(176, G(1000, -300, 0.8)), (T_LIE + 4, G(950, -280, 0.85))], 0.0),
    (T_LIE + 4, [(T_LIE + 4, G(860, -130, 1.6)), (T_WINK - 2, G(860, -150, 1.6))], 0.6),
    (T_WINK - 2, [(T_WINK - 2, (PIPS[0], PIPS[1] + 40, 3.0)), (T_WINK + 2, (PIPS[0], PIPS[1] + 40, 3.1))], 0.0),
    (T_WINK + 2, [(T_WINK + 2, G(880, -110, 2.2)), (T_SLEEP - 2, G(880, -110, 2.3))], 0.8),
    (T_SLEEP - 2, [(T_SLEEP - 2, G(980, -60, 2.8)), (238, G(980, -60, 2.9))], 1.0),
    (238, [(238, G(1100, -300, 0.95)), (250, G(1200, -420, 0.72))], 0.0),
]
SC.subs = [(T_LATE, T_LATE + 2.6, "You're late.", '你们回来晚了。'),
           (T_SAY, T_SAY + 4.6, 'Every time you laugh, a star gets brighter.', '每次你笑，就有一颗星星更亮一点。')]
SC.titles = [(240.5, 249.5, 'The End', '完')]
SC.fade_in, SC.fade_out = 2.0, 2.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, LAND, 'triumph', 0.8), (LAND, T_HANG, 'warm', 0.8), (T_HANG, 186, 'dusk', 0.75), (186, 250, 'night', 0.7)]
SFX = [(0, 'wind', dict(dur=LAND, gain=0.4)), (LAND, 'thump', dict(gain=0.35)), (LAND + 0.5, 'giggle', dict(n=10)), (T_LATE + 4, 'giggle', dict(n=14)),
       (T_LATE + 5, 'chime', dict(notes=[1319, 1568], gain=0.3)), (T_HANG - 8, 'whoosh', dict(dur=2, f=200, gain=0.4)), (T_HANG, 'tap', dict(gain=0.4)),
       (T_CURL - 10, 'whoosh', dict(dur=3, f=200, gain=0.4)), (200, 'crickets', dict(dur=50, gain=0.4)), (T_WINK, 'twinkle', dict(gain=0.5)),
       (T_SAY + 5, 'twinkle', dict(gain=0.4)), (240, 'twinkle', dict(gain=0.4))]

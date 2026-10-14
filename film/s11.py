# S11 · The pilot laughs (270 s). Earth, the desert, night. The pilot sits on the plane's wheel and looks up, as every night.
# He searches. Then, there: faint, but there. He blinks, smiles, and laughs out loud. "There you are."
# The laugh rises as a little gold ribbon of light, all the way up the sky. It reaches Pip. Pip blazes,
# and all the stars start laughing like five hundred million little bells.
import math, numpy as np, cv2
from base import *
from cast import *
from motion import keys
from flight import StarStream, BOY_LAST, SHEEP_LAST
from pilot import draw_pilot, draw_plane
from pip import draw_pip
from moth import draw_moth
from core import pencil

class S11(Scene):
    DURATION = 270.0

SC = S11()
DES = World('night', place='desert'); SKY = World('stairs', place='space')
dgy = DES.gy
T_SEE, T_SMILE, T_LAUGH, T_SAY, T_RIB0, T_UP, T_RIB1, T_BLAZE, T_BELLS, T_BACK = 104.0, 109.0, 116.0, 112.0, 140.0, 196.0, 206.0, 207.0, 216.0, 252.0
SC.worlds = [(0, T_UP, DES), (T_UP, T_UP + 4, (DES, SKY)), (T_UP + 4, T_BACK, SKY), (T_BACK, T_BACK + 4, (SKY, DES)), (T_BACK + 4, 1e9, DES)]

def osc(t0, t1, period, a, b):
    ks = [(t0, a)]; t = t0 + period / 2; i = 0
    while t < t1: ks.append((t, b if i % 2 == 0 else a)); t += period / 2; i += 1
    return ks

PX = 1500
PIP_D = (2160, 300)          # Pip in the desert sky
def in_desert(t): return t < T_UP + 2 or t > T_BACK + 2
def pip_light(t):
    if t < T_BLAZE: return 0.3 + 0.05 * math.sin(t * 1.3)
    return 0.3 + 0.7 * ss((t - T_BLAZE) / 1.5)
def laugh_amt(t): return float(keys([(0, 0), (T_LAUGH - 0.5, 0), (T_LAUGH + 0.4, 1), (175, 0.85), (190, 0.6), (T_BACK + 4, 0.6), (T_BACK + 5, 1), (270, 0.9)], t))

# ---------------------------------------------------------------- the desert: plane, tent, the pilot
def plane_fn(f, X, Y, s, t, W_, C):
    X, Y = C.to_screen(PX, dgy(PX) + 20); draw_plane(f, X, Y, 1.42 * s, light=W_.light, rim=W_.rim)   # sorted behind the pilot
PILOT = {}
def pilot_fn(f, X, Y, s, t, W_, C):
    scan = float(keys([(0, 0.0), (30, 0.0)] + osc(32, T_SEE - 2, 7.0, -0.8, 0.7) + [(T_SEE, 0.8), (300, 0.8)], t))
    draw_pilot(f, X, Y, 0.95 * s, 1, t=t, light=W_.light, rim=W_.rim,
               up=float(keys([(0, 0.2), (18, 0.2), (24, 0.75), (T_SEE, 0.8), (T_SEE + 1, 0.9), (T_RIB0 + 30, 0.95), (270, 0.9)], t)),
               look=(scan, 0), laugh=laugh_amt(t), smile=float(keys([(0, 0.15), (T_SEE, 0.15), (T_SMILE, 0.7), (T_LAUGH, 0.9)], t)),
               talk=float(keys([(T_SAY, 0), (T_SAY + 0.1, 1), (T_SAY + 2.2, 1), (T_SAY + 2.3, 0)], t)),
               blink=(0.0 if T_SEE + 1.6 < t < T_SEE + 1.8 or T_SEE + 2.3 < t < T_SEE + 2.5 else None),
               slump=float(keys([(0, 0.3), (T_SEE, 0.4), (T_SEE + 1, 0.0)], t)),
               arms=({'armL': 10 * math.sin(t * 4) * laugh_amt(t)} if t > T_LAUGH else None))
    PILOT['head'] = (X + 10 * s, Y - 520 * 0.95 * s)
def tent_fn(f, X, Y, s, t, W_, C):
    L = Layer(X - 300 * s - 30, Y - 360 * s - 30, 600 * s + 60, 390 * s + 60)
    def T(pts): return np.asarray(pts, np.float32) * s + [X, Y]
    P = T([(-260, 0), (0, -330), (260, 0)])
    shade(L, L.mask(P, 0.6), '#7a7068', lit='#b8ac9a', shadow='#2a2630', light=W_.light, soft=0.4, tex_amt=0.2, streak=1, poly=P, line='#1a1418', line_w=1.4 * s,
          line_a=0.6, rim=W_.rim, rim_w=0.4)
    D = T([(-70, 0), (0, -190), (70, 0)])
    lamp = 0.85 * (1 - ss((t - 12) / 3))
    L.put(hexc('#ffb860') * (0.35 + 0.65 * lamp) + hexc('#1a1410') * (1 - lamp), L.mask(D, 0.8))
    stroke(L, T([(0, -330), (0, -380)]), '#3a3028', 4 * s, 1, taper=False)
    composite(f, L)
    if lamp > 0.02: glow(f, X, Y - 80 * s, 260 * s, '#ffb060', 0.35 * lamp)
on_d = lambda t: in_desert(t)
plane = Prop(plane_fn, (PX, dgy(PX) - 120), height=300, active=on_d)
pilot = Prop(pilot_fn, (PX - 60, dgy(PX) + 21), height=400, active=on_d)
tent = Prop(tent_fn, (PX + 520, dgy(PX + 520) - 10), height=330, tuft_w=0, active=on_d)

# ---------------------------------------------------------------- up there: Pip in its place, the friends watching
GAP = (1720, 230)
def gpos(t): return (1260 + 10 * math.sin(t * 0.4), 560 + 14 * math.sin(t * 1.2))
on_s = lambda t: not in_desert(t)
BOY = BoyAnim(segs([], 0), k=1.6, t_end=300, hang=[(0, 1)], wind=[(0, 0.3)],
    poses={'armR': [(0, -30), (T_RIB1, -30), (T_RIB1 + 1.5, -120), (240, -120), (242, -30)], 'foreR': [(0, -40), (T_RIB1 + 1.5, -10), (242, -40)],
           'armL': [(0, 40), (T_RIB1, 40), (T_RIB1 + 1.5, 120), (240, 120), (242, 40)], 'foreL': [(0, 30)]},
    look_x=[(0, 0.2), (T_RIB1 - 6, 0.0), (T_RIB1, 0.5), (300, 0.5)], lookup=[(0, -0.9), (T_RIB1 - 6, -0.9), (T_RIB1, 0.8), (230, 0.6), (300, 0.7)],
    brows=[(0, 0.9), (T_RIB1, 0.0)], mouth=[(T_RIB1 - 3, T_RIB1, 'open')], laugh=[(0, 0), (T_BLAZE, 0), (T_BLAZE + 1, 1), (300, 0.9)])
boy = BoyActor(BOY, 0, facing=[(0, 1)], active=on_s); boy.shadow = False; boy.cast = dict(cast=0.0)
boy.foot = lambda t: (gpos(t)[0] - 105, gpos(t)[1] + 245) if on_s(t) else None
SHEEP = SheepAnim(segs([], 0), k=1.6, t_end=300, lift=[(0, 24)],
    look=[(0, (-0.3, 1.0)), (T_RIB1 - 6, (-0.2, 1.0)), (T_RIB1, (0.4, -1.0)), (300, (0.3, -0.9))],
    laugh=[(0, 0), (T_BLAZE, 0), (T_BLAZE + 1, 1), (300, 1)], tail=[(0, 0)] + osc(T_BLAZE + 1, 300, 0.3, -26, 26), sleep=[(0, 0)])
sheep = SheepActor(SHEEP, 0, facing=[(0, 1)], active=on_s); sheep.shadow = False; sheep.cast = dict(cast=0.0)
sheep.foot = lambda t: (gpos(t)[0] + 70, gpos(t)[1] + 262) if on_s(t) else None
class MothActor(Actor):
    height = 600; tuft_w = 0
    def __init__(self): self.shadow = False; self.cast = dict(cast=0.0)
    def foot(self, t): return gpos(t) if on_s(t) else None
    def draw(self, f, X, Y, s, t, W_, C):
        draw_moth(f, X, Y, s * 1.25, t, flip=1, open_=1, flap=0.5, flap_speed=0.7, mood=float(keys([(0, 0.4), (T_BLAZE, 1)], t)),
                  surprise=float(keys([(0, 0), (T_RIB1 - 3, 0), (T_RIB1 - 1, 1), (T_BLAZE + 2, 0)], t)),
                  laugh=float(keys([(0, 0), (T_BLAZE + 1, 0), (T_BLAZE + 2, 1), (300, 1)], t)),
                  look=(0.5, float(keys([(0, 0.9), (T_RIB1 - 6, 0.9), (T_RIB1, -0.8)], t))), hold=(0, 120),
                  glow_amt=0.3 + 0.7 * ss((t - T_BLAZE) / 2), light=W_.light, rim=W_.rim, rim_w=0.55)
moth = MothActor()
SC.actors = [plane, pilot, tent, moth, boy, sheep]

# ---------------------------------------------------------------- the ribbon of laughter, and the laughing stars
def ribbon(f, C, t, src, dst, prog, z, seed=0, amt=1.0):
    """A gold ribbon of light from src to dst (screen points); prog 0..1 is how far its head has got."""
    if prog <= 0: return
    n = 90; pts = []
    for k in range(n + 1):
        u = k / n * prog
        x = src[0] + (dst[0] - src[0]) * u + math.sin(u * 9 + t * 2.2 + seed) * 70 * z * math.sin(math.pi * min(1, u / max(prog, 1e-3)))
        y = src[1] + (dst[1] - src[1]) * u + math.sin(u * 5 + t * 1.6) * 20 * z
        pts.append((x, y))
    P = np.asarray(pts, np.float32)
    g = np.zeros_like(f)
    for w_, c, a in ((14, (1.0, 0.75, 0.3), 0.35), (6, (1.0, 0.86, 0.5), 0.6), (2, (1.0, 0.97, 0.85), 0.9)):
        cv2.polylines(g, [(P * 8).astype(np.int32)], False, tuple(x * a for x in c), max(1, int(w_ * z)), cv2.LINE_AA, shift=3)
    g = cv2.GaussianBlur(g, (0, 0), 1.5 + 2 * z)
    f[:] = f + g * amt
    hx, hy = P[-1]
    glow(f, hx, hy, 40 * z, '#fff0b0', 0.8 * amt)
    r = np.random.default_rng(int(t * 24) + seed)
    for k in range(14):
        i = int(r.random() * len(P)); glow(f, P[i][0] + r.normal(0, 12) * z, P[i][1] + r.normal(0, 12) * z, 2.5 * z, '#fff4c0', 0.7 * amt)
BELLS = np.random.default_rng(41).random((260, 4))
def bells(f, t, amt, ymax):
    """All the stars laughing: little gold twinkles all over the sky, ringing on and off."""
    if amt <= 0: return
    for k in range(len(BELLS)):
        u, v, ph, sz = BELLS[k]
        x, y = u * W, v * ymax
        a = amt * max(0.0, math.sin(t * (2.5 + 3 * ph) + ph * 30)) ** 3
        if a > 0.02:
            glow(f, x, y, (2 + 4 * sz) * 2.2, '#fff0b8', 0.9 * a)
            if sz > 0.75: glow(f, x, y, (2 + 4 * sz) * 7, '#ffd070', 0.25 * a)
TOP = [(GAP[0] - 330, GAP[1] - 60, 30), (GAP[0] - 170, GAP[1] - 190, 26), (GAP[0] + 180, GAP[1] - 170, 32), (GAP[0] + 360, GAP[1] - 40, 28),
       (GAP[0] + 120, GAP[1] + 120, 22), (GAP[0] - 210, GAP[1] + 140, 24)]
STREAM = StarStream(n=120, seed=31)
def sky_fx(f, C, t, W_):
    z = C.z
    if W_ is DES:
        X, Y = C.to_screen(*PIP_D); pl = pip_light(t)
        if t > T_SEE - 30 or t > T_BACK:
            draw_pip(f, X, Y, 9 * z * (1 + 0.5 * ss((t - T_BLAZE) / 2)), t=t, light=pl, face='laugh' if t > T_BACK else 'open', laugh=1.0 if t > T_BACK else 0, glow_amt=0.6 + 0.6 * pl)
            if pl < 0.5 and 60 < t < T_SEE + 4: glow(f, X, Y, 8 * z, '#fff4d0', 0.25 + 0.2 * abs(math.sin(t * 2.7)))
        bells(f, t, ss((t - T_BACK - 4) / 4) * 0.9, H * 0.62)
    else:
        STREAM.draw(f, t, speed=0.06, amt=0.6)
        for (x, y, sz) in TOP:
            X, Y = C.to_screen(x, y); lf = ss((t - T_BELLS) / 3)
            draw_pip(f, X, Y, sz * z, t=t + x * 0.01, light=0.85, face='laugh' if lf > 0.5 else 'open', laugh=lf, glow_amt=0.5)
        bells(f, t, ss((t - T_BELLS) / 4), H)
def front_fx(f, C, t, W_):
    z = C.z
    if W_ is DES:
        if T_RIB0 < t < T_UP + 3 and 'head' in PILOT:
            X, Y = C.to_screen(*PIP_D)
            prog = ss((t - T_RIB0) / (T_UP + 2 - T_RIB0)) * 1.0
            ribbon(f, C, t, (PILOT['head'][0] + 10 * z, PILOT['head'][1] - 10 * z), (X, Y + 200 * z), prog * 1.4 if prog < 0.7 else 0.98, z * 0.5 + 0.5)
        if t > T_BACK and 'head' in PILOT:
            X, Y = C.to_screen(*PIP_D)
            ribbon(f, C, t, PILOT['head'], (X, Y), 1.0, z * 0.5 + 0.5, amt=0.5 * ss((t - T_BACK - 3) / 3))
    else:
        X, Y = C.to_screen(*GAP)
        prog = ss((t - T_UP - 1) / (T_RIB1 - T_UP - 1))
        ribbon(f, C, t, (X - 300 * z, H + 60), (X, Y), prog, z * 0.5 + 0.5, seed=3)
        lit = pip_light(t)
        draw_pip(f, X, Y, 30 * z * (1 + 0.25 * ss((t - T_BLAZE) / 1.5)), t=t, light=lit, face='closed' if t < T_RIB1 - 1 else 'laugh', laugh=1.0 if t > T_BLAZE else 0.0,
                 glow_amt=0.6 + 0.8 * lit, look=(0, 0.8))
        if T_BLAZE - 0.2 < t < T_BLAZE + 3:
            glow(f, X, Y, 500 * z * (0.4 + (t - T_BLAZE) / 3), '#fff0b0', 0.7 * (1 - (t - T_BLAZE) / 3.2))
SC.sky_fx, SC.front_fx = sky_fx, front_fx

# ---------------------------------------------------------------- shots
G = lambda x, dy, z: (x, dgy(x) + dy, z)
PH = (PX - 50, dgy(PX) - 290)          # the pilot's face
def rise_cam(t):
    u = ss((t - T_RIB0 - 20) / (T_UP - T_RIB0 - 20)); return (PX + 300 + 300 * u, dgy(PX) - 250 - 300 * u, 1.0 - 0.15 * u)
SC.shots = [
    (0,   [(0, G(1300, -380, 0.72)), (18, G(1350, -360, 0.78))], 0.0),
    (18,  [(18, G(1700, -200, 1.1)), (34, G(1680, -200, 1.15))], 0.3),
    (34,  [(34, (PH[0], PH[1], 3.2)), (50, (PH[0], PH[1], 3.35))], 1.0),
    (50,  [(50, G(1900, -420, 0.9)), (66, G(1950, -440, 0.95))], 0.0),
    (66,  [(66, (PH[0], PH[1], 3.0)), (80, (PH[0], PH[1], 3.1))], 1.0),
    (80,  [(80, (PIP_D[0] - 200, PIP_D[1] + 120, 1.3)), (92, (PIP_D[0] - 150, PIP_D[1] + 100, 1.45))], 0.0),
    (92,  [(92, (PH[0], PH[1], 3.4)), (100, (PH[0], PH[1], 3.5))], 1.0),
    (100, [(100, (PIP_D[0] - 20, PIP_D[1] + 40, 2.2)), (T_SEE + 1, (PIP_D[0], PIP_D[1] + 20, 3.0))], 0.0),
    (T_SEE + 1, [(T_SEE + 1, (PH[0], PH[1], 3.6)), (T_LAUGH + 2, (PH[0], PH[1], 3.9))], 1.2),
    (T_LAUGH + 2, [(T_LAUGH + 2, G(1600, -260, 1.4)), (128, G(1600, -260, 1.45))], 0.4),
    (128, [(128, G(1300, -360, 0.8)), (T_RIB0, G(1330, -360, 0.82))], 0.0),
    (T_RIB0, [(T_RIB0, (PH[0] + 60, PH[1] - 40, 2.2)), (T_RIB0 + 20, (PH[0] + 100, PH[1] - 120, 1.6))], 0.0),
    (T_RIB0 + 20, rise_cam, 0.0),
    (T_UP + 2, [(T_UP + 2, (GAP[0] - 260, GAP[1] + 320, 1.0)), (T_RIB1, (GAP[0] - 100, GAP[1] + 120, 1.6))], 0.0),
    (T_RIB1, [(T_RIB1, (GAP[0], GAP[1] + 20, 2.6)), (T_BELLS - 1, (GAP[0], GAP[1] + 20, 2.8))], 0.0),
    (T_BELLS - 1, [(T_BELLS - 1, (1440, 420, 0.8)), (232, (1440, 440, 0.85))], 0.0),
    (232, [(232, (1160, 580, 2.0)), (242, (1160, 570, 2.1))], 0.0),
    (242, [(242, (1440, 420, 0.75)), (T_BACK + 4, (1440, 400, 0.72))], 0.0),
    (T_BACK + 4, [(T_BACK + 4, G(1500, -330, 1.3)), (270, G(1500, -500, 0.75))], 0.0),
]
SC.subs = [(T_SAY, T_SAY + 2.5, 'There you are.', '你在这儿啊。')]
SC.fade_in, SC.fade_out = 2.0, 3.0
SCENE = SC

# ---------------------------------------------------------------- music and sound
MUSIC = [(0, T_SEE, 'night', 0.6), (T_SEE, T_RIB0, 'wonder', 0.8), (T_RIB0, T_BLAZE, 'wonder', 0.9), (T_BLAZE, 270, 'triumph', 1.0)]
SFX = [(0, 'crickets', dict(dur=T_UP, gain=0.5)), (0, 'wind', dict(dur=270, gain=0.2)), (T_SEE + 1, 'chime', dict(notes=[1200], gain=0.25)),
       (T_LAUGH, 'giggle', dict(n=20, shift=-22, gain=0.9)), (T_LAUGH + 6, 'giggle', dict(n=12, shift=-20, gain=0.7)), (T_RIB0, 'shimmer', dict(dur=60, gain=0.5)),
       (T_RIB1, 'chime', dict(notes=[1568, 2093, 2637, 3136])), (T_BLAZE, 'sparkle'), (T_BLAZE + 1, 'giggle', dict(n=18)), (T_BACK + 4, 'crickets', dict(dur=14, gain=0.4)),
       (T_BACK + 4, 'giggle', dict(n=14, shift=-22, gain=0.7))]
for k in range(48): SFX.append((T_BELLS + k * 0.75, 'chime', dict(notes=[[2093, 2349, 2637, 3136, 3520][k % 5] * (1 + (k % 3)) // 1], gain=0.15)))

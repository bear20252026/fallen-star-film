# Test shot v2: evening on B612, with real acting. Usage: python3 shot_test2.py START END OUTDIR [SUBSAMPLES]
import sys, os, numpy as np, cv2, math
from core import *
from cam import Cam, grade, light_rays, BS
from motion import flow, travel, keys, ss
from bg import paint_b612
from boy2 import draw_boy
from boy_anim import BoyAnim
from sheep import draw_sheep
from sheep_anim import SheepAnim
from pip import draw_pip
from props import draw_rose, draw_volcano, draw_sprout

FPS = 24; DUR = 22.0
plate, gy, sun = paint_b612()
LIGHT = (0.85, -0.4); RIM = '#ffcf8a'
draw_volcano(plate, 520, gy(520) + 18, 0.9, light=LIGHT, rim=RIM)
draw_volcano(plate, 760, gy(760) + 26, 0.6, light=LIGHT, rim=RIM)
draw_sprout(plate, 2050, gy(2050) + 30, 1.0, light=LIGHT)
draw_sprout(plate, 980, gy(980) + 60, 0.8, light=LIGHT)
PAP = paper()
ROSE = (1440, gy(1440) + 40)
LAND = (1770.0, gy(1770) + 60.0)
FGP = 500
fg = np.zeros((H + 200, W + 2 * FGP, 3), np.float32); fga = np.zeros((H + 200, W + 2 * FGP), np.float32)
r = np.random.default_rng(3)
for k in range(260):
    side = 0 if k % 2 else 1
    x = FGP - 300 + r.random() * 720 if side == 0 else FGP + W - r.random() * 700 + 250
    y = H + 10; ln = 90 + r.random() * 160; lean = (r.random() - 0.5) * 0.8
    c = mix(hexc('#2f4a2c'), hexc('#7a8a48'), r.random() * 0.6); wd = int(4 + r.random() * 5)
    cv2.line(fg, (int(x), int(y)), (int(x + lean * ln), int(y - ln)), c.tolist(), wd, cv2.LINE_AA)
    cv2.line(fga, (int(x), int(y)), (int(x + lean * ln), int(y - ln)), 1.0, wd, cv2.LINE_AA)
fg = cv2.GaussianBlur(fg, (0, 0), 7); fga = cv2.GaussianBlur(fga, (0, 0), 7)

# ---------------- the performance ----------------
boy_path = lambda t: travel(t, 1.8, 7.4, 1020.0, 1300.0, 0.8, 1.0)
BOY = BoyAnim(boy_path, k=1.6, t_end=DUR,
    poses={'chest': [(7.6, 0), (8.2, 6), (8.95, 6), (9.3, -2), (11.0, -2), (11.15, -6), (11.8, 0), (12.0, 0), (12.4, 5), (13.6, 5), (14.2, 1)],
           'armR': [(7.7, 0), (8.3, -32), (8.95, -30), (9.4, 0), (11.0, 0), (11.12, -40), (11.9, -8), (12.1, -8), (12.5, -30), (13.6, -28), (14.3, 0)],
           'foreR': [(7.7, 0), (8.3, -18), (8.95, -18), (9.4, 0), (11.0, 0), (11.12, -30), (11.9, 0), (12.1, 0), (12.5, -26), (13.6, -24), (14.3, 0)],
           'armL': [(11.0, 0), (11.12, 34), (11.9, 4)], 'foreL': [(11.0, 0), (11.12, 24), (11.9, 0)]},
    crouch=[(10.95, 0), (11.1, 12), (11.6, 2), (12.0, 0)],
    lookup=[(0, 0), (8.9, -0.1), (9.0, -0.1), (9.25, 0.9), (10.2, 0.6), (10.9, 0.0), (11.1, -0.2), (12.0, -0.25), (16.0, -0.25), (17.0, 0.1)],
    look_x=[(0, 0.4), (8.9, 0.4), (9.25, 0.9), (10.4, 0.8), (11.0, 0.7), (17.0, 0.6), (17.5, 0.0)],
    laugh=[(17.3, 0), (17.7, 1), (20.6, 1), (21.6, 0.3)],
    talk=[(12.15, 0), (12.25, 1), (13.4, 1), (13.5, 0)],
    brows=[(10.95, 0), (11.1, 1), (12.6, 0.4), (13.6, 0.4), (14.5, 0)],
    mouth=[(11.05, 11.9, 'open')])
def sheep_path(t):
    if t < 13.2: return travel(t, 2.8, 8.4, 740.0, 1150.0, 0.9, 1.1)
    if t < 16.7: return travel(t, 13.2, 15.4, 1150.0, 1630.0, 0.5, 0.8)
    return travel(t, 16.75, 17.25, 1630.0, 1570.0, 0.15, 0.25)
SHEEP = SheepAnim(sheep_path, k=1.6, t_end=DUR,
    sniff=[(0, 1), (2.4, 1), (2.7, 0), (15.3, 0), (15.6, 0.7), (16.5, 0.7), (16.65, -0.6), (17.3, 0)],
    head=[(0, 0), (10.9, 0), (11.05, -14), (11.6, -4), (13.0, 0)],
    hop=[(11.12, 0.32, 26), (16.75, 0.5, 46)],
    look=[(0, (0, 1)), (2.4, (0, 1)), (2.8, (0, 0)), (11.0, (0, -1)), (12.0, (0, 0))],
    laugh=[(17.2, 0), (17.5, 1), (20.6, 1), (21.6, 0.2)],
    tail=[(0, 0)], mouth=[(16.7, 17.3, 'open')])

def pip_state(t):
    """Fall along a gentle arc, then bounce with real decaying hops; squash on contacts, stretch when fast."""
    if t < 9.0: return None
    if t < 11.0:
        u = ((t - 9.0) / 2.0) ** 1.35
        x = 2650 + (LAND[0] - 2650) * u; y = 140 + (LAND[1] - 140) * (u ** 1.15)
        return x, y, -0.22, (t - 9) * 7.0, 0.0
    hops = [(0.62, 48), (0.38, 18), (0.22, 6)]; tt = t - 11.0; x = LAND[0]
    sq = 0.0
    for d, h in hops:
        if tt < d:
            u = tt / d; y = LAND[1] - 4 * h * u * (1 - u)
            sq = 0.3 * h / 48 * math.exp(-tt * 30) - 0.12 * h / 48 * math.sin(math.pi * u)
            return x, y, sq, 0.6 * math.sin(tt * 20) * h / 48, 1.0
        tt -= d
    sq = 0.08 * math.exp(-tt * 12) * math.cos(tt * 25)
    return x, LAND[1], sq, 0.0, 1.0

CAMK = [(0, (1150, 660, 1.0)), (6, (1300, 720, 1.18)), (9.2, (1420, 640, 1.15)), (11.4, (1520, 700, 1.3)),
        (15.2, (1560, 770, 1.5)), (19, (1545, 780, 1.56)), (22, (1540, 782, 1.6))]

def render(t):
    cx, cy, z = flow(CAMK, t)
    C = Cam(cx, cy, z); f = C.view(plate)
    s = 0.5 * z
    # star streak trail behind Pip while falling
    P = pip_state(t)
    if P is not None and t < 11.15:
        for k in range(18):
            tt = t - k * 0.03
            if tt < 9: break
            Q = pip_state(tt); q = C.to_screen(Q[0], Q[1]); u = k / 18
            glow(f, q[0], q[1], 16 * z * (1 - u * 0.7), '#ffe6a0', 0.55 * (1 - u))
    draw_rose(f, *C.to_screen(*ROSE), 0.55 * z, t=t, light=LIGHT, rim=RIM)
    items = []
    bx = boy_path(t); BX, BY = C.to_screen(bx, gy(bx) + 70); BY += BOY.depth(t, 1.8) * s
    items.append((BY, lambda: draw_boy(f, BX, BY, s, 1, t=t, A=BOY.at(t), light=LIGHT, rim=RIM, rim_w=0.55)))
    sx = sheep_path(t); SX, SY = C.to_screen(sx, gy(sx) + 82)
    items.append((SY, lambda: draw_sheep(f, SX, SY, s, 1, t=t, A=SHEEP.at(t), light=LIGHT, rim=RIM, rim_w=0.6)))
    if P is not None:
        X, Y = C.to_screen(P[0], P[1])
        face = 'closed' if t < 16.6 else 'open'
        laugh = float(keys([(17.2, 0), (17.5, 1)], t))
        items.append((Y + 1, lambda: draw_pip(f, X, Y, 30 * z, t=t, light=0.9 + 0.1 * P[4], face=face, laugh=laugh, rot=P[3], squash=P[2])))
    for _, fn in sorted(items, key=lambda a: a[0]): fn()
    f = light_rays(f, *C.to_screen(*sun), amt=0.22, t=t)
    off = (cx - 1150) * 0.6
    M = np.float32([[1, 0, -off - FGP], [0, 1, 0]]); fgs = cv2.warpAffine(fg, M, (W, H)); fas = cv2.warpAffine(fga, M, (W, H))
    f = f * (1 - fas[..., None] * 0.9) + fgs * 0.9 * fas[..., None]
    return grade(f, (1.02, 0.97, 0.95), (0.01, 0.0, 0.02), 1.03)

def frame_at(t, sub=3):
    # film motion blur: a half-frame shutter, averaged over a few moments
    if sub <= 1: f = render(t)
    else: f = sum(render(t + (i / (sub - 1) - 0.5) / (2 * FPS)) for i in range(sub)) / sub
    fade = min(1, t / 1.0, (DUR - t) / 1.0)
    return finish(f * fade, PAP, vign=0.4, grain_seed=int(t * FPS))

if __name__ == '__main__':
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    sub = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    os.makedirs(out, exist_ok=True)
    for i in range(a, b):
        cv2.imwrite(f'{out}/f{i:05d}.jpg', frame_at(i / FPS, sub), [cv2.IMWRITE_JPEG_QUALITY, 94])

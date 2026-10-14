# Test scene v3: the B612 evening told in film shots (wide, tracking, close-ups, cutaways), with scene lighting,
# long evening shadows, wind in the grass, drifting clouds, pollen in the light and depth of field.
# Usage: python3 shot_test3.py START END OUTDIR [SUBSAMPLES]
import sys, os, numpy as np, cv2, math
import core
from core import *
from cam import Cam, grade, light_rays
from motion import flow, keys
from boy2 import draw_boy
from sheep import draw_sheep
from pip import draw_pip
from props import draw_rose, draw_volcano, draw_sprout
from env import Field, tufts, Motes, compose_sky
from perf_test import *

LIGHT = (0.85, -0.4); RIM = '#ffcf8a'
# props baked into the ground layer (alpha recovered by painting over black and over white)
def bake(fn):
    global GROUND, GA
    b = np.zeros_like(GROUND); w_ = np.ones_like(GROUND); fn(b); fn(w_)
    a = np.clip(1 - (w_ - b).mean(axis=2, keepdims=True), 0, 1); col = b / np.maximum(a, 1e-3)
    GROUND = GROUND * (1 - a) + col * a; GA = np.maximum(GA, a)
bake(lambda im: draw_volcano(im, 520, gy(520) + 18, 0.9, light=LIGHT, rim=RIM))
bake(lambda im: draw_volcano(im, 760, gy(760) + 26, 0.6, light=LIGHT, rim=RIM))
bake(lambda im: draw_sprout(im, 2050, gy(2050) + 30, 1.0, light=LIGHT))
bake(lambda im: draw_sprout(im, 980, gy(980) + 60, 0.8, light=LIGHT))
PAP = paper(); FIELD = Field(gy); MOTES = Motes()

def boy_foot(t): x = boy_path(t); return x, gy(x) + 70 + BOY.depth(t, 1.8) * 0.625
def sheep_foot(t): x = sheep_path(t); return x, gy(x) + 82

def follow_boy(t):
    x, y = boy_foot(t); return (x + 150, y - 150, 1.75)
def follow_star(t):
    p = pip_state(min(t + 0.25, 10.99)); return (p[0] - 60, p[1] + 60, 1.2)

# shot list: (start, camera keys or function, depth-of-field blur on the background)
SHOTS = [
    (0.0,   [(0.0, (1150, 700, 0.95)), (4.6, (1205, 722, 1.06))], 0.0),            # wide: evening on the little planet
    (4.6,   follow_boy, 1.0),                                                    # tracking: he walks to his rose
    (8.2,   [(8.2, (1335, 775, 3.0)), (10.0, (1338, 765, 3.25))], 3.5),          # close: at the rose; he hears something
    (10.0,  follow_star, 0.0),                                                    # the sky: a star falls
    (10.9,  [(10.9, (1540, 835, 1.42)), (14.4, (1555, 835, 1.55))], 0.8),         # two-shot: it lands, he startles, speaks
    (14.4,  [(14.4, (1520, 860, 1.9)), (15.5, (1690, 870, 2.1)), (16.55, (1700, 868, 2.2))], 1.8),   # the sheep trots over, sniffs
    (16.55, [(16.55, (1745, 860, 3.1)), (17.7, (1735, 858, 3.25))], 4.0),         # close: the star opens its eyes
    (17.7,  [(17.7, (1530, 830, 1.5)), (22.0, (1500, 805, 1.3))], 0.6),           # everyone laughs; we pull back
]

def camera(t):
    for i, (t0, cam, dof) in enumerate(SHOTS):
        t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else 1e9
        if t0 <= t < t1:
            v = cam(t) if callable(cam) else flow(cam, t)
            return Cam(*v), dof, i
    return Cam(1500, 805, 1.3), 0.6, len(SHOTS) - 1

def set_env(C, foot_y, height, z):
    core.ENV.clear()
    core.ENV.update(tint=(1.0, 0.95, 0.93), fill=(0.10, 0.05, 0.15), bounce=(0.05, 0.06, 0.0), sun=C.to_screen(*SUN),
                    rim_col=(1.0, 0.82, 0.55), rim=0.75, rim_px=3.0 + 1.2 * z, foot_y=foot_y, height=height, cast=0.4, shear=(1.5, 0.1))

def render(t):
    C, dof, shot = camera(t); z = C.z; s = 0.5 * z
    f = compose_sky(C, SKY, CLOUDS, GROUND, GA, t)
    # characters, sorted back to front by where they stand
    chars = []
    bx, by = boy_foot(t); chars.append((by, 'boy', bx))
    sx, sy = sheep_foot(t); chars.append((sy, 'sheep', sx))
    chars.sort()
    FIELD.draw(f, C, t, ymax=chars[0][0] - 1)
    if dof > 0.3: f = cv2.GaussianBlur(f, (0, 0), dof)
    P = pip_state(t)
    if P is not None and t < 11.15:   # the falling star's trail
        for k in range(22):
            tt = t - k * 0.028
            if tt < 9: break
            Q = pip_state(tt); q = C.to_screen(Q[0], Q[1]); u = k / 22
            glow(f, q[0], q[1], 16 * z * (1 - u * 0.7), '#ffe6a0', 0.6 * (1 - u))
    core.ENV.clear(); core.ENV.update(tint=(1.0, 0.96, 0.94), fill=(0.08, 0.04, 0.12), sun=C.to_screen(*SUN), rim=0.5, rim_px=3)
    draw_rose(f, *C.to_screen(*ROSE), 0.55 * z, t=t, light=LIGHT, rim=RIM)
    prev = chars[0][0] - 1
    def field(ymin=-1e9, ymax=1e9, extra=0.0):
        if dof > 0.3:   # out-of-focus grass: draw it on a copy and blur only what was added
            fb = f.copy(); FIELD.draw(fb, C, t, ymin=ymin, ymax=ymax)
            f[:] = f + cv2.GaussianBlur(fb - f, (0, 0), dof * 0.5 + extra)
        else: FIELD.draw(f, C, t, ymin=ymin, ymax=ymax)
    for i, (fy, who, wx) in enumerate(chars):
        if i > 0: field(prev, fy)
        X, Y = C.to_screen(wx, fy)
        if who == 'boy':
            set_env(C, Y, 400 * s, z)
            draw_boy(f, X, Y, s, 1, t=t, A=BOY.at(t), light=LIGHT, rim=RIM, rim_w=0.55, turn=0.28)
            core.ENV.clear(); tufts(f, X, Y, 120 * s, s, t, seed=1)
        else:
            set_env(C, Y, 260 * s, z)
            draw_sheep(f, X, Y, s, 1, t=t, A=SHEEP.at(t), light=LIGHT, rim=RIM, rim_w=0.6)
            core.ENV.clear(); tufts(f, X, Y, 230 * s, s, t, seed=2, n=40)
        prev = fy
    if P is not None:
        X, Y = C.to_screen(P[0], P[1])
        face = 'closed' if t < 16.6 else 'open'
        laugh = float(keys([(17.2, 0), (17.5, 1)], t))
        set_env(C, C.to_screen(P[0], LAND[1])[1] + 30 * z, 60 * z, z); core.ENV['cast'] = 0.15 * P[4]; core.ENV['rim'] = 0.3
        draw_pip(f, X, Y, 30 * z, t=t, light=0.9 + 0.1 * P[4], face=face, laugh=laugh, rot=P[3], squash=P[2])
        core.ENV.clear()
        if P[4] > 0: tufts(f, X, C.to_screen(P[0], LAND[1])[1] + 30 * z, 60 * z, 0.8 * s, t, seed=3, n=12)
    field(prev, extra=dof * 0.6)
    sun = C.to_screen(*SUN)
    f = light_rays(f, *sun, amt=0.24, t=t)
    MOTES.draw(f, t, sun, amt=0.9, cam_dx=C.x * C.k * 0.2)
    # dusk grade: violet lift in the shadows, warm highlights
    lum = f.mean(axis=2, keepdims=True)
    f = f + (1 - np.clip(lum * 1.6, 0, 1)) * np.array([0.035, 0.0, 0.06], np.float32) + np.clip(lum - 0.6, 0, 1) * np.array([0.05, 0.02, -0.03], np.float32)
    return grade(f, (1.02, 0.97, 0.95), (0.0, 0.0, 0.01), 1.04)

def frame_at(t, sub=3):
    C, dof, shot = camera(t)
    ts = [t + (i / (sub - 1) - 0.5) / (2 * FPS) for i in range(sub)] if sub > 1 else [t]
    ts = [x for x in ts if camera(x)[2] == shot] or [t]     # the shutter never spans a cut
    f = sum(render(x) for x in ts) / len(ts)
    fade = min(1, t / 1.0, (DUR - t) / 1.0)
    return finish(f * fade, PAP, vign=0.42, grain_seed=int(t * FPS), bloom=0.4)

if __name__ == '__main__':
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    sub = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    os.makedirs(out, exist_ok=True)
    for i in range(a, b):
        cv2.imwrite(f'{out}/f{i:05d}.jpg', frame_at(i / FPS, sub), [cv2.IMWRITE_JPEG_QUALITY, 94])

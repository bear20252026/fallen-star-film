# Test shot: evening on B612, everything painted in code. Usage: python3 shot_test.py START END OUTDIR
import sys, os, numpy as np, cv2, math
from core import *
from cam import *
from bg import paint_b612
from boy2 import draw_boy
from sheep import draw_sheep
from pip import draw_pip
from props import draw_rose, draw_volcano, draw_sprout

FPS = 24; DUR = 22.0
plate, gy, sun = paint_b612()
# bake static props into the plate (rose, volcanoes, sprouts) at world scale
LIGHT = (0.85, -0.4); RIM = '#ffcf8a'
draw_volcano(plate, 520, gy(520) + 18, 0.9, light=LIGHT, rim=RIM)
draw_volcano(plate, 760, gy(760) + 26, 0.6, light=LIGHT, rim=RIM)
draw_sprout(plate, 2050, gy(2050) + 30, 1.0, light=LIGHT)
draw_sprout(plate, 980, gy(980) + 60, 0.8, light=LIGHT)
PAP = paper()
ROSE = (1580, gy(1580) + 40)
# foreground grass (out of focus), painted once in screen space
fg = np.zeros((H, W, 3), np.float32); fga = np.zeros((H, W), np.float32)
r = np.random.default_rng(3)
for k in range(260):
    side = 0 if k % 2 else 1
    x = r.random() * 420 if side == 0 else W - r.random() * 380
    y = H + 10; ln = 90 + r.random() * 160; lean = (r.random() - 0.5) * 0.8
    c = mix(hexc('#2f4a2c'), hexc('#7a8a48'), r.random() * 0.6)
    cv2.line(fg, (int(x), int(y)), (int(x + lean * ln), int(y - ln)), c.tolist(), int(4 + r.random() * 5), cv2.LINE_AA)
    cv2.line(fga, (int(x), int(y)), (int(x + lean * ln), int(y - ln)), 1.0, int(4 + r.random() * 5), cv2.LINE_AA)
fg = cv2.GaussianBlur(fg, (0, 0), 7); fga = cv2.GaussianBlur(fga, (0, 0), 7)

def frame_at(t):
    # camera: wide establishing, slow push in, then follow the action
    cx, cy, z = track([(0, (1250, 640, 1.0)), (7, (1380, 760, 1.35)), (11, (1560, 700, 1.25)), (16, (1640, 800, 1.7)), (22, (1650, 790, 1.8))], t)
    C = Cam(cx, cy, z)
    f = C.view(plate)
    # the boy walks in from the left to the rose, the sheep trots behind
    bx = track([(0, 880.0), (8, 1430.0), (22, 1445.0)], t); walking = 1.0 if t < 7.6 else max(0, 1 - (t - 7.6) * 3)
    sx = track([(0, 700.0), (8.6, 1330.0), (13, 1300.0), (16, 1750.0), (22, 1760.0)], t)
    swalk = 1.0 if (t < 8.4 or 13 < t < 15.8) else 0.0
    # Pip falls: a streak from the top right, lands at 11.0 and bounces
    land = (1910.0, gy(1910) + 48)
    if t < 9: px, py = None, None
    elif t < 11:
        u = (t - 9) / 2; px = 2700 + (land[0] - 2700) * u; py = 150 + (land[1] - 30 - 150) * (0.6 * u + 0.4 * u * u)
    else:
        b = max(0, 1 - (t - 11) / 1.2); px, py = land[0], land[1] - 30 - abs(math.sin((t - 11) * 9)) * 40 * b
    # shadows + characters, back to front (by world y)
    def put_boy():
        X, Y = C.to_screen(bx, gy(bx) + 70)
        look = (1, -1) if 9 < t < 11.5 else (0, 0)
        draw_boy(f, X, Y, 0.5 * z, 1, t=t, walk=walking, light=LIGHT, rim=RIM, rim_w=0.55, look=look,
                 laugh=1.0 if 17.5 < t < 20.5 else 0.0, talk=1.0 if 12 < t < 13.5 else 0.0, mouth='open' if 11 < t < 12 else 'smile')
    def put_sheep():
        X, Y = C.to_screen(sx, gy(sx) + 82)
        draw_sheep(f, X, Y, 0.5 * z, 1, t=t, walk=swalk, light=LIGHT, rim=RIM, rim_w=0.6, head=-10 if 16 < t < 17.5 else 0,
                   laugh=1.0 if 17 < t < 21 else 0.0, blink=0.0 if (t * 0.7) % 3.1 < 0.1 else None)
    draw_rose(f, *C.to_screen(*ROSE), 0.55 * z, t=t, light=LIGHT, rim=RIM)
    put_sheep(); put_boy()
    if px is not None:
        X, Y = C.to_screen(px, py)
        if t < 11.2:   # the falling streak
            for k in range(14):
                u = k / 14; tt = t - u * 0.5
                if tt < 9: continue
                uu = (tt - 9) / 2; qx = 2700 + (land[0] - 2700) * uu; qy = 150 + (land[1] - 30 - 150) * (0.6 * uu + 0.4 * uu * uu)
                glow(f, *C.to_screen(qx, qy), 16 * z * (1 - u), '#ffe08a', 0.7 * (1 - u))
        lt_ = 1.0 if t > 11 else 0.9
        draw_pip(f, X, Y, 30 * z, t=t, light=lt_, face='closed' if t < 12.5 else 'open', laugh=1.0 if 17 < t < 21 else 0.0, rot=(t - 9) * 6 if t < 11 else 0)
    # light, grade, depth
    f = light_rays(f, *C.to_screen(*sun), amt=0.22, t=t)
    off = (cx - 1250) * 0.6
    M = np.float32([[1, 0, -off], [0, 1, 0]]); fgs = cv2.warpAffine(fg, M, (W, H)); fas = cv2.warpAffine(fga, M, (W, H))
    f = f * (1 - fas[..., None] * 0.9) + fgs * 0.9 * fas[..., None]
    f = grade(f, (1.02, 0.97, 0.95), (0.01, 0.0, 0.02), 1.03)
    fade = min(1, t / 1.0, (DUR - t) / 1.0)
    return finish(f * fade, PAP, vign=0.4, grain_seed=int(t * FPS))

if __name__ == '__main__':
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for i in range(a, b):
        cv2.imwrite(f'{out}/f{i:05d}.jpg', frame_at(i / FPS), [cv2.IMWRITE_JPEG_QUALITY, 94])

import numpy as np, cv2, time, sys
from core import *
from boy2 import draw_boy
from boy_anim import BoyAnim
from motion import travel
s = 0.6
path = lambda t: travel(t, 0.3, 5.0, 0, 520, 0.7, 0.9)
B = BoyAnim(path, k=1.6, t_end=6)
def fr(t):
    f = np.ones((H, W, 3), np.float32) * hexc('#e9dcc6')
    cv2.line(f, (0, 700), (W, 700), (0.6, 0.55, 0.5), 2)
    t0 = time.time(); A = B.at(t); ta = time.time() - t0
    draw_boy(f, 200 + path(t) * 1.6 * s, 640 + B.depth(t) * s, s, 1, t=t, A=A)
    return f, ta
if __name__ == '__main__':
    ims = []
    for i, t in enumerate(np.arange(1.5, 1.5 + 12 / 24, 1 / 24)):
        f, ta = fr(t); x = int(200 + path(t) * 1.6 * s)
        crop = f[380 + int(B.depth(t)*s):720 + int(B.depth(t)*s), max(0, x - 170): x + 170]
        crop = cv2.resize(crop, (340, 340)) if crop.shape[1] != 340 else crop
        ims.append((np.clip(crop, 0, 1) * 255).astype(np.uint8)[..., ::-1])
    print('anim time', ta)
    sheet = np.vstack([np.hstack(ims[0:6]), np.hstack(ims[6:12])])
    cv2.imwrite('../walk_sheet.jpg', sheet)

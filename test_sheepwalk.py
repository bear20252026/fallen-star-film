import numpy as np, cv2, sys
from core import *
from sheep import draw_sheep
from sheep_anim import SheepAnim
from motion import travel
s = 0.6; mode = sys.argv[1]
if mode == 'walk': path = lambda t: travel(t, 0.3, 6.0, 0, 380, 0.7, 0.9); S = SheepAnim(path, t_end=7); T0 = 2.0
elif mode == 'trot': path = lambda t: travel(t, 0.3, 4.0, 0, 520, 0.5, 0.6); S = SheepAnim(path, t_end=7); T0 = 1.5
else: path = lambda t: 0.0; S = SheepAnim(path, hop=[(1.0, 0.45, 60)], t_end=4); T0 = 0.7
ims = []
for t in np.arange(T0, T0 + 12 / 24 * (2 if mode == 'hop' else 1), 1 / 24 * (2 if mode == 'hop' else 1)):
    f = np.ones((H, W, 3), np.float32) * hexc('#e9dcc6'); cv2.line(f, (0, 700), (W, 700), (0.6, 0.55, 0.5), 2)
    X = 300 + path(t) * 1.6 * s
    draw_sheep(f, X, 700, s, 1, t=t, A=S.at(t))
    x = int(X); ims.append((np.clip(f[480:720, x - 150:x + 150], 0, 1) * 255).astype(np.uint8)[..., ::-1])
cv2.imwrite(f'../sheep_{mode}.jpg', np.vstack([np.hstack(ims[0:6]), np.hstack(ims[6:12])]))

import numpy as np, cv2
from core import *
from sheep import draw_sheep
f = np.zeros((H, W, 3), np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
f[:] = hexc('#f3c9a4') * (1 - yy) + hexc('#d98f7a') * yy
draw_sheep(f, 700, 640, 1.4, 1, t=0.3)
draw_sheep(f, 1250, 640, 1.4, -1, t=1.0, head=-12, blink=0.0, mouth='open', walk=0.0)
cv2.imwrite('../t_sheep.png', finish(f, paper()))

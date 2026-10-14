import numpy as np, cv2, sys
from core import *
from boy2 import draw_boy
from sheep import draw_sheep
f = np.zeros((H, W, 3), np.float32)
yy = np.linspace(0, 1, H)[:, None, None]
f[:] = hexc('#f6ead8') * (1 - yy) + hexc('#e9d6bd') * yy
draw_boy(f, 700, 790, 1.75, 1, t=0.3, rim_w=0.2)
draw_boy(f, 1180, 790, 1.75, -1, t=1.0, walk=1.0, talk=1, rim_w=0.2)
draw_sheep(f, 1560, 760, 1.2, -1, t=0.5, rim_w=0.2)
cv2.imwrite('../t_boy.png', finish(f, paper(), vign=0.15))

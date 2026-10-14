import numpy as np, cv2
from core import *
from pip import draw_pip
f = np.zeros((H, W, 3), np.float32); f[:] = hexc('#2a2f55')
for i, (l, fc) in enumerate([(1, 'open'), (0.5, 'closed'), (0.0, 'closed'), (1, 'laugh')]):
    draw_pip(f, 300 + i * 440, 400, 90, t=0.4, light=l, face=fc, laugh=1.0 if fc == 'laugh' else 0)
cv2.imwrite('../t_pip.png', finish(f, paper()))

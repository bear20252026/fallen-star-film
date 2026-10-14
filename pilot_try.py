import sys; sys.path.insert(0,'.')
from core import *
from pilot import draw_pilot, draw_plane
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.25,0.3,0.5],np.float32)
f[650:]=np.array([0.55,0.5,0.45])
draw_plane(f, 960, 700, 1.35)
draw_pilot(f, 880, 700, 0.9, 1, t=1.0, up=0.6)
draw_pilot(f, 1500, 700, 0.9, 1, t=1.0, laugh=1.0, up=0.7)
draw_pilot(f, 1780, 700, 0.6, 1, t=1.0, slump=1.0, up=0.2)
cv2.imwrite('pilot_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

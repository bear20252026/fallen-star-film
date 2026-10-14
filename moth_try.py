import sys; sys.path.insert(0,'.')
from core import *
from moth import draw_moth
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.16,0.14,0.24],np.float32)
draw_moth(f,330,420,0.7,1.0,open_=1,mood=0,surprise=1)
draw_moth(f,960,420,0.7,1.3,open_=0,mood=0,hold=(0,60),glow_amt=0.6,shiver=1)
draw_moth(f,1590,420,0.7,1.0,open_=1,flap=1,mood=1,laugh=1,reach=1)
cv2.imwrite('moth_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

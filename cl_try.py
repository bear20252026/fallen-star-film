import sys; sys.path.insert(0,'.')
from core import *
from cloudchar import draw_cloud_char
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.55,0.6,0.7],np.float32)
draw_cloud_char(f,330,300,1.0,1.0,mood=0,rain=1,sob=1)
draw_cloud_char(f,960,300,1.0,1.0,mood=0.5,talk=1)
draw_cloud_char(f,1590,300,1.0,1.0,mood=1,laugh=1,wave=1)
cv2.imwrite('cl_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

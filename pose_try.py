import sys; sys.path.insert(0,'.')
from core import *
from boy2 import draw_boy
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.8,0.85,0.9],np.float32)
tests=[{'armR':-128,'foreR':-14},{'armR':20,'foreR':80,'armL':-20,'foreL':-80},{'armR':10,'foreR':100,'armL':-10,'foreL':-100},{'armR':30,'foreR':95,'armL':-30,'foreL':-95},{'armR':-5,'foreR':120,'armL':5,'foreL':-120},{'armR':15,'foreR':60,'armL':-15,'foreL':-60}]
for i,p in enumerate(tests):
    draw_boy(f,170+i*310,740,0.75,1,t=1.0,pose=p)
cv2.imwrite('pose_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

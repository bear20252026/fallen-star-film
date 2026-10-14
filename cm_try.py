import sys; sys.path.insert(0,'.')
from core import *
from clockmaker import draw_clockmaker
from clocks import grandfather, post_clock, gear_clock, pocket_watch
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.95,0.7,0.55],np.float32); f[700:]=np.array([0.6,0.5,0.35])
grandfather(f,150,720,1.0,3.3); post_clock(f,330,720,1.0,3.3); gear_clock(f,600,720,1.0,3.3)
for i,kw in enumerate([dict(),dict(u=0.25,walk=1),dict(crank=1.0),dict(laugh=1),dict(frozen=1),dict(up=1,hold=1)]):
    draw_clockmaker(f,880+i*180,720,1.3,1,t=1.0,**kw)
pocket_watch(f,1850,500,1.5,2.0)
cv2.imwrite('cm_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

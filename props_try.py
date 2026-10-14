import sys; sys.path.insert(0,'.')
from core import *
from props3 import telescope, box, Flock
import cv2, numpy as np
f = np.ones((804,1920,3),np.float32)*np.array([0.55,0.7,0.85],np.float32); f[600:]=np.array([0.4,0.6,0.3])
e=telescope(f,250,650,1.2)
box(f,600,650,1.3); box(f,900,650,1.3,glow_amt=1.0,handle=True); box(f,1150,650,1.3,glow_amt=0.4,grey=1)
F=Flock(); F.draw(f,1.0,1550,250,1.0,anchors=[(1500,600),(1600,620)])
cv2.imwrite('props_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

import sys; sys.path.insert(0,'.'); sys.path.insert(0,'film')
from core import *
from sheep import draw_sheep
from sheep_anim import SheepAnim
import cv2, numpy as np
f = np.ones((500,1920,3),np.float32)*np.array([0.6,0.7,0.6],np.float32)
for i,c in enumerate([26,45,60,75,90]):
    A=SheepAnim(lambda t:0, t_end=3, crouch=[(0,c)], sleep=[(0,1)]).at(2.0)
    draw_sheep(f,200+i*380,420,0.9,1,t=2.0,A=A)
cv2.imwrite('lie_try.jpg',np.clip(f[...,::-1]*255,0,255).astype(np.uint8))

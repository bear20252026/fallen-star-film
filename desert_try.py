import sys; sys.path.insert(0,'film'); sys.path.insert(0,'.')
from base import *
from pilot import draw_pilot, draw_plane
import time
t0=time.time(); D=World('night', place='desert'); print('painted', time.time()-t0)
class S(Scene): DURATION=10
sc=S(); sc.worlds=[(0,1e9,D)]
PX=1500
def fn(f,X,Y,s,t,W_,C): draw_plane(f,X,Y,1.35*s/0.5,light=W_.light,rim=W_.rim)
def fp(f,X,Y,s,t,W_,C): draw_pilot(f,X,Y,0.9*s/0.5,1,t=t,up=0.7,light=W_.light,rim=W_.rim)
sc.actors=[Prop(fn,(PX,D.gy(PX)+20),height=300), Prop(fp,(PX-60,D.gy(PX)+21),height=400)]
sc.shots=[(0,[(0,(1440,640,1.0))],0.0)]
a=sc.frame(1,1); sc.shots=[(0,[(0,(PX,760,2.2))],0.0)]; b=sc.frame(1,1)
cv2.imwrite('desert_try.jpg',np.vstack([cv2.resize(a,(960,402)),cv2.resize(b,(960,402))]))

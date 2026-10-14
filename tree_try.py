import sys; sys.path.insert(0,'.')
from places import dead_tree
import numpy as np, cv2
f=np.ones((804,1920,3),np.float32)*0.12
for i,(x,sc) in enumerate(((300,1.2),(900,0.9),(1500,0.7))): dead_tree(f,x,760,sc,seed=i*3+2)
cv2.imwrite('tree_try.jpg',np.clip(f[...,::-1]*255*2.5,0,255).astype(np.uint8))

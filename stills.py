import sys, os, cv2, numpy as np
sys.path.insert(0,'film'); sys.path.insert(0,'.')
import importlib; S = importlib.import_module(sys.argv[1]).SCENE
ts=[float(x) for x in sys.argv[2].split(',')]
ims=[cv2.resize(S.frame(t,1),(640,268)) for t in ts]
while len(ims)%3: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+3]) for i in range(0,len(ims),3)]
cv2.imwrite(sys.argv[3],np.vstack(rows))

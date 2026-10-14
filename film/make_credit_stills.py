# Render the stills the credits are built from (one frame from each chosen moment).
import sys, os, importlib, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, '.')
PICK = [('s01', 250), ('s02', 50), ('s05', 245), ('s06', 210), ('s08', 208), ('s10', 130), ('s11', 262), ('s12', 221)]
for i, (n, t) in enumerate(PICK):
    out = f'film/credits/still_{i}.png'
    if os.path.exists(out): continue
    S = importlib.import_module(n).SCENE; S.subs = []
    cv2.imwrite(out, S.frame(t, 1)); print(out, flush=True)

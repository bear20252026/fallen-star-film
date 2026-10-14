# A tiny 2D skeleton: bones with offsets and angles; parts are shapes in bone space.
import numpy as np, math

class Rig:
    def __init__(self, bones):
        # bones: list of (name, parent, (ox, oy))  offsets are from the parent's pivot in the parent's space
        self.bones = {n: (p, np.array(o, np.float32)) for n, p, o in bones}
        self.order = [n for n, _, _ in bones]
    def solve(self, ang, root=(0, 0)):
        M = {}
        for n in self.order:
            p, o = self.bones[n]
            a = math.radians(ang.get(n, 0.0))
            R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]], np.float32)
            if p is None: M[n] = (R, np.array(root, np.float32) + o)
            else:
                PR, PT = M[p]; M[n] = (PR @ R, PT + PR @ o)
        self.M = M; return M
    def X(self, bone, pts):
        R, T = self.M[bone]; P = np.asarray(pts, np.float32).reshape(-1, 2)
        return P @ R.T + T

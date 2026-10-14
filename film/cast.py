# The cast as scene actors: the boy, the sheep, Pip, the rose, plus helpers for paths and facing.
import math, numpy as np
from base import Actor, Prop
from motion import travel, keys
from boy2 import draw_boy
from boy_anim import BoyAnim
from sheep import draw_sheep, LAST as SHEEP_LAST
from sheep_anim import SheepAnim
from pip import draw_pip
from props import draw_rose

def segs(moves, x_start):
    """Path from a list of moves [(t0, t1, x_to), ...] (eased); holds still between moves."""
    pts = []; x = x_start
    for (t0, t1, x1, *ad) in moves:
        pts.append((t0, t1, x, x1, *(ad or [0.7, 0.9]))); x = x1
    def f(t):
        v = x_start
        for (t0, t1, a, b, acc, dec) in pts:
            if t < t0: return v
            v = travel(t, t0, t1, a, b, acc, dec) if t < t1 else b
        return v
    return f

def steps(ks, t):
    """Step keys [(t, value)]: the latest value at or before t."""
    v = ks[0][1]
    for (tk, vk) in ks:
        if t >= tk: v = vk
        else: break
    return v

class BoyActor(Actor):
    height = 400; tuft_w = 120; tuft_n = 26
    def __init__(self, anim, ybase, facing=None, active=None, prop=None, prop_back=None, turn=0.22, depth=True):
        """ybase(t): world y of the feet (before the walk's drift toward camera). facing: [(t, +1/-1)]."""
        self.anim, self.ybase, self.facing, self.active = anim, ybase, facing or [(0, 1)], active
        self.prop, self.prop_back, self.turn, self.use_depth = prop, prop_back, turn, depth
        self.anchors = [0.0]; self.shadow = True
    def foot(self, t):
        if self.active and not self.active(t): return None
        y = self.ybase(t) if callable(self.ybase) else self.ybase
        return (self.anim.path(t), y)
    def draw(self, f, X, Y, s, t, W_, C):
        fl = steps(self.facing, t)
        pr = self.prop(t) if self.prop else None; pb = self.prop_back(t) if self.prop_back else None
        draw_boy(f, X, Y, s, fl, t=t, A=self.anim.at(t), light=W_.light, rim=W_.rim, rim_w=0.55, turn=self.turn, prop=pr, prop_back=pb,
                 shadow=self.shadow(t) if callable(self.shadow) else self.shadow)

class SheepActor(Actor):
    height = 260; tuft_w = 230; tuft_n = 40
    def __init__(self, anim, ybase, facing=None, active=None):
        self.anim, self.ybase, self.facing, self.active = anim, ybase, facing or [(0, 1)], active; self.shadow = True; self.scale = None
    def foot(self, t):
        if self.active and not self.active(t): return None
        y = self.ybase(t) if callable(self.ybase) else self.ybase
        return (self.anim.path(t), y)
    def draw(self, f, X, Y, s, t, W_, C):
        if self.scale is not None: s = s * self.scale(t)
        draw_sheep(f, X, Y, s, steps(self.facing, t), t=t, A=self.anim.at(t), light=W_.light, rim=W_.rim, rim_w=0.6,
                   shadow=self.shadow(t) if callable(self.shadow) else self.shadow)

class RoseActor(Actor):
    height = 220; tuft_w = 90; tuft_n = 14
    def __init__(self, pos, dome=None, lean=None, talk=None, mood=None):
        self.pos, self.dome, self.lean, self.talk = pos, dome or [(0, 1)], lean or [(0, 0)], talk or [(0, 0)]
        self.mood = mood or [(0, 0)]
    def foot(self, t): return self.pos
    def draw(self, f, X, Y, s, t, W_, C):
        draw_rose(f, X, Y, 0.55 * s / 0.5, t=t, light=W_.light, rim=W_.rim, dome=bool(steps(self.dome, t)),
                  lean=float(keys(self.lean, t)), talk=float(keys(self.talk, t)), mood=float(keys(self.mood, t)))

class PipActor(Actor):
    height = 60; tuft_w = 60; tuft_n = 12
    def __init__(self, state, active=None):
        """state(t) -> dict(x, y, ground_y, light, face, laugh, rot, squash, look, size) or None."""
        self.state, self.active = state, active
    def foot(self, t):
        st = self.state(t)
        if st is None: return None
        return (st['x'], st.get('ground_y', st['y']))
    def draw(self, f, X, Y, s, t, W_, C):
        st = self.state(t); X2, Y2 = C.to_screen(st['x'], st['y']); z = s / 0.5
        draw_pip(f, X2, Y2, st.get('size', 30) * z, t=t, light=st.get('light', 1.0), face=st.get('face', 'open'), laugh=st.get('laugh', 0.0),
                 rot=st.get('rot', 0.0), squash=st.get('squash', 0.0), look=st.get('look', (0, 0)), glow_amt=st.get('glow', 1.0))

class Walker:
    """Gait phase for simple walkers (the Clockmaker, the Moth on foot...): phase from distance travelled."""
    def __init__(self, path, t_end, stride=60.0, t_start=0.0):
        self.path = path; self.dt = 1 / 120; ts = np.arange(t_start - 2, t_end + 2, self.dt)
        xs = np.array([path(t) for t in ts]); v = np.gradient(xs, self.dt)
        self.ts, self.v = ts, v; self.ph = np.cumsum(np.abs(v)) * self.dt / stride
    def at(self, t):
        v = float(np.interp(t, self.ts, self.v)); return float(np.interp(t, self.ts, self.ph)), float(np.clip(abs(v) / 60, 0, 1))

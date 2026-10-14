# Scene framework for the painted film. A scene = worlds (time of day) + actors + shots + subtitles + effects.
import sys, os, math, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core
from core import *
from cam import Cam, grade, light_rays
from motion import flow, keys, ss
from bg import paint_b612, PAL
from places import PLACES
from env import Field, tufts, Motes, compose_sky
from props import draw_volcano, draw_sprout
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS = 24
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE, exist_ok=True)

# ---------------------------------------------------------------- worlds (painted places at a time of day)
LOOK = {
    'morning': dict(light=(-0.6, -0.75), rim='#fff3d0', env=dict(tint=(1.0, 1.0, 1.0), fill=(0.03, 0.05, 0.09), bounce=(0.03, 0.06, 0.0),
                    rim_col=(1.0, 0.97, 0.86), rim=0.4, cast=0.3, shear=(-0.55, 0.14)), grade=((1.0, 1.0, 1.0), (0.0, 0.0, 0.01), 1.05),
                    lift=(0.0, 0.01, 0.03), warm=(0.03, 0.02, -0.01), rays=0.16, motes=0.5, field=('#5c8a44', '#cfe283', False, 1.0)),
    'dusk': dict(light=(0.85, -0.4), rim='#ffcf8a', env=dict(tint=(1.0, 0.95, 0.93), fill=(0.10, 0.05, 0.15), bounce=(0.05, 0.06, 0.0),
                 rim_col=(1.0, 0.82, 0.55), rim=0.75, cast=0.4, shear=(1.5, 0.1)), grade=((1.02, 0.97, 0.95), (0.0, 0.0, 0.01), 1.04),
                 lift=(0.035, 0.0, 0.06), warm=(0.05, 0.02, -0.03), rays=0.24, motes=0.9, field=('#55773f', '#d9d283', True, 1.0)),
    'night': dict(light=(0.3, -0.85), rim='#b8c8ff', env=dict(tint=(0.6, 0.66, 0.92), fill=(0.02, 0.03, 0.08), bounce=(0.0, 0.01, 0.02),
                  rim_col=(0.7, 0.8, 1.0), rim=0.45, cast=0.18, shear=(0.4, 0.15)), grade=((0.95, 0.98, 1.06), (0.0, 0.0, 0.02), 0.95),
                  lift=(0.0, 0.01, 0.05), warm=(0.0, 0.0, 0.02), rays=0.0, motes=0.0, field=('#24403f', '#4e6e68', True, 0.35)),
    'desert_night': dict(light=(-0.6, -0.7), rim='#b8c8ff', env=dict(tint=(0.62, 0.66, 0.9), fill=(0.03, 0.03, 0.08), bounce=(0.02, 0.02, 0.04),
                  rim_col=(0.75, 0.82, 1.0), rim=0.5, cast=0.25, shear=(-0.6, 0.12)), grade=((0.96, 0.98, 1.05), (0.0, 0.0, 0.02), 0.95),
                  lift=(0.0, 0.01, 0.05), warm=(0.0, 0.0, 0.02), rays=0.0, motes=0.0, field=None),
    'space_deep': dict(light=(-0.6, -0.5), rim='#a8b8ff', env=dict(tint=(0.7, 0.72, 0.9), fill=(0.03, 0.03, 0.09), bounce=(0.0, 0.0, 0.0),
                  rim_col=(0.7, 0.78, 1.0), rim=0.55, cast=0.0, shear=(0.0, 0.0)), grade=((0.96, 0.97, 1.05), (0.0, 0.0, 0.02), 0.95),
                  lift=(0.01, 0.0, 0.05), warm=(0.03, 0.01, -0.01), rays=0.0, motes=0.0, field=None),
    'clock_sunset': dict(light=(0.85, -0.35), rim='#ffc070', env=dict(tint=(1.0, 0.92, 0.86), fill=(0.10, 0.04, 0.12), bounce=(0.06, 0.04, 0.0),
                  rim_col=(1.0, 0.75, 0.45), rim=0.85, cast=0.42, shear=(1.6, 0.1)), grade=((1.03, 0.96, 0.92), (0.0, 0.0, 0.01), 1.05),
                  lift=(0.04, 0.0, 0.06), warm=(0.06, 0.02, -0.03), rays=0.3, motes=0.9, field=('#6a5a30', '#f0c870', True, 0.6)),
    'dark_night': dict(light=(0.75, -0.45), rim='#b89aff', env=dict(tint=(0.58, 0.54, 0.78), fill=(0.03, 0.02, 0.07), bounce=(0.01, 0.0, 0.03),
                  rim_col=(0.75, 0.62, 1.0), rim=0.6, cast=0.2, shear=(0.6, 0.12)), grade=((0.96, 0.95, 1.05), (0.01, 0.0, 0.03), 0.92),
                  lift=(0.01, 0.0, 0.05), warm=(0.0, 0.0, 0.02), rays=0.0, motes=0.0, field=None),
    'cloudp_rain': dict(light=(-0.3, -0.9), rim='#d8e0f0', env=dict(tint=(0.82, 0.86, 0.94), fill=(0.04, 0.05, 0.08), bounce=(0.0, 0.02, 0.01),
                  rim_col=(0.85, 0.9, 1.0), rim=0.2, cast=0.08, shear=(0.2, 0.15)), grade=((0.96, 0.98, 1.02), (0.01, 0.01, 0.02), 0.85),
                  lift=(0.02, 0.03, 0.05), warm=(0.0, 0.0, 0.01), rays=0.0, motes=0.0, field=('#33554a', '#7a9a80', False, 0.5)),
    'cloudp_after': dict(light=(-0.6, -0.75), rim='#fff3d0', env=dict(tint=(1.0, 1.0, 1.0), fill=(0.03, 0.05, 0.09), bounce=(0.03, 0.06, 0.0),
                  rim_col=(1.0, 0.97, 0.86), rim=0.45, cast=0.3, shear=(-0.55, 0.14)), grade=((1.0, 1.0, 1.0), (0.0, 0.0, 0.01), 1.1),
                  lift=(0.0, 0.01, 0.03), warm=(0.03, 0.02, -0.01), rays=0.2, motes=0.6, field=('#4a8a50', '#d6ee8a', False, 1.0)),
}

class World:
    """B612 (or another place) painted once at a time of day; cached on disk so render workers start fast."""
    def __init__(self, tod='dusk', place='b612', props=True):
        self.tod, self.place = tod, place
        L = LOOK.get(f'{place}_{tod}') or LOOK.get(tod) or LOOK['space_deep']
        painter = (lambda **kw: paint_b612(tod, layers=True, **kw)) if place == 'b612' else (lambda **kw: PLACES[place](tod, **kw))
        path = os.path.join(CACHE, f'{place}_{tod}.npz')
        if os.path.exists(path):
            z = np.load(path); self.sky, self.ground, self.ga = z['sky'], z['ground'], z['ga']
            self.CL = [(z[f'c{i}'], z[f'a{i}']) for i in range(2)]
            _, _, _, _, self.gy, self.sun = painter(quick=True)
        else:
            self.sky, self.CL, self.ground, self.ga, self.gy, self.sun = painter()
            if props and place == 'b612': self._props(L)
            np.savez(path, sky=self.sky, ground=self.ground, ga=self.ga, c0=self.CL[0][0], a0=self.CL[0][1], c1=self.CL[1][0], a1=self.CL[1][1])
        self.light, self.rim, self.look = L['light'], L['rim'], L
        self.field = None
        if L.get('field'): d, l, rt, fm = L['field']; self.field = Field(self.gy, dark=d, lit=l, lit_right=rt, flower_mul=fm)
        self.motes = Motes()

    def _props(self, L):
        gy = self.gy
        def bake(fn):
            b = np.zeros_like(self.ground); w_ = np.ones_like(self.ground); fn(b); fn(w_)
            a = np.clip(1 - (w_ - b).mean(axis=2, keepdims=True), 0, 1); col = b / np.maximum(a, 1e-3)
            if self.tod == 'night': col = col * np.array([0.42, 0.46, 0.62], np.float32)   # props painted in daylight colours sink into the night
            self.ground = self.ground * (1 - a) + col * a; self.ga = np.maximum(self.ga, a)
        bake(lambda im: draw_volcano(im, 520, gy(520) + 18, 0.9, light=L['light'], rim=L['rim']))
        bake(lambda im: draw_volcano(im, 760, gy(760) + 26, 0.6, light=L['light'], rim=L['rim']))

    def background(self, C, t):
        return compose_sky(C, self.sky, self.CL, self.ground, self.ga, t)

    def set_env(self, C, foot_y, height, z, **kw):
        core.ENV.clear(); core.ENV.update(self.look['env']); core.ENV.update(sun=C.to_screen(*self.sun), rim_px=3.0 + 1.2 * z, foot_y=foot_y, height=height)
        core.ENV.update(kw)

# ---------------------------------------------------------------- actors
class Actor:
    """Something standing in the world. foot(t) -> world (x, y) or None when not in the scene."""
    tuft_w = 120; tuft_n = 26; height = 400; cast = None
    def foot(self, t): return None
    def draw(self, f, X, Y, s, t, W_, C): pass

class Prop(Actor):
    def __init__(self, fn, foot, height=200, tuft_w=0, active=None):
        self.fn, self._foot, self.height, self.tuft_w, self.active = fn, foot, height, tuft_w, active
    def foot(self, t):
        if self.active and not self.active(t): return None
        return self._foot(t) if callable(self._foot) else self._foot
    def draw(self, f, X, Y, s, t, W_, C): self.fn(f, X, Y, s, t, W_, C)

# ---------------------------------------------------------------- subtitles and titles
FONT_CJK = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def _font(size, cjk=False):
    for p in ([FONT_CJK] if cjk else ['/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf', FONT_CJK]):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()
_SUB = {}
def subtitle_img(en, zh):
    k = (en, zh)
    if k in _SUB: return _SUB[k]
    im = Image.new('RGBA', (W, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fe, fz = _font(38), _font(34, True)
    for txt, fnt, y in ((en, fe, 22), (zh, fz, 82)):
        if not txt: continue
        w = d.textlength(txt, font=fnt); x = (W - w) / 2
        d.text((x, y), txt, font=fnt, fill=(255, 250, 238, 255), stroke_width=3, stroke_fill=(40, 26, 30, 200))
    sh = im.filter(ImageFilter.GaussianBlur(6)); base = Image.new('RGBA', im.size, (0, 0, 0, 0))
    a = np.array(sh)[..., 3:4].astype(np.float32) / 255 * 0.55
    rgba = np.array(im).astype(np.float32) / 255
    out = (rgba[..., :3] * rgba[..., 3:4], np.clip(rgba[..., 3:4] + a * (1 - rgba[..., 3:4]), 0, 1), rgba[..., 3:4])
    _SUB[k] = out; return out

def put_subtitle(img_bgr, en, zh, op=1.0):
    col, a, a_txt = subtitle_img(en, zh)
    y0 = H - 178; reg = img_bgr[y0:y0 + 170].astype(np.float32) / 255
    rgb = reg[..., ::-1]
    rgb = rgb * (1 - a * op) + col * op            # text over a soft dark glow
    img_bgr[y0:y0 + 170] = (np.clip(rgb[..., ::-1], 0, 1) * 255 + 0.5).astype(np.uint8)

_TITLE = {}
def title_img(en, zh, size=110):
    k = (en, zh, size)
    if k in _TITLE: return _TITLE[k]
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    fe = _font(size); fz = _font(int(size * 0.62), True)
    we = d.textlength(en, font=fe); wz = d.textlength(zh, font=fz)
    d.text(((W - we) / 2, H * 0.32), en, font=fe, fill=(255, 226, 150, 255))
    d.text(((W - wz) / 2, H * 0.32 + size * 1.25), zh, font=fz, fill=(255, 238, 200, 255))
    a = np.array(im).astype(np.float32) / 255
    glow_ = cv2.GaussianBlur(a[..., 3], (0, 0), 18)
    _TITLE[k] = (a, glow_); return _TITLE[k]

def put_title(f, en, zh, op, size=110):
    """Golden painted title with a warm glow (f is the float RGB frame before finish)."""
    a, g = title_img(en, zh, size)
    f[:] = 1 - (1 - f) * (1 - np.clip(g[..., None] * np.array([1.0, 0.8, 0.45]) * 0.8 * op, 0, 1))
    al = a[..., 3:4] * op
    tex_ = 1 + 0.08 * tex(NOISE[0], 0, 0, W, H, 1.5)[..., None]
    f[:] = f * (1 - al) + a[..., :3] * tex_ * al

# ---------------------------------------------------------------- the scene renderer
class Scene:
    DURATION = 300.0
    def __init__(self):
        self.shots = []      # (t0, cam keys or fn(t)->(x,y,z), dof)
        self.worlds = []     # (t0, t1, World) and dissolves: (t0, t1, (WorldA, WorldB)) with mix over [t0, t1]
        self.actors = []
        self.subs = []       # (t0, t1, en, zh)
        self.titles = []     # (t0, t1, en, zh)
        self.fade_in, self.fade_out = 1.0, 1.0
        self.iris = []       # (t0, t1, fn(t) -> (cx, cy, r) in screen pixels): a soft round window, dark outside

    def camera(self, t):
        for i, (t0, cam, dof) in enumerate(self.shots):
            t1 = self.shots[i + 1][0] if i + 1 < len(self.shots) else 1e9
            if t0 <= t < t1:
                v = cam(t) if callable(cam) else flow(cam, t)
                return Cam(*v), dof, i
        return Cam(1440, 700, 1.0), 0.0, -1

    def world_at(self, t):
        for (t0, t1, w) in self.worlds:
            if t0 <= t < t1:
                if isinstance(w, tuple): return w[0], w[1], ss((t - t0) / (t1 - t0))
                return w, None, 0.0
        w = self.worlds[-1][2]; return (w[1] if isinstance(w, tuple) else w), None, 0.0

    # hooks
    def sky_fx(self, f, C, t, W_): pass         # things in the sky (behind everything on the ground)
    def front_fx(self, f, C, t, W_): pass       # things in front of everything

    def render_world(self, W_, C, t, dof, s, z):
        f = W_.background(C, t)
        self.sky_fx(f, C, t, W_)
        items = []
        for a in self.actors:
            wl = getattr(a, 'worlds', None)
            if wl is not None and W_ not in wl: continue
            p = a.foot(t)
            if p is not None: items.append((p[1], id(a), a, p))
        items.sort(key=lambda q: (q[0], q[1]))
        first = items[0][0] if items else 1e9
        if W_.field: W_.field.draw(f, C, t, ymax=first - 1)
        if dof > 0.3: f = cv2.GaussianBlur(f, (0, 0), dof)
        def field(ymin=-1e9, ymax=1e9, extra=0.0):
            if W_.field is None: return
            if dof > 0.3:
                fb = f.copy(); W_.field.draw(fb, C, t, ymin=ymin, ymax=ymax)
                f[:] = f + cv2.GaussianBlur(fb - f, (0, 0), dof * 0.5 + extra)
            else: W_.field.draw(f, C, t, ymin=ymin, ymax=ymax)
        prev = first - 1
        for i, (fy, _, a, p) in enumerate(items):
            if i > 0: field(prev, fy)
            X, Y = C.to_screen(p[0], p[1])
            if -600 < X < W + 600 and -400 < Y < H + 900:
                W_.set_env(C, Y, a.height * s, z, **((a.cast(t) if callable(a.cast) else a.cast) or {}))
                a.draw(f, X, Y, s, t, W_, C)
                core.ENV.clear()
                if a.tuft_w and W_.field: tufts(f, X, Y, a.tuft_w * s, s, t, seed=id(a) % 97, n=a.tuft_n)
            prev = fy
        field(prev, extra=dof * 0.6)
        self.front_fx(f, C, t, W_)
        L = W_.look; sun = C.to_screen(*W_.sun)
        if L['rays'] > 0: f = light_rays(f, *sun, amt=L['rays'], t=t)
        if L['motes'] > 0: W_.motes.draw(f, t, sun, amt=L['motes'], cam_dx=C.x * C.k * 0.2)
        lum = f.mean(axis=2, keepdims=True)
        f = f + (1 - np.clip(lum * 1.6, 0, 1)) * np.array(L['lift'], np.float32) + np.clip(lum - 0.6, 0, 1) * np.array(L['warm'], np.float32)
        mul, lift, sat = L['grade']
        return grade(f, mul, lift, sat)

    def render(self, t):
        C, dof, shot = self.camera(t); z = C.z; s = 0.5 * z
        A, B, m = self.world_at(t)
        f = self.render_world(A, C, t, dof, s, z)
        if B is not None and m > 0.001:
            f = f * (1 - m) + self.render_world(B, C, t, dof, s, z) * m
        for (t0, t1, fn) in self.iris:
            if t0 <= t < t1:
                cx, cy, r = fn(t); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
                d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
                m = np.clip((r - d) / max(6.0, r * 0.06), 0, 1)[..., None]
                f = f * m + np.array([0.035, 0.03, 0.045], np.float32) * (1 - m)
        for (t0, t1, en, zh) in self.titles:
            if t0 <= t < t1:
                op = min(1, (t - t0) / 1.5, (t1 - t) / 1.5); put_title(f, en, zh, max(0, op))
        return f

    def frame(self, t, sub=2):
        C, dof, shot = self.camera(t)
        ts = [t + (i / (sub - 1) - 0.5) / (2 * FPS) for i in range(sub)] if sub > 1 else [t]
        ts = [x for x in ts if self.camera(x)[2] == shot and 0 <= x < self.DURATION] or [t]
        f = sum(self.render(x) for x in ts) / len(ts)
        fade = min(1, t / self.fade_in if self.fade_in else 1, (self.DURATION - t) / self.fade_out if self.fade_out else 1)
        out = finish(f * max(0, fade), PAP, vign=0.42, grain_seed=int(t * FPS), bloom=0.4)
        for (t0, t1, en, zh) in self.subs:
            if t0 <= t < t1:
                put_subtitle(out, en, zh, min(1, (t - t0) / 0.25, (t1 - t) / 0.25))
        return out

PAP = paper()

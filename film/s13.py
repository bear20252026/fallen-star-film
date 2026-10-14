# S13 · Credits (80 s). Stills from the film appear as pencil drawings, then the watercolour bleeds in; names beside them.
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw
from base import *
from core import paper, ss, hexc

HERE = os.path.dirname(os.path.abspath(__file__))
STILLS = [cv2.imread(os.path.join(HERE, 'credits', f'still_{i}.png')).astype(np.float32) / 255 for i in range(8)]
LINES = [("The Fallen Star", "坠落的星星"),
         ("A story about a boy, a sheep and a little star", "一个男孩、一只羊和一颗小星星的故事"),
         ("The Boy · The Sheep · Pip · The Rose", "小王子 · 小羊 · 小星星 · 玫瑰"),
         ("The Clockmaker · The Cloud", "钟表匠 · 云朵"),
         ("Moth", "飞蛾"),
         ("Five hundred million little bells", "五亿个小铃铛"),
         ("The Pilot", "飞行员"),
         ("Painted in code, frame by frame, for bear", "一帧一帧用代码画成，献给 bear")]
PAPER = paper()
PAPER3 = np.dstack([PAPER] * 3) if PAPER.ndim == 2 else PAPER
_rng = np.random.default_rng(3)
def _noise(h, w, sc, seed):
    r = np.random.default_rng(seed).random((h // sc + 2, w // sc + 2)).astype(np.float32)
    return cv2.GaussianBlur(cv2.resize(r, (w, h), interpolation=cv2.INTER_CUBIC), (0, 0), sc * 0.3)
SW, SH = 1100, 460
PREP = []
_xx = np.arange(SW, dtype=np.float32)[None, :]; _yy = np.arange(SH, dtype=np.float32)[:, None]
EDGE0 = np.minimum(np.minimum(_xx, SW - 1 - _xx), np.minimum(_yy, SH - 1 - _yy)) / 14
for i, im in enumerate(STILLS):
    im = cv2.resize(im, (SW, SH), interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    dog = cv2.GaussianBlur(g, (0, 0), 1.0) - cv2.GaussianBlur(g, (0, 0), 3.0)
    lines = np.clip(-dog * 9, 0, 1) ** 0.8                       # pencil: dark where edges are
    shade_ = np.clip((0.55 - cv2.GaussianBlur(g, (0, 0), 4)) * 0.6, 0, 0.35)   # a little soft hatching tone
    n = _noise(SH, SW, 40, i) * 0.6 + _noise(SH, SW, 9, i + 50) * 0.4
    wash = cv2.GaussianBlur(im, (0, 0), 1.2) * 0.9 + im * 0.1
    PREP.append((lines, shade_, n, wash))
CREAM = np.array([0.93, 0.95, 0.97], np.float32)   # BGR paper
PENCIL = np.array([0.30, 0.28, 0.30], np.float32)
_TXT = {}
def text_img(en, zh, big=False):
    k = (en, zh, big)
    if k in _TXT: return _TXT[k]
    im = Image.new('L', (720, 200), 0); d = ImageDraw.Draw(im)
    fe, fz = font_for(54 if big else 38), font_for(44 if big else 32, True)
    d.text((360, 60), en, font=fe, fill=255, anchor='mm'); d.text((360, 130), zh, font=fz, fill=255, anchor='mm')
    a = np.asarray(im, np.float32) / 255; _TXT[k] = a; return a
def font_for(size, cjk=False):
    import base as _b
    return _b._font(size, cjk)

class S13(Scene):
    DURATION = 80.0
    def frame(self, t, sub=2):
        f = np.ones((H, W, 3), np.float32) * CREAM
        f *= (1 + 0.012 * (PAPER3[:H, :W] if PAPER3.shape[0] >= H else 0))
        T0, D = 2.0, 9.0
        i = int((t - T0) // D)
        if 0 <= i < 8 and t < T0 + 8 * D:
            u = t - T0 - i * D
            lines, shade_, n, wash = PREP[i]
            a_in = ss(u / 1.2) * (1 - ss((u - 8.0) / 1.0))
            pen = ss(u / 2.2)                                   # the pencil draws itself in
            col = ss((u - 2.0) / 2.4)                            # then the colour bleeds in, patch by patch
            m_pen = np.clip((pen * 1.25 - n) * 4, 0, 1)
            m_col = np.clip((col * 1.6 - n * (1 - col * 0.5)) * 4, 0, 1)[..., None]
            card = np.ones((SH, SW, 3), np.float32) * CREAM
            card = card * (1 - (shade_ * m_pen)[..., None] * 0.6)
            card = card * (1 - m_col) + wash * m_col
            card = card * (1 - (lines * m_pen)[..., None] * (1 - 0.7 * m_col) * 0.85) + PENCIL * 0
            x0 = 120 if i % 2 == 0 else W - 120 - SW; y0 = (H - SH) // 2 - 10
            region = f[y0:y0 + SH, x0:x0 + SW]
            # a soft deckled edge
            edge = np.clip(EDGE0 - n * 0.4, 0, 1)[..., None]
            region[:] = region * (1 - edge * a_in) + card * edge * a_in
            ta = ss((u - 1.5) / 1.0) * (1 - ss((u - 7.8) / 1.0))
            txt = text_img(*LINES[i], big=(i == 0))
            tx = x0 + SW + 30 if i % 2 == 0 else 60
            tx = min(max(0, tx), W - txt.shape[1]); ty = H // 2 - 100
            reg = f[ty:ty + txt.shape[0], tx:tx + txt.shape[1]]
            reg[:] = reg * (1 - txt[..., None] * ta) + np.array([0.20, 0.24, 0.32], np.float32) * txt[..., None] * ta
        elif t >= T0 + 8 * D:
            u = t - T0 - 8 * D
            a = ss((u - 0.3) / 1.2) * (1 - ss((u - 4.6) / 1.2))
            txt = text_img("The Fallen Star", "坠落的星星", big=True)
            tx, ty = (W - txt.shape[1]) // 2, H // 2 - 100
            reg = f[ty:ty + txt.shape[0], tx:tx + txt.shape[1]]
            reg[:] = reg * (1 - txt[..., None] * a) + np.array([0.18, 0.5, 0.75], np.float32) * txt[..., None] * a
            for k in range(5):   # a few gold stars around the name
                ang = k / 5 * 6.283 + u * 0.3; X = W / 2 + math.cos(ang) * 420; Y = H / 2 + math.sin(ang) * 170
                cv2.circle(f, (int(X), int(Y)), 5, (0.35, 0.75, 0.95), -1, cv2.LINE_AA)
        fade = min(1.0, t / 1.5, (self.DURATION - t) / 1.5)
        f = f * fade
        return np.clip(f * 255, 0, 255).astype(np.uint8)

SCENE = S13()
MUSIC = [(0, 80, 'warm', 0.8)]
SFX = [(2 + 9 * k + 2.2, 'twinkle', dict(gain=0.25)) for k in range(8)] + [(74.5, 'chime', dict(notes=[1568, 2093, 2637], gain=0.4))]

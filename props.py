# Props painted in code: the rose under its glass dome, little volcanoes, baobab sprouts.
import numpy as np, math
from core import *

def draw_rose(frame, x, y, s=1.0, t=0.0, light=(0.7, -0.6), dome=True, rim='#ffe0b0', sway=1.0, mood=0.0, lean=0.0, talk=0.0):
    """lean: + leans right, - leans back (a huff). talk: petals pulse as she speaks."""
    pad = 30; L = Layer(x - 140 * s - pad, y - 300 * s - pad, 280 * s + 2 * pad, 320 * s + 2 * pad)
    sw = math.sin(t * 1.3) * 2 * sway + lean
    # stem
    stem = [(x, y), (x + 2 * s, y - 60 * s), (x - 3 * s + sw * s, y - 120 * s), (x + sw * 2 * s, y - 170 * s)]
    stroke(L, catmull(stem, closed=False, n=6), '#4f7a3a', 7 * s, 1.0, taper=False)
    for side, yy, ln in ((-1, -70, 46), (1, -105, 40)):   # leaves
        b = np.array([x + side * 2 * s, y + yy * s]); tip = b + [side * ln * s, -ln * (0.5 + 0.45 * mood) * s + math.sin(t * 1.7 + side) * 3 * s]
        n_ = np.array([-(tip - b)[1], (tip - b)[0]]) / (np.linalg.norm(tip - b) + 1e-6)
        P = catmull([b, (b + tip) / 2 + n_ * 12 * s, tip, (b + tip) / 2 - n_ * 10 * s], n=8)
        shade(L, L.mask(P, 0.5), '#5f9346', lit='#9cc76e', shadow='#335a2c', light=light, rim=rim, rim_w=0.4, soft=0.8, tex_amt=0.06, line='#3a4a24', line_w=1.2 * s, line_a=0.6, poly=P)
        stroke(L, [b, (b + tip) / 2 + n_ * 2 * s, tip], '#3f6a30', 1.4 * s, 0.6)
    # bloom: layered petals
    cx, cy = x + sw * 2 * s, y - 190 * s
    pul = 1 + talk * 0.06 * abs(math.sin(t * 10)) + 0.08 * mood
    for k, (ang, rx, ry, dy, c) in enumerate([(-0.5, 34, 26, 6, '#c9455a'), (0.5, 34, 26, 6, '#c9455a'), (0, 36, 30, -4, '#d75466'), (-0.3, 24, 22, -10, '#e56a78'), (0.35, 24, 22, -8, '#e56a78'), (0, 16, 16, -14, '#f08994')]):
        P = ellipse_pts(cx + math.sin(ang) * 18 * s * pul, cy + dy * s, rx * s * pul, ry * s * pul, ang, 40)
        shade(L, L.mask(P, 0.6), c, lit='#ffb3b8', shadow='#8a2238', light=light, rim=rim, rim_w=0.35, soft=0.85, tex_amt=0.05, line='#6a1c2a', line_w=1.2 * s, line_a=0.55, poly=P)
    for k in range(3):
        a0 = 0.6 + k * 1.9; pencil(L, catmull([(cx + math.cos(a0) * 10 * s, cy - 6 * s + math.sin(a0) * 8 * s), (cx, cy - 10 * s), (cx + math.cos(a0 + 1) * 8 * s, cy - 8 * s)], closed=False, n=4), '#7a2234', 1.2 * s, 0.6, light, closed=False)
    composite(frame, L)
    if mood > 0.02: glow(frame, cx, cy, 70 * s, '#ffc0b8', 0.35 * mood)   # a happy little blush of light
    if dome:   # glass dome: faint body, bright reflections, rim at the bottom
        D = Layer(x - 120 * s - pad, y - 320 * s - pad, 240 * s + 2 * pad, 340 * s + 2 * pad)
        body = catmull([(x - 92 * s, y), (x - 96 * s, y - 180 * s), (x - 60 * s, y - 262 * s), (x, y - 280 * s), (x + 60 * s, y - 262 * s), (x + 96 * s, y - 180 * s), (x + 92 * s, y)])
        m = D.mask(body, 1.0)
        D.put(hexc('#e8f2ff'), m * 0.12)
        e = Mask(m.x0, m.y0, m.x1, m.y1, np.clip(m.m - cv2.GaussianBlur(m.m, (0, 0), 6), 0, 1) * 1.6)
        D.put(hexc('#ffffff'), e * 0.5)
        stroke(D, catmull([(x - 70 * s, y - 40 * s), (x - 78 * s, y - 160 * s), (x - 46 * s, y - 236 * s)], closed=False, n=8), '#ffffff', 9 * s, 0.55, blur=2.5)
        stroke(D, catmull([(x + 62 * s, y - 200 * s), (x + 72 * s, y - 150 * s)], closed=False, n=5), '#fff6e0', 5 * s, 0.4, blur=2)
        knob = ellipse_pts(x, y - 284 * s, 12 * s, 9 * s)
        D.put(hexc('#eef6ff'), D.mask(knob, 1) * 0.6)
        base = ellipse_pts(x, y, 94 * s, 10 * s)
        D.put(hexc('#f8fbff'), D.mask(base, 1.5) * 0.25)
        composite(frame, D)

def draw_volcano(frame, x, y, s=1.0, t=0.0, light=(0.7, -0.6), smoke=0.0, rim='#ffd9a0'):
    pad = 20; L = Layer(x - 130 * s - pad, y - 140 * s - pad, 260 * s + 2 * pad, 160 * s + 2 * pad)
    P = catmull([(x - 120 * s, y), (x - 60 * s, y - 70 * s), (x - 34 * s, y - 104 * s), (x + 34 * s, y - 104 * s), (x + 62 * s, y - 72 * s), (x + 120 * s, y)])
    shade(L, L.mask(P, 0.6), '#8f6d5c', lit='#d9a47f', shadow='#4f3a3c', light=light, rim=rim, rim_w=0.5, soft=0.6, tex_amt=0.1, streak=1, line='#4a3028', line_w=1.5 * s, line_a=0.55, poly=P)
    cr = ellipse_pts(x, y - 104 * s, 34 * s, 9 * s)
    shade(L, L.mask(cr, 0.6), '#3a2a2a', lit='#6a4a40', shadow='#1e1416', light=(-light[0], -light[1]), tex_amt=0.05, line='#2a1a18', line_w=1.2 * s, line_a=0.6, poly=cr)
    composite(frame, L)

def draw_sprout(frame, x, y, s=1.0, t=0.0, light=(0.7, -0.6)):
    pad = 10; L = Layer(x - 40 * s - pad, y - 60 * s - pad, 80 * s + 2 * pad, 64 * s + 2 * pad)
    stroke(L, [(x, y), (x + 1 * s, y - 24 * s)], '#5d8a3e', 4 * s, 1, taper=False)
    for side in (-1, 1):
        b = np.array([x, y - 24 * s]); tip = b + [side * 26 * s, -14 * s + math.sin(t * 2 + side) * 2 * s]
        n_ = np.array([-(tip - b)[1], (tip - b)[0]]) / (np.linalg.norm(tip - b) + 1e-6)
        P = catmull([b, (b + tip) / 2 + n_ * 9 * s, tip, (b + tip) / 2 - n_ * 7 * s], n=8)
        shade(L, L.mask(P, 0.5), '#6ea44c', lit='#b2d97c', shadow='#3b6a2e', light=light, soft=0.8, tex_amt=0.05, line='#3a4a24', line_w=1.0 * s, line_a=0.6, poly=P)
    composite(frame, L)

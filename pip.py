# Pip, the little fallen star: a soft, puffy five-pointed star with a face. light 0 (grey) .. 1 (gold, glowing).
import numpy as np, math
from core import *

def star_pts(cx, cy, R, r, rot=0.0, round_=0.35, n=5):
    pts = []
    for i in range(n * 2):
        a = rot - math.pi / 2 + i * math.pi / n
        if i % 2 == 0:   # rounded tip: two points either side
            for da in (-0.09, 0.09): pts.append((cx + math.cos(a + da) * R * 0.97, cy + math.sin(a + da) * R * 0.97))
        else: pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return catmull(pts, n=8)

def draw_pip(frame, x, y, size=60, t=0.0, light=1.0, face='open', laugh=0.0, rot=0.0, squash=0.0, glow_amt=1.0, look=(0, 0), lt=(-0.5, -0.7)):
    pad = 20; R = size
    L = Layer(x - R * 1.4 - pad, y - R * 1.4 - pad, R * 2.8 + 2 * pad, R * 2.8 + 2 * pad)
    br = 1 + math.sin(t * 2.4) * 0.02 + laugh * abs(math.sin(t * 14)) * 0.05
    P = star_pts(x, y, R * br * (1 + squash * 0.3), R * 0.6 * br, rot)
    P[:, 1] = y + (P[:, 1] - y) * (1 - squash)
    gold = (hexc('#f7c548'), hexc('#fff3a6'), hexc('#d98a1e'))
    grey = (hexc('#c9c6c9'), hexc('#efedee'), hexc('#8f8b93'))
    pale = (hexc('#f6e3a0'), hexc('#fff8d8'), hexc('#c9a560'))
    def lerp3(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))
    c = lerp3(grey, pale, ss(light * 2)) if light < 0.5 else lerp3(pale, gold, ss(light * 2 - 1))
    if light > 0.05 and glow_amt > 0: glow(frame, x, y, R * (1.2 + 0.9 * light), '#ffd877', 0.75 * light * glow_amt)
    m = L.mask(P, 0.6)
    shade(L, m, c[0], lit=c[1], shadow=c[2], light=lt, soft=0.95, tex_amt=0.05, edge_dark=0.1, weave=0.05, line='#6a3c1c', line_w=max(1.2, R * 0.05), line_a=0.85, poly=P,
          glow_in='#fff6c8' if light > 0.6 else None)
    k = R / 60
    for sx in (-1, 1):
        L.put(hexc('#f4a08e'), L.mask(ellipse_pts(x + sx * 22 * k, y + 10 * k, 8 * k, 5 * k), 3 * k) * 0.6)
    bk = 1.0
    if face == 'closed' or laugh > 0.5: bk = 0.0
    else:
        bt = (t + 0.7) % 3.9
        if bt < 0.13: bk = 0.0
    for sx in (-1, 1):
        ex, ey = x + sx * 14 * k + look[0] * 2 * k, y - 4 * k + look[1] * 2 * k
        if bk > 0.1:
            E = L.mask(ellipse_pts(ex, ey, 6 * k, 8 * k), 0.4)
            shade(L, E, '#3a2214', lit='#6a4228', shadow='#1a0e08', light=(0.3, 0.9), tex_amt=0.02, edge_dark=0, weave=0)
            L.put(np.array([1, 1, 0.97], np.float32), L.mask(ellipse_pts(ex - 1.8 * k, ey - 3 * k, 2.4 * k, 2.4 * k), 0.4))
        else:
            arc = [(ex - 6 * k, ey + (2 if laugh > 0.5 else 0) * k), (ex, ey - (4 if laugh > 0.5 else -3) * k), (ex + 6 * k, ey + (2 if laugh > 0.5 else 0) * k)]
            pencil(L, catmull(arc, closed=False, n=5), '#3a2214', max(1.4, 2.2 * k), 0.9, lt, closed=False)
    mx, my = x, y + 12 * k
    if laugh > 0.3 or face == 'laugh':
        Mp = catmull([(mx - 7 * k, my - 2 * k), (mx + 7 * k, my - 2 * k), (mx, my + 8 * k)])
        shade(L, L.mask(Mp), '#a2493a', lit='#c86450', light=lt, tex_amt=0.02, edge_dark=0.1, weave=0, line='#4a2414', line_w=1.2 * k, line_a=0.8, poly=Mp)
    elif face == 'sad' or light < 0.3:
        pencil(L, catmull([(mx - 5 * k, my + 3 * k), (mx, my), (mx + 5 * k, my + 3 * k)], closed=False, n=4), '#4a2414', max(1.2, 1.8 * k), 0.9, lt, closed=False)
    else:
        pencil(L, catmull([(mx - 7 * k, my - 1 * k), (mx, my + 4 * k), (mx + 7 * k, my - 1 * k)], closed=False, n=4), '#4a2414', max(1.2, 1.9 * k), 0.9, lt, closed=False)
    composite(frame, L)
    if light > 0.6:  # a few twinkles
        for i in range(4):
            a = t * 0.8 + i * 1.57; rr = R * (1.5 + 0.2 * math.sin(t * 3 + i))
            glow(frame, x + math.cos(a) * rr, y + math.sin(a) * rr, R * 0.08, '#fff2b0', (light - 0.6) * 2 * (0.5 + 0.5 * math.sin(t * 5 + i * 2)))
    return L

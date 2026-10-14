# The pilot: a grown man sitting on his plane's wheel in the desert, 3/4 front view. Painted like the boy.
# Units: ~400 tall when seated, the seat (wheel top) at y=-150, boots at y=0.
import numpy as np, math
from core import *
from rig import Rig

INK = '#4a3020'
SKIN, SKIN_LIT, SKIN_SH = '#efc7a4', '#ffe6d0', '#c98f72'
JACK, JACK_LIT, JACK_SH = '#7c4c2e', '#b47c52', '#43261a'
TROU, TROU_LIT, TROU_SH = '#8a7a5a', '#b9a77e', '#544a34'
CAP, CAP_LIT, CAP_SH = '#6a4026', '#9a6a44', '#3a2214'
SCARF, SCARF_LIT, SCARF_SH = '#efe7d8', '#ffffff', '#b8ab98'
BOOT, BOOT_LIT, BOOT_SH = '#4e3424', '#7a5a42', '#2a1a10'

RIG = Rig([
    ('hips', None, (0, -150)),
    ('chest', 'hips', (0, 0)),
    ('head', 'chest', (4, -168)),
    ('armL', 'chest', (-50, -146)), ('foreL', 'armL', (0, 76)),
    ('armR', 'chest', (54, -146)), ('foreR', 'armR', (0, 76)),
])

def draw_pilot(frame, x, y, s=1.0, flip=1, t=0.0, up=0.0, laugh=0.0, slump=0.0, talk=0.0, blink=None, smile=0.3,
               light=(-0.5, -0.7), rim='#b8c8ff', rim_w=0.45, look=(0.0, 0.0), wind=0.3, arms=None):
    """up: 0 looking ahead .. 1 looking straight up at the sky. slump: shoulders drop (sad). laugh 0..1."""
    ch = laugh * abs(math.sin(t * 2 * math.pi * 3.2)) * (0.6 + 0.4 * math.sin(t * 5))
    breath = math.sin(t * 2 * math.pi / 4.2)
    ang = {'chest': -3 + 6 * slump - 6 * laugh - 2 * ch + 0.6 * breath, 'head': -24 * up + 10 * slump - 10 * laugh - 5 * ch,
           'armL': -22 + 30 * laugh, 'foreL': -26 + 60 * laugh, 'armR': -10 - 22 * laugh, 'foreR': -22 - 50 * laugh}
    if arms: ang.update({k: ang[k] + v for k, v in arms.items()})
    root = (0, 8 * slump + 3 * ch + 0.8 * breath)
    RIG.solve(ang, root)
    pad = 60
    L = Layer(x - 300 * s - pad, y - 600 * s - pad, 640 * s + 2 * pad, 640 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def X(bone, pts):
        P = RIG.X(bone, pts) if bone else np.asarray(pts, np.float32).reshape(-1, 2).copy()
        P[:, 0] *= flip; return P * s + [x, y]
    def part(bone, pts, base, lit, sh, **kw):
        P = X(bone, pts); m = L.mask(P, kw.pop('blur', 0.5))
        kw.setdefault('line', INK); kw.setdefault('line_w', 1.6 * s); kw.setdefault('line_a', 0.7)
        kw.setdefault('rim', rim); kw.setdefault('rim_w', rim_w)
        shade(L, m, base, lit=lit, shadow=sh, light=lt, poly=P, **kw); return P
    def fill(P, color, a=1.0, blur=1.0): L.put(hexc(color), L.mask(P, blur) * a)
    ground_shadow(frame, x + 30 * s * flip, y + 2, 120 * s, 14 * s, 0.45)
    # ---- scarf tail behind, streaming in the night wind
    nk = RIG.X('chest', [(-20, -150)])[0]; pts = []
    for i in range(10):
        u = i / 9
        pts.append(nk + [-14 - u * (20 + 150 * wind) + math.sin(t * 2.6 - u * 4) * 12 * u * wind, u * (160 - 80 * wind) + math.sin(t * 3.3 - u * 5) * 16 * u * wind])
    pts = np.array(pts); d = np.gradient(pts, axis=0); nrm = np.stack([-d[:, 1], d[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6
    wdt = np.linspace(16, 20, 10)[:, None]
    Psc = catmull(np.concatenate([pts + nrm * wdt, (pts - nrm * wdt)[::-1]]), n=6); Psc[:, 0] *= flip; Psc = Psc * s + [x, y]
    shade(L, L.mask(Psc, 0.6), SCARF, lit=SCARF_LIT, shadow=SCARF_SH, light=lt, rim=rim, rim_w=rim_w, streak=2, tex_amt=0.1, line=INK, line_w=1.3 * s, line_a=0.5, poly=Psc)
    # ---- back arm
    part('armL', catmull([(-20, -8), (20, -8), (22, 40), (18, 78), (-18, 80), (-22, 40)]), JACK, JACK_LIT, JACK_SH, soft=0.85, streak=1, tex_amt=0.1)
    part('foreL', catmull([(-18, -4), (18, -4), (19, 50), (16, 72), (-16, 72), (-19, 40)]), JACK, JACK_LIT, JACK_SH, soft=0.85, streak=1, tex_amt=0.1)
    part('foreL', catmull([(-13, 68), (13, 68), (15, 86), (6, 98), (-8, 96), (-14, 84)]), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    # ---- body: leather flight jacket with a fleece collar
    jac = catmull([(-52, -150), (-24, -166), (26, -166), (56, -150), (62, -90), (68, -20), (80, 14), (40, 26), (0, 22), (-50, 18), (-64, -20), (-60, -90)])
    part('chest', jac, JACK, JACK_LIT, JACK_SH, soft=0.9, streak=1, tex_amt=0.12, ao=0.1, spec=0.12)
    pencil(L, X('chest', catmull([(4, -150), (2, -90), (6, -20), (4, 8)], closed=False, n=8)), '#3a2014', 2.0 * s, 0.7, lt, closed=False)
    for yy in (-120, -86, -52):
        part('chest', ellipse_pts(14, yy, 4, 4), '#c9a36a', '#f2d9a0', '#7a5a30', line_a=0.4, line_w=0.8 * s, spec=0.4, rim_w=0)
        part('chest', catmull([(-48, -150), (-20, -174), (24, -174), (52, -150), (34, -132), (0, -126), (-30, -132)]), '#e9dcc4', '#fffaf0', '#b3a184', soft=0.6, tex_amt=0.2, line_a=0.5)
    # ---- legs: thighs forward along the wheel, shins down to the sand (static: he is sitting)
    for k, (hx, kx, by_) in enumerate(((-22, 70, -6), (24, 112, 0))):
        tc = TROU_SH if k == 0 else TROU
        part(None, catmull([(hx - 30, -172), (hx + 20, -178), (kx + 26, -170), (kx + 30, -128), (kx - 16, -122), (hx - 26, -126)]), tc, TROU_LIT, TROU_SH, soft=0.8, streak=2, tex_amt=0.1)
        part(None, catmull([(kx - 16, -150), (kx + 28, -150), (kx + 24, -70), (kx + 20, -26), (kx - 16, -26), (kx - 20, -80)]), tc, TROU_LIT, TROU_SH, soft=0.8, streak=2, tex_amt=0.1)
        part(None, catmull([(kx - 20, -34), (kx + 22, -34), (kx + 24, -10), (kx + 48, -6), (kx + 50, 4 + by_), (kx - 22, 4 + by_)]), BOOT, BOOT_LIT, BOOT_SH, soft=0.85, spec=0.2, tex_amt=0.08)
    # ---- scarf wrap
    part('chest', catmull([(-34, -168), (-10, -184), (22, -184), (40, -166), (30, -150), (0, -146), (-28, -152)]), SCARF, SCARF_LIT, SCARF_SH, streak=2, tex_amt=0.12, soft=0.7)
    # ---- head: aviator cap with flaps and goggles pushed up
    HS = 1.0
    def H(pts): return X('head', np.asarray(pts, np.float32))
    hy = -66; tx = 10
    face = [(-40, hy - 46), (-12, hy - 60), (24, hy - 58), (46, hy - 40), (50, hy - 4), (44, hy + 28), (26, hy + 50), (4, hy + 56), (-18, hy + 48), (-34, hy + 26), (-42, hy - 6)]
    P = H(catmull(face)); shade(L, L.mask(P, 0.5), SKIN, lit=SKIN_LIT, shadow=SKIN_SH, light=lt, rim=rim, rim_w=rim_w, soft=0.9, tex_amt=0.05, edge_dark=0.08, poly=P, line=INK, line_w=1.5 * s, line_a=0.6)
    fill(H(catmull([(-30, hy + 22), (-12, hy + 46), (8, hy + 54), (28, hy + 44), (40, hy + 24), (20, hy + 34), (0, hy + 36), (-18, hy + 30)])), '#a88470', 0.18, 6)   # stubble shadow
    for cx in (-12 + tx, 30 + tx):
        fill(H(ellipse_pts(cx, hy + 18, 9, 5)), '#e79c88', 0.35 + 0.3 * laugh, 5)
    bk = 1.0 if blink is None else blink
    if laugh > 0.5: bk = 0.0
    eyy = hy - 4 - 6 * up
    for ex, sc_ in ((-8 + tx, 0.9), (26 + tx, 1.0)):
        ex += look[0] * 2.5
        if bk > 0.15:
            fill(H(ellipse_pts(ex, eyy, 7 * sc_, 8 * bk + 0.5)), '#fffaf2', 0.85, 0.5)
            fill(H(ellipse_pts(ex + 0.5 + look[0], eyy + 0.5 - 2 * up, 5 * sc_, 6.5 * bk)), '#2e1c12', 0.95, 0.5)
            fill(H(ellipse_pts(ex - 1.5, eyy - 2.5 * bk - 2 * up, 1.8, 1.8)), '#ffffff', 1.0, 0.3)
        else:
            lid = [(ex - 7, eyy + 1), (ex, eyy - 4), (ex + 7, eyy + 1)] if laugh > 0.5 else [(ex - 7, eyy), (ex, eyy + 3), (ex + 7, eyy)]
            pencil(L, H(lid), '#2e1a10', 2.2 * s, 0.9, lt, closed=False)
        br = 4 * slump
        pencil(L, H(catmull([(ex - 9, eyy - 14 + (br if ex < tx else -br * 0.3)), (ex, eyy - 18 - 2 * laugh), (ex + 9, eyy - 15 + (br if ex > tx else -br * 0.3))], closed=False, n=5)), '#3a2416', 2.6 * s, 0.75, lt, closed=False)
    pencil(L, H(catmull([(8 + tx, hy - 2), (13 + tx, hy + 14), (6 + tx, hy + 18)], closed=False, n=5)), '#b07a62', 1.8 * s, 0.8, lt, closed=False)
    mo = talk * abs(math.sin(t * 10)) + laugh * (0.7 + 0.3 * abs(math.sin(t * 13)))
    mx, my = 8 + tx, hy + 32
    if mo > 0.15:
        M = H(catmull([(mx - 13, my - 3), (mx + 13, my - 3), (mx + 8, my + 4 + 10 * mo), (mx - 8, my + 4 + 10 * mo)]))
        shade(L, L.mask(M), '#83382f', lit='#a85048', light=lt, tex_amt=0.02, edge_dark=0.2, line=INK, line_w=1.2 * s, line_a=0.7, poly=M, weave=0)
        fill(H(catmull([(mx - 10, my - 2), (mx + 10, my - 2), (mx + 8, my + 2), (mx - 8, my + 2)])), '#fbf3ea', 0.85, 0.6)
    else:
        c = smile - 0.8 * slump
        pencil(L, H([(mx - 11, my - c * 3), (mx - 4, my + c * 4), (mx + 4, my + c * 4), (mx + 11, my - c * 3)]), '#8a4a3a', 2.0 * s, 0.85, lt, closed=False)
    # cap
    cap = catmull([(-46, hy - 30), (-44, hy - 62), (-16, hy - 86), (24, hy - 86), (50, hy - 64), (54, hy - 30), (40, hy - 40), (10, hy - 48), (-24, hy - 42)])
    P = H(cap); shade(L, L.mask(P, 0.5), CAP, lit=CAP_LIT, shadow=CAP_SH, light=lt, rim=rim, rim_w=rim_w, soft=0.8, tex_amt=0.12, spec=0.25, poly=P, line=INK, line_w=1.5 * s, line_a=0.7)
    for sx in (-1,):   # ear flap (the near one sits behind the face edge)
        fl = catmull([(-46, hy - 30), (-36, hy - 26), (-34, hy + 16), (-42, hy + 26), (-52, hy + 8)])
        P = H(fl); shade(L, L.mask(P, 0.5), CAP, lit=CAP_LIT, shadow=CAP_SH, light=lt, rim=rim, rim_w=rim_w, soft=0.8, tex_amt=0.12, poly=P, line=INK, line_w=1.3 * s, line_a=0.6)
    stroke(L, H(catmull([(-40, hy - 30), (2, hy - 34), (52, hy - 30)], closed=False, n=6)), '#3a2216', 4 * s, 0.7, taper=False)
    for gx in (-6, 30):   # goggles pushed up on the cap
        G = H(ellipse_pts(gx, hy - 62, 15, 11)); shade(L, L.mask(G, 0.5), '#8a6a3a', lit='#d9b878', shadow='#4a3418', light=lt, spec=0.5, poly=G, line=INK, line_w=1.2 * s, line_a=0.6)
        Gl = H(ellipse_pts(gx, hy - 62, 10, 7)); shade(L, L.mask(Gl, 0.5), '#6f8fb4', lit='#d6ecff', shadow='#30445c', light=lt, spec=0.8, poly=Gl)
    stroke(L, H([(-40, hy - 60), (-21, hy - 62)]), '#3a2216', 3 * s, 0.8, taper=False)
    # ---- front arm, hand on the knee
    part('armR', catmull([(-20, -8), (21, -8), (23, 40), (19, 78), (-19, 80), (-22, 40)]), JACK, JACK_LIT, JACK_SH, soft=0.85, streak=1, tex_amt=0.1, spec=0.1)
    part('foreR', catmull([(-18, -4), (19, -4), (20, 50), (17, 72), (-17, 72), (-19, 40)]), JACK, JACK_LIT, JACK_SH, soft=0.85, streak=1, tex_amt=0.1, spec=0.1)
    part('foreR', catmull([(-14, 68), (14, 68), (16, 86), (7, 99), (-8, 97), (-15, 84)]), SKIN, SKIN_LIT, SKIN_SH, soft=0.9)
    composite(frame, L)

def draw_plane(frame, x, y, s=1.0, light=(-0.5, -0.7), rim='#b8c8ff', rim_w=0.4, flip=1, t=0.0):
    """The little crash-landed monoplane, side view, nose to the left, sitting on the sand. (x, y) = the right wheel's contact.
    Returns the seat point (top of the wheel) in screen space."""
    pad = 40; L = Layer(x - 760 * s - pad, y - 420 * s - pad, 1100 * s + 2 * pad, 460 * s + 2 * pad)
    lt = (light[0] * flip, light[1])
    def T(pts): P = np.asarray(pts, np.float32).reshape(-1, 2).copy(); P[:, 0] *= flip; return P * s + [x, y]
    def part(pts, base, lit, sh, **kw):
        P = T(pts); kw.setdefault('line', '#3a2a24'); kw.setdefault('line_w', 1.6 * s); kw.setdefault('line_a', 0.7)
        shade(L, L.mask(P, 0.5), base, lit=lit, shadow=sh, light=lt, poly=P, rim=rim, rim_w=rim_w, **kw); return P
    ground_shadow(frame, x - 220 * s * flip, y + 4, 520 * s, 30 * s, 0.4)
    # far wing (behind the fuselage)
    part(catmull([(-470, -205), (-180, -215), (-150, -190), (-470, -180)]), '#c9b8a0', '#efe2cc', '#8e7c66', soft=0.8, tex_amt=0.1)
    # tail and fuselage
    part(catmull([(140, -250), (260, -330), (300, -330), (290, -250), (240, -210)]), '#b5402e', '#e0705a', '#6e2218', soft=0.8, tex_amt=0.1)
    fus = catmull([(-640, -230), (-600, -282), (-380, -300), (100, -280), (300, -262), (300, -236), (100, -196), (-380, -166), (-600, -176), (-646, -200)])
    part(fus, '#e9dcc2', '#fff6e2', '#a6957c', soft=0.75, tex_amt=0.12, streak=1, spec=0.2, ao=0.2)
    stroke(L, T(catmull([(-600, -224), (-380, -230), (100, -232), (296, -246)], closed=False, n=10)), '#b5402e', 10 * s, 0.9, taper=False)
    for xx in (-470, -300, -120, 60):   # panel lines and rivets
        stroke(L, T([(xx, -292), (xx + 6, -180)]), '#8a7a64', 1.2 * s, 0.5, taper=False)
    part(catmull([(-420, -300), (-370, -336), (-300, -338), (-270, -300)]), '#9fc0d8', '#e8f6ff', '#4e6a80', soft=0.8, spec=0.6, line_a=0.5)   # windscreen
    # cowling and the bent propeller
    part(catmull([(-650, -200), (-640, -270), (-600, -290), (-590, -180)]), '#7a7a80', '#c8c8d0', '#3a3a40', soft=0.8, spec=0.5)
    part(catmull([(-662, -238), (-648, -250), (-640, -236), (-650, -224)]), '#5a4a3a', '#8a7a62', '#2a2018', spec=0.3)
    part(catmull([(-656, -244), (-668, -360), (-650, -372), (-640, -246)]), '#8a6a44', '#c09a6a', '#4a3420', soft=0.85, tex_amt=0.15)
    part(catmull([(-656, -232), (-700, -140), (-690, -126), (-642, -228)]), '#8a6a44', '#c09a6a', '#4a3420', soft=0.85, tex_amt=0.15)
    # near wing
    part(catmull([(-500, -190), (-160, -200), (-110, -170), (-130, -150), (-500, -152)]), '#e3d4ba', '#fff6e2', '#9a8a72', soft=0.75, tex_amt=0.12, spec=0.15)
    stroke(L, T([(-480, -172), (-140, -178)]), '#b5402e', 6 * s, 0.85, taper=False)
    # landing gear: two struts and the wheel (the pilot's seat)
    for (a, b) in (((-360, -168), (-40, -52)), ((-250, -168), (-40, -52))):
        stroke(L, T([a, b]), '#4a4a52', 9 * s, 1.0, taper=False)
    wc = (-40, -50)
    W_ = T(ellipse_pts(wc[0], wc[1], 22, 50)); shade(L, L.mask(W_, 0.5), '#2e2a2a', lit='#6a6464', shadow='#141010', light=lt, spec=0.2, poly=W_, line='#141010', line_w=1.4 * s, line_a=0.7, rim=rim, rim_w=rim_w)
    Hb = T(ellipse_pts(wc[0] - 3, wc[1], 9, 18)); shade(L, L.mask(Hb, 0.5), '#9a9aa4', lit='#e0e0ea', shadow='#4a4a52', light=lt, spec=0.6, poly=Hb)
    composite(frame, L)

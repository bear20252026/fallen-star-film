# Trailer picture: shots from the film with a cinematic grade and slow camera moves, plus painted-gold title cards.
import numpy as np, cv2, subprocess, sys, math, os
from PIL import Image, ImageDraw, ImageFont

FPS = 24; W, H = 1920, 804; OUT_H = 1080; BAR = (OUT_H - H) // 2
SC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'scenes') + '/'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
CJK = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

# segment: kind, args, duration, dissolve-out frames (into next segment)
SEG = [
 ('card', ('On a tiny planet, far away…', '在很远很远的一颗小星球上……'), 2.8, 0),
 ('shot', ('S01', 200, 'in'), 2.6, 10), ('shot', ('S01', 150, 'left'), 2.2, 0),
 ('shot', ('S02', 20, 'in'), 2.6, 10), ('shot', ('S02', 60, 'in'), 2.6, 0),
 ('card', ('one night, a little star fell.', '一个夜晚，一颗小星星坠落了。'), 2.6, 0),
 ('shot', ('S02', 250, 'in'), 2.2, 0), ('shot', ('S03', 88, 'in'), 2.2, 0),
 ('card', ('To bring it home, they must cross the whole sky.', '为了送它回家，他们要穿越整片天空。'), 2.8, 0),
 ('shot', ('S04', 70, 'fast'), 1.6, 0), ('shot', ('S05', 160, 'fast'), 1.6, 0), ('shot', ('S06', 68, 'fast'), 1.6, 0), ('shot', ('S06', 220, 'fast'), 1.6, 0),
 ('shot', ('S07', 130, 'fast'), 1.2, 0), ('shot', ('S07', 150, 'fast'), 1.2, 0), ('shot', ('S08', 120, 'fast'), 1.2, 0), ('shot', ('S09', 100, 'fast'), 1.2, 0),
 ('shot', ('S09', 80, 'fast'), 1.2, 0), ('shot', ('S09', 30, 'fast'), 0.8, 0), ('shot', ('S10', 30, 'fast'), 0.8, 0), ('shot', ('S10', 240, 'fast'), 1.6, 0),
 ('black', (), 0.8, 0),
 ('shot', ('S11', 210, 'in'), 3.0, 10), ('shot', ('S11', 230, 'out'), 2.5, 10), ('shot', ('S12', 200, 'in'), 2.5, 10), ('shot', ('S12', 230, 'in'), 2.4, 0),
 ('title', (), 5.8, 0),
 ('end', (), 4.0, 0),
]

def grade(f):
    x = f.astype(np.float32) / 255.0
    # soft bloom from highlights
    small = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(small.max(axis=2, keepdims=True) - 0.9, 0, 1) * 4 * small
    bloom = cv2.resize(cv2.GaussianBlur(hi, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR)
    x = x + bloom * np.array([1.0, 0.85, 0.65], np.float32) * 0.18   # BGR: warm glow
    # gentle contrast with a soft highlight shoulder (keeps painted skies from clipping)
    x = np.clip(x, 0, 1.2) ** 1.06
    x = 0.48 + (x - 0.48) * 1.10
    x = np.where(x > 0.9, 0.9 + (1 - np.exp(-(x - 0.9) / 0.1)) * 0.1, x)
    # saturation
    l = x.mean(axis=2, keepdims=True); x = l + (x - l) * 1.10
    # split tone: teal shadows, warm highlights (BGR)
    l = np.clip(l, 0, 1)
    x += (1 - l) ** 2 * np.array([0.035, 0.02, -0.01], np.float32) + l ** 2 * np.array([-0.025, 0.005, 0.03], np.float32)
    x = np.clip(x, 0, 1) * VIG
    return x

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.32 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)).clip(0.45, 1)[..., None]
RNG = np.random.default_rng(7)
GRAIN = [cv2.resize(RNG.normal(0, 0.012, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None] for _ in range(8)]

def read_frames(scene, t0, n):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', str(t0), '-i', SC + scene + '.mp4', '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    fr = []
    for _ in range(n):
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        fr.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
    p.wait()
    while len(fr) < n: fr.append(fr[-1])
    return fr

def move(img, u, mode):
    if mode == 'in': s = 1.0 + 0.07 * u; dx = 0; dy = 0
    elif mode == 'out': s = 1.08 - 0.07 * u; dx = 0; dy = 0
    elif mode == 'left': s = 1.07; dx = (u - 0.5) * 60; dy = 0
    else: s = 1.05 + 0.08 * u; dx = 0; dy = -10 * u   # fast push
    M = np.float32([[s, 0, W / 2 * (1 - s) + dx], [0, s, H / 2 * (1 - s) + dy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def font(p, size): return ImageFont.truetype(p, size)

def gold_text(lines, tracking=0.0, glow=1.0):
    """lines: list of (text, fontpath, size, y_center). returns (rgba float BGR, alpha) at W x H"""
    mask = Image.new('L', (W, H), 0); d = ImageDraw.Draw(mask)
    for text, fp, size, yc in lines:
        f = font(fp, size)
        if tracking:
            ws = [d.textlength(c, font=f) for c in text]; tot = sum(ws) + tracking * size * (len(text) - 1)
            x = (W - tot) / 2
            for c, w in zip(text, ws):
                d.text((x, yc), c, font=f, fill=255, anchor='lm'); x += w + tracking * size
        else:
            d.text((W / 2, yc), text, font=f, fill=255, anchor='mm')
    a = np.asarray(mask, np.float32) / 255.0
    grad = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    top = np.array([0.72, 0.90, 0.99], np.float32); bot = np.array([0.30, 0.62, 0.86], np.float32)   # BGR pale gold -> deep gold
    col = top + (bot - top) * ((grad * 3) % 1.0)[..., None] * 0.0
    col = np.broadcast_to(top, (H, W, 3)).copy()
    # local vertical gradient per line band
    for text, fp, size, yc in lines:
        y0, y1 = int(max(0, yc - size * 0.6)), int(min(H, yc + size * 0.6))
        g = np.linspace(0, 1, y1 - y0, dtype=np.float32)[:, None, None]
        col[y0:y1] = top + (bot - top) * g
    gl = cv2.GaussianBlur(a, (0, 0), 14) * 0.9 * glow + cv2.GaussianBlur(a, (0, 0), 40) * 0.5 * glow
    return col, a, gl

class Dust:
    def __init__(self, n=260, seed=3):
        r = np.random.default_rng(seed)
        self.p = r.random((n, 2)) * [W, H]; self.v = (r.random((n, 2)) - 0.5) * [14, 8] + [6, -4]
        self.s = r.random(n) ** 3 * 2.6 + 0.6; self.ph = r.random(n) * 6.28; self.f = 0.6 + r.random(n) * 1.6
    def draw(self, t, amt=1.0):
        im = np.zeros((H // 2, W // 2), np.float32)
        P = (self.p + self.v * t) % [W, H] / 2
        tw = 0.45 + 0.55 * np.sin(self.ph + t * self.f * 3) ** 2
        xi = P[:, 0].astype(int); yi = P[:, 1].astype(int)
        for x, y, s, b in zip(xi, yi, self.s, tw):
            cv2.circle(im, (int(x), int(y)), max(1, int(s / 2 + 0.5)), float(b), -1, cv2.LINE_AA)
        im = cv2.resize(im, (W, H)); im = im * 0.7 + cv2.GaussianBlur(im, (0, 0), 6) * 2.0
        return im[..., None] * np.array([0.55, 0.82, 1.0], np.float32) * amt

DUST = Dust()

def bg_dark(t):
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    base = np.array([0.06, 0.03, 0.02], np.float32) * (1 - g) + np.array([0.02, 0.01, 0.01], np.float32) * g
    return np.broadcast_to(base, (H, W, 3)).copy()

def ease(u): return u * u * (3 - 2 * u)

def card_frames(args, dur, start_t):
    en, zh = args; n = int(round(dur * FPS)); out = []
    col, a, gl = gold_text([(en, SERIF, 64, H / 2 - 30), (zh, CJK, 34, H / 2 + 50)])
    for i in range(n):
        t = i / FPS; u = t / dur
        fi = ease(min(1, t / 0.7)); fo = ease(min(1, (dur - t) / 0.5))
        al = fi * fo
        base = bg_dark(t) + DUST.draw(start_t + t, 0.45)
        shift = int((1 - fi) * 14)
        A = np.roll(a, -shift, 0)[..., None]; G = np.roll(gl, -shift, 0)[..., None]
        x = base + G * np.array([0.25, 0.55, 0.9], np.float32) * 0.5 * al
        x = x * (1 - A * al) + col * A * al
        out.append(np.clip(x * min(1, fo + 0.3) , 0, 1))
    return out

STAR_BG = None
def title_frames(dur, start_t):
    global STAR_BG
    if STAR_BG is None:
        f = read_frames('S11', 100, 1)[0].astype(np.float32) / 255
        STAR_BG = cv2.GaussianBlur(f, (0, 0), 2) * 0.75
    n = int(round(dur * FPS)); out = []
    zh = gold_text([('坠落的星星', CJK, 46, H / 2 + 92)], glow=0.6)
    for i in range(n):
        t = i / FPS
        trk = 0.18 + 0.10 * (t / dur)
        col, a, gl = gold_text([('THE FALLEN STAR', SERIF_B, 120, H / 2 - 20)], tracking=trk, glow=1.3)
        s = 1.04 + 0.04 * t / dur
        M = np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]])
        x = cv2.warpAffine(STAR_BG, M, (W, H)) + DUST.draw(start_t + t, 0.8)
        hit = 0.6  # shooting star arrives
        if t < hit:   # streak from top-right to center
            u = t / hit; px, py = W * (0.95 - 0.45 * u), H * (0.05 + 0.40 * u)
            st = np.zeros((H, W), np.float32)
            for k in range(40):
                q = max(0, u - k * 0.012); qx, qy = W * (0.95 - 0.45 * q), H * (0.05 + 0.40 * q)
                cv2.circle(st, (int(qx), int(qy)), max(1, 6 - k // 8), 1 - k / 40, -1, cv2.LINE_AA)
            st = st + cv2.GaussianBlur(st, (0, 0), 10) * 3
            x = x + st[..., None] * np.array([0.7, 0.92, 1.0], np.float32)
            al = 0.0
        else:
            al = ease(min(1, (t - hit) / 0.35))
            flash = max(0, 1 - (t - hit) / 0.5) ** 2
            x = x + flash * 0.9 * np.exp(-(((xx - W / 2) / 700) ** 2 + ((yy - H / 2) / 300) ** 2))[..., None] * np.array([0.75, 0.92, 1.0], np.float32)
        fo = ease(min(1, (dur - t) / 0.6))
        A = a[..., None] * al
        x = x + gl[..., None] * np.array([0.3, 0.6, 1.0], np.float32) * 0.55 * al
        x = x * (1 - A) + col * A
        zal = ease(np.clip((t - 1.3) / 0.8, 0, 1))
        zA = zh[1][..., None] * zal
        x = x * (1 - zA) + zh[0] * zA + zh[2][..., None] * np.array([0.3, 0.6, 1.0], np.float32) * 0.3 * zal
        out.append(np.clip(x * fo, 0, 1))
    return out

def end_frames(dur, start_t):
    n = int(round(dur * FPS)); out = []
    tag = gold_text([('Every light finds its way home.', SERIF, 58, H / 2 - 50), ('每一束光，都会找到回家的路。', CJK, 32, H / 2 + 20)])
    soon = gold_text([('C O M I N G   S O O N   ·   敬 请 期 待', CJK, 26, H / 2 + 120)], glow=0.5)
    for i in range(n):
        t = i / FPS
        x = bg_dark(t) + DUST.draw(start_t + t, 0.5)
        a1 = ease(min(1, t / 0.8)); a2 = ease(np.clip((t - 1.4) / 0.8, 0, 1)); fo = ease(min(1, (dur - t) / 0.9))
        for (col, a, gl), al in ((tag, a1), (soon, a2)):
            A = a[..., None] * al
            x = x + gl[..., None] * np.array([0.25, 0.55, 0.9], np.float32) * 0.4 * al
            x = x * (1 - A) + col * A
        out.append(np.clip(x * fo, 0, 1))
    return out

def shot_frames(args, dur, extra):
    scene, t0, mode = args; n = int(round(dur * FPS)); tot = n + extra
    src = read_frames(scene, t0, tot); out = []
    fast = mode == 'fast'
    for i, f in enumerate(src):
        u = i / max(1, n - 1)
        x = grade(move(f, min(u, 1.05), mode))
        out.append(x)
    return out

def main(outpath):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{OUT_H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outpath], stdin=subprocess.PIPE)
    canvas = np.zeros((OUT_H, W, 3), np.uint8); fidx = 0
    pending = []   # frames to dissolve into the next segment
    t_now = 0.0
    def emit(x):
        nonlocal fidx
        g = GRAIN[fidx % len(GRAIN)]
        y = np.clip(x + g * (0.6 + 0.4 * x.mean(axis=2, keepdims=True)), 0, 1)
        canvas[BAR:BAR + H] = (y * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(canvas.tobytes()); fidx += 1
    for k, (kind, args, dur, xout) in enumerate(SEG):
        n = int(round(dur * FPS))
        if kind == 'shot': fr = shot_frames(args, dur, xout)
        elif kind == 'card': fr = card_frames(args, dur, t_now)
        elif kind == 'title': fr = title_frames(dur, t_now)
        elif kind == 'end': fr = end_frames(dur, t_now)
        else: fr = [np.zeros((H, W, 3), np.float32)] * n
        # fade shots that touch cards / black
        prev = SEG[k - 1][0] if k else 'black'; nxt = SEG[k + 1][0] if k + 1 < len(SEG) else 'black'
        if kind == 'shot':
            if prev != 'shot':
                for i in range(min(6, n)): fr[i] = fr[i] * ease((i + 1) / 7)
            if nxt != 'shot' and nxt != 'black':
                for i in range(min(6, n)): fr[n - 1 - i] = fr[n - 1 - i] * ease((i + 1) / 7)
        main_fr = fr[:n]; tail = fr[n:]
        for i, f in enumerate(main_fr):
            if i < len(pending):
                w = (i + 1) / (len(pending) + 1); f = pending[i] * (1 - w) + f * w
            emit(f)
        pending = tail; t_now += n / FPS
        print(kind, args[:2] if args else '', f'{t_now:.2f}', flush=True)
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    main(sys.argv[1])

# Trailer score, all synthesized: music-box opening, pulsing build, drum-driven montage, hard stop, emotional swell, title hit, tag.
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'film'))
from audio import Mix, SR, note, bell, pluck, pad, flute, sfx, env_ar
from scipy.signal import fftconvolve, butter, sosfilt

DUR = 59.083
# timeline landmarks (must match render.py)
T_CARD2, T_CARD3, T_FAST, T_STOP, T_SWELL, T_TITLE, T_END = 12.75, 19.75, 22.542, 38.083, 38.875, 49.292, 55.083
FAST_CUTS = [22.542, 24.125, 25.708, 27.292, 28.875, 30.083, 31.292, 32.5, 33.708, 34.917, 35.708, 36.5]

M = Mix(DUR, seed=11); r = M.r
dry = M          # main bus
def tsig(d): return np.arange(int(d * SR)) / SR

def strings(freqs, d, amp, att=0.6, rel=0.8, bright=0.5):
    t = tsig(d); e = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, d - t) / rel)
    s = 0
    for f in freqs:
        for det in (-0.25, 0, 0.21):
            ph = 2 * np.pi * f * (1 + det / 100) * t + 0.002 * np.sin(2 * np.pi * 5.5 * t)
            s = s + sum((bright ** (k - 1)) / k * np.sin(k * ph) for k in range(1, 7))
    return (s * e * amp / (3 * len(freqs))).astype(np.float32)

def choir(freqs, d, amp, att=1.2, rel=1.2):
    t = tsig(d); e = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, d - t) / rel)
    s = 0
    for f in freqs:
        for det in (-0.3, 0.3):
            ph = 2 * np.pi * f * (1 + det / 100) * t + 0.01 * np.sin(2 * np.pi * 4.8 * t)
            # "ah" formants: emphasize harmonics near 700 and 1200 Hz
            s = s + sum(np.exp(-((k * f - 750) / 300) ** 2) * 0.8 + np.exp(-((k * f - 1150) / 300) ** 2) * 0.5 + (0.3 if k == 1 else 0) for k in [1]) * 0 + \
                sum((np.exp(-((k * f - 750) / 350) ** 2) + 0.6 * np.exp(-((k * f - 1150) / 350) ** 2) + 0.15 / k) * np.sin(k * ph) for k in range(1, 12))
    return (s * e * amp / (2 * len(freqs))).astype(np.float32)

def boom(d=3.0, amp=1.0, f0=55):
    t = tsig(d); f = f0 * (1 + 1.5 * np.exp(-t * 12))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 1.2) + M.band(len(t), 180, 0.6) * np.exp(-t * 7) * 0.5 + M.band(len(t), 2500, 1.0) * np.exp(-t * 25) * 0.25
    return (s * amp * np.minimum(1, t * 800)).astype(np.float32)

def tom(f0=90, amp=0.5):
    t = tsig(0.6); f = f0 * (1 + 0.6 * np.exp(-t * 25)); ph = 2 * np.pi * np.cumsum(f) / SR
    return ((np.sin(ph) * np.exp(-t * 7) + M.band(len(t), 400, 0.5) * np.exp(-t * 30) * 0.3) * amp).astype(np.float32)

def riser(d, amp, f0=200, f1=2400):
    t = tsig(d); u = t / d; f = f0 * (f1 / f0) ** (u ** 1.6); ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(np.sin(k * ph) / k for k in range(1, 5))
    noise = M.band(len(t), 3000, 1.4) * u ** 2
    return ((tone * 0.25 + noise * 0.6) * u ** 2.2 * amp).astype(np.float32)

def rev_swell(d, amp):
    t = tsig(d); u = t / d
    return (M.band(len(t), 5000, 1.5) * u ** 3 * amp).astype(np.float32)

# --- 0 - 12.8: music box over a soft pad (D major / lydian flavour)
for t0, ch in [(0.3, [62, 66, 69, 74]), (3.5, [59, 62, 66, 71]), (6.7, [55, 59, 62, 67]), (9.9, [57, 61, 64, 69])]:
    M.add(pad([note(n) for n in ch], 3.8, 0.06, att=1.2, rel=1.5), t0)
    M.add(pluck(note(ch[0] - 24), 3.0, 0.12, 0.3), t0)
motif = [(0, 74), (0.4, 78), (0.8, 81), (1.2, 86), (2.0, 85), (2.4, 81), (3.2, 78), (3.6, 76), (4.4, 74), (4.8, 79), (5.2, 83), (6.4, 81), (6.8, 78), (7.6, 79), (8.0, 76), (8.8, 74), (9.6, 76), (10.0, 78), (10.4, 81), (11.2, 85)]
for dt, m in motif: M.add(bell(note(m + 12), 2.2, 0.07), 0.9 + dt, pan=0.4 + 0.2 * r.random())
sfx(M, 'birds', 3.2, 0.6, n=4)
sfx(M, 'sparkle', 10.0, 1.4)          # Pip glowing in the grass
sfx(M, 'whoosh', 11.3, 0.7, dur=1.5, f=900)

# --- 12.8 - 22.6: turn to minor, a pulse starts and grows
for t0, ch in [(12.8, [59, 62, 66]), (15.2, [55, 59, 62]), (17.6, [50, 54, 57]), (20.0, [57, 61, 64])]:
    M.add(strings([note(n) for n in ch], 2.8, 0.08 + 0.02 * (t0 - 12.8) / 7), t0)
    M.add(pluck(note(ch[0] - 12), 2.4, 0.15, 0.3), t0)
for k in range(int((T_FAST - 13.6) / 0.4)):
    t = 13.6 + k * 0.4; g = 0.04 + 0.08 * (t - 13.6) / 9
    m = [47, 47, 54, 47, 43, 43, 50, 43, 38, 38, 45, 38, 45, 45, 52, 45][(k // 1) % 16]
    M.add(pluck(note(m), 0.4, g, 0.6), t, pan=0.5)
sfx(M, 'twinkle', 13.1, 1.5, m=93)
for m in [86, 90, 93]: M.add(bell(note(m), 2.5, 0.04), 15.0 + (m - 86) * 0.05)
M.add(boom(2.5, 0.25, 50), T_CARD3)   # soft hit on the third card
M.add(rev_swell(1.4, 0.18), T_FAST - 1.4)
M.add(riser(2.4, 0.18, 300, 1800), T_FAST - 2.4)

# --- 22.6 - 38.2: drum-driven montage, hit on every cut
for c in FAST_CUTS:
    M.add(boom(1.8, 0.55, 48), c); M.add(M.band(int(0.5 * SR), 6000, 1.2) * np.exp(-tsig(0.5) * 8) * 0.10, c, pan=0.5)
step = 0.2
n16 = int((T_STOP - T_FAST) / step)
prog = [[50, 57, 62], [46, 53, 58], [43, 50, 55], [45, 52, 57]]   # Dm Bb G A (dorian-ish lift)
for k in range(n16):
    t = T_FAST + k * step; bar = int(k // 16) % 4; ch = prog[bar]; u = k / n16
    m = ch[[0, 1, 2, 1][k % 4]] + 12
    M.add(strings([note(m)], 0.22, 0.05 + 0.04 * u, att=0.01, rel=0.08, bright=0.65), t, pan=0.35 + 0.3 * (k % 2))
    if k % 8 == 0: M.add(tom(70, 0.35 + 0.2 * u), t, pan=0.5)
    if k % 8 == 6: M.add(tom(110, 0.22 + 0.15 * u), t, pan=0.4)
    if k % 4 == 2: M.add(M.band(int(0.12 * SR), 7000, 1.0) * env_ar(int(0.12 * SR), 0.001, 0.03) * (0.04 + 0.04 * u), t, pan=0.65)
    if k % 16 == 0: M.add(strings([note(n) for n in ch], 3.3, 0.10 + 0.06 * u, att=0.3), t)
# brass-like stabs on the bigger moments (moth, meteors)
for c in [28.875, 30.083, 33.708]:
    M.add(strings([note(n) for n in [38, 45, 50, 57]], 0.9, 0.25, att=0.02, rel=0.5, bright=0.8), c)
sfx(M, 'whoosh', 28.2, 1.0, dur=0.8, f=1500); sfx(M, 'whoosh', 31.6, 1.2, dur=1.0, f=700); sfx(M, 'whoosh', 33.0, 1.0, dur=0.8, f=1100)
sfx(M, 'shimmer', 35.0, 1.5, dur=3)
M.add(riser(4.0, 0.35, 150, 3000), T_STOP - 4.0)
M.add(rev_swell(2.0, 0.25), T_STOP - 2.0)
cut = int(T_STOP * SR)   # hard stop: silence the bus from here (tails included)

def finish_first_half():
    M.buf[cut:] = 0
finish_first_half()

# --- 38.2 - 39.0: silence, one breath of a high bell
M.add(bell(note(98), 1.5, 0.05), T_STOP + 0.3, pan=0.6)

# --- 39.0 - 49.4: emotional swell, D major, choir and strings, melody on top
O = -0.125
prog2 = [(38.875, [62, 66, 69], 50), (41.475, [57, 61, 64], 45), (44.075, [59, 62, 66], 47), (46.675, [55, 59, 62, 67], 43)]
for i, (t0, ch, b) in enumerate(prog2):
    g = 0.6 + 0.4 * i / 3
    M.add(choir([note(n) for n in ch], 2.9, 0.10 * g), t0)
    M.add(strings([note(n) for n in ch] + [note(ch[0] + 12)], 2.9, 0.11 * g, att=0.5), t0)
    M.add(strings([note(b - 12), note(b)], 2.9, 0.14 * g, att=0.3, bright=0.4), t0)
    M.add(boom(2.5, 0.18 * g, 45), t0)
mel = [(39.3, 81, 1.0), (40.3, 78, 0.6), (40.9, 76, 0.7), (41.6, 76, 1.2), (42.8, 73, 0.6), (43.4, 74, 0.8), (44.2, 78, 1.0), (45.2, 81, 0.6), (45.8, 83, 0.9), (46.8, 86, 1.4), (48.2, 85, 1.2)]
for t0, m, d in mel:
    t0 += O
    M.add(flute(note(m), d + 0.2, 0.10), t0, pan=0.55)
    M.add(strings([note(m)], d + 0.3, 0.06, att=0.15, rel=0.3, bright=0.6), t0, pan=0.45)
sfx(M, 'sparkle', 39.075, 1.0)
# timpani roll + riser into the title
for k in range(int(2.4 / 0.06)):
    t = T_TITLE - 2.4 + k * 0.06; M.add(tom(62, 0.05 + 0.25 * (k / 40) ** 2), t, pan=0.45 + 0.1 * (k % 2))
M.add(riser(2.2, 0.35, 220, 2600), T_TITLE - 2.2)
M.add(rev_swell(1.2, 0.3), T_TITLE - 1.2)

# --- 49.4: TITLE HIT (the shooting star lands at +0.6)
hit = T_TITLE + 0.6
M.add(riser(0.6, 0.25, 1500, 4000), T_TITLE)
M.add(boom(4.5, 1.0, 38), hit); M.add(boom(3.0, 0.5, 76), hit)
M.add(strings([note(n) for n in [38, 50, 57, 62, 66, 69, 74]], 4.5, 0.32, att=0.02, rel=2.5, bright=0.7), hit)
M.add(choir([note(n) for n in [62, 66, 69, 74]], 4.6, 0.18, att=0.05, rel=2.5), hit)
for k, m in enumerate([86, 90, 93, 98, 102]): M.add(bell(note(m), 3.5, 0.08), hit + k * 0.05, pan=0.3 + 0.1 * k)
sfx(M, 'shimmer', hit + 0.3, 1.6, dur=4)

# --- 55.2 - end: music box returns, last chord, a final twinkle
for dt, m in [(0, 74), (0.4, 78), (0.8, 81), (1.2, 86), (2.0, 85), (2.6, 86)]: M.add(bell(note(m + 12), 2.5, 0.07), T_END + 0.3 + dt, pan=0.5)
M.add(pad([note(n) for n in [62, 66, 69, 74]], 3.9, 0.06, att=0.8, rel=1.8), T_END)
sfx(M, 'twinkle', DUR - 1.2, 1.2, m=98)

# --- reverb on everything, keep the hard stop clean, master
def reverb(x, secs=2.8, mix=0.28):
    n = int(secs * SR); t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = np.random.default_rng(ch + 5).normal(0, 1, n) * np.exp(-t * 6.9 / secs)
        ir = sosfilt(butter(2, 6000, fs=SR, output='sos'), ir); ir /= np.sqrt((ir ** 2).sum())
        out[:, ch] = fftconvolve(x[:, ch], ir)[:len(x)]
    return x * (1 - mix) + out * mix * 1.4

i0, i1 = int(T_SWELL * SR), int((T_TITLE + 0.55) * SR)
M.buf[i0:i1] *= np.linspace(1.5, 1.8, i1 - i0)[:, None]
y = reverb(M.buf)
y[cut:int(T_SWELL * SR)] *= np.linspace(1, 0, int(T_SWELL * SR) - cut)[:, None] ** 4   # let the reverb drop fast in the silence
# gentle compression via soft clip, then fade
y = y / np.abs(y).max() * 1.6; y = np.tanh(y) / np.tanh(1.6)
tt = np.arange(len(y)) / SR; y *= np.minimum(1, (DUR - tt) / 1.0)[:, None]
M.buf = y.astype(np.float32)
M.save(sys.argv[1], peak=0.89)
print('ok')

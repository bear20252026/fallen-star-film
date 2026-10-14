# Music and sound, all made in code. A scene lists MUSIC sections and SFX cues; build() mixes them into a wav.
import numpy as np, wave, math

SR = 48000

def note(m): return 440.0 * 2 ** ((m - 69) / 12)

class Mix:
    def __init__(self, dur, seed=1):
        self.N = int(dur * SR); self.buf = np.zeros((self.N, 2), np.float32); self.r = np.random.default_rng(seed); self.dur = dur
    def add(self, sig, at, gain=1.0, pan=0.5):
        if sig.ndim == 1: sig = np.stack([sig * math.cos(pan * math.pi / 2), sig * math.sin(pan * math.pi / 2)], 1) * 1.41
        i = int(at * SR); j = min(self.N, i + len(sig))
        if j > i and i >= 0: self.buf[i:j] += sig[:j - i] * gain
    def band(self, n, f0, q=0.5):
        sp = np.fft.rfft(self.r.normal(0, 1, n)); fr = np.fft.rfftfreq(n, 1 / SR)
        sp *= np.exp(-((np.log(fr + 1) - np.log(f0)) ** 2) / q); y = np.fft.irfft(sp, n).astype(np.float32)
        return y / (np.abs(y).max() + 1e-9)
    def save(self, path, peak=0.85):
        b = self.buf / max(1e-6, np.abs(self.buf).max()) * peak
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((b * 32767).astype(np.int16).tobytes())

def env_ar(n, a, r):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)); return e * np.exp(-t / max(r, 1e-4))

def bell(f, dur=2.5, amp=0.3):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 1.3), (2.76, .45, 2.6), (5.4, .25, 4), (8.9, .1, 6)])
    return (s * amp * np.minimum(1, t * 400)).astype(np.float32)

def pluck(f, dur=1.6, amp=0.3, bright=0.5):
    t = np.arange(int(dur * SR)) / SR
    s = sum((bright ** (k - 1)) / k * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (2.2 + k * 1.1)) for k in range(1, 7))
    return (s * amp * np.minimum(1, t * 300)).astype(np.float32)

def pad(freqs, dur, amp=0.05, att=1.5, rel=1.5, wob=0.3):
    t = np.arange(int(dur * SR)) / SR; e = np.minimum(1, t / att) * np.minimum(1, np.maximum(0, (dur - t)) / rel)
    s = 0
    for i, f in enumerate(freqs):
        for det in (-0.12, 0.12):
            s = s + np.sin(2 * np.pi * f * (1 + det / 100) * t + wob * np.sin(2 * np.pi * f * 2 * t)) * (1.2 if i == 0 else 1.0)
    return (s * e * amp / len(freqs)).astype(np.float32)

def flute(f, dur, amp=0.12):
    t = np.arange(int(dur * SR)) / SR; vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.4)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    e = np.minimum(1, t / 0.08) * np.minimum(1, np.maximum(0, dur - t) / 0.25)
    return ((np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) * e * amp).astype(np.float32)

# moods: (root midi, scale degrees, chord progression as scale-degree roots, tempo bpm, instrument)
SCALES = {'major': [0, 2, 4, 5, 7, 9, 11], 'minor': [0, 2, 3, 5, 7, 8, 10], 'lydian': [0, 2, 4, 6, 7, 9, 11], 'dorian': [0, 2, 3, 5, 7, 9, 10]}
MOODS = {
    'warm':      (62, 'major', [0, 5, 3, 4], 84, 'pluck'),
    'playful':   (67, 'major', [0, 3, 4, 0, 5, 3, 4, 4], 108, 'pluck'),
    'wonder':    (65, 'lydian', [0, 1, 0, 4], 66, 'bell'),
    'dusk':      (62, 'major', [5, 3, 0, 4], 70, 'bell'),
    'night':     (57, 'minor', [0, 5, 3, 4], 60, 'bell'),
    'sad':       (57, 'minor', [0, 3, 5, 4], 56, 'flute'),
    'adventure': (62, 'dorian', [0, 6, 3, 4], 116, 'pluck'),
    'tense':     (55, 'minor', [0, 1, 0, 5], 92, 'pluck'),
    'triumph':   (62, 'major', [0, 4, 5, 3, 0, 4, 3, 4], 96, 'flute'),
}

def chord_notes(root, scale, deg):
    sc = SCALES[scale]; return [root + sc[(deg + k) % 7] + 12 * ((deg + k) // 7) for k in (0, 2, 4)]

def music(M, t0, t1, mood, gain=1.0, seed=0):
    """A soft score for a section: pad chords, a bass note, and a gentle melody that follows the chords."""
    root, scale, prog, bpm, inst = MOODS[mood]; r = np.random.default_rng(seed)
    beat = 60.0 / bpm; bar = beat * 4; t = t0; k = 0
    sc = SCALES[scale]; last = root + 12
    while t < t1 - 0.5:
        deg = prog[k % len(prog)]; ch = chord_notes(root, scale, deg); d = min(bar * 2, t1 - t)
        fade = min(1, (t - t0) / 3 + 0.2, (t1 - t) / 3 + 0.1)
        M.add(pad([note(n) for n in ch] + [note(ch[0] - 12)], d + 1.2, 0.07 * gain * fade, att=1.2, rel=1.4), t, pan=0.5)
        M.add(pluck(note(ch[0] - 24), 2.5, 0.10 * gain * fade, 0.3), t, pan=0.45)
        # melody: stepwise around chord tones, with rests; phrases of 2 bars
        nb = int(d / beat)
        for b in range(nb):
            if r.random() < (0.55 if inst != 'flute' else 0.4):
                tgt = [n + 12 for n in ch] + [root + 12 + sc[r.integers(0, 7)]]
                cand = min(tgt, key=lambda n: abs(n - last) + r.random() * 3)
                last = cand; tt = t + b * beat + (beat / 2 if r.random() < 0.2 else 0)
                if inst == 'bell': M.add(bell(note(cand + 12), 2.5, 0.05 * gain * fade), tt, pan=0.35 + 0.3 * r.random())
                elif inst == 'pluck': M.add(pluck(note(cand + 12), 1.4, 0.07 * gain * fade, 0.55), tt, pan=0.35 + 0.3 * r.random())
                else: M.add(flute(note(cand), beat * (1 + r.integers(0, 2)), 0.06 * gain * fade), tt, pan=0.55)
        t += d; k += 2

# ---- sound effects
def sfx(M, name, at, gain=1.0, pan=0.5, **kw):
    r = M.r
    if name == 'step':
        n = int(0.09 * SR); M.add(M.band(n, 2400, 0.6) * env_ar(n, 0.002, 0.03) * 0.06 * gain, at, pan=pan)
    elif name == 'hoof':
        n = int(0.06 * SR); M.add(M.band(n, 1500, 0.4) * env_ar(n, 0.001, 0.015) * 0.07 * gain, at, pan=pan)
    elif name == 'whoosh':
        d = kw.get('dur', 1.5); n = int(d * SR); tt = np.arange(n) / SR
        M.add(M.band(n, kw.get('f', 1200), 1.0) * (tt / d) ** 2 * np.minimum(1, (d - tt) * 8) * 0.3 * gain, at, pan=pan)
    elif name == 'chime':
        for k, f in enumerate(kw.get('notes', [1568, 2093, 2637])): M.add(bell(f, 2.0, 0.07 * gain), at + k * 0.06, pan=pan)
    elif name == 'tap':
        M.add(bell(kw.get('f', 880), 0.4, 0.05 * gain), at, pan=pan)
    elif name == 'thump':
        n = int(0.25 * SR); tt = np.arange(n) / SR
        M.add((np.sin(2 * np.pi * (110 - 50 * tt) * tt) * np.exp(-tt * 18) * 0.3 + M.band(n, 300, 0.4) * np.exp(-tt * 30) * 0.1) * gain, at, pan=pan)
    elif name == 'giggle':   # bright bell trills for laughter
        for k in range(kw.get('n', 10)): M.add(bell(note([86, 88, 90, 93][k % 4] + kw.get('shift', 0)), 0.5, 0.035 * gain), at + k * 0.2, pan=0.3 + 0.4 * (k % 2))
    elif name == 'baa':      # a soft cartoon bleat
        d = kw.get('dur', 0.6); tt = np.arange(int(d * SR)) / SR; f0 = kw.get('f', 330)
        f = f0 * (1 + 0.03 * np.sin(2 * np.pi * 18 * tt)) * (1 - 0.1 * tt / d); ph = 2 * np.pi * np.cumsum(f) / SR
        s = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 9)) * np.minimum(1, tt / 0.04) * np.minimum(1, (d - tt) / 0.15)
        M.add((s * 0.07 * gain).astype(np.float32), at, pan=pan)
    elif name == 'sneeze':
        n = int(0.5 * SR); tt = np.arange(n) / SR
        M.add((M.band(n, 600, 0.8) * np.exp(-((tt - 0.12) / 0.06) ** 2) * 0.1 + M.band(n, 3000, 0.6) * np.exp(-((tt - 0.3) / 0.05) ** 2) * 0.25) * gain, at, pan=pan)
    elif name == 'pop':
        n = int(0.12 * SR); tt = np.arange(n) / SR
        M.add((np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt * 40) * 0.25) * gain, at, pan=pan)
    elif name == 'pour':
        d = kw.get('dur', 3.0); n = int(d * SR)
        M.add(M.band(n, 3200, 1.2) * (0.6 + 0.4 * M.band(n, 8, 0.5)) * np.minimum(1, np.arange(n) / SR / 0.3) * np.minimum(1, (d - np.arange(n) / SR) / 0.3) * 0.06 * gain, at, pan=pan)
    elif name == 'sweep':
        d = kw.get('dur', 0.5); n = int(d * SR); tt = np.arange(n) / SR
        M.add(M.band(n, 4000, 0.9) * np.sin(np.pi * tt / d) ** 2 * 0.07 * gain, at, pan=pan)
    elif name == 'birds':
        for k in range(kw.get('n', 6)):
            d = 0.12 + r.random() * 0.1; tt = np.arange(int(d * SR)) / SR; f0 = 2800 + r.random() * 1500
            f = f0 * (1 + 0.25 * np.sin(np.pi * tt / d)); ph = 2 * np.pi * np.cumsum(f) / SR
            M.add((np.sin(ph) * np.sin(np.pi * tt / d) * 0.03 * gain).astype(np.float32), at + k * (0.15 + r.random() * 0.3), pan=r.random())
    elif name == 'wind':
        d = kw.get('dur', 10); n = int(d * SR); tt = np.arange(n) / SR
        M.add(M.band(n, 400, 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * tt)) * np.minimum(1, np.minimum(tt, d - tt) / 2) * 0.05 * gain, at, pan=pan)
    elif name == 'crickets':
        d = kw.get('dur', 10); n = int(d * SR); tt = np.arange(n) / SR
        g = (np.sin(2 * np.pi * 4300 * tt) * (np.sin(2 * np.pi * 30 * tt) > 0.3) * (np.sin(2 * np.pi * 0.8 * tt + 1) > 0)).astype(np.float32)
        M.add(g * np.minimum(1, np.minimum(tt, d - tt) / 2) * 0.01 * gain, at, pan=0.7)
    elif name == 'twinkle':
        M.add(bell(note(kw.get('m', 96)), 1.2, 0.04 * gain), at, pan=pan)
    elif name == 'sparkle':
        for k in range(8): M.add(bell(note(96 + [0, 4, 7, 12, 7, 4, 12, 16][k]), 1.0, 0.03 * gain), at + k * 0.07, pan=0.3 + 0.05 * k)
    elif name == 'shimmer':
        d = kw.get('dur', 3);
        for k in range(int(d * 6)): M.add(bell(note(90 + r.integers(0, 12)), 1.5, 0.015 * gain), at + k / 6 + r.random() * 0.1, pan=r.random())
    elif name == 'clap':
        n = int(0.05 * SR); M.add(M.band(n, 1800, 0.8) * env_ar(n, 0.001, 0.01) * 0.12 * gain, at, pan=pan)

def build(path, dur, music_plan, cues, seed=1):
    M = Mix(dur, seed)
    for i, sec in enumerate(music_plan):
        t0, t1, mood = sec[:3]; g = sec[3] if len(sec) > 3 else 1.0
        music(M, t0, t1, mood, g, seed=seed * 31 + i)
    for c in cues:
        at, name = c[0], c[1]; kw = c[2] if len(c) > 2 else {}
        sfx(M, name, at, **kw)
    tt = np.arange(M.N) / SR; M.buf *= np.minimum(1, np.minimum(tt / 1.0, (dur - tt) / 2.0))[:, None]
    M.save(path)

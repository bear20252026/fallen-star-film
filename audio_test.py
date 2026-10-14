# Sound for the 22 s test: warm pad, soft wind, falling-star whoosh, landing chime, laughing bells.
import numpy as np, wave, sys
SR = 48000; DUR = 22.0; N = int(SR * DUR); rng = np.random.default_rng(5)
mix = np.zeros((N, 2), np.float32); t_all = np.arange(N) / SR
def add(sig, at, gain=1.0, pan=0.5):
    if sig.ndim == 1: sig = np.stack([sig * (1.2 - pan), sig * (0.2 + pan)], 1)
    i = int(at * SR); j = min(N, i + len(sig)); mix[i:j] += sig[:j - i] * gain
def band(n, f0, q=0.5):
    sp = np.fft.rfft(rng.normal(0, 1, n)); fr = np.fft.rfftfreq(n, 1 / SR)
    sp *= np.exp(-((np.log(fr + 1) - np.log(f0)) ** 2) / q); y = np.fft.irfft(sp, n).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9)
def bell(f, dur=3.0, amp=0.3):
    t = np.arange(int(dur * SR)) / SR
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in [(1, 1, 1.3), (2.76, .45, 2.6), (5.4, .25, 4), (8.9, .1, 6)])
    return (s * amp * np.minimum(1, t * 400)).astype(np.float32)
def note(f): return 440 * 2 ** ((f - 69) / 12)
# pad: D major -> B minor -> G major -> A, soft detuned saws through a slow envelope
chords = [(0, [62, 66, 69, 74]), (5.5, [59, 62, 66, 71]), (11, [55, 62, 67, 71]), (16.5, [57, 61, 64, 69])]
for k, (st, ns) in enumerate(chords):
    d = 6.5; t = np.arange(int(d * SR)) / SR; e = np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5)
    s = sum(np.sin(2 * np.pi * note(n) * t + 0.3 * np.sin(2 * np.pi * note(n) * 2 * t)) * (1 if i else 1.3) for i, n in enumerate(ns))
    s += 0.5 * np.sin(2 * np.pi * note(ns[0] - 12) * t)
    add((s * e * 0.05).astype(np.float32), st, pan=0.3 + 0.4 * (k % 2))
# gentle melody on a music-box bell
mel = [(1.0, 74), (1.8, 76), (2.6, 78), (4.0, 81), (6.5, 78), (7.3, 76), (8.1, 74), (12.5, 79), (13.3, 78), (14.1, 76), (15.5, 74), (19.0, 81), (19.5, 83), (20.0, 86)]
for at, n in mel: add(bell(note(n), 2.5, 0.06), at, pan=0.6)
wind = band(N, 500, 1.5) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t_all)); add(wind * 0.035, 0)
# falling star whoosh (9-11 s) panned right to center, landing chime and sparkle
n = int(2.1 * SR); tt = np.arange(n) / SR; w = band(n, 1500, 1.0) * (tt / 2.1) ** 2
for i, p in enumerate(np.linspace(0.95, 0.55, 8)):
    seg = slice(i * n // 8, (i + 1) * n // 8); add(w[seg] * 0.25, 9 + i * 2.1 / 8, pan=p)
for k, f in enumerate([1568, 2093, 2637, 3136]): add(bell(f, 2.0, 0.08), 11.0 + k * 0.06, pan=0.6)
# little bounce taps (Pip's hops land at 11.62, 12.0, 12.22) and the sheep's two hops
for k, at in enumerate((11.62, 12.0, 12.22)): add(bell(880, 0.4, 0.05 * (1 - k * 0.3)), at, pan=0.6)
for at in (11.44, 17.25):
    n2 = int(0.2 * SR); tt2 = np.arange(n2) / SR
    add((np.sin(2 * np.pi * (110 - 50 * tt2) * tt2) * np.exp(-tt2 * 20)).astype(np.float32) * 0.25 + band(n2, 300, 0.4) * np.exp(-tt2 * 30) * 0.08, at, pan=0.45)
# soft footsteps on grass while walking
for k in range(int((7.4 - 2.1) * 1.9)): add(band(int(0.08 * SR), 2500, 0.6) * np.exp(-np.arange(int(0.08 * SR)) / SR * 50) * 0.05, 2.1 + k / 1.9, pan=0.45)
# laughter: quick bright bell trills
for k in range(14): add(bell(note([86, 88, 90, 93][k % 4]), 0.6, 0.04), 17.3 + k * 0.22, pan=0.3 + 0.4 * (k % 2))
fade = np.minimum(1, np.minimum(t_all / 1.0, (DUR - t_all) / 1.5))[:, None]; mix *= fade
mix /= max(1e-6, np.abs(mix).max()) / 0.8
with wave.open(sys.argv[1], 'wb') as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mix * 32767).astype(np.int16).tobytes())

# Film 2 sound kit: builds on film 1's sfx/planet helpers and adds a soft piano, a mood-driven
# underscore (pad + piano arpeggios) and Pip's theme. Everything is synthesized.
import sys, numpy as np
sys.path.insert(0, 'sound')
from sfx import *
from planet import space, wings, flight, step, hop, brass

def piano(f, d=2.5, amp=0.3):
    t = T(d); s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.6 + k * 0.9)) for k, a in [(1, 1), (2, .45), (3, .22), (4, .12), (5, .06)])
    return (s * amp * np.minimum(1, t * 600)).astype(np.float32)

PROG = {
  'warm':  [['C3', 'C4', 'E4', 'G4'], ['A2', 'A3', 'C4', 'E4'], ['F2', 'F3', 'A3', 'C4'], ['G2', 'G3', 'B3', 'D4']],
  'joy':   [['C3', 'C4', 'E4', 'G4'], ['F2', 'F3', 'A3', 'C4'], ['G2', 'G3', 'B3', 'D4'], ['C3', 'C4', 'E4', 'G4']],
  'dusk':  [['F2', 'F3', 'A3', 'E4'], ['C3', 'C4', 'E4', 'G4'], ['D3', 'A3', 'D4', 'F4'], ['A#2', 'A#3', 'D4', 'F4']],
  'night': [['A2', 'A3', 'C4', 'E4'], ['F2', 'F3', 'A3', 'C4'], ['C3', 'C4', 'E4', 'G4'], ['G2', 'G3', 'B3', 'D4']],
  'sad':   [['A2', 'A3', 'C4', 'E4'], ['E2', 'E3', 'G3', 'B3'], ['F2', 'F3', 'A3', 'C4'], ['C3', 'C4', 'E4', 'G4']],
  'tense': [['D2', 'D3', 'F3', 'A3'], ['A#1', 'A#2', 'D3', 'F3'], ['C2', 'C3', 'E3', 'G3'], ['A1', 'A2', 'C#3', 'E3']],
  'wonder':[['D3', 'A3', 'D4', 'F#4'], ['B2', 'B3', 'D4', 'F#4'], ['G2', 'G3', 'B3', 'D4'], ['A2', 'A3', 'C#4', 'E4']],
}
def score(M, at, dur, mood='warm', each=4.0, gain=0.05, arp=True, arp_gain=0.035, beat=None, pan=0.5):
    """underscore: pad chords every `each` s, plus soft piano arpeggios"""
    ch = PROG[mood]; n = int(np.ceil(dur / each)); beat = beat or each / 8
    for i in range(n):
        c = ch[i % len(ch)]; a = at + i * each
        rem = min(each, at + dur - a)
        if rem <= 0: break
        t = T(rem + 1.5); e = ss(t / 1.2) * (1 - ss((t - rem) / 1.5))
        s = sum(np.sin(2 * np.pi * hz(x) * t + 0.3 * np.sin(2 * np.pi * 5 * t)) + 0.25 * np.sin(2 * np.pi * hz(x) * 2.003 * t) for x in c[1:]) / 3
        s += 0.6 * np.sin(2 * np.pi * hz(c[0]) * t)
        M.add((s * e).astype(np.float32), a, gain, pan)
        if arp:
            notes = c[1:] + [c[2][:-1] + str(int(c[2][-1]) + 1)]
            k = 0; x = a
            while x < a + rem - 0.05:
                nn = notes[[0, 1, 2, 3, 2, 1, 0, 1][k % 8]]
                M.add(piano(hz(nn), 2.0, 1.0), x, arp_gain * (0.8 + 0.2 * ((k % 4) == 0)), 0.35 + 0.3 * ((k % 3) / 2))
                k += 1; x += beat

# Pip's theme (a little star tune): rising, a hop, a giggle at the end
PIP = [('G5', 1), ('C6', 1), ('E6', 1), ('D6', 0.5), ('C6', 0.5), ('A5', 1), ('G5', 2), ('E5', 1), ('G5', 1), ('C6', 1), ('D6', 1), ('E6', 2), (None, 1)]
def melody(M, notes, at, beat=0.45, gain=0.06, inst='piano', pan=0.5, transpose=0):
    x = at
    for n, b in notes:
        if n:
            f = hz(n) * 2 ** (transpose / 12)
            M.add(piano(f, 2.4, 1.0) if inst == 'piano' else bell(f, 2.6, 1.0), x, gain, pan)
        x += b * beat
    return x
def chime(M, at, gain=0.05, pan=0.5, n=3, up=True):          # Pip's voice: a tiny run of bells
    notes = ['C7', 'E7', 'G7', 'C8'] if up else ['G7', 'E7', 'C7', 'G6']
    for i in range(n): M.add(bell(hz(notes[i % 4]), 1.6, 0.3), at + i * 0.07, gain, pan)
def giggle(M, at, gain=0.04, pan=0.5, n=7):                  # laughter as tumbling bells
    rs = np.random.RandomState(int(at * 10) % 1000)
    for i in range(n): M.add(bell(hz(['E7', 'G7', 'A7', 'C8', 'D7'][rs.randint(5)]), 1.0, 0.3), at + i * 0.09 + rs.rand() * 0.03, gain, pan + (rs.rand() - 0.5) * 0.3)
def twinkles(M, a, d, rate=1.5, gain=0.01):
    rs = np.random.RandomState(int(a))
    for i in range(int(d * rate)): M.add(bell(hz(['C7', 'E7', 'G7', 'B6', 'D7', 'A7'][i % 6]), 2.0, 0.3), a + rs.rand() * d, gain, rs.rand())
def birdsong(M, a, d, gain=0.02):
    rs = np.random.RandomState(int(a) + 3)
    for i in range(int(d / 2.2)):
        x = a + rs.rand() * d; t = T(0.18); f = 2600 + 1400 * np.sin(np.pi * t / 0.18) + rs.rand() * 600
        M.add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.18) ** 2).astype(np.float32), x, gain, rs.rand())
        M.add((np.sin(2 * np.pi * np.cumsum(f * 1.1) / SR) * np.sin(np.pi * t / 0.18) ** 2).astype(np.float32), x + 0.22, gain * 0.8, rs.rand())
def amb(M, a, d, kind='day', gain=1.0):
    n = int(d * SR)
    if kind == 'day': w = wind(d, 500); M.add(np.stack([w, np.roll(w, 1500)], 1) * env(n, 2, 2)[:, None] * 0.02 * gain, a); birdsong(M, a, d, 0.012 * gain)
    if kind == 'night': w = wind(d, 260); M.add(np.stack([w, np.roll(w, 1800)], 1) * env(n, 2, 2)[:, None] * 0.03 * gain, a); c = crickets(d); M.add(np.stack([c, np.roll(c, 900)], 1) * env(n, 2, 2)[:, None] * 0.012 * gain, a)
    if kind == 'space': space(M, d, 55, 0.04 * gain) if a == 0 else None
    if kind == 'rain': r = band(n, 3500, 2.0) * 0.5 + band(n, 900, 1.0) * 0.3; M.add(np.stack([r, np.roll(r, 2400)], 1) * env(n, 2, 2)[:, None] * 0.05 * gain, a)
def splash():
    t = T(0.3); return band(len(t), 2200, 1.0) * np.exp(-t * 14)
def sneeze():
    t = T(0.6); a = band(len(t), 1500, 1.2) * np.exp(-((t - 0.1) ** 2) / 0.004) * 0.4; b = band(len(t), 3000, 1.0) * np.exp(-((t - 0.32) ** 2) / 0.003)
    return (a + b).astype(np.float32)
def pop():
    t = T(0.25); f = 200 + 900 * np.exp(-t * 20); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)).astype(np.float32)
def swish():
    t = T(0.35); return band(len(t), 1800, 1.0) * np.sin(np.pi * t / 0.35) ** 2
def tick(f=3000):
    t = T(0.04); return band(len(t), f, 0.2) * np.exp(-t * 120)

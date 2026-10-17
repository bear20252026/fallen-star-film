import sys; sys.path.insert(0, 'sound2'); from lib2 import *
D = 300; M = Mix(D)
# rain fades out 190→204
n = int(210 * SR); r = band(n, 3500, 2.0) * 0.5 + band(n, 900, 1.0) * 0.3
e = np.ones(n, np.float32); e[:int(2 * SR)] = np.linspace(0, 1, int(2 * SR)); i0, i1 = int(190 * SR), int(204 * SR); e[i0:i1] = np.linspace(1, 0, i1 - i0); e[i1:] = 0
M.add(np.stack([r * e, np.roll(r * e, 2400)], 1) * 0.06, 0)
for a in np.arange(3, 190, 0.37): M.add(tap(2600 + (a * 97) % 900, 0.05), a, 0.004, (a * 0.37) % 1)
flight(M, 0, 40)
score(M, 0, 50, 'sad', 6, 0.035, beat=0.75, arp_gain=0.02)
score(M, 50, 62, 'night', 6, 0.035, beat=0.75, arp_gain=0.02)
for a in (58, 66, 88): M.add(sniff(), a, 0.04, 0.3); M.add(sniff(), a + 0.5, 0.04, 0.3)
giggle(M, 80, 0.02, 0.6, 8)
# the chase: bouncy
score(M, 112, 74, 'joy', 3, 0.04, beat=0.375, arp_gain=0.03)
for a in np.arange(117, 184, 0.25 * 2): M.add(hop(), a, 0.008, 0.5)
giggle(M, 126, 0.02, 0.6, 10); giggle(M, 150, 0.03, 0.4, 12); giggle(M, 160, 0.03, 0.4, 12); giggle(M, 172, 0.03, 0.6, 12)
# the sun: a swell; Pip blazes
pad([['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4'], ['A3', 'C4', 'E4', 'A4'], ['G3', 'D4', 'G4', 'B4']], 190, 6, 0.06, M)
twinkles(M, 200, 20, 4, 0.012); chime(M, 205, 0.05, 0.75, 4)
melody(M, PIP, 214, 0.5, 0.055, 'bell')
amb(M, 204, 96, 'day', 0.7)
score(M, 226, 74, 'warm', 4, 0.04, beat=0.5)
giggle(M, 250, 0.025, 0.3, 8); flight(M, 256, 40)
melody(M, PIP, 270, 0.45, 0.05)
M.write(sys.argv[1], 2.0, 2.5)
print('ok')

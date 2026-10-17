import sys; sys.path.insert(0, 'sound2'); from lib2 import *
D = 300; M = Mix(D)
space(M, D, 55, 0.04)
M.add(wings(44, 2.2), 0, 0.06, 0.5)
score(M, 0, 44, 'joy', 4, 0.04, beat=0.5)
giggle(M, 5, 0.03, 0.6, 10)
score(M, 44, 26, 'tense', 6, 0.035, arp=False)
# the stone river: low rumble, whooshes of passing rocks
w = wind(70, 90); M.add(np.stack([w, np.roll(w, 3000)], 1) * env(len(w), 6, 6)[:, None] * 0.06, 52)
for a in np.arange(56, 118, 2.3): M.add(swish(), a, 0.05, 0.2 + 0.6 * ((a * 7) % 1))
for a in np.arange(58, 116, 3.1): M.add(thump(70 + (a * 13) % 40), a, 0.05, 0.5)
score(M, 70, 40, 'tense', 4, 0.04, beat=0.4, arp_gain=0.02)
M.add(wings(56, 3.2), 70, 0.07, 0.5)
M.add(thump(45), 111.6, 0.2, 0.5); M.add(thump(60), 111.8, 0.15, 0.4); M.add(swish(), 110.5, 0.12, 0.8)
# silence, then sadness
score(M, 120, 56, 'sad', 8, 0.035, beat=2, arp_gain=0.012)
M.add(bell(hz('A5'), 4, 0.3), 136, 0.012, 0.6); M.add(bell(hz('E5'), 4, 0.3), 142, 0.012, 0.6)
# memories: laughing through tears
score(M, 176, 50, 'wonder', 6, 0.035, beat=1)
for a in (185.5, 204, 222): giggle(M, a, 0.025, 0.55, 8); chime(M, a + 0.6, 0.03, 0.6, 2)
for a in (224, 226, 228): giggle(M, a, 0.03, 0.5, 12)
# Pip wakes up
chime(M, 252, 0.05, 0.6, 4); giggle(M, 258, 0.04, 0.6, 14)
pad([['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4'], ['G3', 'D4', 'G4', 'B4'], ['C4', 'E4', 'G4', 'C5']], 252, 6, 0.06, M)
melody(M, PIP, 262, 0.45, 0.05, 'bell')
score(M, 262, 38, 'joy', 4, 0.04, beat=0.5)
twinkles(M, 274, 26, 3, 0.012)
M.write(sys.argv[1], 2.0, 2.5)
print('ok')

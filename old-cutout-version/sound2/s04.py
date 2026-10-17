import sys; sys.path.insert(0, 'sound2'); from lib2 import *
D = 300; M = Mix(D)
space(M, D, 55, 0.035)
flight(M, 0, 60); flight(M, 60, 60); flight(M, 120, 80); flight(M, 200, 62); flight(M, 262, 38)
score(M, 0, 58, 'night', 7, 0.035, beat=1.75, arp_gain=0.018)
score(M, 58, 70, 'sad', 7, 0.04, beat=1.75, arp_gain=0.02)
for a in np.arange(80, 128, 8): M.add(bell(hz('E6'), 2.5, 0.3), a, 0.008, 0.7)
# the dance: a silly bouncy tune (bassoon-ish = brass low)
from lib2 import brass
x = 134
for n, b in [('C3', 1), ('G2', 1), ('C3', 1), ('G2', 1), ('E3', 1), ('D3', 1), ('C3', 2)] * 3:
    M.add(brass(n, b * 0.36 * 1.1), x, 0.05, 0.3); x += b * 0.36
for a in np.arange(134.2, 160, 0.72): M.add(bell(hz('G6'), 0.4, 0.3), a, 0.012, 0.3)
for a in np.arange(140, 160, 1.4): M.add(swish(), a, 0.025, 0.3)
M.add(pop(), 162.5, 0.03, 0.5)   # the boy's snort
giggle(M, 164, 0.03, 0.5, 14); giggle(M, 168, 0.03, 0.55, 14); giggle(M, 172, 0.025, 0.5, 10)
pad([['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4']], 168, 6, 0.06, M); twinkles(M, 168, 14, 5, 0.015); chime(M, 170, 0.04, 0.75, 4)
score(M, 186, 36, 'wonder', 6, 0.035, beat=0.75)
giggle(M, 221.5, 0.03, 0.4, 12); chime(M, 223, 0.04, 0.75, 4); twinkles(M, 222, 8, 4, 0.012)
score(M, 236, 64, 'joy', 4, 0.045, beat=0.5)
melody(M, PIP, 240, 0.42, 0.05); melody(M, PIP, 266, 0.42, 0.05, 'bell')
giggle(M, 241, 0.03, 0.5, 14); giggle(M, 246, 0.025, 0.5, 10); giggle(M, 252, 0.025, 0.5, 10)
twinkles(M, 240, 60, 2, 0.01)
M.write(sys.argv[1], 2.0, 2.5)
print('ok')

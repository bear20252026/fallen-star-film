import sys; sys.path.insert(0, 'sound2'); from lib2 import *
D = 300; M = Mix(D)
# ticking everywhere until the gear stops at 144.5; then silence; ticking comes back gently at the end
rs = np.random.RandomState(5)
for k in range(7):
    per = 0.5 + 0.13 * k; a0 = rs.rand() * per
    for x in np.arange(a0 + 2, 144.5, per): M.add(tick(2200 + 500 * k), x, 0.012 if k else 0.02, (k / 6))
for x in np.arange(150, 300, 1.0): pass
flight(M, 0, 36)
w = wind(D, 420); M.add(np.stack([w, np.roll(w, 1500)], 1) * env(len(w), 2, 2)[:, None] * 0.015, 0)
score(M, 0, 40, 'warm', 5, 0.035, beat=0.62)
# the busy clockmaker's tune: quick staccato
x = 40
while x < 108:
    for n in ['C5', 'E5', 'G5', 'E5', 'D5', 'F5', 'A5', 'F5']:
        M.add(piano(hz(n), 0.4, 1.0), x, 0.03, 0.4); x += 0.2
for a in np.arange(46, 108, 6.0): M.add(clank(1400, 0.5), a + 0.1, 0.02, 0.55)
score(M, 108, 36, 'joy', 3, 0.03, beat=0.375)
for a in np.arange(126, 144, 2): M.add(step(), a, 0.02, 0.6)
M.add(clank(900, 1.2), 144.5, 0.08, 0.7); M.add(thump(90), 144.6, 0.12, 0.7)
# silence… then the sunset
pad([['F3', 'A3', 'C4', 'E4']], 168, 8, 0.03, M)
score(M, 180, 22, 'dusk', 5.5, 0.045, beat=0.7)
giggle(M, 202, 0.03, 0.6, 14); giggle(M, 206, 0.03, 0.5, 14); giggle(M, 210, 0.025, 0.45, 12); chime(M, 204, 0.04, 0.4, 4)
twinkles(M, 203, 18, 3, 0.012)
score(M, 202, 60, 'joy', 4, 0.04, beat=0.5)
for x in np.arange(226, 300, 0.75): M.add(tick(2600), x, 0.006, 0.7)
M.add(bell(hz('E7'), 2, 0.3), 252.5, 0.02, 0.5)
flight(M, 258, 40); melody(M, PIP, 266, 0.45, 0.05)
pad([['C4', 'E4', 'G4', 'C5'], ['F3', 'A3', 'C4', 'F4'], ['G3', 'D4', 'G4', 'B4'], ['C4', 'E4', 'G4', 'C5']], 262, 9, 0.045, M)
M.write(sys.argv[1], 2.0, 2.5)
print('ok')

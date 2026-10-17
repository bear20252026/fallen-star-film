import sys; sys.path.insert(0, 'sound2'); from lib2 import *
D = 300; M = Mix(D)
space(M, D, 55, 0.035)
flight(M, 0, 60); flight(M, 60, 62); flight(M, 122, 20)
score(M, 0, 62, 'night', 7, 0.04, beat=0.875, arp_gain=0.022)
melody(M, PIP, 30, 0.6, 0.035, 'bell')
# the shadow
score(M, 62, 60, 'tense', 6, 0.045, arp=False)
for a in (72, 98): M.add(whoosh(3.5, True, 220), a - 1.2, 0.2, 0.2); M.add(whoosh(3, False, 220), a + 1.6, 0.2, 0.8); M.add(wings(4, 1.6), a, 0.12, 0.5)
for a in np.arange(76, 120, 0.5): M.add(wings(1.0, 9), a, 0.015, (a * 0.3) % 1)
# the grab
score(M, 122, 60, 'tense', 4, 0.05, arp=True, beat=0.25, arp_gain=0.02)
M.add(wings(20, 1.8), 126, 0.12, 0.6); M.add(whoosh(4, True, 260), 132, 0.2, 0.6)
M.add(boom(2.5), 137, 0.15, 0.5); chime(M, 137.2, 0.05, 0.6, 4, False)
for a in np.arange(139, 150, 0.15): M.add(wings(1.0, 12), a, 0.012, (a * 0.7) % 1)
M.add(whoosh(6, False, 300), 140, 0.15, 0.85)
# alone
score(M, 182, 60, 'sad', 7, 0.045, beat=1.75, arp_gain=0.02)
M.add(thump(100), 198, 0.1, 0.45); M.add(thump(140), 200, 0.08, 0.55)
score(M, 242, 58, 'wonder', 6, 0.045, beat=0.75)
flight(M, 276, 24)
pad([['D4', 'F#4', 'A4', 'D5']], 282, 8, 0.05, M)
M.write(sys.argv[1], 2.0, 2.5)
print('ok')

# The acted performance of the B612 test scene (shared by the shot scripts).
import math, numpy as np
from motion import travel, keys
from boy_anim import BoyAnim
from sheep_anim import SheepAnim
from bg import paint_b612
FPS = 24; DUR = 22.0
SKY, CLOUDS, GROUND, GA, gy, SUN = paint_b612(layers=True)
ROSE = (1440, gy(1440) + 40)
LAND = (1770.0, gy(1770) + 60.0)
# ---------------- the performance ----------------
boy_path = lambda t: travel(t, 1.8, 7.4, 1020.0, 1300.0, 0.8, 1.0)
BOY = BoyAnim(boy_path, k=1.6, t_end=DUR,
    poses={'chest': [(7.6, 0), (8.2, 6), (8.95, 6), (9.3, -2), (11.0, -2), (11.15, -6), (11.8, 0), (12.0, 0), (12.4, 5), (13.6, 5), (14.2, 1)],
           'armR': [(7.7, 0), (8.3, -32), (8.95, -30), (9.4, 0), (11.0, 0), (11.12, -40), (11.9, -8), (12.1, -8), (12.5, -30), (13.6, -28), (14.3, 0)],
           'foreR': [(7.7, 0), (8.3, -18), (8.95, -18), (9.4, 0), (11.0, 0), (11.12, -30), (11.9, 0), (12.1, 0), (12.5, -26), (13.6, -24), (14.3, 0)],
           'armL': [(11.0, 0), (11.12, 34), (11.9, 4)], 'foreL': [(11.0, 0), (11.12, 24), (11.9, 0)]},
    crouch=[(10.95, 0), (11.1, 12), (11.6, 2), (12.0, 0)],
    lookup=[(0, 0), (8.9, -0.1), (9.0, -0.1), (9.25, 0.9), (10.2, 0.6), (10.9, 0.0), (11.1, -0.2), (12.0, -0.25), (16.0, -0.25), (17.0, 0.1)],
    look_x=[(0, 0.4), (8.9, 0.4), (9.25, 0.9), (10.4, 0.8), (11.0, 0.7), (17.0, 0.6), (17.5, 0.0)],
    laugh=[(17.3, 0), (17.7, 1), (20.6, 1), (21.6, 0.3)],
    talk=[(12.15, 0), (12.25, 1), (13.4, 1), (13.5, 0)],
    brows=[(10.95, 0), (11.1, 1), (12.6, 0.4), (13.6, 0.4), (14.5, 0)],
    mouth=[(11.05, 11.9, 'open')])
def sheep_path(t):
    if t < 13.2: return travel(t, 2.8, 8.4, 740.0, 1150.0, 0.9, 1.1)
    if t < 16.7: return travel(t, 13.2, 15.4, 1150.0, 1630.0, 0.5, 0.8)
    return travel(t, 16.75, 17.25, 1630.0, 1570.0, 0.15, 0.25)
SHEEP = SheepAnim(sheep_path, k=1.6, t_end=DUR,
    sniff=[(0, 1), (2.4, 1), (2.7, 0), (15.3, 0), (15.6, 0.7), (16.5, 0.7), (16.65, -0.6), (17.3, 0)],
    head=[(0, 0), (10.9, 0), (11.05, -14), (11.6, -4), (13.0, 0)],
    hop=[(11.12, 0.32, 26), (16.75, 0.5, 46)],
    look=[(0, (0, 1)), (2.4, (0, 1)), (2.8, (0, 0)), (11.0, (0, -1)), (12.0, (0, 0))],
    laugh=[(17.2, 0), (17.5, 1), (20.6, 1), (21.6, 0.2)],
    tail=[(0, 0)], mouth=[(16.7, 17.3, 'open')])

def pip_state(t):
    """Fall along a gentle arc, then bounce with real decaying hops; squash on contacts, stretch when fast."""
    if t < 9.0: return None
    if t < 11.0:
        u = ((t - 9.0) / 2.0) ** 1.35
        x = 2650 + (LAND[0] - 2650) * u; y = 140 + (LAND[1] - 140) * (u ** 1.15)
        return x, y, -0.22, (t - 9) * 7.0, 0.0
    hops = [(0.62, 48), (0.38, 18), (0.22, 6)]; tt = t - 11.0; x = LAND[0]
    sq = 0.0
    for d, h in hops:
        if tt < d:
            u = tt / d; y = LAND[1] - 4 * h * u * (1 - u)
            sq = 0.3 * h / 48 * math.exp(-tt * 30) - 0.12 * h / 48 * math.sin(math.pi * u)
            return x, y, sq, 0.6 * math.sin(tt * 20) * h / 48, 1.0
        tt -= d
    sq = 0.08 * math.exp(-tt * 12) * math.cos(tt * 25)
    return x, LAND[1], sq, 0.0, 1.0


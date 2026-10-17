// S01 — MORNING ON B612 (5:00). A happy ordinary day: watering the rose, a sneeze, pulling baobab
// sprouts, sweeping a volcano. At dusk the boy points out one star: a friend on Earth laughs at it. TITLE.
import { makeScene, track, ss, env, clamp, stars, birds, glowDot, sparkles, svg, rnd, flareStar } from './kit.js';
import { BOY, SHEEP, CAN, SPROUT, puffEl } from './common.js';

const D = 300;
const FRIEND = { x: 1880, y: 250 };   // the friend's star in the dusk sky (B2)

const subs = [
  [60.5, 64.0, 'Careful. I am very delicate.', '小心点，我很娇贵的。', 'it'],
  [69.5, 72.0, 'Bless you!', '长命百岁！'],
  [118.0, 121.6, 'Good sheep! Three before breakfast.', '好羊！早饭前就拔了三棵。'],
  [166.0, 169.0, 'You look like a little chimney sweep.', '你像个小小的扫烟囱工。'],
  [236.0, 239.6, 'That one belongs to a friend of mine.', '那颗星星属于我的一个朋友。'],
  [241.0, 244.6, 'He lives far away, on Earth.', '他住在很远的地方，在地球上。'],
  [246.0, 250.0, 'Every night he looks at it… and he laughs.', '每天晚上他看着它……然后就笑了。'],
  [262.0, 265.0, 'Goodnight, little star.', '晚安，小星星。'],
];

// the sky's birds: a loose V crossing the frame
const flock = (t, t0, x0, y0, dir = 1, n = 5, s = 0.8) => Array.from({ length: n }, (_, i) => {
  const u = t - t0;
  return { x: x0 + dir * u * 160 - dir * Math.abs(i - 2) * 70, y: y0 + Math.abs(i - 2) * 40 + Math.sin(u * 1.3 + i) * 10, s, op: clamp(u / 2) };
});

const shots = [
  // 1. Morning. Down from the sky onto the little planet; birds cross.
  { t0: 0, t1: 24, xf: 0, plate: 'B1_b612_day',
    cam: [[0, { x: 1440, y: 330, z: 1.25 }], [16, { x: 1440, y: 600, z: 1.0 }], [24, { x: 1380, y: 620, z: 1.04 }]],
    init(c) { c.b = birds(c.fxw, 5); },
    draw(t, c) { c.b(t, flock(t, 2, 600, 250, 1, 5, 0.7)); } },

  // 2. The boy walks in with his watering can; the sheep trots behind. He waters the rose.
  { t0: 24, t1: 74, xf: 1.2, plate: 'B1_b612_day',
    cam: [[24, { x: 820, y: 720, z: 1.5 }], [44, { x: 1000, y: 680, z: 1.6 }], [58, { x: 1060, y: 660, z: 1.9 }], [66, { x: 1060, y: 660, z: 1.9 }], [74, { x: 1040, y: 680, z: 1.7 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, track: [[24, { x: 320, y: 840, walk: 1, armR: 10 }], [44, { x: 900, y: 790, walk: 1 }], [45.5, { walk: 0 }],
        [50, { armR: 10, rot: 0 }], [52, { armR: -55, rot: -3 }], [58, { armR: -55, rot: -3 }], [59.5, { armR: 5, rot: 0 }]] },
      can: { h: 1, z: 4, init: CAN, k: 0.75, track: [[24, { x: 400, y: 760, rot: 0 }], [44, { x: 975, y: 712 }], [50, { x: 975, y: 712, rot: 0 }], [52, { x: 1010, y: 640, rot: -30 }], [58, { x: 1010, y: 640, rot: -30 }], [59.5, { x: 975, y: 712, rot: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 2, flip: -1, track: [[24, { x: 100, y: 860, walk: 1, flip: -1 }], [46, { x: 770, y: 820, walk: 1, flip: -1 }], [47, { walk: 0 }],
        [62, { x: 770, y: 820, flip: -1, head: 0 }], [64, { x: 980, y: 800, walk: 1, flip: 1 }], [65.5, { walk: 0, head: 0 }],
        [67.6, { head: -8, face: 'open' }], [68.2, { head: 14, face: 'closed', x: 985 }], [68.5, { head: 14 }], [69, { head: 0, face: 'open', x: 1000 }]] },
    },
    init(c) {
      c.drops = Array.from({ length: 26 }, (_, i) => svg(c.fxw, 'ellipse', { rx: 4, ry: 7, fill: '#bfe1ef', stroke: '#5b7f95', 'stroke-width': 1.2 }));
      c.pollen = sparkles(c.fxw, 18, '#ffe7a8', 5);
    },
    draw(t, c) {
      const on = env(t, 52, 58.5, 0.4, 0.4);
      c.drops.forEach((d, i) => {
        const u = ((t * 1.4 + i / 26) % 1);
        d.setAttribute('cx', (930 + 10 - u * 30 - 70).toFixed(1)); d.setAttribute('cy', (602 + u * u * 150).toFixed(1));
        d.setAttribute('opacity', (on * (1 - u)).toFixed(3));
      });
      c.pollen(t, 1030, 690, env(t, 67.6, 70, 0.2, 1.2), 90);
    } },

  // 3. Pulling baobab sprouts. The third one is stubborn; the sheep lands on its bottom.
  { t0: 74, t1: 128, xf: 1.4, plate: 'B1_b612_day',
    cam: [[74, { x: 1650, y: 840, z: 1.55 }], [96, { x: 1700, y: 850, z: 1.6 }], [104, { x: 1760, y: 860, z: 1.9 }], [114, { x: 1720, y: 850, z: 1.75 }], [128, { x: 1680, y: 840, z: 1.6 }]],
    actors: {
      sp1: { h: 1, z: 1, init: SPROUT, k: 0.8, track: [[74, { x: 1460, y: 960, rot: 0, op: 1 }], [79, { x: 1460, y: 960 }], [80, { x: 1430, y: 880, rot: -40 }], [81.5, { x: 1360, y: 990, rot: -160, op: 0 }]] },
      sp2: { h: 1, z: 1, init: SPROUT, k: 0.8, track: [[74, { x: 1640, y: 935, rot: 0, op: 1 }], [88, { x: 1640, y: 935 }], [89, { x: 1610, y: 860, rot: 30 }], [90.5, { x: 1540, y: 980, rot: 200, op: 0 }]] },
      sp3: { h: 1, z: 1, init: SPROUT, k: 0.95, track: [[74, { x: 1860, y: 960, rot: 0 }], [98, { rot: 0 }], [99, { rot: 8 }], [100, { rot: -6 }], [101, { rot: 10 }], [102, { rot: -4 }], [104.6, { x: 1860, y: 960, rot: 12 }], [105, { x: 1880, y: 900, rot: 40 }], [106.4, { x: 1960, y: 1040, rot: 150 }], [107, { op: 1 }], [109, { op: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, track: [
        [74, { x: 1530, y: 970, flip: 1, head: 0 }], [77, { x: 1500, y: 968, walk: 1 }], [78, { walk: 0, head: 12 }], [79.5, { head: -18, x: 1520 }], [81, { head: 0 }],
        [84, { x: 1530, y: 968, flip: 1 }], [86, { x: 1690, y: 950, walk: 1, flip: -1 }], [87, { walk: 0, flip: -1, head: 12 }], [88.8, { head: -18, x: 1700 }], [90.5, { head: 0, face: 'laughing', laugh: 1 }], [92, { laugh: 0, face: 'open' }],
        [94, { x: 1700, y: 950, flip: -1 }], [96.5, { x: 1910, y: 972, walk: 1, flip: 1 }], [97.5, { walk: 0, head: 14 }],
        [99, { head: 18, rot: 4, x: 1915 }], [100, { head: 22, rot: -3, x: 1918 }], [101, { rot: 5, x: 1920 }], [102, { rot: -2, x: 1922 }], [104.6, { head: 24, rot: 4, x: 1925 }],
        [105.4, { x: 2040, y: 980, rot: 38, head: -10, face: 'closed' }], [106.2, { x: 2080, y: 990, rot: 26 }], [108, { x: 2080, y: 990, rot: 18, face: 'closed' }],
        [110, { rot: 0, face: 'laughing', laugh: 1 }], [116, { laugh: 0, face: 'open', rot: 0 }]] },
      boy: { char: 'C6', h: BOY, z: 2, poses: ['laughing'], track: [[74, { x: 1250, y: 940, op: 0, pose: 'rig' }], [92, { op: 0 }], [93, { op: 1, x: 1270 }],
        [96, { x: 1380, y: 935, walk: 1, pose: 'rig' }], [97.5, { walk: 0 }], [106.5, { pose: 'laughing' }], [116, { pose: 'rig', talk: 1, armR: -20 }], [122, { talk: 0, armR: 0 }]] },
    },
    init(c) { c.dust = puffEl(c.fxw, 12, '#b49a74'); },
    draw(t, c) { c.dust(t, 2060, 990, clamp((t - 105.3) / 1.6), 40); } },

  // 4. Sweeping a volcano: the sheep backs in with its tail as a duster, a puff of soot, a grey sheep.
  { t0: 128, t1: 182, xf: 1.4, plate: 'B1_b612_day',
    cam: [[128, { x: 2200, y: 760, z: 1.55 }], [150, { x: 2220, y: 780, z: 1.7 }], [160, { x: 2200, y: 800, z: 2.0 }], [172, { x: 2160, y: 800, z: 1.8 }], [182, { x: 2120, y: 790, z: 1.7 }]],
    actors: {
      sheep: { char: 'C5', h: SHEEP, z: 3, track: [[128, { x: 1900, y: 860, flip: 1 }], [134, { x: 2120, y: 800, walk: 1, flip: 1 }], [135, { walk: 0, flip: 1 }],
        [138, { x: 2150, y: 825, walk: 0.6, flip: -1 }], [140, { x: 2170, y: 825, flip: -1, walk: 0, tail: 0 }],
        [141, { tail: 30 }], [141.5, { tail: -30 }], [142, { tail: 30 }], [142.5, { tail: -30 }], [143, { tail: 30 }], [143.5, { tail: -30 }], [144, { tail: 30 }], [144.5, { tail: -30 }], [145, { tail: 0 }],
        [150, { x: 2170, y: 825, f: '' }], [151, { x: 2140, y: 835, rot: -10, f: 'brightness(.62) saturate(.4)' }], [153, { rot: 0, face: 'closed' }],
        [155, { face: 'open' }], [160, { face: 'laughing', laugh: 1 }], [172, { laugh: 0, face: 'open' }], [176, { x: 2140, y: 835, f: 'brightness(.62) saturate(.4)' }], [180, { x: 2060, y: 820, walk: 1, flip: 1 }]] },
      boy: { char: 'C6', h: BOY, z: 2, poses: ['laughing'], track: [[128, { x: 1860, y: 880, pose: 'rig' }], [135, { x: 1960, y: 870, walk: 1 }], [136, { walk: 0 }],
        [152, { pose: 'laughing' }], [164, { pose: 'rig', talk: 1 }], [169.5, { talk: 0 }], [174, { pose: 'laughing' }]] },
    },
    init(c) { c.soot = puffEl(c.fxw, 16, '#5e5852'); c.soot2 = puffEl(c.fxw, 10, '#7c766f'); },
    draw(t, c) { c.soot(t, 2210, 720, clamp((t - 149.6) / 2.5), 80); c.soot2(t, 2180, 760, clamp((t - 150.4) / 2.2), 50); } },

  // 5. Dusk. They sit on the edge of the little world and watch the stars come out.
  { t0: 182, t1: 232, xf: 2.5, plates: ['B1_b612_day', 'B2_b612_dusk'], plateMix: [[182, { m: 0 }], [196, { m: 1 }]],
    cam: [[182, { x: 1440, y: 560, z: 1.05 }], [210, { x: 1440, y: 520, z: 1.12 }], [232, { x: 1500, y: 600, z: 1.3 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 2, poses: ['sitting'], track: [[182, { x: 1520, y: 820, pose: 'sitting' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sitting'], track: [[182, { x: 1650, y: 832, pose: 'sitting' }]] },
    },
    init(c) { c.st = stars(c.fxw, 70, { y1: 520, seed: 3 }); c.b = birds(c.fxw, 5, { fill: '#e8d7d8' }); c.friend = flareStar(c.fxw, 'fr5'); },
    draw(t, c) {
      c.st(t, ss((t - 192) / 22));
      c.b(t, flock(t, 184, 2900, 330, -1, 5, 0.6));
      c.friend(FRIEND.x, FRIEND.y, 34 + 4 * Math.sin(t * 3), ss((t - 200) / 8));
    } },

  // 6. Close: the boy stands and points. The friend's star twinkles back, almost a giggle.
  { t0: 232, t1: 274, xf: 1.0, plate: 'B2_b612_dusk',
    cam: [[232, { x: 1560, y: 600, z: 2.0 }], [240, { x: 1580, y: 560, z: 2.1 }], [250, { x: 1700, y: 420, z: 1.6 }], [258, { x: 1800, y: 330, z: 1.9 }], [266, { x: 1760, y: 400, z: 1.5 }], [274, { x: 1650, y: 520, z: 1.25 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 2, poses: ['waving', 'standing'], track: [[232, { x: 1520, y: 820, pose: 'standing' }], [235.5, { pose: 'waving' }], [262, { pose: 'standing' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sitting'], track: [[232, { x: 1650, y: 832, pose: 'sitting', rot: 0 }], [247, { rot: -4 }], [262, { rot: 0 }]] },
    },
    init(c) { c.st = stars(c.fxw, 70, { y1: 520, seed: 3 }); c.friend = flareStar(c.fxw, 'fr6'); c.sp = sparkles(c.fxw, 14, '#fff1b8', 9); },
    draw(t, c) {
      const gig = env(t, 252, 260, 0.5, 1.5);
      c.st(t, 1);
      c.friend(FRIEND.x, FRIEND.y, 34 + 4 * Math.sin(t * 3) + gig * 16 * Math.abs(Math.sin(t * 15)));
      c.sp(t, FRIEND.x, FRIEND.y + 30, gig, 70);
    } },

  // 7. Title over the dusk sky.
  { t0: 274, t1: 300, xf: 2.5, plates: ['B2_b612_dusk', 'title/T1_title_card'], plateMix: [[276, { m: 0 }], [282, { m: 1 }]],
    cam: [[274, { x: 1440, y: 603, z: 1.0 }], [300, { x: 1440, y: 603, z: 1.06 }]] },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.5, out: 2.5 } });
export const AUDIO = 'audio2/s01.wav';

// S03 — GREY BY TOMORROW (5:00). Morning: Pip is paler. Through the telescope, far away on Earth, the pilot
// looks for his star and can't find it. The boy decides: take it home before its light goes out.
// The old box becomes a lantern. The birds come. Goodbye to the rose; up and away.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, birds, strand, glowDot, toScreen } from './kit.js';
import { BOY, SHEEP, PIP, SCOPE } from './common.js';

const D = 300;
const NIGHT9 = { f: 'brightness(.92)', af: 'brightness(.8) saturate(.85) hue-rotate(-6deg)' };

const subs = [
  [16.0, 18.8, 'You’re paler than last night.', '你比昨晚更苍白了。'],
  [36.0, 38.6, 'Are you poorly, little star?', '你不舒服吗，小星星？'],
  [64.0, 66.8, 'Let’s see who’s missing you.', '我们看看是谁在想你。'],
  [104.0, 107.0, '…Where did you go?', '……你去哪儿了？', 'it'],
  [138.0, 140.6, 'We have to take it home.', '我们得送它回家。'],
  [141.6, 145.0, 'Before its light goes out.', '在它的光熄灭之前。'],
  [158.0, 161.4, 'But how do you carry a star?', '可是，星星要怎么带呢？'],
  [214.0, 216.6, 'The box!', '那个箱子！'],
  [262.0, 264.6, 'Go, then.', '那就去吧。', 'it'],
  [265.6, 268.6, 'And come back.', '要回来哦。', 'it'],
];

const BOXAT = { x: 1480, y: 960 };
const shots = [
  // 1. Morning. The boy kneels by the sheep and the little star. Pip is paler.
  { t0: 0, t1: 56, xf: 0, plate: 'B1_b612_day',
    cam: [[0, { x: 1300, y: 700, z: 1.2 }], [14, { x: 1270, y: 790, z: 2.3 }], [40, { x: 1260, y: 800, z: 2.6 }], [56, { x: 1300, y: 780, z: 2.0 }]],
    actors: {
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sleeping'], track: [[0, { x: 1330, y: 880, pose: 'sleeping' }], [22, { pose: 'sleeping' }], [22.1, { pose: 'rig', flip: 1, face: 'open' }], [28, { head: 14 }], [30, { head: 4 }], [33, { head: 14 }], [35, { head: 0 }]] },
      pip: { char: 'C1', h: PIP, z: 5, glow: { r: 2.2, op: 0.6 }, track: [[0, { x: 1262, y: 860, light: 0.72, face: 'closed' }], [10, { face: 'open' }], [26, { light: 0.6 }], [29, { light: 0.72, rot: 10 }], [31, { light: 0.55, rot: 0 }], [56, { light: 0.48 }]] },
      boy: { char: 'C6', h: BOY, z: 2, poses: ['sitting'], track: [[0, { x: 1110, y: 900, pose: 'sitting' }]] },
    },
    init(c) { c.sp = sparkles(c.fxw, 10, '#ffe7a6', 4); },
    draw(t, c) { c.sp(t, 1262, 850, env(t, 28, 31, 0.4, 1), 40); } },

  // 2. He fetches his little telescope.
  { t0: 56, t1: 78, xf: 1.0, plate: 'B1_b612_day',
    cam: [[56, { x: 1500, y: 780, z: 1.5 }], [78, { x: 1560, y: 760, z: 1.7 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, track: [[56, { x: 1900, y: 930, walk: 1 }], [64, { x: 1560, y: 900, walk: 1, talk: 1 }], [65, { walk: 0 }], [67, { talk: 0 }]] },
      scope: { h: 1, z: 2, init: SCOPE, k: 0.9, track: [[56, { x: 1960, y: 930, rot: 0 }], [64, { x: 1630, y: 905, rot: 0 }], [66, { x: 1660, y: 905, rot: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[56, { x: 1320, y: 930, flip: -1 }], [70, { x: 1440, y: 925, walk: 1, flip: -1 }], [71, { walk: 0 }]] },
      pip: { char: 'C1', h: PIP, z: 5, glow: { r: 2.2, op: 0.6 }, track: [[56, { x: 1262, y: 880, light: 0.48 }], [70, { x: 1400, y: 860, light: 0.47 }]] },
    } },

  // 3. Through the telescope: the desert at night, far away. The pilot looks for his star.
  { t0: 78, t1: 128, xf: 0.8, plate: 'B9_desert_night', grade: [[0, NIGHT9]],
    cam: [[78, { x: 1700, y: 300, z: 1.5 }], [92, { x: 1500, y: 600, z: 1.25 }], [110, { x: 1450, y: 700, z: 1.5 }], [128, { x: 1430, y: 720, z: 1.6 }]],
    actors: {
      pilot: { char: 'C7', h: 270, z: 2, poses: ['rear_view', 'sitting'], track: [[78, { x: 1420, y: 1000, pose: 'rear_view', rot: 0 }], [96, { rot: -3 }], [100, { rot: 3 }], [104, { rot: 0 }], [113, { pose: 'rear_view' }], [114, { pose: 'sitting', x: 1440 }]] },
    },
    init(c) {
      c.st = stars(c.fxw, 60, { y1: 650, seed: 21 });
      c.iris = document.createElement('div'); c.iris.style.cssText = 'position:absolute;inset:0;pointer-events:none'; c.el.appendChild(c.iris);
    },
    draw(t, c) {
      c.st(t, 1);
      const r = 380 + 900 * ss((t - 120) / 8);
      c.iris.style.background = `radial-gradient(circle at 50% 48%, rgba(0,0,0,0) ${r}px, rgba(8,6,12,1) ${r + 18}px)`;
    } },

  // 4. Back on B612. The boy decides.
  { t0: 128, t1: 196, xf: 1.2, plate: 'B1_b612_day',
    cam: [[128, { x: 1500, y: 760, z: 2.0 }], [146, { x: 1510, y: 760, z: 2.2 }], [156, { x: 1480, y: 780, z: 1.7 }], [196, { x: 1520, y: 800, z: 1.6 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, track: [[128, { x: 1560, y: 900, face: 'closed' }], [132, { face: 'open', head: -4 }], [137, { talk: 1, head: 0 }], [145, { talk: 0 }], [157, { talk: 1, armR: -30 }], [161.5, { talk: 0, armR: 0 }], [172, { head: 6 }]] },
      scope: { h: 1, z: 2, init: SCOPE, k: 0.9, track: [[128, { x: 1660, y: 905 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[128, { x: 1440, y: 925, flip: -1 }], [140, { head: 10 }], [141, { head: -6 }], [142, { head: 10 }], [143, { head: 0 }],
        [166, { head: 14 }], [172, { head: -10 }], [176, { head: 0, face: 'laughing' }], [178, { face: 'open', x: 1440, flip: 1 }], [186, { x: 1100, y: 940, walk: 1, flip: 1 }], [187, { op: 1 }], [190, { x: 960, op: 0, walk: 1 }]] },
      pip: { char: 'C1', h: PIP, z: 5, glow: { r: 2.2, op: 0.6 }, track: [[128, { x: 1400, y: 860, light: 0.47 }], [196, { light: 0.43 }]] },
    } },

  // 5. The sheep drags in the old box. Pip hops in, and the box becomes a lantern.
  { t0: 196, t1: 250, xf: 1.0, plate: 'B1_b612_day',
    cam: [[196, { x: 1420, y: 820, z: 1.6 }], [214, { x: 1440, y: 840, z: 1.8 }], [228, { x: 1470, y: 860, z: 2.4 }], [244, { x: 1470, y: 860, z: 2.5 }], [250, { x: 1460, y: 840, z: 2.2 }]],
    actors: {
      box: { h: 150, z: 3, img: 'props/P1_box_lantern.png', isize: [1500, 1400], anchor: [750, 1141], glow: { r: 1.5, dy: -0.45, op: 0.9 },
        track: [[196, { x: 900, y: 980, f: 'brightness(.62) saturate(.55)', glow: 0 }], [208, { x: BOXAT.x, y: BOXAT.y }], [230, { f: 'brightness(.62) saturate(.55)', glow: 0 }], [232, { f: 'brightness(1.08) saturate(1.05)', glow: 1 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[196, { x: 780, y: 990, walk: 1, flip: -1, rot: -4 }], [208, { x: 1360, y: 965, walk: 1, rot: -4 }], [209, { walk: 0, rot: 0 }], [214, { face: 'laughing' }], [217, { face: 'open' }]] },
      boy: { char: 'C6', h: BOY, z: 2, poses: ['laughing'], track: [[196, { x: 1580, y: 900, pose: 'rig', talk: 0 }], [213.5, { talk: 1 }], [216.5, { talk: 0 }], [234, { pose: 'laughing' }]] },
      pip: { char: 'C1', h: PIP, z: 5, glow: { r: 2.2, op: 0.6 }, track: [[196, { x: 1400, y: 860, light: 0.43, op: 1, s: 1 }], [222, { x: 1400, y: 880 }], [223.5, { x: 1440, y: 820, rot: 20 }], [225, { x: 1475, y: 860, rot: 0 }], [228, { x: 1478, y: 846, s: 1 }], [229.5, { x: 1480, y: 900, op: 1, s: 0.6 }], [230, { op: 0 }]] },
    },
    init(c) { c.sp = sparkles(c.fxw, 30, '#ffe6a0', 12); },
    draw(t, c) { c.sp(t, BOXAT.x, BOXAT.y - 80, env(t, 231, 240, 0.3, 3), 110); } },

  // 6. The birds come. Strings for the boy, the sheep, the lantern. Goodbye to the rose; up and away.
  { t0: 250, t1: 300, xf: 1.2, plate: 'B1_b612_day',
    cam: [[250, { x: 1300, y: 640, z: 1.35 }], [268, { x: 1300, y: 620, z: 1.4 }], [282, { x: 1360, y: 520, z: 1.3 }], [300, { x: 1440, y: 470, z: 1.1 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, track: [[250, { x: 1480, y: 900, armR: 0 }], [258, { armR: -150, armL: 0 }], [264, { head: -8 }], [270, { head: 0 }], [276, { x: 1480, y: 900, armR: -150 }], [300, { x: 1560, y: 120 }, 'in']] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[250, { x: 1330, y: 930, flip: -1 }], [277, { x: 1330, y: 930 }], [300, { x: 1420, y: 160 }, 'in']] },
      box: { h: 110, z: 5, img: 'props/P1_box_lantern.png', isize: [1500, 1400], anchor: [750, 1141], glow: { r: 1.6, dy: -0.45, op: 0.9 }, track: [[250, { x: 1250, y: 950, glow: 1 }], [278, { x: 1250, y: 950 }], [300, { x: 1340, y: 190 }, 'in']] },
    },
    init(c) {
      c.b = birds(c.fxw, 7); c.str = Array.from({ length: 3 }, () => strand(c.fxw));
    },
    draw(t, c) {
      const arrive = ss((t - 250) / 7);
      const B = c.actors.boy.last, S = c.actors.sheep.last, X = c.actors.box.last;
      const hands = [[B.x + 70, B.y - 205], [S.x, S.y - 120], [X.x, X.y - 120]];
      const L = [];
      for (let i = 0; i < 7; i++) {
        const h = hands[i < 3 ? 0 : i < 5 ? 1 : 2];
        const tx = h[0] + (i % 3 - 1) * 70, ty = h[1] - 260 - (i % 2) * 40;
        L.push({ x: lerp(-200 + i * 60, tx, arrive) + Math.sin(t * 2 + i) * 10, y: lerp(150 + i * 20, ty, arrive) + Math.sin(t * 3 + i * 2) * 8, s: 0.9, speed: 10 });
      }
      c.b(t, L);
      const k = ss((t - 257) / 2);
      c.str[0](L[1].x, L[1].y + 6, hands[0][0], hands[0][1], 12, k);
      c.str[1](L[3].x, L[3].y + 6, hands[1][0], hands[1][1], 10, k);
      c.str[2](L[5].x, L[5].y + 6, hands[2][0], hands[2][1], 10, k);
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s03.wav';

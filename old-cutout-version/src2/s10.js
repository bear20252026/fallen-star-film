// S10 — THE STAR STAIRS (5:00). Moth carries them up a staircase of stars. Halfway he is too tired; they
// land and climb the last steps on foot, each star chiming. At the top: an empty dark place in the sky.
// A goodbye. They set Pip back in its place. It shines, but so small. Far, far below: the Earth.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg } from './kit.js';
import { BOY, SHEEP, PIP, MOTH, BOXDEF } from './common.js';
import { RIDE_ACTORS, rideDraw } from './ride.js';

const D = 300;
const HOLE = { x: 1452, y: 112 };
// the staircase, bottom left to the loop at the top (plate pixels)
const PTS = [[300, 1125], [525, 1035], [720, 966], [885, 900], [1035, 849], [1140, 774], [1035, 705], [930, 654], [885, 594], [930, 540], [1020, 498], [1110, 471], [1194, 450], [1275, 420], [1350, 393], [1404, 354], [1365, 315], [1320, 285], [1275, 240], [1230, 195], [1224, 150], [1290, 114], [1365, 84]];
const at = (u) => { const f = clamp(u) * (PTS.length - 1), i = Math.min(PTS.length - 2, Math.floor(f)), r = f - i; return [lerp(PTS[i][0], PTS[i + 1][0], r), lerp(PTS[i][1], PTS[i + 1][1], r)]; };
const sizeAt = (y) => lerp(0.32, 0.9, clamp((y - 100) / 1000));   // characters get smaller as the stairs go up and away
const subs = [
  [16.0, 18.6, 'Look! A road of stars!', '看！一条星星铺的路！'],
  [20.0, 23.6, 'It goes all the way up to where Pip lives.', '它一直通到皮皮住的地方。'],
  [70.0, 73.0, 'I’m sorry… my wings are so tired.', '对不起……我的翅膀好累。', 'it'],
  [74.0, 76.6, 'Then we’ll walk!', '那我们走上去！'],
  [158.0, 160.6, 'There. That’s your place.', '那儿。那是你的位置。'],
  [176.0, 179.0, 'Goodbye, little star.', '再见，小星星。'],
  [181.0, 184.6, 'We’ll look for you every night.', '我们每天晚上都会找你。'],
  [222.0, 224.6, 'It’s so small.', '它好小啊。'],
  [228.0, 232.0, 'One star is hard to see from far away.', '一颗星星，从很远的地方很难看见。', 'it'],
  [252.0, 255.6, 'Somebody down there has to look up.', '下面得有人抬头看才行。'],
  [262.0, 265.0, 'And laugh.', '还要笑。'],
];

const steps = (c) => { c.chime = sparkles(c.fxw, 24, '#fff0b8', 23); c.st = stars(c.fxw, 30, { y1: 1206, seed: 77, r: 1.6 }); };

const shots = [
  // 1. The reveal: the staircase rises out of the dark.
  { t0: 0, t1: 44, xf: 0, plate: 'B8_star_stairs', actors: RIDE_ACTORS(0.7),
    cam: [[0, { x: 900, y: 900, z: 1.6 }], [14, { x: 900, y: 860, z: 1.5 }], [30, { x: 1200, y: 603, z: 1.0 }], [44, { x: 1200, y: 603, z: 1.0 }]],
    init: steps,
    draw(t, c) {
      c.st(t, 1);
      const u = ss(t / 40);
      rideDraw(c, t, { x: lerp(-150, 420, u), y: lerp(1000, 880, u), k: lerp(0.8, 0.65, u), rot: -4, light: 0.85, pipFace: 'open',
        boy: { talk: env(t, 15.6, 18.8, 0.2, 0.2) + env(t, 19.6, 23.8, 0.2, 0.2) }, moth: { mood: t > 10 ? 'surprised' : 'laughing' } });
    } },

  // 2. Moth flies up along the stairs; every star they pass lights up. He tires and lands.
  { t0: 44, t1: 84, xf: 1.2, plate: 'B8_star_stairs', actors: RIDE_ACTORS(0.6),
    cam: [[44, { x: 760, y: 900, z: 1.4 }], [62, { x: 1000, y: 700, z: 1.5 }], [76, { x: 1060, y: 560, z: 1.8 }], [84, { x: 1060, y: 560, z: 1.8 }]],
    init: steps,
    draw(t, c) {
      c.st(t, 1);
      const u = lerp(0.04, 0.47, ss((t - 44) / 26)), [x, y] = at(u), k = sizeAt(y) * 0.85;
      const land = ss((t - 66) / 4);
      const P = rideDraw(c, t, { x, y: y - lerp(150, 70, land) * k, k, rot: -10 * (1 - land), light: 0.8, bob: 1 - land,
        moth: { mood: t > 68 ? 'sad' : 'laughing', flap: 1 - 0.8 * land, talk: env(t, 69.6, 73.2, 0.2, 0.2) },
        boy: { talk: env(t, 73.6, 76.8, 0.2, 0.2) } });
      c.chime(t, x, y, env(t, 46, 68, 1, 1), 60);
    } },

  // 3. On foot: the sheep hops from star to star, the boy carries the lantern. Each step chimes.
  { t0: 84, t1: 150, xf: 1.0, plate: 'B8_star_stairs',
    actors: {
      moth: { char: 'C2', h: MOTH * 0.36, z: 1, flapSpeed: 5, breath: 2, track: [[84, { x: 1110, y: 420, wings: 'folded', mood: 'laughing' }], [120, { wings: 'open' }]] },
      boy: { char: 'C6', h: BOY * 0.4, z: 3, track: [[84, {}]] },
      sheep: { char: 'C5', h: SHEEP * 0.4, z: 4, track: [[84, {}]] },
      box: BOXDEF(34, { z: 5 }),
      pip: { char: 'C1', h: PIP * 0.4, z: 6, top: true, glow: { r: 2.6 }, track: [[84, {}]] },
    },
    cam: [[84, { x: 1150, y: 480, z: 1.9 }], [110, { x: 1260, y: 380, z: 2.0 }], [135, { x: 1300, y: 260, z: 2.1 }], [150, { x: 1330, y: 230, z: 2.1 }]],
    init: steps,
    draw(t, c) {
      c.st(t, 1);
      const L = c.actors;
      // step index along the stairs; one step every ~2.8 s
      const sf = lerp(11.2, 20.6, clamp((t - 88) / 56)), f = sf / (PTS.length - 1);
      const hop = Math.abs(Math.sin(Math.PI * ((t - 88) / 56 * 9.4))) * 18 * (t > 88 && t < 144 ? 1 : 0);
      const [sx, sy] = at(f + 0.012), [bx, by] = at(f - 0.01);
      L.sheep.render({ x: sx, y: sy - 8 - hop, flip: sx > at(f + 0.03)[0] ? -1 : 1, walk: t > 88 && t < 144 ? 0.6 : 0, face: 'laughing' }, t);
      L.boy.render({ x: bx, y: by - 8, walk: t > 88 && t < 144 ? 0.8 : 0, armR: -40, flip: bx > at(f + 0.01)[0] ? -1 : 1 }, t);
      const hx = bx + 22, hy = by - 50;
      L.box.render({ x: hx, y: hy, glow: 0.8, rot: Math.sin(t * 3) * 4 }, t);
      L.pip.render({ x: hx, y: hy - 28, light: 0.8, face: 'open', laugh: env(t, 100, 104, 0.3, 0.5) + env(t, 126, 130, 0.3, 0.5) }, t);
      // the star under the sheep chimes as it lands
      const ring = Math.abs(Math.sin(Math.PI * ((t - 88) / 56 * 9.4)));
      c.chime(t, sx, sy, (1 - ring) * 0.8 * (t > 88 && t < 144 ? 1 : 0), 30);
    } },

  // 4. The top. The empty dark place. A goodbye.
  { t0: 150, t1: 200, xf: 1.2, plate: 'B8_star_stairs',
    actors: {
      boy: { char: 'C6', h: BOY * 0.36, z: 3, track: [[150, { x: 1240, y: 145, flip: -1 }], [170, { head: 6 }], [175, { talk: 1 }], [185, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.36, z: 4, track: [[150, { x: 1296, y: 108, flip: -1, face: 'open' }], [166, { head: -10 }], [178, { face: 'closed', head: -14 }], [190, { face: 'open', head: 0 }]] },
      box: BOXDEF(30, { z: 5, track: [[150, { x: 1262, y: 104, glow: 0.8 }]] }),
      pip: { char: 'C1', h: PIP * 0.42, z: 6, top: true, glow: { r: 2.6 }, track: [[150, { x: 1262, y: 80, light: 0.8, face: 'open' }], [164, { x: 1262, y: 80 }], [168, { x: 1290, y: 78 }], [178, { x: 1290, y: 80, face: 'closed' }], [186, { face: 'open', x: 1262, y: 80 }]] },
    },
    cam: [[150, { x: 1350, y: 210, z: 2.2 }], [162, { x: 1400, y: 210, z: 2.3 }], [174, { x: 1290, y: 210, z: 2.5 }], [200, { x: 1330, y: 210, z: 2.3 }]],
    init(c) { steps(c); c.ring = svg(c.fxw, 'circle', { cx: HOLE.x, cy: HOLE.y, r: 44, fill: 'none', stroke: '#ffe7a6', 'stroke-width': 3, 'stroke-dasharray': '3 9', opacity: 0 }); },
    draw(t, c) {
      c.st(t, 1);
      c.ring.setAttribute('opacity', (0.5 * env(t, 154, 200, 3, 1) * (0.7 + 0.3 * Math.sin(t * 2))).toFixed(3));
    } },

  // 5. They let Pip go. It floats up into its place and settles. So small.
  { t0: 200, t1: 244, xf: 1.0, plate: 'B8_star_stairs',
    actors: {
      boy: { char: 'C6', h: BOY * 0.36, z: 3, track: [[200, { x: 1240, y: 145, flip: -1, armR: 0 }], [204, { armR: -120 }], [212, { armR: -40 }], [221.6, { talk: 1 }], [224.8, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.36, z: 4, track: [[200, { x: 1296, y: 108, flip: -1, head: -16 }]] },
      moth: { char: 'C2', h: MOTH * 0.3, z: 1, flapSpeed: 5, breath: 2, track: [[200, { x: 1150, y: 290, wings: 'open', flap: 0.6, mood: 'laughing', op: 0 }], [214, { op: 0 }], [218, { op: 1, x: 1170, y: 250 }], [227.6, { talk: 1 }], [232.2, { talk: 0 }]] },
      box: BOXDEF(30, { z: 5, track: [[200, { x: 1262, y: 104, glow: 0.8 }], [212, { glow: 0.3 }]] }),
      pip: { char: 'C1', h: PIP * 0.42, z: 6, top: true, glow: { r: 2.6 }, track: [[200, { x: 1262, y: 80, light: 0.8, face: 'open' }], [204, { x: 1262, y: 80 }], [212, { x: HOLE.x, y: HOLE.y + 14, s: 1.4 }], [214, { s: 1.3, light: 0.55 }], [244, { light: 0.5 }]] },
    },
    cam: [[200, { x: 1330, y: 210, z: 2.3 }], [212, { x: 1400, y: 210, z: 2.4 }], [226, { x: 1380, y: 220, z: 1.9 }], [244, { x: 1400, y: 300, z: 1.4 }]],
    init(c) { steps(c); c.sp = sparkles(c.fxw, 20, '#ffe08a', 29); },
    draw(t, c) { c.st(t, 1); const p = c.actors.pip.last; c.sp(t, p.x, p.y, env(t, 204, 216, 1, 2), 50); } },

  // 6. Look down: far, far below, the Earth. Somebody has to look up. And laugh.
  { t0: 244, t1: 300, xf: 1.5, plate: 'B8_star_stairs',
    actors: {
      boy: { char: 'C6', h: BOY * 0.36, z: 3, track: [[244, { x: 1240, y: 145, flip: 1, head: 10 }], [251.6, { talk: 1 }], [255.8, { talk: 0 }], [261.6, { talk: 1, face: 'laughing' }], [265.2, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.36, z: 4, track: [[244, { x: 1296, y: 108, flip: 1, head: 12 }]] },
      moth: { char: 'C2', h: MOTH * 0.3, z: 1, flapSpeed: 5, breath: 2, track: [[244, { x: 1170, y: 250, wings: 'open', flap: 0.6, mood: 'laughing' }]] },
      pip: { char: 'C1', h: PIP * 0.42, z: 6, top: true, glow: { r: 2.6 }, track: [[244, { x: HOLE.x, y: HOLE.y + 14, s: 1.3, light: 0.5, face: 'open' }]] },
    },
    cam: [[244, { x: 1350, y: 260, z: 1.9 }], [266, { x: 1300, y: 300, z: 1.6 }], [300, { x: 1440, y: 900, z: 1.0 }]],
    init(c) {
      steps(c);
      c.halo = svg(c.fxw, 'circle', { cx: 1900, cy: 960, r: 90, fill: '#9fd0ff', opacity: 0, style: 'filter:blur(20px)' });
      c.earth = svg(c.fxw, 'circle', { cx: 1900, cy: 960, r: 44, fill: '#7fb0d8', stroke: '#e6f3fb', 'stroke-width': 4, opacity: 0 });
    },
    draw(t, c) { c.st(t, 1); const e = ss((t - 272) / 8); c.earth.setAttribute('opacity', (0.9 * e).toFixed(3)); c.halo.setAttribute('opacity', (0.5 * e).toFixed(3)); } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s10.wav';

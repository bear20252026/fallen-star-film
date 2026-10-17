// S02 — THE STAR FALLS (5:00). Night. The friend's star hiccups, wobbles and falls into the rose's garden.
// It is Pip: tiny, grey-gold and scared. The sheep makes friends with it and keeps it warm all night.
// The boy wakes and sees the dark gap in the sky: "That's his star."
import { makeScene, track, ss, env, clamp, lerp, stars, sparkles, svg, flareStar, glowDot, toScreen, noise } from './kit.js';
import { BOY, SHEEP, PIP } from './common.js';

const D = 300;
const FRIEND = { x: 1880, y: 250 };
const LAND = { x: 1250, y: 800 };
const NIGHT = { f: 'brightness(.42) saturate(.7) hue-rotate(-12deg) contrast(1.05)', af: 'brightness(.62) saturate(.75) hue-rotate(-8deg)' };

const subs = [
  [150.0, 152.6, 'Hello?', '你好呀？'],
  [171.5, 174.5, 'Well? Don’t just stand there.', '愣着干嘛？', 'it'],
  [175.0, 177.6, 'It’s cold.', '它冷着呢。', 'it'],
  [266.0, 268.6, 'Sheep? What is it?', '小羊？怎么了？'],
  [284.0, 286.0, 'Oh no.', '糟了。'],
  [287.0, 290.6, 'That’s his star.', '那是他的星星。'],
];

// where the falling star is at time t (world px) along its arc
const fallPos = (u) => {
  const x = lerp(FRIEND.x, LAND.x, u), y = lerp(FRIEND.y, LAND.y, u * u) - Math.sin(u * Math.PI) * 60;
  return [x, y];
};
const nightStars = (c, n = 90, seed = 11) => stars(c.fxw, n, { y1: 560, seed });

const shots = [
  // 1. Night on B612. Everyone asleep. The friend's star hiccups.
  { t0: 0, t1: 42, xf: 0, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[0, { x: 1500, y: 560, z: 1.05 }], [30, { x: 1560, y: 520, z: 1.15 }], [42, { x: 1640, y: 470, z: 1.25 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 2, poses: ['sleeping'], breath: 2, track: [[0, { x: 1520, y: 850, pose: 'sleeping' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sleeping'], breath: 2, track: [[0, { x: 1730, y: 862, pose: 'sleeping' }]] },
    },
    init(c) { c.st = nightStars(c); c.fr = flareStar(c.fxw, 'f21'); },
    draw(t, c) {
      c.st(t, 1);
      const hic = [24, 29, 33.5, 37, 39.5].reduce((m, a) => Math.max(m, Math.exp(-((t - a) ** 2) / 0.02)), 0);
      c.fr(FRIEND.x, FRIEND.y + hic * 6, 34 + 4 * Math.sin(t * 3) + hic * 26, 1 - hic * 0.4);
    } },

  // 2. Close on the star: it wobbles, slips and falls.
  { t0: 42, t1: 60, xf: 0.8, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[42, { x: 1860, y: 300, z: 2.4 }], [50, { x: 1840, y: 320, z: 2.6 }], [52, { x: 1800, y: 360, z: 2.0 }], [60, { x: 1440, y: 560, z: 1.05 }]],
    init(c) {
      c.st = nightStars(c, 90, 11); c.fr = flareStar(c.fxw, 'f22');
      c.trail = svg(c.fxw, 'path', { fill: 'none', stroke: '#ffe7a6', 'stroke-width': 10, 'stroke-linecap': 'round', opacity: 0.8 });
      c.trail2 = svg(c.fxw, 'path', { fill: 'none', stroke: '#fff8e0', 'stroke-width': 3, 'stroke-linecap': 'round' });
      c.sp = sparkles(c.fxw, 30, '#ffe7a6', 3);
    },
    draw(t, c) {
      c.st(t, 1);
      const wob = t < 51 ? Math.sin(t * 9) * 10 * ss((t - 43) / 6) : 0;
      const u = ss((t - 51) / 8);
      const [x, y] = u > 0 ? fallPos(u) : [FRIEND.x + wob, FRIEND.y + Math.abs(wob) * 0.3];
      c.fr(x, y, 30 + (t < 51 ? 6 * Math.sin(t * 13) : 0), 1);
      if (u > 0) {
        const pts = []; for (let k = 0; k <= 16; k++) { const [px, py] = fallPos(Math.max(0, u - 0.25 * k / 16)); pts.push(`${px.toFixed(1)} ${py.toFixed(1)}`); }
        c.trail.setAttribute('d', 'M' + pts.join(' L')); c.trail2.setAttribute('d', 'M' + pts.join(' L'));
        c.trail.setAttribute('opacity', (0.7 * (1 - ss((t - 58.6) / 0.6))).toFixed(3));
      }
      c.sp(t, x, y + 20, u > 0 ? 1 : 0, 60);
    } },

  // 3. Plink. It lands in the rose's garden. The sheep's ear twitches; it wakes.
  { t0: 60, t1: 86, xf: 0.6, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[60, { x: 1440, y: 620, z: 1.2 }], [66, { x: 1440, y: 640, z: 1.25 }], [74, { x: 1560, y: 760, z: 1.9 }], [86, { x: 1560, y: 760, z: 2.0, shake: 0 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 2, poses: ['sleeping'], breath: 2, track: [[0, { x: 1520, y: 850, pose: 'sleeping' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sleeping'], breath: 2, track: [[60, { x: 1730, y: 862, pose: 'sleeping', op: 1 }], [76.9, { op: 1 }], [77, { op: 0 }]] },
      sheepUp: { char: 'C5', h: SHEEP, z: 3, track: [[60, { x: 1730, y: 862, op: 0, flip: 1 }], [76.9, { op: 0 }], [77, { op: 1, face: 'closed', head: 10 }], [78.5, { face: 'open', head: 0 }], [80, { head: -12 }], [82, { head: 6 }], [84, { head: -6 }]] },
    },
    init(c) {
      c.st = nightStars(c); c.glow = glowDot(c.fxw, 'g23'); c.sp = sparkles(c.fxw, 30, '#ffe7a6', 6);
      c.ring = svg(c.fxw, 'ellipse', { fill: 'none', stroke: '#fff3c8', 'stroke-width': 4 });
    },
    draw(t, c) {
      c.st(t, 1);
      const a = ss((t - 61.4) / 0.3);
      c.glow.setAttribute('cx', LAND.x); c.glow.setAttribute('cy', LAND.y - 10);
      c.glow.setAttribute('r', (a * (90 + 60 * Math.exp(-(t - 61.6) * 2))).toFixed(1));
      const u = clamp((t - 61.6) / 1.4);
      c.ring.setAttribute('cx', LAND.x); c.ring.setAttribute('cy', LAND.y); c.ring.setAttribute('rx', 20 + u * 220); c.ring.setAttribute('ry', 6 + u * 50);
      c.ring.setAttribute('opacity', (u > 0 && u < 1 ? 0.8 * (1 - u) : 0).toFixed(3));
      c.sp(t, LAND.x, LAND.y, env(t, 61.5, 66, 0.2, 2), 140);
    } },

  // 4. The sheep creeps over the dark grass towards the glow.
  { t0: 86, t1: 126, xf: 1.0, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[86, { x: 1500, y: 760, z: 1.8 }], [110, { x: 1340, y: 760, z: 1.9 }], [120, { x: 1290, y: 770, z: 2.6 }], [126, { x: 1280, y: 775, z: 2.8 }]],
    actors: {
      sheep: { char: 'C5', h: SHEEP, z: 3, wspeed: 4, track: [[86, { x: 1700, y: 860, walk: 0.5, flip: 1, head: 6 }], [104, { x: 1420, y: 835, walk: 0.5, head: 6 }], [106, { walk: 0, head: -4 }], [109, { head: 6 }], [112, { x: 1420, y: 835, walk: 0 }], [117, { x: 1350, y: 830, walk: 0.4, head: 12 }], [118, { walk: 0 }]] },
      pip: { char: 'C1', h: PIP, z: 5, top: true, glow: { r: 2.2 }, track: [[86, { x: LAND.x, y: LAND.y - 20, light: 0.35, face: 'closed', rot: 0 }]] },
    },
    init(c) { c.st = nightStars(c); },
    draw(t, c) { c.st(t, 1); c.actors.pip.el.style.transform += ` rotate(${(Math.sin(t * 40) * 3).toFixed(2)}deg)`; } },

  // 5. First meeting. Pip opens its eyes, squeaks, hides by the rose. The rose takes its side.
  { t0: 126, t1: 200, xf: 0.8, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[126, { x: 1290, y: 770, z: 2.7 }], [140, { x: 1270, y: 760, z: 3.0 }], [158, { x: 1220, y: 740, z: 2.6 }], [170, { x: 1180, y: 700, z: 2.2 }], [182, { x: 1220, y: 750, z: 2.6 }], [200, { x: 1260, y: 770, z: 3.0 }]],
    actors: {
      sheep: { char: 'C5', h: SHEEP, z: 3, track: [[126, { x: 1350, y: 830, flip: 1, head: 12 }], [134, { head: 18, x: 1335 }], [136, { head: -6, x: 1360 }], [140, { head: 0 }],
        [146, { x: 1350, y: 830, talk: 1 }], [152, { talk: 0, head: 8 }], [160, { head: -10 }], [166, { head: 4 }], [186, { x: 1340, y: 830, head: 0 }], [192, { x: 1320, y: 832, walk: 0.4 }], [193, { walk: 0, head: 14 }]] },
      pip: { char: 'C1', h: PIP, z: 5, top: true, glow: { r: 2.2 }, track: [
        [126, { x: LAND.x, y: LAND.y - 20, light: 0.35, face: 'closed', rot: 0 }], [137.5, { face: 'closed' }], [138, { face: 'open', rot: 0 }],
        [140, { x: LAND.x, y: LAND.y - 20, rot: 0 }], [140.4, { x: 1210, y: 735, rot: -20 }], [140.8, { x: 1170, y: 770, rot: -30 }], [141.2, { x: 1140, y: 720, rot: -10 }], [141.6, { x: 1110, y: 760, rot: 0 }],
        [156, { x: 1110, y: 760 }], [158, { x: 1125, y: 755, rot: 12 }], [176, { x: 1125, y: 755, rot: 12, light: 0.38 }],
        [182, { x: 1150, y: 765, rot: 0 }], [183, { x: 1180, y: 745 }], [184, { x: 1200, y: 768 }], [188, { x: 1200, y: 768 }], [189, { x: 1230, y: 750 }], [190, { x: 1262, y: 775, light: 0.42 }]] },
    },
    init(c) { c.st = nightStars(c); c.sp = sparkles(c.fxw, 10, '#ffe7a6', 8); },
    draw(t, c) {
      c.st(t, 1);
      const p = c.actors.pip.last; if (p) c.sp(t, p.x, p.y, env(t, 138, 142, 0.2, 1) + env(t, 182, 191, 0.3, 1), 50);
      if (t < 137.5) c.actors.pip.el.style.transform += ` rotate(${(Math.sin(t * 40) * 3).toFixed(2)}deg)`;
    } },

  // 6. The sheep lies down and curls round the little star. Pip warms up and glows.
  { t0: 200, t1: 262, xf: 1.5, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[200, { x: 1290, y: 780, z: 2.6 }], [230, { x: 1300, y: 790, z: 3.1 }], [250, { x: 1310, y: 780, z: 2.4 }], [262, { x: 1380, y: 700, z: 1.6 }]],
    actors: {
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sitting', 'sleeping'], breath: 2, track: [[200, { x: 1330, y: 840, pose: 'sitting' }], [214, { pose: 'sitting' }], [215, { pose: 'sleeping', x: 1310 }]] },
      pip: { char: 'C1', h: PIP, z: 5, top: true, glow: { r: 2.6 }, track: [[200, { x: 1262, y: 775, light: 0.42, face: 'open' }], [215, { x: 1262, y: 790 }], [218, { x: 1262, y: 800, face: 'closed' }], [240, { light: 0.7 }], [262, { light: 0.72 }]] },
    },
    init(c) { c.st = nightStars(c); c.gl = glowDot(c.fxw, 'g26', '#ffcf7a'); },
    draw(t, c) { c.st(t, 1); c.gl.setAttribute('cx', 1262); c.gl.setAttribute('cy', 800); c.gl.setAttribute('r', (160 * ss((t - 218) / 20)).toFixed(1)); c.gl.setAttribute('opacity', 0.45); } },

  // 7. The boy wakes, looks up. The friend's star is gone: a dark gap.
  { t0: 262, t1: 300, xf: 1.2, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[262, { x: 1420, y: 700, z: 1.8 }], [272, { x: 1440, y: 680, z: 1.9 }], [278, { x: 1720, y: 380, z: 1.6 }], [292, { x: 1860, y: 280, z: 2.2 }], [300, { x: 1860, y: 280, z: 2.3 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 2, poses: ['sitting'], track: [[262, { x: 1460, y: 850, pose: 'sitting' }], [270, { pose: 'rig', face: 'open', talk: 1, head: 0 }], [272, { talk: 0, head: -6 }], [282, { talk: 1 }], [291, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 3, poses: ['sleeping'], breath: 2, track: [[262, { x: 1310, y: 840, pose: 'sleeping' }]] },
      pip: { char: 'C1', h: PIP, z: 5, top: true, glow: { r: 2.6 }, track: [[262, { x: 1262, y: 800, light: 0.72, face: 'closed' }]] },
    },
    init(c) { c.st = nightStars(c); c.gap = svg(c.fxw, 'circle', { cx: FRIEND.x, cy: FRIEND.y, r: 0, fill: 'none', stroke: 'rgba(255,240,200,.25)', 'stroke-width': 3, 'stroke-dasharray': '6 10' }); },
    draw(t, c) { c.st(t, 1); c.gap.setAttribute('r', (26 * ss((t - 284) / 3)).toFixed(1)); } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.5 } });
export const AUDIO = 'audio2/s02.wav';

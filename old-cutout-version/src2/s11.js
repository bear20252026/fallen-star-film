// S11 — THE PILOT LAUGHS (4:30). The desert at night. The pilot looks up, as every night, at the empty place.
// Then: a tiny faint star. Is that you? He laughs, a little, then out loud. The laugh rises like a gold
// ribbon all the way up the sky to the star stairs. Pip blazes. And all the stars in the sky laugh with him.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, flareStar } from './kit.js';
import { BOY, SHEEP, PIP, MOTH } from './common.js';

const D = 270;
const NIGHT9 = { f: 'brightness(.92)', af: 'brightness(.8) saturate(.85) hue-rotate(-6deg)' };
const STAR = { x: 1900, y: 330 };      // "his" star in the desert sky
const HOLE = { x: 1452, y: 112 };      // Pip's place at the top of the star stairs
const PH = 360;                         // pilot height
const subs = [
  [20.0, 23.0, 'Every night I look for you.', '每天晚上，我都在找你。'],
  [26.0, 29.0, 'Every night, an empty place.', '每天晚上，那里都是空的。'],
  [72.0, 74.6, '…Is that you?', '……是你吗？'],
  [100.0, 103.6, 'Are you laughing up there?', '你在上面笑吗？'],
  [176.0, 178.6, 'Listen!', '听！'],
  [180.0, 182.6, 'He’s laughing!', '他在笑！'],
  [236.0, 239.6, 'There you are, little star.', '你在那儿呢，小星星。'],
];

// Pip's light, as seen from the desert and at the top of the stairs
const PIPL = (t) => clamp(-0.25 + 0.4 * ss((t - 56) / 10) + 0.15 * ss((t - 96) / 8) + 0.2 * env(t, 110, 140, 2, 6) + 0.9 * ss((t - 160) / 6));

const ribbon = (c, color = '#ffd978') => {
  const glow = svg(c.fxw, 'path', { fill: 'none', stroke: color, 'stroke-width': 26, 'stroke-linecap': 'round', opacity: 0, style: 'filter:blur(10px)' });
  const line = svg(c.fxw, 'path', { fill: 'none', stroke: '#fff1c4', 'stroke-width': 6, 'stroke-linecap': 'round', opacity: 0 });
  return (t, pts, draw, op) => {
    const d = 'M' + pts.map((p) => `${p[0].toFixed(0)} ${p[1].toFixed(0)}`).join(' L');
    for (const e of [glow, line]) { e.setAttribute('d', d); e.setAttribute('pathLength', 1000); e.setAttribute('stroke-dasharray', `${(1000 * clamp(draw)).toFixed(0)} 2000`); }
    glow.setAttribute('opacity', (0.7 * op).toFixed(3)); line.setAttribute('opacity', (0.9 * op).toFixed(3));
  };
};
// a wavy rising line from (x0,y0) to (x1,y1)
const wave = (t, x0, y0, x1, y1, amp = 60, n = 40) => Array.from({ length: n + 1 }, (_, i) => { const u = i / n; return [lerp(x0, x1, u) + Math.sin(u * 14 - t * 3) * amp * Math.sin(u * Math.PI), lerp(y0, y1, u)]; });

const pilotA = (track) => ({ char: 'C7', h: PH, z: 2, poses: ['rear_view', 'sitting', 'standing', 'laughing'], track });
let NID = 0;
const skyDot = (c) => { c.fl = flareStar(c.fxw, 'pf' + (NID++)); };
const drawDot = (c, t, L) => c.fl(STAR.x, STAR.y, (10 + 22 * L) * (1 + 0.08 * Math.sin(t * 5)), clamp(0.25 + L));

const shots = [
  // 1. Desert night, wide. The pilot sits by his plane looking up.
  { t0: 0, t1: 44, xf: 0, plate: 'B9_desert_night', grade: [[0, NIGHT9]],
    cam: [[0, { x: 1440, y: 603, z: 1.0 }], [24, { x: 1300, y: 760, z: 1.3 }], [44, { x: 1350, y: 800, z: 1.6 }]],
    actors: { pilot: pilotA([[0, { x: 1220, y: 1010, pose: 'sitting', flip: 1 }]]) },
    init(c) { c.st = stars(c.fxw, 70, { y1: 650, seed: 41 }); skyDot(c); },
    draw(t, c) { c.st(t, 1); drawDot(c, t, PIPL(t)); } },

  // 2. From behind him: the sky, the empty place. A tiny faint light appears. "…Is that you?"
  { t0: 44, t1: 90, xf: 1.2, plate: 'B9_desert_night', grade: [[0, NIGHT9]],
    cam: [[44, { x: 1500, y: 700, z: 1.4 }], [60, { x: 1700, y: 500, z: 1.8 }], [70, { x: 1800, y: 420, z: 2.2 }], [80, { x: 1600, y: 620, z: 1.5 }], [90, { x: 1500, y: 700, z: 1.5 }]],
    actors: { pilot: pilotA([[44, { x: 1300, y: 1010, pose: 'rear_view' }], [68, { rot: 0 }], [70, { rot: 3 }], [72, { rot: 0 }]]) },
    init(c) { c.st = stars(c.fxw, 70, { y1: 650, seed: 41 }); skyDot(c); },
    draw(t, c) { c.st(t, 1); drawDot(c, t, PIPL(t)); } },

  // 3. He stands. Closer. "Are you laughing up there?" A chuckle, then he laughs out loud.
  { t0: 90, t1: 150, xf: 1.0, plate: 'B9_desert_night', grade: [[0, NIGHT9]],
    cam: [[90, { x: 1380, y: 820, z: 1.9 }], [112, { x: 1380, y: 820, z: 2.1 }], [128, { x: 1400, y: 780, z: 1.8 }], [150, { x: 1500, y: 600, z: 1.3 }]],
    actors: { pilot: pilotA([[90, { x: 1320, y: 1010, pose: 'standing', rot: 0 }], [109, { pose: 'standing', rot: 0 }], [110, { pose: 'laughing', laugh: 0.4 }], [116, { laugh: 1 }], [150, { pose: 'laughing', laugh: 0.6 }]]) },
    init(c) { c.st = stars(c.fxw, 70, { y1: 650, seed: 41 }); skyDot(c); c.rb = ribbon(c); },
    draw(t, c) {
      c.st(t, 1); drawDot(c, t, PIPL(t));
      const u = ss((t - 122) / 22);
      c.rb(t, wave(t, 1380, 630, STAR.x, STAR.y, 70), u, env(t, 122, 152, 1, 1));
    } },

  // 4. Far above, at the top of the star stairs: the gold ribbon arrives. Pip blazes. The boy and the sheep hear it.
  { t0: 150, t1: 200, xf: 1.0, plate: 'B8_star_stairs', free: false,
    actors: {
      boy: { char: 'C6', h: BOY * 0.36, z: 3, track: [[150, { x: 1240, y: 145, flip: 1, head: 10 }], [164, { head: 0, flip: -1 }], [175.6, { talk: 1 }], [178.8, { talk: 0 }], [179.6, { talk: 1, face: 'laughing' }], [182.8, { talk: 0, laugh: 1 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.36, z: 4, track: [[150, { x: 1296, y: 108, flip: 1, head: 12 }], [164, { head: -10, flip: -1 }], [170, { face: 'laughing', laugh: 1 }]] },
      moth: { char: 'C2', h: MOTH * 0.3, z: 1, flapSpeed: 5, breath: 2, track: [[150, { x: 1170, y: 250, wings: 'open', flap: 0.6, mood: 'sad' }], [166, { mood: 'surprised' }], [172, { mood: 'laughing', laugh: 1 }]] },
      pip: { char: 'C1', h: PIP * 0.42, z: 6, top: true, glow: { r: 2.6 }, track: [[150, { x: HOLE.x, y: HOLE.y + 14, s: 1.3, light: 0.5, face: 'closed' }], [162, { face: 'open', light: 0.5 }], [168, { light: 1, s: 1.6, laugh: 1 }]] },
    },
    cam: [[150, { x: 1350, y: 480, z: 1.2 }], [164, { x: 1400, y: 260, z: 1.9 }], [176, { x: 1380, y: 220, z: 2.3 }], [200, { x: 1400, y: 300, z: 1.6 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 1206, seed: 77, r: 1.6 }); c.rb = ribbon(c); c.sp = sparkles(c.fxw, 40, '#ffe08a', 31); },
    draw(t, c) {
      c.st(t, 1, env(t, 168, 200, 2, 1));
      const u = ss((t - 150) / 16);
      const pts = wave(t, 1700, 1300, HOLE.x, HOLE.y + 14, 90);
      c.rb(t, pts, u, env(t, 150, 176, 0.5, 6));
      c.sp(t, HOLE.x, HOLE.y, env(t, 166, 200, 1, 2), 160);
    } },

  // 5. All the stars laugh. Back in the desert the whole sky twinkles; the pilot laughs with tears in his eyes.
  { t0: 200, t1: 244, xf: 1.2, plate: 'B9_desert_night', grade: [[200, NIGHT9], [220, { f: 'brightness(1.0)', af: 'brightness(.88) saturate(.9)' }]],
    cam: [[200, { x: 1600, y: 500, z: 1.2 }], [214, { x: 1440, y: 603, z: 1.0 }], [230, { x: 1380, y: 840, z: 1.9 }], [244, { x: 1380, y: 840, z: 2.0 }]],
    actors: { pilot: pilotA([[200, { x: 1320, y: 1010, pose: 'laughing' }], [214, { laugh: 1 }], [230, { laugh: 0.3 }]]) },
    init(c) { c.st = stars(c.fxw, 120, { y1: 700, seed: 43, r: 2.6 }); skyDot(c); c.sp = sparkles(c.fxw, 40, '#fff1c4', 37); },
    draw(t, c) { c.st(t, 1, 1); drawDot(c, t, 1); c.sp(t, 1440, 300, env(t, 200, 244, 2, 2), 1300); } },

  // 6. Wide: a man, a little plane, and a sky full of laughing stars. One shines brightest.
  { t0: 244, t1: 270, xf: 1.5, plate: 'B9_desert_night', grade: [[0, { f: 'brightness(1.0)', af: 'brightness(.88) saturate(.9)' }]],
    cam: [[244, { x: 1500, y: 650, z: 1.2 }], [270, { x: 1440, y: 603, z: 1.0 }]],
    actors: { pilot: pilotA([[244, { x: 1320, y: 1010, pose: 'standing' }]]) },
    init(c) { c.st = stars(c.fxw, 120, { y1: 700, seed: 43, r: 2.6 }); skyDot(c); },
    draw(t, c) { c.st(t, 1, 0.6); drawDot(c, t, 1); } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.5 } });
export const AUDIO = 'audio2/s11.wav';

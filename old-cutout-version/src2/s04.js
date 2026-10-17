// S04 — THE QUIET (5:00). Deep, empty space. Pip fades and the boy goes quiet. To cheer him up the sheep
// does a silly upside-down dance on its string; the boy laughs, and Pip flares gold. They discover it:
// laughter feeds the star's light. They fly on, laughing, leaving a little gold trail.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg } from './kit.js';
import { PARTY_ACTORS, partyInit, partyDraw } from './common.js';

const D = 300;
const subs = [
  [72.0, 74.6, 'It’s getting so dark in there.', '它里面越来越暗了。'],
  [98.0, 101.0, 'Hold on, little star.', '坚持住，小星星。'],
  [204.0, 206.6, 'Did you see that?', '你看见了吗？'],
  [214.0, 216.6, 'Do it again!', '再来一次！'],
  [234.0, 236.6, 'It’s the laughing!', '是笑声！'],
  [237.4, 241.0, 'Laughing makes it shine!', '笑声让它亮起来！'],
];

// Pip's light over the whole scene
const LIGHT = (t) => {
  let L = lerp(0.5, 0.18, ss((t - 30) / 100));
  L += 0.8 * env(t, 168, 188, 2, 6) + 0.6 * env(t, 222, 232, 0.6, 2.5) + 0.6 * env(t, 238, 300, 1.5, 0.1);
  return clamp(L, 0, 1);
};
const sad = (t) => ss((t - 60) / 10) * (1 - ss((t - 160) / 4));

const space = (c) => { c.st = stars(c.fxw, 50, { y1: 1206, seed: 31, r: 2 }); c.party = partyInit(c); c.trail = sparkles(c.fxw, 40, '#ffd978', 8); };

const shots = [
  // 1. Wide: a tiny party crossing the dark.
  { t0: 0, t1: 58, xf: 0, plate: 'B3_the_quiet', actors: PARTY_ACTORS(0.55),
    cam: [[0, { x: 1100, y: 600, z: 1.0 }], [58, { x: 1700, y: 580, z: 1.15 }]],
    init: space,
    draw(t, c) { c.st(t, 1); partyDraw(c, t, { x: lerp(500, 1900, t / 58), y: lerp(760, 640, t / 58), k: 0.55, light: LIGHT(t), pipFace: 'open' }); } },

  // 2. Medium: the light is fading. The boy goes quiet.
  { t0: 58, t1: 122, xf: 1.5, plate: 'B3_the_quiet', actors: PARTY_ACTORS(1),
    cam: [[58, { x: 1440, y: 560, z: 1.5 }], [90, { x: 1520, y: 560, z: 1.9 }], [110, { x: 1560, y: 560, z: 2.2 }], [122, { x: 1500, y: 560, z: 1.9 }]],
    init: space,
    draw(t, c) {
      c.st(t, 1);
      const s = sad(t);
      partyDraw(c, t, { x: 1500, y: 720, k: 1, light: LIGHT(t), pipFace: t > 80 ? 'closed' : 'open',
        boy: { head: 8 * s, face: t > 104 && t < 114 ? 'closed' : 'open', talk: env(t, 71.5, 75, 0.2, 0.2) + env(t, 97.5, 101.2, 0.2, 0.2) },
        sheep: { head: t > 108 ? -14 : 0 } });
    } },

  // 3. The silly dance: the sheep swings upside-down, legs kicking. The boy snorts, then laughs. Pip flares.
  { t0: 122, t1: 200, xf: 1.0, plate: 'B3_the_quiet', actors: PARTY_ACTORS(1),
    cam: [[122, { x: 1360, y: 600, z: 1.8 }], [150, { x: 1360, y: 620, z: 2.0 }], [166, { x: 1420, y: 600, z: 1.7 }], [184, { x: 1540, y: 560, z: 2.1 }], [200, { x: 1500, y: 580, z: 1.8 }]],
    init: space,
    draw(t, c) {
      c.st(t, 1);
      const flipU = ss((t - 132) / 3) * (1 - ss((t - 160) / 3));     // upside down
      const dance = env(t, 134, 160, 1, 1);
      const L = LIGHT(t);
      partyDraw(c, t, { x: 1500, y: 720, k: 1, light: L, pipFace: L > 0.5 ? 'open' : 'closed', pipLaugh: env(t, 170, 186, 0.5, 1),
        sheepRot: 180 * flipU + Math.sin(t * 5) * 18 * dance, sheepDy: -60 * flipU,
        sheep: { walk: dance * 1.4, head: Math.sin(t * 9) * 16 * dance, face: dance > 0.5 ? 'laughing' : 'open', tail: Math.sin(t * 12) * 40 * dance },
        boy: { head: lerp(8, 0, ss((t - 150) / 4)), face: t > 163 && t < 190 ? 'laughing' : 'open', laugh: env(t, 164, 190, 0.5, 1.5) } });
      c.trail(t, 1660, 600, env(t, 168, 190, 1, 3), 120);
    } },

  // 4. They notice. Again: the boy pulls a face, the sheep laughs, Pip glows.
  { t0: 200, t1: 262, xf: 1.0, plate: 'B3_the_quiet', actors: PARTY_ACTORS(1),
    cam: [[200, { x: 1460, y: 580, z: 2.0 }], [212, { x: 1600, y: 560, z: 2.6 }], [222, { x: 1560, y: 560, z: 2.3 }], [238, { x: 1460, y: 580, z: 2.0 }], [262, { x: 1500, y: 580, z: 1.8 }]],
    init: space,
    draw(t, c) {
      c.st(t, 1);
      const L = LIGHT(t);
      partyDraw(c, t, { x: 1500, y: 720, k: 1, light: L, pipFace: 'open', pipLaugh: env(t, 222, 232, 0.3, 1) + env(t, 240, 262, 1, 0.5),
        boy: { talk: env(t, 203.5, 206.8, 0.2, 0.2) + env(t, 213.5, 216.8, 0.2, 0.2) + env(t, 233.5, 241, 0.2, 0.2), face: t > 218 && t < 222 ? 'closed' : t > 238 ? 'laughing' : 'open', head: t > 218 && t < 222 ? Math.sin(t * 20) * 8 : 0, laugh: env(t, 241, 262, 1, 1) },
        sheep: { face: t > 221 && t < 233 || t > 240 ? 'laughing' : 'open', laugh: env(t, 221, 233, 0.4, 1) + env(t, 240, 262, 1, 1) } });
      c.trail(t, 1660, 600, env(t, 222, 234, 0.5, 2) + env(t, 240, 262, 1, 1), 120);
    } },

  // 5. On they fly, laughing; a little gold trail behind them. Wide.
  { t0: 262, t1: 300, xf: 1.5, plate: 'B3_the_quiet', actors: PARTY_ACTORS(0.6),
    cam: [[262, { x: 1300, y: 600, z: 1.3 }], [300, { x: 1700, y: 580, z: 1.0 }]],
    init(c) { space(c); c.gold = svg(c.fxw, 'path', { fill: 'none', stroke: '#ffd978', 'stroke-width': 6, 'stroke-linecap': 'round', opacity: 0.55, 'stroke-dasharray': '2 22' }); },
    draw(t, c) {
      c.st(t, 1);
      const x = lerp(900, 2300, (t - 262) / 38), y = lerp(700, 520, (t - 262) / 38);
      const P = partyDraw(c, t, { x, y, k: 0.6, light: 1, pipFace: 'open', pipLaugh: 1, boy: { laugh: 0.8, face: 'laughing' }, sheep: { laugh: 0.8, face: 'laughing' } });
      const pts = []; for (let k = 0; k <= 20; k++) { const u = k / 20, xx = P.pip[0] - u * 900, yy = P.pip[1] + u * 140 + Math.sin(u * 9 + t) * 20; pts.push(`${xx.toFixed(0)} ${yy.toFixed(0)}`); }
      c.gold.setAttribute('d', 'M' + pts.join(' L'));
      c.trail(t, P.pip[0] - 60, P.pip[1] + 20, 1, 70);
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s04.wav';

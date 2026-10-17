// S06 — THE CLOUD (5:00). A small planet in endless soft rain. A lonely cloud cries because nobody plays
// with her. She thinks the sheep is a baby cloud. They play chase; she laughs; the rain stops; a rainbow.
// Pip shines gold. A little rainbow follows them for a while.
import { makeScene, ss, env, clamp, lerp, sparkles, svg, rain } from './kit.js';
import { BOY, SHEEP, PIP, PARTY_ACTORS, BOXDEF, partyInit, partyDraw } from './common.js';

const D = 300;
const CL = 300;
const WET = { f: 'brightness(.95) saturate(.9)', af: 'brightness(.88) saturate(.8) hue-rotate(-4deg)' };
const subs = [
  [62.0, 64.6, 'Oh! Who are you?', '哦！你是谁呀？', 'it'],
  [72.0, 75.0, 'A little cloud!', '一朵小云！', 'it'],
  [76.0, 79.0, 'Are you lost too?', '你也迷路了吗？', 'it'],
  [92.0, 95.6, 'Nobody ever plays with me.', '从来没有人陪我玩。', 'it'],
  [104.0, 106.6, 'Go on. Play with her.', '去吧，陪她玩。'],
  [128.0, 130.0, 'Tag! You’re it!', '抓到你了！该你了！', 'it'],
  [252.0, 255.0, 'Come back and play!', '再回来玩呀！', 'it'],
];
const RAIN = (t) => 1 - ss((t - 190) / 14);
const LIGHT = (t) => clamp(0.92 - 0.35 * ss((t - 8) / 30) + 0.45 * ss((t - 196) / 10));

const rainy = (c) => { c.rain = rain(c.fxs, 160); c.drip = rain(c.fxs, 40, 'rgba(240,245,255,.35)'); };

const shots = [
  // 1. Down into the rain.
  { t0: 0, t1: 50, xf: 0, plate: 'B5_cloud_planet_rain', grade: [[0, WET]], actors: PARTY_ACTORS(0.8),
    cam: [[0, { x: 1440, y: 480, z: 1.0 }], [34, { x: 1440, y: 640, z: 1.2 }], [50, { x: 1440, y: 680, z: 1.35 }]],
    init(c) { rainy(c); c.party = partyInit(c); },
    draw(t, c) {
      c.rain(t, 1); c.drip(t * 0.7, 0.7);
      const u = ss(t / 32);
      partyDraw(c, t, { x: lerp(1100, 1440, u), y: lerp(260, 880, u), k: 0.8, light: LIGHT(t), pipFace: t > 30 ? 'closed' : 'open', strOp: 1 - ss((t - 40) / 3), boy: { head: 6 * ss((t - 34) / 3) } });
    } },

  // 2. The cloud drifts over, raining. She thinks the sheep is a baby cloud.
  { t0: 50, t1: 112, xf: 1.0, plate: 'B5_cloud_planet_rain', grade: [[0, WET]],
    cam: [[50, { x: 1440, y: 620, z: 1.3 }], [66, { x: 1340, y: 640, z: 1.6 }], [80, { x: 1300, y: 660, z: 1.75 }], [96, { x: 1440, y: 600, z: 1.45 }], [112, { x: 1440, y: 620, z: 1.4 }]],
    actors: {
      boy: { char: 'C6', h: BOY * 0.8, z: 3, track: [[50, { x: 1500, y: 880, head: 6 }], [70, { head: 0 }], [80, { face: 'laughing', laugh: 1 }], [86, { laugh: 0, face: 'open' }], [103.5, { talk: 1, armR: -40 }], [107, { talk: 0, armR: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.8, z: 4, track: [[50, { x: 1330, y: 905, flip: -1 }], [62, { head: -10 }], [74, { head: -14 }], [79, { flip: -1 }], [80, { flip: 1, head: 0 }], [82, { flip: -1 }], [83, { flip: 1 }], [85, { flip: -1, head: -14 }], [100, { head: -6 }]] },
      box: BOXDEF(88, { z: 2, track: [[50, { x: 1640, y: 900, glow: 0.57 }]] }),
      pip: { char: 'C1', h: PIP * 0.8, z: 6, top: true, glow: { r: 2.4 }, track: [[50, { x: 1640, y: 830, light: 0.57, face: 'closed' }]] },
      cloud: { char: 'C4', h: CL, z: 1, track: [[50, { x: 600, y: 300, mood: 'sad', rain: 1, flip: 1 }], [70, { x: 1150, y: 420 }], [74, { rot: -6 }], [80, { rot: 4 }], [86, { x: 1190, y: 440, rot: 0 }], [112, { x: 1230, y: 430 }]] },
    },
    init(c) { rainy(c); },
    draw(t, c) { c.rain(t, 1); c.drip(t * 0.7, 0.7); const p = c.actors.cloud.last; c.actors.cloud.el.style.transform += ` translateY(${(Math.sin(t * 1.2) * 10).toFixed(1)}px)`; } },

  // 3. Chase! Round and round the little planet; the rain breaks up in patches.
  { t0: 112, t1: 186, xf: 1.0, plate: 'B5_cloud_planet_rain', grade: [[0, WET]],
    cam: [[112, { x: 1440, y: 620, z: 1.35 }], [140, { x: 1440, y: 600, z: 1.2 }], [160, { x: 1300, y: 640, z: 1.5 }], [186, { x: 1440, y: 620, z: 1.3 }]],
    actors: {
      boy: { char: 'C6', h: BOY * 0.8, z: 3, poses: ['laughing'], track: [[112, { x: 1500, y: 880, pose: 'rig' }], [126, { pose: 'laughing' }]] },
      sheep: { char: 'C5', h: SHEEP * 0.8, z: 4, wspeed: 12, track: [[112, { x: 1330, y: 905, flip: -1 }]] },
      cloud: { char: 'C4', h: CL, z: 1, track: [[112, { x: 1230, y: 430, mood: 'sad', rain: 1 }]] },
      box: BOXDEF(88, { z: 2, track: [[112, { x: 1640, y: 900, glow: 0.57 }]] }),
      pip: { char: 'C1', h: PIP * 0.8, z: 6, top: true, glow: { r: 2.4 }, track: [[112, { x: 1640, y: 830, light: 0.57, face: 'open' }], [150, { laugh: 1 }]] },
    },
    init(c) { rainy(c); },
    draw(t, c) {
      const k = clamp((t - 116) / 4), r = RAIN(t) * (1 - 0.4 * env(t, 150, 186, 4, 1));
      c.rain(t, r); c.drip(t * 0.7, r * 0.7);
      // the sheep runs a loop round the boy; the cloud chases it, then they swap
      const a = (t - 116) * 0.55, run = k * env(t, 116, 184, 1, 2);
      const sx = lerp(1330, 1440 + Math.cos(a) * 520, run), sy = lerp(905, 880 + Math.sin(a) * 70, run);
      const fl = -Math.sin(a) >= 0 ? -1 : 1;
      const jump = Math.abs(Math.sin(t * 4)) * 50 * run;
      c.actors.sheep.render({ x: sx, y: sy - jump, flip: run > 0.1 ? fl : -1, walk: run * 1.2, face: t > 124 ? 'laughing' : 'open', tail: 20 }, t);
      const b = a - 0.9;
      const cx = lerp(1230, 1440 + Math.cos(b) * 560, run), cy = lerp(430, 520 + Math.sin(b) * 60, run) + Math.sin(t * 1.4) * 14;
      c.actors.cloud.render({ x: cx, y: cy, mood: t > 150 ? 'happy' : 'sad', rain: RAIN(t) * (t > 150 ? 0.4 : 1), flip: fl, rot: Math.sin(t * 2) * 5 * run }, t);
    } },

  // 4. She laughs. The rain stops. The sun comes; a rainbow. Pip blazes gold.
  { t0: 186, t1: 244, xf: 1.0, plates: ['B5_cloud_planet_rain', 'B5_cloud_planet_after_rain'], plateMix: [[190, { m: 0 }], [204, { m: 1 }]], grade: [[186, WET], [204, { f: '', af: '' }]],
    cam: [[186, { x: 1300, y: 600, z: 1.5 }], [200, { x: 1400, y: 520, z: 1.2 }], [216, { x: 1440, y: 500, z: 1.05 }], [230, { x: 1500, y: 680, z: 1.5 }], [244, { x: 1500, y: 700, z: 1.6 }]],
    actors: {
      cloud: { char: 'C4', h: CL, z: 1, track: [[186, { x: 1200, y: 470, mood: 'happy', rain: 0.4, laugh: 1 }], [196, { rain: 0 }], [212, { x: 1150, y: 400, laugh: 1 }], [226, { laugh: 0.3 }]] },
      boy: { char: 'C6', h: BOY * 0.8, z: 3, poses: ['laughing'], track: [[186, { x: 1500, y: 880, pose: 'laughing' }]] },
      sheep: { char: 'C5', h: SHEEP * 0.8, z: 4, track: [[186, { x: 1330, y: 905, flip: -1, face: 'laughing', laugh: 1 }], [214, { laugh: 0.3 }]] },
      box: BOXDEF(88, { z: 2, track: [[186, { x: 1640, y: 900, glow: 0.6 }], [206, { glow: 1 }]] }),
      pip: { char: 'C1', h: PIP * 0.8, z: 6, top: true, glow: { r: 2.6 }, track: [[186, { x: 1640, y: 830, light: 0.6, laugh: 1 }], [206, { light: 1 }]] },
    },
    init(c) { rainy(c); c.sp = sparkles(c.fxw, 30, '#ffe08a', 4); },
    draw(t, c) { const r = RAIN(t); c.rain(t, r); c.drip(t * 0.7, r * 0.7); c.sp(t, 1640, 820, env(t, 200, 230, 2, 4), 120); c.actors.cloud.el.style.transform += ` translateY(${(Math.sin(t * 1.2) * 10).toFixed(1)}px)`; } },

  // 5. Goodbye. Up and away; a little rainbow follows for a while.
  { t0: 244, t1: 300, xf: 1.0, plate: 'B5_cloud_planet_after_rain', actors: { ...PARTY_ACTORS(0.8),
      cloud: { char: 'C4', h: CL, z: 1, track: [[244, { x: 1150, y: 430, mood: 'happy', rain: 0 }], [250, { rot: -8 }], [252, { rot: 8 }], [254, { rot: -8 }], [256, { rot: 0 }], [266, { x: 1250, y: 330 }], [300, { x: 1400, y: 220 }]] } },
    cam: [[244, { x: 1450, y: 640, z: 1.5 }], [262, { x: 1450, y: 600, z: 1.4 }], [300, { x: 1500, y: 470, z: 1.05 }]],
    init(c) {
      c.party = partyInit(c);
      c.bow = ['#e88a8a', '#efb877', '#ede07e', '#8fcf8a', '#86b3e3', '#a693d8'].map((col) => svg(c.fxw, 'path', { fill: 'none', stroke: col, 'stroke-width': 9, opacity: 0.6, 'stroke-linecap': 'round' }));
    },
    draw(t, c) {
      const u = ss((t - 258) / 36);
      const P = partyDraw(c, t, { x: lerp(1460, 1900, u), y: lerp(880, -80, u), k: 0.8, light: 1, pipFace: 'open', pipLaugh: 0.5, strOp: ss((t - 256) / 2.5),
        boy: { armR: lerp(-60, -150, ss((t - 256) / 2)) } });
      const bx = P.pip[0] - 60, by = P.pip[1] + 40, a = env(t, 262, 300, 3, 0.1);
      c.bow.forEach((p, i) => { const r = 120 - i * 9; p.setAttribute('d', `M${bx - r} ${by} A${r} ${r} 0 0 1 ${bx + r} ${by}`); p.setAttribute('opacity', (0.55 * a).toFixed(3)); });
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s06.wav';

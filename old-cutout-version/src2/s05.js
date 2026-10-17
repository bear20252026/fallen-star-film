// S05 — THE CLOCKMAKER (5:00). A planet of clocks at sunset. A tiny old man winds them all and never stops.
// The sheep tries to help and gets its tail stuck in the big gear: everything stops. Nothing bad happens.
// He has a free minute, sees the sunset for the first time in years, and laughs. Pip brightens. A gift.
import { makeScene, ss, env, clamp, lerp, sparkles, svg } from './kit.js';
import { BOY, SHEEP, PIP, INK, WATCH, svgProp, PARTY_ACTORS, BOXDEF, partyInit, partyDraw } from './common.js';

const D = 300;
const CM = BOY * 0.62;
const GEAR = { x: 2160, y: 900 };
const gearSvg = () => {
  let d = ''; const n = 14, R = 120, r = 100;
  for (let i = 0; i < n; i++) {
    const a0 = (i / n) * Math.PI * 2, a1 = a0 + Math.PI / n * 0.5, a2 = a0 + Math.PI / n, a3 = a0 + Math.PI / n * 1.5;
    const P = (a, rr) => `${(Math.cos(a) * rr).toFixed(1)} ${(Math.sin(a) * rr).toFixed(1)}`;
    d += (i ? ' L' : 'M') + P(a0, r) + ' L' + P(a1, R) + ' L' + P(a2, R) + ' L' + P(a3, r);
  }
  return `<path d="${d}Z" fill="#d1a24c" stroke="${INK}" stroke-width="5"/><circle r="62" fill="#b9873a" stroke="${INK}" stroke-width="4"/>
   ${[0, 1, 2, 3, 4, 5].map((i) => `<path d="M0 0 L${(Math.cos(i) * 60).toFixed(1)} ${(Math.sin(i) * 60).toFixed(1)}" stroke="#e8c27a" stroke-width="10"/>`).join('')}
   <circle r="20" fill="#e3b860" stroke="${INK}" stroke-width="4"/><path d="M-80 -40 A90 90 0 0 1 -20 -88" fill="none" stroke="#f7e1a6" stroke-width="7" opacity=".7"/>`;
};
const GEARP = svgProp(260, 260, 130, 130, gearSvg());

const subs = [
  [47.0, 49.6, 'Hello! Excuse me…', '你好！打扰一下……'],
  [55.0, 58.6, 'No time, no time!', '没时间，没时间！', 'it'],
  [59.4, 62.6, 'If I stop, they stop!', '我一停，它们就停了！', 'it'],
  [80.0, 83.4, 'Seven hundred clocks, and only one of me!', '七百座钟，只有我一个人！', 'it'],
  [112.0, 114.6, 'We’ll help!', '我们来帮忙！'],
  [160.0, 162.4, 'Oh dear.', '哎呀。'],
  [176.0, 178.4, 'Nothing… happened.', '什么……都没发生。', 'it'],
  [186.0, 188.0, 'Oh.', '哦。', 'it'],
  [189.0, 192.6, 'I forgot it was so pretty.', '我都忘了，它这么美。', 'it'],
  [248.0, 251.6, 'For when you need a minute.', '等你需要一分钟的时候用。', 'it'],
  [254.0, 256.0, 'Thank you!', '谢谢您！'],
];

const LIGHT = (t) => clamp(0.4 + 0.5 * ss((t - 196) / 10) + 0.1 * ss((t - 236) / 6));

const shots = [
  // 1. The party floats down onto a planet of clocks at sunset.
  { t0: 0, t1: 40, xf: 0, plate: 'B4_clockmaker_planet', actors: PARTY_ACTORS(0.75),
    cam: [[0, { x: 1440, y: 500, z: 1.0 }], [30, { x: 1440, y: 620, z: 1.15 }], [40, { x: 1440, y: 650, z: 1.2 }]],
    init(c) { c.party = partyInit(c); },
    draw(t, c) {
      const u = ss(t / 30);
      partyDraw(c, t, { x: lerp(1800, 1460, u), y: lerp(250, 860, u), k: 0.75, light: 0.42, pipFace: 'open', strOp: 1 - ss((t - 34) / 3) });
    } },

  // 2. The clockmaker rushes from clock to clock. No time to talk.
  { t0: 40, t1: 110, xf: 1.0, plate: 'B4_clockmaker_planet',
    cam: [[40, { x: 1300, y: 760, z: 1.5 }], [56, { x: 1150, y: 780, z: 1.9 }], [66, { x: 1300, y: 760, z: 1.5 }], [80, { x: 1550, y: 780, z: 1.8 }], [96, { x: 1400, y: 760, z: 1.45 }], [110, { x: 1400, y: 760, z: 1.45 }]],
    actors: {
      boy: { char: 'C6', h: BOY * 0.75, z: 4, track: [[40, { x: 1460, y: 860 }], [46.5, { talk: 1, armR: -30 }], [50, { talk: 0, armR: 0 }], [66, { x: 1460, y: 860, head: 0 }], [72, { head: 8 }], [76, { head: -8 }], [80, { head: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.75, z: 5, track: [[40, { x: 1330, y: 880, flip: -1 }], [56, { head: 10 }], [60, { head: -10 }], [70, { head: 10, flip: 1 }], [78, { head: -10, flip: -1 }], [84, { head: 0 }]] },
      box: BOXDEF(82, { z: 3, track: [[40, { x: 1590, y: 870, glow: 0.42 }]] }),
      pip: { char: 'C1', h: PIP * 0.75, z: 6, top: true, glow: { r: 2.4 }, track: [[40, { x: 1590, y: 805, light: 0.42 }]] },
      cm: { char: 'C3', h: CM, z: 2, wspeed: 14, track: [
        [40, { x: 1000, y: 850, wind: 1, flip: 1, walk: 0 }], [46, { x: 1000, wind: 1, walk: 0 }], [46.1, { wind: 0, walk: 1 }], [50, { x: 1250, y: 840, walk: 1, flip: -1 }], [50.1, { x: 1250, walk: 0, wind: 1 }],
        [54, { x: 1250, wind: 1, talk: 0 }], [54.5, { x: 1250, wind: 0, talk: 1 }], [63, { x: 1250, talk: 0, walk: 0 }], [63.1, { x: 1250, wind: 0, walk: 1 }], [66, { x: 1800, y: 860, walk: 1, flip: -1 }], [66.1, { x: 1800, walk: 0, wind: 1 }],
        [72, { x: 1800, wind: 1, walk: 0 }], [72.1, { x: 1800, wind: 0, walk: 1 }], [75, { x: 2050, y: 880, walk: 1 }], [75.1, { x: 2050, walk: 0, wind: 1 }], [79, { x: 2050, wind: 1 }], [79.1, { x: 2050, wind: 0, talk: 1 }],
        [84, { x: 2050, talk: 0, walk: 0 }], [84.1, { x: 2050, walk: 1, flip: 1 }], [86, { x: 1700, y: 860, walk: 1, flip: 1 }], [86.1, { x: 1700, walk: 0, wind: 1 }], [92, { x: 1700, wind: 1, walk: 0 }], [92.1, { x: 1700, wind: 0, walk: 1 }], [96, { x: 1100, y: 850, walk: 1 }], [96.1, { x: 1100, walk: 0, wind: 1 }],
        [102, { x: 1100, wind: 1, walk: 0 }], [102.1, { x: 1100, wind: 0, walk: 1, flip: -1 }], [106, { x: 1500, y: 870, walk: 1, flip: -1 }], [110, { x: 1900, y: 880, walk: 1 }]] },
    },
    init(c) { c.sp = sparkles(c.fxw, 8, '#f6dc9a', 4); },
    draw(t, c) { const p = c.actors.cm.last; if (p && p.wind) c.sp(t, p.x, p.y - 80, 0.6, 30); else c.sp(t, 0, 0, 0); } },

  // 3. The sheep "helps": it backs into the big gear. Its tail gets caught. Everything stops.
  { t0: 110, t1: 172, xf: 1.0, plate: 'B4_clockmaker_planet',
    cam: [[110, { x: 1800, y: 780, z: 1.4 }], [130, { x: 1950, y: 800, z: 1.6 }], [146, { x: 2080, y: 830, z: 2.2 }], [156, { x: 2100, y: 830, z: 2.4 }], [164, { x: 1950, y: 800, z: 1.6 }], [172, { x: 1900, y: 790, z: 1.5 }]],
    actors: {
      gear: { h: 1, z: 1, init: GEARP, k: 1, track: [[110, { x: GEAR.x, y: GEAR.y - 40 }]] },
      boy: { char: 'C6', h: BOY * 0.75, z: 4, track: [[110, { x: 1600, y: 870, talk: 0 }], [111.6, { talk: 1, armR: -40 }], [115, { talk: 0, armR: 0 }], [150, { head: 0 }], [152, { head: 8 }], [159.5, { talk: 1 }], [162.6, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.75, z: 5, track: [[110, { x: 1700, y: 890, flip: -1 }], [126, { x: 1980, y: 900, walk: 1, flip: -1 }], [127, { walk: 0 }],
        [132, { head: 10 }], [136, { head: -6, flip: 1 }], [140, { x: 2050, y: 900, walk: 0.5, flip: 1, tail: 0 }], [143, { x: 2080, y: 898, walk: 0.5, tail: 0 }], [144, { walk: 0, tail: 30, face: 'closed', rot: -4 }], [146, { tail: 32, rot: 6, x: 2075 }], [148, { rot: -6, x: 2085 }], [150, { rot: 0, face: 'open', head: -14 }], [160, { head: 6 }]] },
      cm: { char: 'C3', h: CM, z: 2, wspeed: 14, track: [[110, { x: 2350, y: 900, wind: 1, flip: 1 }], [144, { wind: 1 }], [145.5, { wind: 0, rot: 0 }], [146, { rot: -6 }], [170, { rot: -6 }]] },
    },
    draw(t, c) {
      const stopT = 144.5, ang = t < stopT ? t * 40 : stopT * 40 + 6 * (1 - Math.exp(-(t - stopT) * 3)) * Math.sin((t - stopT) * 20);
      c.actors.gear.el.style.transform += ` rotate(${ang.toFixed(2)}deg)`;
    } },

  // 4. Silence. He has a free minute. He looks up: the sunset. He laughs for the first time in years.
  { t0: 172, t1: 238, xf: 1.2, plate: 'B4_clockmaker_planet',
    cam: [[172, { x: 2200, y: 800, z: 2.4 }], [184, { x: 2150, y: 780, z: 2.2 }], [196, { x: 1900, y: 700, z: 1.4 }], [212, { x: 1880, y: 680, z: 1.3 }], [222, { x: 2140, y: 800, z: 2.2 }], [238, { x: 2000, y: 780, z: 1.7 }]],
    actors: {
      cm: { char: 'C3', h: CM, z: 2, track: [[172, { x: 2240, y: 890, flip: 1, rot: -6, head: 0, wind: 0 }], [176, { rot: 0, talk: 1 }], [178.6, { talk: 0, head: -6 }], [185.5, { head: -12, talk: 1 }], [192.8, { talk: 0 }], [200, { laugh: 0 }], [202, { laugh: 1 }], [222, { laugh: 1 }], [226, { laugh: 0, head: 0 }]] },
      sheep: { char: 'C5', h: SHEEP * 0.75, z: 5, track: [[172, { x: 2085, y: 898, flip: 1, head: -10 }], [200, { head: 0 }], [204, { face: 'laughing', laugh: 1 }], [222, { laugh: 0, face: 'open' }]] },
      boy: { char: 'C6', h: BOY * 0.75, z: 4, track: [[172, { x: 1880, y: 880 }], [203, { face: 'laughing', laugh: 1 }], [222, { laugh: 0, face: 'open' }]] },
      box: BOXDEF(82, { z: 3, track: [[172, { x: 1980, y: 910, glow: 0.42 }], [196, { glow: 0.42 }], [206, { glow: 0.92 }]] }),
      pip: { char: 'C1', h: PIP * 0.75, z: 6, top: true, glow: { r: 2.6 }, track: [[172, { x: 1980, y: 845, light: 0.42 }], [196, { light: 0.42 }], [206, { light: 0.92, laugh: 1 }], [224, { laugh: 0 }]] },
    },
    init(c) { c.sp = sparkles(c.fxw, 28, '#ffe08a', 7); },
    draw(t, c) { c.sp(t, 1980, 840, env(t, 202, 222, 1, 3), 110); } },

  // 5. The gift, and goodbye. Up they go; he waves.
  { t0: 238, t1: 300, xf: 1.0, plate: 'B4_clockmaker_planet', actors: { ...PARTY_ACTORS(0.75),
      cm: { char: 'C3', h: CM, z: 2, track: [[238, { x: 2100, y: 890, flip: 1 }], [247.6, { talk: 1, armR: -20 }], [251.8, { talk: 0, armR: 0 }], [266, { armR: 0 }], [268, { armR: -100 }], [270, { armR: -70 }], [272, { armR: -100 }], [274, { armR: -70 }], [276, { armR: -100 }], [278, { armR: -70 }]] },
      watch: { h: 1, z: 7, init: WATCH, k: 0.6, track: [[238, { x: 2050, y: 820, op: 1 }], [250, { x: 2050, y: 820 }], [253, { x: 1980, y: 740 }], [258, { op: 1 }], [259, { op: 0 }]] } },
    cam: [[238, { x: 2000, y: 760, z: 1.9 }], [260, { x: 1980, y: 750, z: 1.8 }], [272, { x: 1800, y: 640, z: 1.3 }], [300, { x: 1600, y: 500, z: 1.05 }]],
    init(c) { c.party = partyInit(c); c.sp = sparkles(c.fxw, 20, '#ffe08a', 9); },
    draw(t, c) {
      const u = ss((t - 262) / 30);
      const P = partyDraw(c, t, { x: lerp(1900, 1400, u), y: lerp(880, -150, u), k: 0.75, light: 0.92, pipFace: 'open', flip: 1,
        strOp: ss((t - 258) / 3), boy: { talk: env(t, 253.6, 256.4, 0.2, 0.2), armR: lerp(0, -150, ss((t - 258) / 3)), armL: lerp(0, 10, ss((t - 258) / 3)) } });
      c.sp(t, P.pip[0], P.pip[1], u > 0 ? 1 : 0, 60);
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s05.wav';

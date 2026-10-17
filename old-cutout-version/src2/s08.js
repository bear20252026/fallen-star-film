// S08 — THE DARK PLANET (5:00). The sheep goes on alone across a cold dark planet and finds Moth curled up,
// hugging the lantern like a hot-water bottle. Moth isn't a monster: he is cold and lonely, and because he
// is sad, Pip is fading. The sheep snuggles up to him; it tickles; Moth laughs, and Pip glows again.
// Moth gives the lantern back and asks to come along. The boy arrives. They all fly off on Moth's back.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, birds, strand, glowDot } from './kit.js';
import { BOY, SHEEP, PIP, MOTH, BOXDEF } from './common.js';

const D = 300;
const DARK = { f: 'brightness(.9)', af: 'brightness(.78) saturate(.75) hue-rotate(10deg)' };
const MO = { x: 2120, y: 900 };     // where Moth is curled up
const subs = [
  [18.0, 21.0, 'I’ll wait here with the birds.', '我和小鸟在这儿等你。'],
  [22.0, 24.6, 'Be careful, sheep.', '小心点，小羊。'],
  [136.0, 138.6, 'It’s so cold here.', '这里好冷。', 'it'],
  [140.0, 143.6, 'I only wanted a little light.', '我只是想要一点点光。', 'it'],
  [148.0, 151.4, 'But the more I hold it, the dimmer it gets.', '可是我抱得越紧，它就越暗。', 'it'],
  [250.0, 252.6, 'Can I come with you?', '我能跟你们一起去吗？', 'it'],
  [253.4, 256.0, 'I’ll carry you.', '我来驮你们。', 'it'],
  [266.0, 268.6, 'Sheep! You found it!', '小羊！你找到它了！'],
];

const mothA = (track) => ({ char: 'C2', h: MOTH, z: 2, flapSpeed: 5, breath: 2, track });

const shots = [
  // 1. Two birds set them down on the dark planet. The boy stays; the sheep goes on.
  { t0: 0, t1: 32, xf: 0, plate: 'B6_moth_dark_planet', grade: [[0, DARK]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, track: [[0, { x: 700, y: 300, armR: -150 }], [12, { x: 760, y: 900, armR: -150 }, 'out'], [14, { armR: 0 }], [17.6, { talk: 1 }], [24.8, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[0, { x: 900, y: 360, flip: -1 }], [12.5, { x: 920, y: 925 }, 'out'], [26, { x: 920, y: 925, head: 8 }], [27, { head: -6 }], [28, { head: 8 }], [29, { head: 0 }], [30, { x: 980, y: 925, walk: 1 }]] },
    },
    cam: [[0, { x: 1000, y: 600, z: 1.2 }], [14, { x: 900, y: 760, z: 1.6 }], [32, { x: 900, y: 760, z: 1.7 }]],
    init(c) { c.b = birds(c.fxw, 2); c.s1 = strand(c.fxw); c.s2 = strand(c.fxw); },
    draw(t, c) {
      const B = c.actors.boy.last, S = c.actors.sheep.last, up = ss((t - 14) / 4);
      const p1 = [B.x + 70, B.y - 470 + up * 120], p2 = [S.x, S.y - 400 + up * 140];
      c.b(t, [{ x: p1[0], y: p1[1], s: 1 }, { x: p2[0], y: p2[1], s: 1 }]);
      c.s1(p1[0], p1[1] + 6, B.x + 70, B.y - 205, 10, 1 - up); c.s2(p2[0], p2[1] + 6, S.x, S.y - 125, 10, 1 - up);
    } },

  // 2. The sheep walks alone across the dark. Dead trees. Very quiet.
  { t0: 32, t1: 84, xf: 1.2, plate: 'B6_moth_dark_planet', grade: [[0, DARK]],
    actors: { sheep: { char: 'C5', h: SHEEP, z: 4, wspeed: 6, track: [[32, { x: 700, y: 900, walk: 1, flip: -1 }], [56, { x: 1300, y: 850, walk: 1 }], [57, { walk: 0, head: -10 }], [61, { head: 8 }], [63, { head: 0, walk: 1, x: 1300 }], [84, { x: 1850, y: 880, walk: 1 }]] } },
    cam: [[32, { x: 800, y: 700, z: 1.5 }], [56, { x: 1300, y: 700, z: 1.5 }], [62, { x: 1300, y: 640, z: 1.25 }], [84, { x: 1800, y: 700, z: 1.5 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 520, seed: 51 }); },
    draw(t, c) { c.st(t, 0.8); } },

  // 3. Moth, curled up, hugging the lantern. Pip almost grey.
  { t0: 84, t1: 132, xf: 1.0, plate: 'B6_moth_dark_planet', grade: [[0, DARK]],
    actors: {
      moth: mothA([[84, { x: MO.x, y: MO.y - 160, wings: 'folded', mood: 'sad', rot: 0 }]]),
      box: BOXDEF(90, { z: 3, track: [[84, { x: MO.x, y: MO.y - 40, glow: 0.22 }]] }),
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.2 }, track: [[84, { x: MO.x, y: MO.y - 112, light: 0.2, face: 'closed' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[84, { x: 1700, y: 890, walk: 1, flip: -1 }], [96, { x: 1880, y: 895, walk: 0.5 }], [97, { walk: 0, head: 12 }], [110, { head: 4 }], [118, { x: 1930, y: 895, walk: 0.4 }], [119, { walk: 0 }]] },
    },
    cam: [[84, { x: 1900, y: 740, z: 1.6 }], [100, { x: 2000, y: 720, z: 1.9 }], [116, { x: 2060, y: 710, z: 2.1 }], [132, { x: 2060, y: 710, z: 2.05 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 520, seed: 51 }); },
    draw(t, c) { c.st(t, 0.8); c.actors.moth.el.style.transform += ` translateX(${(Math.sin(t * 30) * 1.5).toFixed(2)}px)`; } },

  // 4. He isn't a monster. He is cold.
  { t0: 132, t1: 182, xf: 0.8, plate: 'B6_moth_dark_planet', grade: [[0, DARK]],
    actors: {
      moth: mothA([[132, { x: MO.x, y: MO.y - 160, wings: 'folded', mood: 'sad' }], [134, { mood: 'surprised' }], [135.6, { mood: 'sad', talk: 1 }], [152, { talk: 0, head: -6 }]]),
      box: BOXDEF(90, { z: 3, track: [[132, { x: MO.x, y: MO.y - 40, glow: 0.2 }]] }),
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.2 }, track: [[132, { x: MO.x, y: MO.y - 112, light: 0.2, face: 'closed' }], [182, { light: 0.15 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sitting'], track: [[132, { x: 1930, y: 895, flip: -1, head: 0 }], [160, { head: 6 }], [168, { pose: 'rig' }], [169, { pose: 'sitting', x: 1945 }]] },
    },
    cam: [[132, { x: 2090, y: 690, z: 2.15 }], [150, { x: 2100, y: 690, z: 2.25 }], [164, { x: 2040, y: 720, z: 1.9 }], [182, { x: 2050, y: 715, z: 2.0 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 520, seed: 51 }); },
    draw(t, c) { c.st(t, 0.8); c.actors.moth.el.style.transform += ` translateX(${(Math.sin(t * 30) * 1.5).toFixed(2)}px)`; } },

  // 5. The sheep snuggles up; wool on fur; it tickles. Moth giggles, then laughs. Pip glows again.
  { t0: 182, t1: 242, xf: 1.0, plate: 'B6_moth_dark_planet', grade: [[182, DARK], [230, { f: 'brightness(1.05) saturate(1.05)', af: 'brightness(.95) saturate(.95)' }]],
    actors: {
      moth: mothA([[182, { x: MO.x, y: MO.y - 160, wings: 'folded', mood: 'sad' }], [196, { mood: 'surprised' }], [202, { mood: 'laughing', laugh: 0.4 }], [210, { laugh: 1 }], [228, { laugh: 1, wings: 'folded' }], [230, { wings: 'open' }], [234, { laugh: 0.4 }]]),
      box: BOXDEF(90, { z: 3, track: [[182, { x: MO.x, y: MO.y - 40, glow: 0.15 }], [204, { glow: 0.2 }], [222, { glow: 0.9 }]] }),
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.6 }, track: [[182, { x: MO.x, y: MO.y - 112, light: 0.15, face: 'closed' }], [204, { light: 0.2 }], [208, { face: 'open' }], [222, { light: 0.9, laugh: 1 }], [236, { laugh: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[182, { x: 1945, y: 895, flip: -1 }], [190, { x: 2010, y: 890, walk: 0.4 }], [191, { walk: 0, rot: 6, head: 10 }], [194, { rot: -4, x: 2025 }], [196, { rot: 6 }], [198, { rot: -4 }], [200, { rot: 4, face: 'closed' }], [206, { rot: 0, face: 'laughing', laugh: 1 }], [230, { laugh: 0.5 }]] },
    },
    cam: [[182, { x: 2050, y: 715, z: 2.0 }], [200, { x: 2080, y: 700, z: 2.2 }], [214, { x: 2100, y: 700, z: 2.05 }], [230, { x: 2050, y: 700, z: 1.6 }], [242, { x: 2000, y: 700, z: 1.5 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 520, seed: 51 }); c.sp = sparkles(c.fxw, 30, '#ffe08a', 3); c.warm = glowDot(c.fxw, 'w85', '#ffcf7a'); },
    draw(t, c) {
      c.st(t, 0.8 + 0.4 * ss((t - 222) / 8));
      c.sp(t, MO.x, MO.y - 120, env(t, 214, 242, 2, 1), 150);
      c.warm.setAttribute('cx', MO.x); c.warm.setAttribute('cy', MO.y - 120); c.warm.setAttribute('r', (380 * ss((t - 214) / 14)).toFixed(1)); c.warm.setAttribute('opacity', 0.35);
    } },

  // 6. He gives the lantern back. "Can I come with you?" The boy arrives. Off they go on Moth's back.
  { t0: 242, t1: 300, xf: 1.0, plate: 'B6_moth_dark_planet', grade: [[0, { f: 'brightness(1.05) saturate(1.05)', af: 'brightness(.95) saturate(.95)' }]],
    actors: {
      moth: mothA([[242, { x: MO.x, y: MO.y - 160, wings: 'open', mood: 'laughing', flap: 0 }], [249.6, { mood: 'surprised', talk: 1 }], [256.2, { talk: 0, mood: 'laughing' }], [278, { x: MO.x, y: MO.y - 160, flap: 0 }], [278.5, { flap: 1 }], [300, { x: 2500, y: -100, flap: 1, rot: 10 }, 'in']]),
      box: BOXDEF(80, { z: 6, track: [[242, { x: MO.x, y: MO.y - 40, glow: 0.92 }], [246, { x: MO.x, y: MO.y - 40 }], [248, { x: 2010, y: 900 }], [276, { x: 2010, y: 900 }], [278, { x: MO.x + 60, y: MO.y - 250 }, 'out'], [300, { x: 2560, y: -190 }, 'in']] }),
      pip: { char: 'C1', h: PIP, z: 7, top: true, glow: { r: 2.6 }, track: [[242, { x: MO.x, y: MO.y - 104, light: 0.92 }], [246, { x: MO.x, y: MO.y - 104 }], [248, { x: 2010, y: 836 }], [276, { x: 2010, y: 836 }], [278, { x: MO.x + 60, y: MO.y - 316 }, 'out'], [300, { x: 2560, y: -256 }, 'in']] },
      sheep: { char: 'C5', h: SHEEP, z: 5, poses: ['sitting'], track: [[242, { x: 1940, y: 895, flip: -1, pose: 'rig', face: 'laughing' }], [262, { face: 'open' }], [276, { x: 1940, y: 895, pose: 'rig' }], [276.1, { pose: 'sitting' }], [278, { x: MO.x - 90, y: MO.y - 190 }, 'out'], [300, { x: 2410, y: -130 }, 'in']] },
      boy: { char: 'C6', h: BOY, z: 4, poses: ['sitting'], track: [[242, { x: 1300, y: 860, op: 0 }], [258, { x: 1300, op: 0 }], [258.1, { op: 1, walk: 1 }], [265, { x: 1800, y: 880, walk: 1 }], [265.5, { walk: 0, talk: 1, face: 'laughing' }], [269, { talk: 0 }], [276, { x: 1800, y: 880, pose: 'rig' }], [276.1, { pose: 'sitting' }], [278, { x: MO.x + 10, y: MO.y - 200 }, 'out'], [300, { x: 2510, y: -140 }, 'in']] },
    },
    cam: [[242, { x: 2050, y: 760, z: 1.9 }], [258, { x: 1900, y: 740, z: 1.5 }], [270, { x: 1950, y: 740, z: 1.6 }], [300, { x: 2300, y: 500, z: 1.1 }]],
    init(c) { c.st = stars(c.fxw, 40, { y1: 520, seed: 51 }); c.sp = sparkles(c.fxw, 20, '#ffe08a', 13); },
    draw(t, c) { c.st(t, 1.2); const p = c.actors.pip.last; c.sp(t, p.x, p.y, 0.6, 60); } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s08.wav';

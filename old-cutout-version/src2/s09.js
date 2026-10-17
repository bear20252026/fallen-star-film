// S09 — THE STONE RIVER (5:00). Riding on Moth, they cross a river of tumbling rocks. Moth dodges and
// dodges; a huge rock thunders past; the fright puts Pip out. Grey and silent. In the quiet after the storm
// they cry, then start remembering silly things (the sneeze, the cloud's game of tag, the clockmaker's face)
// and laugh through their tears. Pip flickers, then opens its eyes and laughs too. Far ahead: a stair of stars.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, rnd } from './kit.js';
import { RIDE_ACTORS, rideDraw } from './ride.js';

const D = 300;
const subs = [
  [20.0, 23.0, 'Home is past the stone river.', '回家的路，要穿过石头河。', 'it'],
  [24.0, 26.6, 'Hold on tight!', '抓紧了！', 'it'],
  [52.0, 54.4, 'Here they come!', '它们来了！'],
  [136.0, 138.0, 'Pip?', '皮皮？'],
  [142.0, 144.6, 'Pip, wake up!', '皮皮，醒醒！'],
  [154.0, 157.6, 'It was too scared. All its light ran away.', '它太害怕了，光都跑掉了。', 'it'],
  [162.0, 165.6, 'When I was sad, my light went out too.', '我难过的时候，我的光也灭了。', 'it'],
  [180.0, 183.6, 'Remember when the sheep sneezed on the rose?', '还记得小羊对着玫瑰打喷嚏吗？'],
  [198.0, 201.6, 'And the little cloud shouting “Tag! You’re it!”', '还有那朵小云喊“抓到你了！”'],
  [216.0, 219.6, 'And the clockmaker’s face when time stopped!', '还有时间停下时，钟表匠的那张脸！', 'it'],
  [258.0, 260.0, 'Pip!', '皮皮！'],
  [280.0, 282.6, 'Look! Up there!', '看！在上面！'],
];

// Pip's light over the whole scene
const LIGHT = (t) => {
  let L = 0.95 - 0.35 * ss((t - 60) / 30) - 0.6 * ss((t - 112) / 3);
  L += 0.25 * env(t, 186, 191, 0.4, 2) + 0.35 * env(t, 205, 211, 0.4, 2) + 0.45 * env(t, 223, 231, 0.4, 3) + 1.0 * ss((t - 252) / 8);
  if (t > 60 && t < 112) L += 0.18 * Math.sin(t * 9) * Math.sin(t * 2.3);
  return clamp(L, 0, 1);
};
const SAD = { f: 'brightness(.85) saturate(.85)', af: 'brightness(.88) saturate(.85)' };

// tumbling rocks: [img, h, z, y, speed, phase, spin, blur]
const ROCKS = [
  [1, 260, 1, 300, 260, 0, 12, 0], [3, 180, 1, 980, 200, 900, -8, 0], [5, 340, 1, 560, 300, 1700, 6, 0],
  [2, 140, 1, 160, 180, 500, 20, 0], [8, 220, 1, 820, 240, 2300, -14, 0], [6, 120, 1, 640, 160, 1300, 18, 0],
  [4, 900, 9, 1150, 520, 2600, 5, 4], [7, 620, 9, -60, 460, 400, -6, 3],
];
const rockActors = (on) => Object.fromEntries(ROCKS.map(([n, h, z], i) => [`r${i}`, { h, z, img: `props/B7_rocks/B7_rock_0${n}.png`, isize: [800, 800], anchor: [400, 400], track: [[0, { op: on ? 1 : 0 }]] }]));
// rocks stream from right to left across the world; big near rocks only now and then
const drawRocks = (c, t, amt) => ROCKS.forEach(([n, h, z, y, sp, ph, spin, blur], i) => {
  const near = z > 5, span = near ? 7000 : 3800;
  const x = 3300 - ((t * sp * 1.4 + ph) % span);
  const op = amt * (near ? 1 : 0.95);
  c.actors[`r${i}`].render({ x, y: y + Math.sin(t * 0.7 + i) * 30, rot: t * spin, op, f: blur ? `blur(${blur}px) brightness(.8)` : 'brightness(.92)' }, t);
});
// the great rock that thunders past at ~110
const bigRock = { h: 1100, z: 10, img: 'props/B7_rocks/B7_rock_04.png', isize: [800, 800], anchor: [400, 400], track: [[0, { op: 0 }]] };

// memory bubbles: soft round windows onto earlier places
const bubble = (bg) => ({ h: 1206, z: 0, img: `backgrounds/${bg}.jpg`, isize: [2880, 1206], anchor: [1440, 603], track: [[0, { op: 0 }]],
  init(el, inner) { const im = inner.querySelector('img'); const m = 'radial-gradient(circle 560px at 50% 50%, #000 62%, transparent 100%)'; im.style.maskImage = m; im.style.webkitMaskImage = m; } });

const space = (c) => { c.st = stars(c.fxw, 60, { y1: 1206, seed: 91, r: 2 }); c.sp = sparkles(c.fxw, 30, '#ffe08a', 19); };

const shots = [
  // 1. Riding Moth through calm space. Everyone happy; Pip bright.
  { t0: 0, t1: 44, xf: 0, plate: 'B7_space_clean', actors: RIDE_ACTORS(0.7),
    cam: [[0, { x: 1100, y: 640, z: 1.05 }], [18, { x: 1350, y: 600, z: 1.5 }], [30, { x: 1450, y: 600, z: 1.7 }], [44, { x: 1700, y: 600, z: 1.2 }]],
    init: space,
    draw(t, c) {
      c.st(t, 1);
      const x = lerp(700, 1900, ss(t / 44) * 0.6 + t / 44 * 0.4);
      rideDraw(c, t, { x, y: 700, k: 0.7, rot: 4, light: LIGHT(t), pipLaugh: env(t, 4, 14, 1, 2),
        moth: { talk: env(t, 19.6, 23.2, 0.2, 0.2) + env(t, 23.8, 26.8, 0.2, 0.2), mood: t > 23 && t < 32 ? 'surprised' : 'laughing' } });
    } },

  // 2. Ahead: a river of rocks. The plate darkens into the storm.
  { t0: 44, t1: 70, xf: 1.5, plates: ['B7_space_clean', 'B7_meteor_storm'], plateMix: [[46, { m: 0 }], [62, { m: 1 }]], actors: { ...RIDE_ACTORS(0.7), ...rockActors(true) },
    cam: [[44, { x: 1500, y: 620, z: 1.3 }], [56, { x: 1500, y: 620, z: 1.9 }], [70, { x: 1500, y: 600, z: 1.2 }]],
    init: space,
    draw(t, c) {
      c.st(t, 1 - ss((t - 50) / 10));
      drawRocks(c, t, ss((t - 52) / 8));
      rideDraw(c, t, { x: 1500, y: 700, k: 0.7, rot: 0, light: LIGHT(t), moth: { mood: 'surprised' }, boy: { talk: env(t, 51.6, 54.6, 0.2, 0.2) } });
    } },

  // 3. The storm: Moth dodges left, right, down. Shaking camera. Then the great rock. Pip goes out.
  { t0: 70, t1: 128, xf: 0.8, plate: 'B7_meteor_storm', actors: { ...RIDE_ACTORS(0.75), ...rockActors(true), big: bigRock },
    cam: [[70, { x: 1440, y: 620, z: 1.25, shake: 0.6 }], [90, { x: 1400, y: 640, z: 1.45, shake: 0.8 }], [108, { x: 1440, y: 620, z: 1.55, shake: 0.6 }], [112, { shake: 2.2 }], [116, { shake: 0.4 }], [128, { x: 1460, y: 620, z: 1.9, shake: 0 }]],
    init(c) { space(c); c.flash = svg(c.fxs, 'rect', { x: 0, y: 0, width: 1920, height: 804, fill: '#fff4dc', opacity: 0 }); },
    draw(t, c) {
      drawRocks(c, t, 1 - ss((t - 118) / 8));
      // dodging: a slalom of sudden swerves
      const dx = Math.sin(t * 0.9) * 220 + Math.sin(t * 2.3) * 60, dy = Math.sin(t * 1.3 + 1) * 120 - 140 * env(t, 108, 113, 1, 3);
      const rot = Math.cos(t * 0.9) * 14 + 10 * env(t, 108, 113, 1, 3);
      rideDraw(c, t, { x: 1440 + dx * (1 - ss((t - 116) / 10)), y: 700 + dy * (1 - ss((t - 116) / 10)), k: 0.75, rot: rot * (1 - ss((t - 116) / 10)), light: LIGHT(t), pipFace: t > 112 ? 'closed' : 'open',
        moth: { mood: t > 116 ? 'sad' : 'surprised' }, bob: 0.5 });
      // the great rock, foreground, right to left
      const u = (t - 106) / 9;
      c.actors.big.render({ x: lerp(3600, -700, u), y: 460 + Math.sin(u * 3) * 40, rot: t * 10, op: u > 0 && u < 1 ? 1 : 0, f: 'blur(5px) brightness(.7)' }, t);
      c.flash.setAttribute('opacity', (0.3 * env(t, 111.5, 113.5, 0.15, 1.6)).toFixed(3));
    } },

  // 4. Quiet after the storm. Pip is grey. "Pip, wake up!" Moth remembers his own dark.
  { t0: 128, t1: 176, xf: 1.5, plate: 'B7_space_clean', grade: [[0, SAD]], actors: RIDE_ACTORS(1),
    cam: [[128, { x: 1460, y: 640, z: 1.6 }], [140, { x: 1500, y: 600, z: 2.3 }], [152, { x: 1460, y: 650, z: 1.8 }], [176, { x: 1440, y: 640, z: 1.6 }]],
    init: space,
    draw(t, c) {
      c.st(t, 0.6);
      rideDraw(c, t, { x: 1440, y: 720, k: 1, rot: 0, light: LIGHT(t), pipFace: 'closed', bob: 0.4,
        moth: { mood: 'sad', flap: 0.5, talk: env(t, 153.6, 157.8, 0.2, 0.2) + env(t, 161.6, 165.8, 0.2, 0.2) },
        boy: { head: 8, talk: env(t, 135.6, 138.2, 0.2, 0.2) + env(t, 141.6, 144.8, 0.2, 0.2) }, sheep: { rot: Math.sin(t * 1.4) * 2 } });
    } },

  // 5. Memories. Laughing through tears; Pip flickers with each laugh.
  { t0: 176, t1: 250, xf: 1.2, plate: 'B7_space_clean', grade: [[176, SAD], [236, { f: '', af: '' }]],
    actors: { ...RIDE_ACTORS(1), m1: bubble('B1_b612_day'), m2: bubble('B5_cloud_planet_after_rain'), m3: bubble('B4_clockmaker_planet') },
    cam: [[176, { x: 1440, y: 640, z: 1.6 }], [196, { x: 1420, y: 620, z: 1.5 }], [214, { x: 1480, y: 620, z: 1.55 }], [234, { x: 1460, y: 640, z: 1.8 }], [250, { x: 1440, y: 640, z: 1.8 }]],
    init: space,
    draw(t, c) {
      c.st(t, 0.6 + 0.4 * ss((t - 230) / 10));
      const L = LIGHT(t), lg = env(t, 185, 192, 0.5, 2) + env(t, 203, 212, 0.5, 2) + env(t, 221, 248, 0.5, 3);
      const P = rideDraw(c, t, { x: 1440, y: 720, k: 1, light: L, pipFace: L > 0.5 ? 'open' : 'closed', bob: 0.4 + lg * 0.4,
        moth: { mood: lg > 0.3 ? 'laughing' : 'sad', laugh: env(t, 220, 248, 1, 3), talk: env(t, 215.6, 219.8, 0.2, 0.2), flap: 0.5 },
        boy: { head: 8 * (1 - lg), laugh: lg * 0.8, talk: env(t, 179.6, 183.8, 0.2, 0.2) + env(t, 197.6, 201.8, 0.2, 0.2) },
        sheep: { laugh: lg * 0.8 } });
      // bubbles rise from the boy's head and drift up
      [['m1', 178, 196, 1080, 470], ['m2', 196, 214, 1820, 460], ['m3', 214, 234, 1090, 460]].forEach(([id, a, b, x, y]) => {
        const u = clamp((t - a) / (b - a));
        c.actors[id].render({ x: x, y: y - u * 40, s: 0.3 + 0.04 * u, op: 0.92 * env(t, a, b + 2, 1.6, 2.4), f: 'sepia(.25) brightness(1.05)' }, t);
      });
      c.sp(t, P.pip[0], P.pip[1], lg * 0.6, 60);
    } },

  // 6. Pip opens its eyes and laughs. Gold again. Far ahead and above: a stair of stars.
  { t0: 250, t1: 300, xf: 1.0, plate: 'B7_space_clean', actors: RIDE_ACTORS(0.8),
    cam: [[250, { x: 1460, y: 640, z: 2.0 }], [262, { x: 1460, y: 640, z: 1.9 }], [276, { x: 1600, y: 500, z: 1.4 }], [300, { x: 1900, y: 420, z: 1.1 }]],
    init(c) {
      space(c);
      c.stair = Array.from({ length: 14 }, (_, i) => svg(c.fxw, 'circle', { r: 7, fill: '#ffeab0', opacity: 0 }));
    },
    draw(t, c) {
      c.st(t, 1);
      const u = ss((t - 270) / 30);
      const P = rideDraw(c, t, { x: lerp(1460, 1900, u), y: lerp(760, 640, u), k: 0.8, rot: -6 * u, light: LIGHT(t), pipFace: t > 254 ? 'open' : 'closed', pipLaugh: env(t, 258, 300, 1, 1),
        moth: { mood: 'laughing', laugh: env(t, 260, 276, 1, 3) }, boy: { laugh: env(t, 258, 274, 1, 3) }, sheep: { laugh: env(t, 258, 274, 1, 3) } });
      c.sp(t, P.pip[0], P.pip[1], env(t, 254, 300, 2, 1), 140);
      c.stair.forEach((e, i) => {
        const x = 2200 + i * 40 + (i % 2) * 30, y = 620 - i * 42;
        e.setAttribute('cx', x); e.setAttribute('cy', y);
        e.setAttribute('opacity', (env(t, 274 + i * 0.6, 302, 1.2, 1) * (0.6 + 0.4 * Math.sin(t * 3 + i))).toFixed(3));
      });
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s09.wav';

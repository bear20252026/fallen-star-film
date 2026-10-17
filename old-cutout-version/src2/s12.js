// S12 — HOME (4:10). Dawn: Moth sets them down on B612. The rose. A watering can, a sneeze, a hug.
// Moth stays: it is warm here. Dusk: they sit together and look up at Pip's star, which winks at them.
// Night: Moth curls up beside them, glowing softly like a night lamp; the boy and the sheep fall asleep.
// "Every time you laugh, a star somewhere shines brighter." The End.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, flareStar } from './kit.js';
import { BOY, SHEEP, PIP, MOTH, CAN } from './common.js';
import { RIDE_ACTORS, rideDraw } from './ride.js';

const D = 250;
const FRIEND = { x: 1880, y: 250 };
const NIGHT = { f: 'brightness(.42) saturate(.7) hue-rotate(-12deg) contrast(1.05)', af: 'brightness(.62) saturate(.75) hue-rotate(-8deg)' };
const DAWN = { f: 'brightness(.9) saturate(1.05) sepia(.15)', af: 'brightness(.95) sepia(.08)' };
const subs = [
  [22.0, 24.0, 'We’re home!', '我们到家了！'],
  [56.0, 59.0, 'You came back.', '你们回来了。', 'it'],
  [60.0, 62.6, 'And you brought a friend.', '还带来了一个朋友。', 'it'],
  [82.0, 84.6, 'It’s warm here.', '这里好暖和。', 'it'],
  [86.0, 89.0, 'Can I stay?', '我可以留下来吗？', 'it'],
  [90.0, 92.0, 'Of course!', '当然可以！'],
  [140.0, 143.0, 'There it is. There’s Pip.', '在那儿。那是皮皮。'],
  [160.0, 164.0, 'Every time you laugh,', '每一次你笑的时候，'],
  [164.4, 168.6, 'a star somewhere shines a little brighter.', '某个地方就有一颗星星，亮了一点点。'],
  [999, 999, '', '完'],   // never shown; makes sure the font has 完 for the end card
];

const shots = [
  // 1. Dawn. Moth glides in over B612 and lands.
  { t0: 0, t1: 40, xf: 0, plates: ['B2_b612_dusk', 'B1_b612_day'], plateMix: [[0, { m: 0 }], [30, { m: 1 }]], grade: [[0, DAWN], [36, { f: '', af: '' }]], actors: RIDE_ACTORS(0.75),
    cam: [[0, { x: 1600, y: 450, z: 1.05 }], [24, { x: 1500, y: 580, z: 1.2 }], [40, { x: 1500, y: 680, z: 1.5 }]],
    init(c) { c.st = stars(c.fxw, 50, { y1: 520, seed: 61 }); },
    draw(t, c) {
      c.st(t, 1 - ss(t / 20));
      const u = ss(t / 30);
      rideDraw(c, t, { x: lerp(2700, 1650, u), y: lerp(200, 700, u), k: 0.75, rot: lerp(10, 0, u), light: 1, pipFace: 'open', pipLaugh: env(t, 20, 26, 0.5, 1),
        boy: { talk: env(t, 21.6, 24.2, 0.2, 0.2) }, moth: { flap: 1 - 0.7 * ss((t - 28) / 4) }, bob: 1 - ss((t - 28) / 4) });
    } },

  // 2. The rose. The boy runs to her; the sheep sneezes (of course). Pip hops up to the sky? Not yet: it rides on.
  { t0: 40, t1: 100, xf: 1.2, plate: 'B1_b612_day',
    cam: [[40, { x: 1200, y: 700, z: 1.5 }], [56, { x: 1080, y: 680, z: 1.9 }], [70, { x: 1150, y: 690, z: 1.7 }], [82, { x: 1500, y: 640, z: 1.5 }], [100, { x: 1400, y: 660, z: 1.4 }]],
    actors: {
      moth: { char: 'C2', h: MOTH * 0.75, z: 1, flapSpeed: 5, breath: 2, track: [[40, { x: 1750, y: 700, wings: 'folded', mood: 'laughing' }], [80, { mood: 'sad' }], [81.6, { talk: 1, mood: 'laughing' }], [89.2, { talk: 0 }], [90.5, { mood: 'laughing', laugh: 1 }], [96, { laugh: 0.2 }]] },
      boy: { char: 'C6', h: BOY, z: 3, track: [[40, { x: 1600, y: 860, flip: -1 }], [42, { walk: 1 }], [50, { x: 1180, y: 800, walk: 1 }], [51, { walk: 0 }], [52, { armL: -40, armR: -40 }], [56, { face: 'laughing' }], [64, { armL: 0, armR: 0, face: 'open' }], [80, { x: 1180, y: 800, flip: 1 }], [89.6, { talk: 1, face: 'laughing' }], [92.2, { talk: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[40, { x: 1700, y: 880, flip: -1 }], [44, { walk: 1 }], [54, { x: 1290, y: 830, walk: 1 }], [55, { walk: 0 }], [65.6, { head: -8 }], [66.2, { head: 14, face: 'closed', x: 1295 }], [66.6, { head: 0, face: 'open', x: 1300 }], [70, { face: 'laughing', laugh: 1 }], [74, { laugh: 0, face: 'open' }]] },
      box: { h: 80, z: 5, img: 'props/P1_box_lantern.png', isize: [1500, 1400], anchor: [750, 1141], glow: { r: 1.6, dy: -0.45, op: 0.9 }, track: [[40, { x: 1360, y: 840, glow: 1 }]] },
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.4 }, track: [[40, { x: 1360, y: 776, light: 1, face: 'open' }], [66.4, { laugh: 0 }], [67, { laugh: 1 }], [74, { laugh: 0 }]] },
    },
    init(c) { c.sp = sparkles(c.fxw, 16, '#ffe7a8', 41); },
    draw(t, c) { c.sp(t, 1040, 660, env(t, 52, 64, 1, 2), 80); } },

  // 3. A day at home, in a few warm moments: sweeping, giggling, Pip riding the sheep's back.
  { t0: 100, t1: 130, xf: 1.5, plates: ['B1_b612_day', 'B2_b612_dusk'], plateMix: [[110, { m: 0 }], [128, { m: 1 }]],
    cam: [[100, { x: 1440, y: 600, z: 1.1 }], [130, { x: 1500, y: 560, z: 1.15 }]],
    actors: {
      moth: { char: 'C2', h: MOTH * 0.75, z: 1, flapSpeed: 5, breath: 2, track: [[100, { x: 1950, y: 700, wings: 'open', mood: 'laughing', flap: 0.3 }]] },
      boy: { char: 'C6', h: BOY, z: 3, track: [[100, { x: 900, y: 790, walk: 1, flip: 1 }], [118, { x: 1400, y: 840, walk: 1 }], [119, { walk: 0, face: 'laughing' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, track: [[100, { x: 760, y: 820, walk: 1, flip: 1, face: 'laughing' }], [118, { x: 1260, y: 860, walk: 1 }], [119, { walk: 0 }]] },
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.4 }, track: [[100, { x: 760, y: 735, light: 1, laugh: 1 }], [118, { x: 1260, y: 775 }], [124, { laugh: 0.4 }]] },
    },
    draw(t, c) { const s = c.actors.sheep.last; c.actors.pip.render({ ...c.actors.pip.last, x: s.x + 10, y: s.y - 92 - Math.abs(Math.sin(t * 7.5)) * 6 * (s.walk || 0) }, t); } },

  // 4. Dusk. Pip says goodbye and floats back up to its place. They look up. It winks.
  { t0: 130, t1: 176, xf: 1.2, plate: 'B2_b612_dusk', grade: [[130, { f: '', af: '' }], [176, { f: 'brightness(.7) saturate(.85)', af: 'brightness(.8)' }]],
    cam: [[130, { x: 1440, y: 700, z: 1.7 }], [136, { x: 1600, y: 500, z: 1.3 }], [150, { x: 1640, y: 470, z: 1.25 }], [158, { x: 1460, y: 720, z: 1.8 }], [176, { x: 1460, y: 720, z: 1.9 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, poses: ['sitting'], track: [[130, { x: 1400, y: 840, pose: 'sitting' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sitting'], track: [[130, { x: 1250, y: 860, pose: 'sitting', flip: 1 }]] },
      moth: { char: 'C2', h: MOTH * 0.75, z: 1, flapSpeed: 5, breath: 2, track: [[130, { x: 1650, y: 780, wings: 'folded', mood: 'laughing' }]] },
      pip: { char: 'C1', h: PIP, z: 6, top: true, glow: { r: 2.4 }, track: [[130, { x: 1330, y: 760, light: 1, face: 'open' }], [131, { face: 'laughing' }], [132, { x: 1400, y: 640 }], [137, { x: FRIEND.x, y: FRIEND.y, s: 0.6, op: 1 }], [139, { op: 0 }]] },
    },
    init(c) { c.st = stars(c.fxw, 70, { y1: 520, seed: 3 }); c.fr = flareStar(c.fxw, 'f12a'); c.sp = sparkles(c.fxw, 18, '#ffe7a8', 43); },
    draw(t, c) {
      c.st(t, ss((t - 136) / 20));
      const wink = Math.exp(-((t - 148) ** 2) / 0.05) + Math.exp(-((t - 171) ** 2) / 0.05);
      c.fr(FRIEND.x, FRIEND.y, (30 + 4 * Math.sin(t * 3)) * (1 - 0.6 * wink) + 20 * env(t, 148.3, 150, 0.2, 1), ss((t - 137) / 2));
      const p = c.actors.pip.last; if (p) c.sp(t, p.x, p.y, env(t, 131, 139, 0.5, 1), 50); else c.sp(t, 0, 0, 0, 50);
      const B = c.actors.boy; B.render({ ...B.last, rot: t > 160 && t < 169 ? Math.sin(t * 2) * 1 : 0 }, t);
    } },

  // 5. Night. Moth, warm at last, glows softly beside them like a night lamp. They fall asleep.
  { t0: 176, t1: 226, xf: 2.0, plate: 'B2_b612_dusk', grade: [[0, NIGHT]],
    cam: [[176, { x: 1500, y: 720, z: 1.8 }], [200, { x: 1500, y: 700, z: 1.6 }], [226, { x: 1560, y: 560, z: 1.2 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, poses: ['sleeping'], breath: 2, track: [[176, { x: 1430, y: 850, pose: 'sleeping' }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sleeping'], breath: 2, track: [[176, { x: 1250, y: 862, pose: 'sleeping' }]] },
      moth: { char: 'C2', h: MOTH * 0.75, z: 1, flapSpeed: 5, breath: 2, glow: { r: 1.7, dy: -0.3, op: 1, c: 'rgba(255,226,170,.75)', c2: 'rgba(255,200,130,.3)' }, track: [[176, { x: 1700, y: 780, wings: 'folded', mood: 'laughing', glow: 0.8 }], [196, { glow: 1 }]] },
    },
    init(c) { c.st = stars(c.fxw, 90, { y1: 560, seed: 11 }); c.fr = flareStar(c.fxw, 'f12b'); },
    draw(t, c) {
      c.st(t, 1, 0.3);
      const wink = Math.exp(-((t - 214) ** 2) / 0.05);
      c.fr(FRIEND.x, FRIEND.y, (34 + 4 * Math.sin(t * 3)) * (1 - 0.6 * wink), 1);
    } },

  // 6. Pull back: the little planet, the lamp, the laughing star. The End.
  { t0: 226, t1: 250, xf: 1.5, plates: ['B2_b612_dusk', 'title/T1_title_card'], plateMix: [[234, { m: 0 }], [240, { m: 1 }]], grade: [[226, NIGHT], [240, { f: '', af: '' }]],
    cam: [[226, { x: 1500, y: 560, z: 1.15 }], [240, { x: 1440, y: 603, z: 1.0 }], [250, { x: 1440, y: 603, z: 1.03 }]],
    actors: {
      boy: { char: 'C6', h: BOY, z: 3, poses: ['sleeping'], breath: 2, track: [[226, { x: 1430, y: 850, pose: 'sleeping' }], [234, { op: 1 }], [239, { op: 0 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sleeping'], breath: 2, track: [[226, { x: 1250, y: 862, pose: 'sleeping' }], [234, { op: 1 }], [239, { op: 0 }]] },
      moth: { char: 'C2', h: MOTH * 0.75, z: 1, flapSpeed: 5, breath: 2, glow: { r: 1.7, dy: -0.3, op: 1, c: 'rgba(255,226,170,.75)', c2: 'rgba(255,200,130,.3)' }, track: [[226, { x: 1700, y: 780, wings: 'folded', mood: 'laughing', glow: 1 }], [234, { op: 1 }], [239, { op: 0 }]] },
    },
    init(c) {
      c.st = stars(c.fxw, 90, { y1: 560, seed: 11 }); c.fr = flareStar(c.fxw, 'f12c');
      c.end = document.createElement('div');
      c.end.style.cssText = 'position:absolute;left:0;right:0;top:640px;text-align:center;font-family:Lora,"Noto Serif SC",serif;font-style:italic;font-size:54px;color:#ffe9b0;text-shadow:0 0 10px rgba(10,8,30,.95),0 0 24px rgba(10,8,30,.8);opacity:0;letter-spacing:2px';
      c.end.innerHTML = 'The End · 完<div style="display:none;font-size:34px;font-style:normal;margin-top:6px;font-family:\'Noto Serif SC\',serif">完</div>';
      c.el.appendChild(c.end);
    },
    draw(t, c) {
      c.st(t, 1 - ss((t - 234) / 5), 0.3);
      c.fr(FRIEND.x, FRIEND.y, 34 + 4 * Math.sin(t * 3), 1 - ss((t - 236) / 4));
      c.end.style.opacity = ss((t - 241) / 2.5).toFixed(3);
    } },
];

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 3.0 } });
export const AUDIO = 'audio2/s12.wav';

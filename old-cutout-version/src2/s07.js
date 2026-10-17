// S07 — MOTH TAKES PIP (5:00). Calm night flying; the boy dozes, the sheep keeps watch. A huge soft shadow
// passes. Moth swoops down and carries off the lantern with Pip. The birds scatter. The boy and the sheep
// drift down onto a lonely rock and watch the light go off towards a faint violet glow. The sheep decides.
import { makeScene, ss, env, clamp, lerp, stars, sparkles, svg, glowDot } from './kit.js';
import { BOY, SHEEP, PIP, MOTH, PARTY_ACTORS, partyInit, partyDraw } from './common.js';

const D = 300;
const GLOW = { x: 2560, y: 330 };   // the far violet glow of Moth's planet
const subs = [
  [14.0, 17.4, 'Wake me if anything happens.', '有什么事就叫醒我。'],
  [148.0, 150.4, 'Hey! Stop!', '喂！停下！'],
  [151.4, 154.4, 'Give it back!', '还给我们！'],
  [244.0, 246.6, 'It took Pip…', '它把小星星带走了……'],
  [262.0, 265.0, 'You want to go after it?', '你想去追它？'],
  [272.0, 275.0, 'Then so do I.', '那我也去。'],
];

const ROCK = { x: 1440, y: 900 };
const rockA = { h: 520, z: 1, img: 'props/B7_rocks/B7_rock_04.png', isize: [800, 800], anchor: [400, 400], track: [[0, { x: ROCK.x, y: ROCK.y + 200 }]] };
const mothA = (z = 5) => ({ char: 'C2', h: MOTH, z, flapSpeed: 6, track: [[0, { op: 0 }]] });

const shots = [
  // 1. Calm night flying. The boy dozes off.
  { t0: 0, t1: 60, xf: 0, plate: 'B3_the_quiet', actors: PARTY_ACTORS(1),
    cam: [[0, { x: 1300, y: 600, z: 1.3 }], [30, { x: 1440, y: 580, z: 1.6 }], [60, { x: 1500, y: 580, z: 1.8 }]],
    init(c) { c.st = stars(c.fxw, 60, { y1: 1206, seed: 41 }); c.party = partyInit(c); },
    draw(t, c) {
      c.st(t, 1);
      partyDraw(c, t, { x: 1500, y: 720, light: 0.95, pipFace: t > 40 ? 'closed' : 'open',
        boy: { talk: env(t, 13.6, 17.6, 0.2, 0.2), face: t > 24 ? 'closed' : 'open', head: 10 * ss((t - 24) / 4) }, sheep: { head: -8 } });
    } },

  // 2. A shadow passes, huge and soft. Wing dust. The birds panic.
  { t0: 60, t1: 122, xf: 1.0, plate: 'B3_the_quiet', actors: { ...PARTY_ACTORS(1), shadow: { char: 'C2', h: MOTH * 3, z: 9, top: true, flapSpeed: 4, track: [[0, { op: 0 }]] } },
    cam: [[60, { x: 1500, y: 580, z: 1.7 }], [80, { x: 1480, y: 580, z: 1.8 }], [100, { x: 1440, y: 600, z: 1.5 }], [122, { x: 1440, y: 600, z: 1.5 }]],
    init(c) { c.st = stars(c.fxw, 60, { y1: 1206, seed: 41 }); c.party = partyInit(c); c.dust = sparkles(c.fxw, 40, '#cfc6dc', 9); },
    draw(t, c) {
      c.st(t, 1);
      const pan = env(t, 74, 120, 0.3, 2) * (1 + 0.5 * env(t, 100, 104, 0.3, 1));
      partyDraw(c, t + pan * Math.sin(t * 20) * 0.04, { x: 1500 + pan * Math.sin(t * 13) * 14, y: 720 + pan * Math.sin(t * 17) * 10, light: 0.95, pipFace: t > 76 ? 'open' : 'closed',
        boy: { face: 'closed', head: 10 }, sheep: { head: t > 75 ? -20 + Math.sin(t * 3) * 14 : -8, face: 'open' } });
      // the shadow crosses in the foreground twice
      const u1 = (t - 72) / 3.2, u2 = (t - 98) / 4;
      const sh = c.actors.shadow;
      if (u1 > 0 && u1 < 1) sh.render({ x: lerp(-600, 3400, u1), y: 500 + Math.sin(u1 * 3) * 80, flap: 1, mood: 'sad', f: 'brightness(0) blur(14px)', op: 0.85, rot: -10 }, t);
      else if (u2 > 0 && u2 < 1) sh.render({ x: lerp(3400, -600, u2), y: 300 + u2 * 200, flap: 1, mood: 'sad', f: 'brightness(0) blur(14px)', op: 0.8, flip: -1, rot: 8 }, t);
      else sh.render({ op: 0 }, t);
      c.dust(t, 1500, 400, env(t, 74, 90, 0.5, 6) + env(t, 100, 116, 0.5, 6), 500);
    } },

  // 3. Moth swoops in and takes the lantern. The sheep hangs on, then is shaken off. The birds scatter.
  { t0: 122, t1: 182, xf: 0.6, plate: 'B3_the_quiet', actors: { ...PARTY_ACTORS(1), moth: mothA(5) },
    cam: [[122, { x: 1500, y: 560, z: 1.5 }], [134, { x: 1600, y: 520, z: 1.4 }], [140, { x: 1640, y: 500, z: 1.3, shake: 0.6 }], [150, { x: 1600, y: 520, z: 1.3, shake: 0.3 }], [165, { x: 1700, y: 480, z: 1.15, shake: 0 }], [182, { x: 1800, y: 470, z: 1.1 }]],
    init(c) { c.st = stars(c.fxw, 60, { y1: 1206, seed: 41 }); c.party = partyInit(c); c.dust = sparkles(c.fxw, 30, '#cfc6dc', 3); },
    draw(t, c) {
      c.st(t, 1);
      // moth path: from top-right, down to the lantern (136), then away to the right and up
      const a = ss((t - 126) / 10), b = ss((t - 140) / 30);
      const mx = lerp(lerp(2900, 1930, a), 3100, b), my = lerp(lerp(-200, 440, a), 120, b) + Math.sin(t * 6) * 12;
      c.actors.moth.render({ x: mx, y: my, flap: 1, mood: t < 140 ? 'surprised' : 'sad', op: t > 125 ? 1 : 0, rot: lerp(-14, 8, b), flip: 1 }, t);
      const grabbed = t > 137;
      const hang = grabbed ? [mx - 60, my + 290] : null;
      const sheepHold = env(t, 137, 147, 0.2, 0.6);      // the sheep bites the lantern's string, swings, lets go
      const sc = ss((t - 139) / 6);
      partyDraw(c, t, { x: 1550, y: 720 + 30 * sc, light: 0.95, pipFace: grabbed ? 'closed' : 'open', boxAt: hang, strBox: grabbed ? 0 : 1, scatter: sc, strOp: 1 - ss(sc * 2),
        sheepDx: -sheepHold * 60, sheepDy: -sheepHold * 40, sheepRot: sheepHold * Math.sin(t * 8) * 30,
        boy: { face: t > 140 ? 'open' : 'closed', head: t > 140 ? -10 : 10, armR: -150, talk: env(t, 147.6, 154.6, 0.2, 0.2), legL: 20 * Math.sin(t * 7) * sc, legR: -20 * Math.sin(t * 7) * sc } });
      c.dust(t, mx, my + 100, t > 126 ? 1 : 0, 300);
    } },

  // 4. Without the birds they drift down onto a lonely rock. The lantern's light goes, far away.
  { t0: 182, t1: 240, xf: 1.2, plate: 'B3_the_quiet',
    actors: {
      rock: rockA,
      boy: { char: 'C6', h: BOY, z: 3, poses: ['sitting'], track: [[182, { x: 1340, y: 300, rot: -10, armR: -60 }], [198, { x: 1400, y: 830, rot: 0, armR: -20 }, 'out'], [206, { pose: 'rig' }], [207, { pose: 'sitting', x: 1400, y: 840 }]] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sitting'], track: [[182, { x: 1600, y: 250, rot: 20, flip: 1 }], [200, { x: 1540, y: 840, rot: 0 }, 'out'], [214, { pose: 'rig' }], [215, { pose: 'sitting' }]] },
    },
    cam: [[182, { x: 1440, y: 560, z: 1.3 }], [200, { x: 1440, y: 700, z: 1.5 }], [222, { x: 1700, y: 600, z: 1.2 }], [240, { x: 1800, y: 560, z: 1.15 }]],
    init(c) { c.st = stars(c.fxw, 60, { y1: 1206, seed: 41 }); c.lan = glowDot(c.fxw, 'l74', '#ffd27a'); c.vio = glowDot(c.fxw, 'v74', '#b9a0ff'); },
    draw(t, c) {
      c.st(t, 1);
      const u = ss((t - 182) / 50);
      c.lan.setAttribute('cx', lerp(2200, GLOW.x, u)); c.lan.setAttribute('cy', lerp(150, GLOW.y, u)); c.lan.setAttribute('r', lerp(60, 8, u));
      c.vio.setAttribute('cx', GLOW.x); c.vio.setAttribute('cy', GLOW.y); c.vio.setAttribute('r', 90 + 6 * Math.sin(t * 1.3)); c.vio.setAttribute('opacity', 0.55);
    } },

  // 5. The sheep stands, looks at the violet glow, and decides. The boy goes too. Two birds come back.
  { t0: 240, t1: 300, xf: 1.0, plate: 'B3_the_quiet',
    actors: {
      rock: rockA,
      boy: { char: 'C6', h: BOY, z: 3, poses: ['sitting'], track: [[240, { x: 1400, y: 840, pose: 'sitting' }], [256, { pose: 'sitting' }], [256.1, { pose: 'rig', x: 1400, y: 835 }], [261.6, { talk: 1 }], [265, { talk: 0 }], [271.6, { talk: 1, face: 'open' }], [275, { talk: 0 }], [282, { x: 1400, y: 835, armR: 0 }], [286, { armR: -150 }], [300, { x: 1900, y: 420, armR: -150 }, 'in']] },
      sheep: { char: 'C5', h: SHEEP, z: 4, poses: ['sitting'], track: [[240, { x: 1540, y: 840, pose: 'sitting', flip: 1 }], [250, { pose: 'sitting' }], [250.1, { pose: 'rig', flip: -1, head: -10 }], [258, { head: -16 }], [266, { head: 10 }], [267, { head: -6 }], [268, { head: 10 }], [269, { head: 0 }], [283, { x: 1540, y: 840 }], [300, { x: 2100, y: 470 }, 'in']] },
    },
    cam: [[240, { x: 1500, y: 700, z: 1.8 }], [256, { x: 1500, y: 700, z: 2.0 }], [272, { x: 1470, y: 700, z: 1.9 }], [284, { x: 1700, y: 600, z: 1.3 }], [300, { x: 2000, y: 480, z: 1.15 }]],
    init(c) { c.st = stars(c.fxw, 60, { y1: 1206, seed: 41 }); c.vio = glowDot(c.fxw, 'v75', '#b9a0ff'); },
    draw(t, c) {
      c.st(t, 1);
      c.vio.setAttribute('cx', GLOW.x); c.vio.setAttribute('cy', GLOW.y); c.vio.setAttribute('r', 90 + 6 * Math.sin(t * 1.3)); c.vio.setAttribute('opacity', 0.55);
    } },
];

// two birds come back for the last shot
import { birds, strand } from './kit.js';
const last = shots[4];
const baseInit = last.init, baseDraw = last.draw;
last.init = (c) => { baseInit(c); c.bb = birds(c.fxw, 2); c.s1 = strand(c.fxw); c.s2 = strand(c.fxw); };
last.draw = (t, c) => {
  baseDraw(t, c);
  const B = c.actors.boy.last, S = c.actors.sheep.last, a = ss((t - 276) / 8);
  const p1 = [lerp(600, B.x + 70, a), lerp(200, B.y - 470, a)], p2 = [lerp(700, S.x, a), lerp(180, S.y - 400, a)];
  c.bb(t, [{ x: p1[0], y: p1[1], s: 1 }, { x: p2[0], y: p2[1], s: 1 }]);
  const k = ss((t - 284) / 2);
  c.s1(p1[0], p1[1] + 6, B.x + 70, B.y - 205, 10, k); c.s2(p2[0], p2[1] + 6, S.x, S.y - 125, 10, k);
};

export const { html, css, setup, SUB_TEXT, DURATION } = makeScene({ duration: D, shots, subs, fades: { in: 2.0, out: 2.0 } });
export const AUDIO = 'audio2/s07.wav';

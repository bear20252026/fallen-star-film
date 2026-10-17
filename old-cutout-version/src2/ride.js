// ---------- riding on Moth: Moth (C2) carries the boy, the sheep and the box-lantern with Pip on top.
// Shots declare RIDE_ACTORS(k) and call rideDraw(c, t, {x, y, k, rot, light, ...}) in draw.
// Offsets match the boarding in S08 (Moth at MO.y-160: sheep -90,-30; boy +10,-40; box +60,-90; Pip +60,-156).
import { BOY, SHEEP, PIP, MOTH, BOXDEF } from './common.js';

export const RIDE_ACTORS = (k = 1) => ({
  moth: { char: 'C2', h: MOTH * k, z: 2, flapSpeed: 5, breath: 2, track: [[0, {}]] },
  sheep: { char: 'C5', h: SHEEP * k, z: 5, poses: ['sitting'], track: [[0, {}]] },
  boy: { char: 'C6', h: BOY * k, z: 4, poses: ['sitting'], track: [[0, {}]] },
  box: BOXDEF(80 * k, { z: 6 }),
  pip: { char: 'C1', h: PIP * k, z: 7, top: true, glow: { r: 2.6 }, track: [[0, {}]] },
});
// o: {x, y (Moth), k, rot (deg), light, moth:{}, boy:{}, sheep:{}, pip:{}, bob (amount)}
export function rideDraw(c, t, o) {
  const k = o.k || 1, r = ((o.rot || 0) * Math.PI) / 180, cs = Math.cos(r), sn = Math.sin(r);
  const bob = Math.sin(t * 2.2) * 10 * k * (o.bob ?? 1);
  const X = o.x, Y = o.y + bob;
  const at = (dx, dy) => [X + (dx * cs - dy * sn) * k, Y + (dx * sn + dy * cs) * k];
  const L = c.actors;
  L.moth.render({ x: X, y: Y, rot: o.rot || 0, wings: 'open', flap: 1, mood: 'laughing', ...(o.moth || {}) }, t);
  const s = at(-90, -30), b = at(10, -40), x = at(60, -90), p = at(60, -156);
  L.sheep.render({ x: s[0], y: s[1], rot: o.rot || 0, flip: -1, pose: 'sitting', ...(o.sheep || {}) }, t);
  L.boy.render({ x: b[0], y: b[1], rot: o.rot || 0, pose: 'sitting', ...(o.boy || {}) }, t);
  L.box.render({ x: x[0], y: x[1], rot: (o.rot || 0) + Math.sin(t * 1.5) * 3, glow: o.light ?? 0.9 }, t);
  L.pip.render({ x: p[0], y: p[1], light: o.light ?? 0.9, face: o.pipFace, laugh: o.pipLaugh || 0, ...(o.pip || {}) }, t);
  return { moth: [X, Y], sheep: s, boy: b, box: x, pip: p };
}

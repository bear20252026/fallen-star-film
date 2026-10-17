// Shared sizes and small painted props for film 2 (drawn in SVG in the illustrators' palette:
// warm brown outline, soft fills, a little paper-wobble on the edges).
export const BOY = 260;            // the boy's standing height in plate pixels
export const SHEEP = BOY * 0.62;
export const PIP = 46;
export const MOTH = BOY * 1.5;
export const INK = '#5a3b2a';

let uid = 0;
const wob = (id, sc = 2.5) => `<filter id="${id}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="${(uid % 7) + 1}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="${sc}" xChannelSelector="R" yChannelSelector="G"/></filter>`;
// an inline SVG prop; origin (0,0) at the prop's anchor. body = svg markup in local coords.
export const svgProp = (w, h, ox, oy, body) => (el, inner) => {
  const id = 'wob' + uid++;
  inner.innerHTML = `<svg width="${w}" height="${h}" viewBox="${-ox} ${-oy} ${w} ${h}" style="position:absolute;left:${-ox}px;top:${-oy}px;overflow:visible"><defs>${wob(id)}</defs><g filter="url(#${id})">${body}</g></svg>`;
};
// watering can, spout to the left; anchor = handle grip
export const CAN = svgProp(140, 110, 90, 40, `
  <path d="M-60 -10 L-110 -40 L-104 -46 L-52 -22Z" fill="#9fb3bf" stroke="${INK}" stroke-width="3" stroke-linejoin="round"/>
  <ellipse cx="-110" cy="-43" rx="9" ry="6" fill="#b7c7d0" stroke="${INK}" stroke-width="3"/>
  <path d="M-60 -30 Q-62 30 -40 36 L20 36 Q40 30 38 -30Z" fill="#a9bfcb" stroke="${INK}" stroke-width="3.5"/>
  <path d="M-55 -20 Q-50 20 -30 28" fill="none" stroke="#e6f0f4" stroke-width="5" opacity=".7"/>
  <ellipse cx="-11" cy="-30" rx="49" ry="9" fill="#8ea3b0" stroke="${INK}" stroke-width="3"/>
  <path d="M-30 -36 Q0 -80 30 -34" fill="none" stroke="${INK}" stroke-width="6"/>
  <path d="M-30 -36 Q0 -80 30 -34" fill="none" stroke="#9fb3bf" stroke-width="3"/>`);
// a baobab sprout; anchor = ground under the bulb
export const SPROUT = svgProp(120, 140, 60, 120, `
  <path d="M-4 -40 Q-40 -80 -50 -60 Q-44 -40 -4 -44Z" fill="#7fa45a" stroke="${INK}" stroke-width="3"/>
  <path d="M4 -42 Q42 -90 54 -66 Q46 -42 4 -46Z" fill="#8cb563" stroke="${INK}" stroke-width="3"/>
  <path d="M0 -42 L0 -26" stroke="${INK}" stroke-width="4"/>
  <path d="M-22 -2 Q-30 -30 0 -30 Q30 -30 22 -2 Q14 6 0 6 Q-14 6 -22 -2Z" fill="#d9c3a0" stroke="${INK}" stroke-width="3.5"/>
  <path d="M-14 -16 Q-6 -24 6 -22" fill="none" stroke="#f2e6cf" stroke-width="4" opacity=".8"/>
  <path d="M-6 6 L-10 18 M2 6 L4 20 M8 4 L14 14" stroke="${INK}" stroke-width="2.5" fill="none"/>`);
// a little brass telescope on a tripod; anchor = feet
export const SCOPE = svgProp(200, 220, 100, 210, `
  <path d="M0 -110 L-50 0 M0 -110 L50 0 M0 -110 L0 0" stroke="${INK}" stroke-width="6" stroke-linecap="round"/>
  <path d="M0 -110 L-50 0 M0 -110 L50 0 M0 -110 L0 0" stroke="#a87b4f" stroke-width="3" stroke-linecap="round"/>
  <g transform="translate(0,-118) rotate(-32)">
    <rect x="-70" y="-13" width="120" height="26" rx="6" fill="#d6a64e" stroke="${INK}" stroke-width="3.5"/>
    <rect x="44" y="-17" width="34" height="34" rx="6" fill="#c18f3c" stroke="${INK}" stroke-width="3.5"/>
    <rect x="-92" y="-9" width="26" height="18" rx="4" fill="#c18f3c" stroke="${INK}" stroke-width="3"/>
    <path d="M-60 -6 L40 -6" stroke="#f6dc9a" stroke-width="4" opacity=".8"/></g>`);
// pocket watch (the clockmaker's gift); anchor = centre
export const WATCH = svgProp(80, 100, 40, 50, `
  <path d="M0 -36 Q-8 -50 0 -54 Q8 -50 0 -36" fill="none" stroke="#c9952f" stroke-width="5"/>
  <circle r="30" fill="#e4b54a" stroke="${INK}" stroke-width="3.5"/><circle r="23" fill="#fbf2dc" stroke="${INK}" stroke-width="2"/>
  <path d="M0 0 L0 -15 M0 0 L10 5" stroke="${INK}" stroke-width="3" stroke-linecap="round"/>`);
// a puff of soot / dust; draw-time only (see puff())
export const puffEl = (parent, n, color = '#6e6a66') => {
  const NS = 'http://www.w3.org/2000/svg'; const g = document.createElementNS(NS, 'g'); parent.appendChild(g); const L = [];
  const fid = 'pf' + uid++; const df = document.createElementNS(NS, 'defs'); df.innerHTML = `<filter id="${fid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>`; parent.appendChild(df); g.setAttribute('filter', `url(#${fid})`);
  for (let i = 0; i < n; i++) { const c = document.createElementNS(NS, 'circle'); c.setAttribute('fill', color); g.appendChild(c); L.push({ c, a: (i / n) * 6.28 + i, sp: 0.6 + (i % 5) * 0.15 }); }
  return (t, x, y, u, size = 60) => { // u: 0..1 progress of the puff
    for (const p of L) {
      const r = size * (0.3 + u * 1.1) * p.sp, d = size * u * 1.6 * p.sp;
      p.c.setAttribute('cx', (x + Math.cos(p.a) * d).toFixed(1)); p.c.setAttribute('cy', (y + Math.sin(p.a) * d * 0.6 - u * size).toFixed(1));
      p.c.setAttribute('r', Math.max(0, r).toFixed(1)); p.c.setAttribute('opacity', (u > 0 && u < 1 ? 0.32 * (1 - u) : 0).toFixed(3));
    }
  };
};

// ---------- the flying party: the boy on the birds' strings, the sheep and the box-lantern (with Pip riding on top)
// Shots that use it declare actors boy (C6), sheep (C5), box (lantern img) and pip (C1, top) and call
// c.party = partyInit(c) in init and partyDraw(c, t, {...}) in draw.
import { birds as _birds, strand as _strand, lerp as _lerp, ss } from './kit.js';
export const BOXDEF = (h = 110, extra = {}) => ({ h, z: 4, img: 'props/P1_box_lantern.png', isize: [1500, 1400], anchor: [750, 1141], glow: { r: 1.6, dy: -0.45, op: 0.9 }, track: [[0, {}]], ...extra });
export const PARTY_ACTORS = (k = 1) => ({
  boy: { char: 'C6', h: BOY * k, z: 3, track: [[0, {}]] },
  sheep: { char: 'C5', h: SHEEP * k, z: 4, track: [[0, {}]] },
  box: BOXDEF(110 * k),
  pip: { char: 'C1', h: PIP * k, z: 6, top: true, glow: { r: 2.4 }, track: [[0, {}]] },
});
export function partyInit(c) { return { b: _birds(c.fxw, 7), str: Array.from({ length: 4 }, () => _strand(c.fxw)) }; }
// o: {x, y (boy's feet), k (scale), light (Pip), boy:{...extra props}, sheep:{...}, pip:{...}, flip, sheepRot, sheepDx, sheepDy}
export function partyDraw(c, t, o) {
  const k = o.k || 1, sw = Math.sin(t * 0.9) * 10 * k, f = o.flip || 1;
  const bx = o.x + sw, by = o.y + Math.sin(t * 1.3) * 8 * k;
  const sx = o.x - f * 170 * k + sw * 1.3 + (o.sheepDx || 0) * k, sy = o.y + 50 * k + Math.sin(t * 1.1 + 1) * 10 * k + (o.sheepDy || 0) * k;
  let xx = o.x + f * 160 * k + sw * 1.2, xy = o.y + 30 * k + Math.sin(t * 1.2 + 2) * 9 * k;
  if (o.boxAt) { xx = o.boxAt[0]; xy = o.boxAt[1]; }
  const L = c.actors;
  L.boy.render({ x: bx, y: by, armR: -150, armL: 10, legL: 8, legR: -6, ...(o.boy || {}) }, t);
  L.sheep.render({ x: sx, y: sy, flip: o.sheepFlip ?? -f, rot: o.sheepRot ?? 0, legFL: 10, legFR: -8, ...(o.sheep || {}) }, t);
  L.box.render({ x: xx, y: xy, glow: o.light ?? 0.5, rot: Math.sin(t * 1.5) * 3 }, t);
  L.pip.render({ x: xx, y: xy - 88 * k, light: o.light ?? 0.5, face: o.pipFace, laugh: o.pipLaugh || 0, ...(o.pip || {}) }, t);
  const sr = ((o.sheepRot ?? 0) * Math.PI) / 180;
  const hands = [[bx + 70 * k, by - 205 * k], [sx + Math.sin(sr) * 60 * k, sy - 60 * k - Math.cos(sr) * 65 * k], [xx, xy - 125 * k]];
  const L7 = [];
  for (let i = 0; i < 7; i++) {
    const h = hands[i < 3 ? 0 : i < 5 ? 1 : 2];
    const sc = o.scatter || 0, ang = i * 2.1 + 0.5;
    L7.push({ x: h[0] + (i % 3 - 1) * 70 * k + Math.sin(t * 2 + i) * 8 * k + Math.cos(ang) * sc * 1400, y: h[1] - (250 + (i % 2) * 40) * k + Math.sin(t * 3 + i * 2) * 8 * k - Math.abs(Math.sin(ang)) * sc * 900, s: 0.9 * k, speed: 9 + (i % 3) + sc * 10, op: (o.birdsOp ?? 1) * (1 - ss(sc * 1.5 - 0.5)) });
  }
  c.party.b(t, L7);
  const op = o.strOp ?? 1;
  c.party.str[0](L7[1].x, L7[1].y + 6 * k, hands[0][0], hands[0][1], 12 * k, op);
  c.party.str[1](L7[3].x, L7[3].y + 6 * k, hands[1][0], hands[1][1], 10 * k, op);
  const ob = o.strBox ?? op;
  c.party.str[2](L7[5].x, L7[5].y + 6 * k, hands[2][0], hands[2][1], 10 * k, ob);
  c.party.str[3](L7[6].x, L7[6].y + 6 * k, hands[2][0], hands[2][1], 10 * k, ob);
  return { boy: [bx, by], sheep: [sx, sy], box: [xx, xy], pip: [xx, xy - 88 * k] };
}

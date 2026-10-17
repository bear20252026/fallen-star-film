// FILM 2 KIT — "The Fallen Star". Everything a scene needs, as pure functions of time:
// shots (each with its own painted plate, camera, actors and effects, dissolving into each other),
// puppets built from the illustrators' layered parts or their painted poses, keyframe tracks,
// subtitles, glow, stars, rain, birds, and the shared cinema pass (grain, vignette, weave).
import RIG from './rig.json';

export const W = 1920, H = 804;
const BS = W / 2400; // world (plate px) → screen at zoom 1: a 2400 px window fills the frame

// ---------- maths ----------
export const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const ss = (u) => { u = clamp(u); return u * u * (3 - 2 * u); };
export const lerp = (a, b, u) => a + (b - a) * u;
const hash = (n) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
export const rnd = hash;
export const noise = (t) => { const i = Math.floor(t), f = t - i, u = f * f * (3 - 2 * f); return (hash(i) * (1 - u) + hash(i + 1) * u) * 2 - 1; };
const EASE = {
  io: ss, lin: (u) => u, in: (u) => u * u, out: (u) => 1 - (1 - u) * (1 - u),
  back: (u) => { const c = 1.6; u = u - 1; return 1 + (c + 1) * u * u * u + c * u * u; },
  hold: (u) => (u < 1 ? 0 : 1),
};
const HOLD = new Set(['flip', 'z']);
// keyframe track: keys = [[t, {props}, ease?], ...]. Numbers ease between keys, anything else holds.
export function track(keys, t) {
  const out = {};
  for (const [, p] of keys) for (const k in p) if (!(k in out)) out[k] = undefined;
  for (const k in out) {
    let prev = null, next = null;
    for (const key of keys) {
      if (!(k in key[1])) continue;
      if (key[0] <= t) prev = key; else { next = key; break; }
    }
    if (!prev) { out[k] = next ? next[1][k] : undefined; continue; }
    const a = prev[1][k];
    if (!next || typeof a !== 'number' || HOLD.has(k)) { out[k] = a; continue; }
    const u = (EASE[next[2] || 'io'])((t - prev[0]) / (next[0] - prev[0]));
    out[k] = a + (next[1][k] - a) * u;
  }
  return out;
}
// a 0..1 envelope: up over [a, a+fi], down over [b-fo, b]
export const env = (t, a, b, fi = 0.6, fo = 0.6) => Math.min(ss((t - a) / fi), ss((b - t) / fo));

// ---------- rigs ----------
// slot: [name, variants, pivot[x,y] (canvas px), parent slot]. Draw order = list order.
const RIGS = {
  C5: { anchor: [611, 1263], h: 844, slots: [
    ['legHL', ['leg_hind_left'], [695, 995]], ['legHR', ['leg_hind_right'], [890, 995]],
    ['tail', ['tail'], [905, 785]], ['body', ['body'], [700, 1000]],
    ['legFL', ['leg_front_left'], [475, 1025]], ['legFR', ['leg_front_right'], [610, 1038]],
    ['head', ['head_open', 'head_closed', 'head_laughing'], [560, 770]]] },
  C6: { anchor: [600, 1162], h: 930, slots: [
    ['armL', ['arm_screen_left'], [506, 644]], ['armR', ['arm_screen_right'], [694, 645]],
    ['legL', ['leg_screen_left'], [534, 930]], ['legR', ['leg_screen_right'], [659, 935]],
    ['body', ['body'], [600, 900]], ['head', ['head_open', 'head_closed', 'head_laughing'], [600, 600]],
    ['scarf', ['scarf_gold'], [620, 600]]] },
  C7: { anchor: [600, 1173], h: 954, slots: [
    ['armL', ['arm_screen_left'], [505, 629]], ['armR', ['arm_screen_right'], [694, 636]],
    ['legL', ['leg_screen_left'], [533, 940]], ['legR', ['leg_screen_right'], [659, 950]],
    ['body', ['body'], [600, 920]], ['head', ['head_open', 'head_closed', 'head_laughing'], [600, 615]],
    ['scarf', ['scarf_white'], [620, 610]]] },
  C2: { anchor: [600, 830], h: 808, slots: [
    ['wingL', ['wing_left_open', 'wing_left_folded'], [615, 900]], ['wingR', ['wing_right_open', 'wing_right_folded'], [585, 900]],
    ['body', ['body'], [600, 800]], ['head', ['head'], [600, 700]],
    ['face', ['face_sad', 'face_surprised', 'face_laughing'], [600, 700], 'head']] },
  C3: { anchor: [600, 1385], h: 1143, slots: [
    ['body', ['body'], [600, 1300]], ['head', ['head'], [600, 720]],
    ['armL', ['arm_left_rest', 'arm_left_winding_clock'], [495, 600]], ['armR', ['arm_right_rest', 'arm_right_winding_key'], [700, 600]]] },
  C1: { anchor: [600, 725], h: 1034, slots: [
    ['grey', ['body_grey'], [600, 725]], ['pale', ['body_pale'], [600, 725]], ['bright', ['body_bright'], [600, 725]],
    ['eyes', ['eyes_open', 'eyes_closed', 'eyes_laugh'], [600, 725]], ['mouth', ['mouth_smile', 'mouth_tired', 'mouth_laugh'], [600, 725]]] },
  C4: { anchor: [600, 615], h: 808, slots: [
    ['rain', ['rain'], [600, 1000]], ['body', ['body'], [600, 615]], ['face', ['face_sad', 'face_happy'], [600, 650]]] },
};
const POSEH = { // painted poses: height on screen as a fraction of the character's standing height
  C5_front: 1, C5_laughing: 1.02, C5_sitting: 0.86, C5_sleeping: 0.66, C5_standing: 1, C5_walking: 1,
  C6_laughing: 1, C6_sitting: 0.64, C6_sleeping: 0.5, C6_standing: 1, C6_walking: 0.98, C6_waving: 1.04,
  C7_laughing: 1, C7_rear_view: 1, C7_sitting: 0.62, C7_sleeping: 0.42, C7_standing: 1, C7_walking: 0.98,
};

// ---------- the scene builder ----------
// A scene = a list of shots. Each shot is its own layer (plate + actors + fx), so shots can dissolve.
export function makeScene({ shots, subs = [], css = '', fades = { in: 1.2, out: 1.6 }, duration }) {
  const SUB_TEXT = subs.map((s) => s[3]).join('');
  const html = (IMG) => {
    const A = IMG.replace(/img\/$/, 'art2/');
    return `<div id="stage">
${shots.map((s, i) => `<div class="shot" id="shot${i}"><div class="world" id="w${i}">
  ${(s.plates || [s.plate]).map((p, j) => `<img class="plate" id="pl${i}_${j}" src="${A}${p.includes('/') ? p : 'backgrounds/' + p}.jpg">`).join('')}
  <div class="actors" id="ac${i}"></div><div class="actors" id="at${i}"></div><svg class="fxw" id="fxw${i}" viewBox="0 0 2880 1206"></svg></div>
  <svg class="fxs" id="fxs${i}" viewBox="0 0 1920 804"></svg><div class="tint" id="tint${i}"></div></div>`).join('')}
 <div id="glowL"></div>
 <svg id="grain" viewBox="0 0 1920 804"><filter id="grainF" x="0" y="0" width="100%" height="100%">
  <feTurbulence id="grainT" type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="1" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/></filter><rect width="1920" height="804" filter="url(#grainF)"/></svg>
 <img id="paper" src="${IMG}paper.jpg"><div id="vig"></div>
 <div id="subs"><div class="en"></div><div class="zh"></div></div>
 <div id="fade"></div></div>
 <span id="ART" data-a="${A}" style="display:none"></span>`;
  };
  const fullCss = `
#stage{position:relative;width:1920px;height:804px;overflow:hidden;background:#000}
.shot{position:absolute;inset:0;overflow:hidden;opacity:0}
.world{position:absolute;left:0;top:0;width:2880px;height:1206px;transform-origin:0 0}
.plate{position:absolute;left:0;top:0;width:2880px;height:1206px}
.actors{position:absolute;left:0;top:0}
.fxw{position:absolute;left:0;top:0;width:2880px;height:1206px;overflow:visible;pointer-events:none}
.fxs{position:absolute;left:0;top:0;width:1920px;height:804px;overflow:visible;pointer-events:none}
.tint{position:absolute;inset:0;pointer-events:none;opacity:0}
.actor{position:absolute;left:0;top:0;width:0;height:0;transform-origin:0 0}
.actor .in{position:absolute;left:0;top:0;transform-origin:0 0}
.actor img{position:absolute;display:block}
.slot{position:absolute;left:0;top:0;width:0;height:0}
.glow{position:absolute;border-radius:50%;pointer-events:none;mix-blend-mode:screen}
#glowL{position:absolute;inset:0;pointer-events:none;mix-blend-mode:soft-light;opacity:0}
#grain{position:absolute;left:0;top:0;width:1920px;height:804px;pointer-events:none;mix-blend-mode:overlay;opacity:.10}
#paper{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:multiply;opacity:.16;pointer-events:none}
#vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 75% 70% at 50% 48%,rgba(0,0,0,0) 58%,rgba(20,10,4,.38) 100%)}
#subs{position:absolute;left:0;right:0;bottom:30px;text-align:center;pointer-events:none}
#subs .en{font:40px/1.25 Lora,Georgia,serif;color:#fffaf0;text-shadow:0 0 6px rgba(20,12,30,.9),0 0 18px rgba(20,12,30,.7)}
#subs .en.it{font-style:italic}
#subs .zh{font:31px/1.5 "Noto Serif SC",serif;color:#fff3e0;text-shadow:0 0 6px rgba(20,12,30,.9),0 0 16px rgba(20,12,30,.7)}
#fade{position:absolute;inset:0;background:#000}
${css}`;

  function setup() {
    const $ = (s) => document.querySelector(s);
    const A = $('#ART').dataset.a;
    const S = shots.map((s, i) => {
      const ctx = {
        i, el: $('#shot' + i), world: $('#w' + i), acEl: $('#ac' + i), atEl: $('#at' + i), fxw: $('#fxw' + i), fxs: $('#fxs' + i), tint: $('#tint' + i),
        plates: (s.plates || [s.plate]).map((_, j) => $(`#pl${i}_${j}`)), actors: {}, A, cam: { x: 1440, y: 603, z: 1 },
      };
      for (const [name, def] of Object.entries(s.actors || {})) ctx.actors[name] = makeActor(ctx, name, def, A);
      if (s.init) s.init(ctx);
      return ctx;
    });
    return {
      render: (t) => {
        let glowAmt = 0;
        shots.forEach((s, i) => {
          const c = S[i], xf = s.xf ?? 1.2;
          const vis = t >= s.t0 - xf && t < s.t1 + (shots[i + 1]?.t0 === s.t1 ? 0.0001 : 0) + ((shots[i + 1]?.xf ?? 0) > 0 && shots[i + 1].t0 < s.t1 + 0.001 ? 0 : 0);
          // a shot is drawn from (t0 - its xf) to t1; the next one dissolves in on top of it
          const on = t >= s.t0 - xf && t < s.t1;
          c.el.style.display = on ? 'block' : 'none';
          if (!on) return;
          const lt = t;
          c.el.style.opacity = xf > 0 ? ss((t - (s.t0 - xf)) / xf).toFixed(4) : '1';
          const cam = track(s.cam || [[0, { x: 1440, y: 603, z: 1 }]], lt);
          const shake = cam.shake || 0;
          c.cam = { x: cam.x + noise(lt * 7) * shake * 20, y: cam.y + noise(lt * 7 + 30) * shake * 14, z: cam.z, r: cam.r || 0 };
          if (!s.free) { const hw = 960 / (BS * c.cam.z) + 2, hh = 402 / (BS * c.cam.z) + 2; c.cam.x = clamp(c.cam.x, hw, 2880 - hw); c.cam.y = clamp(c.cam.y, hh, 1206 - hh); }
          const z = BS * c.cam.z;
          c.world.style.transform = `translate(960px,402px) rotate(${c.cam.r}deg) scale(${z}) translate(${-c.cam.x}px,${-c.cam.y}px)`;
          if (s.plates) { const p = track(s.plateMix || [[0, { m: 0 }]], lt).m; c.plates.forEach((pl, j) => { pl.style.opacity = j === 0 ? 1 : clamp(p - (j - 1)).toFixed(4); }); }
          if (s.grade) { const g = track(s.grade, lt); c.plates.forEach((pl) => { pl.style.filter = g.f || ''; }); c.acEl.style.filter = g.af || ''; if (g.tint !== undefined) { c.tint.style.background = g.tc || '#000'; c.tint.style.opacity = g.tint; c.tint.style.mixBlendMode = g.tb || 'multiply'; } }
          for (const [name, a] of Object.entries(c.actors)) a.render(track(a.def.track || [[0, {}]], lt), lt);
          if (s.draw) s.draw(lt, c);
          glowAmt = Math.max(glowAmt, c.glow || 0);
        });
        // subtitles
        let on = null;
        for (const sb of subs) if (t >= sb[0] - 0.25 && t <= sb[1] + 0.35) on = sb;
        const en = $('#subs .en'), zh = $('#subs .zh');
        if (on) {
          en.textContent = on[2]; zh.textContent = on[3]; en.className = 'en' + (on[4] === 'it' ? ' it' : '');
          $('#subs').style.opacity = Math.min(ss((t - on[0] + 0.25) / 0.3), ss((on[1] + 0.35 - t) / 0.3)).toFixed(3);
        } else $('#subs').style.opacity = 0;
        // fades, grain, weave
        $('#fade').style.opacity = Math.max(1 - ss(t / fades.in), ss((t - (duration - fades.out)) / fades.out)).toFixed(4);
        const f = Math.floor(t * 24);
        $('#grainT').setAttribute('seed', String((f % 97) + 1));
        const st = $('#stage');
        st.style.transform = `translate(${((hash(f) - 0.5) * 0.8).toFixed(2)}px,${((hash(f + 50) - 0.5) * 0.8).toFixed(2)}px)`;
      },
    };
  }
  return { html, css: fullCss, setup, SUB_TEXT, DURATION: duration };
}

// ---------- world/screen helpers ----------
export const toScreen = (c, x, y) => [960 + (x - c.cam.x) * BS * c.cam.z, 402 + (y - c.cam.y) * BS * c.cam.z];

// ---------- actors ----------
// def: {char:'C6', h: standing height (world px), track:[...], z: order, mode:'rig'|'pose', glow:{...}}
// track props: x y (feet / anchor in world px), s (scale), flip (1 | -1), rot, op, pose (a painted pose name, or 'rig'),
// face ('open'|'closed'|'laughing'...), walk (0..1), talk (0..1), laugh (0..1), armL armR legL legR head tail (deg),
// wings ('open'|'folded'), flap (0..1), light (Pip: 0 grey … 1 gold), bob, blur, bright
function makeActor(ctx, name, def, A) {
  const char = def.char;
  const el = document.createElement('div'); el.className = 'actor'; el.style.zIndex = def.z || 0;
  const inner = document.createElement('div'); inner.className = 'in'; el.appendChild(inner);
  (def.top ? ctx.atEl : ctx.acEl).appendChild(el);
  const rig = RIGS[char], parts = RIG[char]?.parts;
  const slots = {};
  const rigEl = document.createElement('div'); rigEl.style.position = 'absolute'; inner.appendChild(rigEl);
  if (rig) {
    for (const [sn, vars, piv, parent] of rig.slots) {
      const g = document.createElement('div'); g.className = 'slot';
      g.style.transformOrigin = `${piv[0]}px ${piv[1]}px`;
      const imgs = {};
      for (const v of vars) {
        const b = parts[v]; const im = document.createElement('img');
        im.src = `${A}rig/${char}/${v}.png`; im.style.left = b[0] + 'px'; im.style.top = b[1] + 'px'; im.style.width = b[2] + 'px'; im.style.height = b[3] + 'px';
        g.appendChild(im); imgs[v] = im;
      }
      (parent ? slots[parent].g : rigEl).appendChild(g);
      slots[sn] = { g, imgs, vars, piv };
    }
  }
  // painted poses
  const poses = {};
  const poseEl = document.createElement('div'); poseEl.style.position = 'absolute'; inner.appendChild(poseEl);
  for (const pn of def.poses || []) {
    const key = `${char}_${pn}`, b = RIG.poses[key]; const im = document.createElement('img');
    im.src = `${A}rig/poses/${key}.png`; im.style.display = 'none'; poseEl.appendChild(im); poses[pn] = { im, b, k: POSEH[key] || 1 };
  }
  // extra images (props): def.img = 'props/P1_box_lantern.png', anchor [x,y] in that image, ih = natural height
  let propIm = null;
  if (def.img) { propIm = document.createElement('img'); propIm.src = A + def.img; inner.appendChild(propIm); }
  // glow
  let glow = null;
  if (def.glow) { glow = document.createElement('div'); glow.className = 'glow'; el.insertBefore(glow, inner); }
  if (def.init) def.init(el, inner);

  const anchor = rig ? rig.anchor : [0, 0];
  const a = {
    def, el, inner, slots, poses,
    render(p, t) {
      const op = p.op ?? 1;
      el.style.display = op <= 0.001 ? 'none' : 'block';
      if (op <= 0.001) return;
      el.style.opacity = op;
      const hgt = def.h * (p.s ?? 1);
      const ph = (def.phase || 0);
      const walk = p.walk || 0, talk = p.talk || 0, laugh = p.laugh || 0;
      const wt = t * (def.wspeed || 7.5) + ph;
      const bob = (p.bob || 0) + walk * Math.abs(Math.sin(wt)) * -0.035 * hgt + laugh * Math.abs(Math.sin(t * 16)) * -0.02 * hgt
        + Math.sin(t * 1.7 + ph) * 0.004 * hgt * (def.breath ?? 1);
      const breath = 1 + Math.sin(t * 1.9 + ph) * 0.006 * (def.breath ?? 1);
      const rot = (p.rot || 0) + walk * Math.sin(wt) * 1.5 + laugh * Math.sin(t * 13) * 2;
      const flip = p.flip ?? 1;
      el.style.transform = `translate(${p.x}px,${(p.y + bob).toFixed(2)}px) rotate(${rot.toFixed(2)}deg) scale(${flip},1)`;
      el.style.filter = p.f || '';
      const pose = p.pose || def.pose || 'rig';
      if (pose === 'rig' && rig) {
        rigEl.style.display = 'block'; poseEl.style.display = 'none';
        const k = hgt / rig.h;
        inner.style.transform = `scale(${k.toFixed(5)},${(k * breath).toFixed(5)}) translate(${-anchor[0]}px,${-anchor[1]}px)`;
        if (propIm) propIm.style.display = 'none';
        // blinks every few seconds unless the face is set
        let face = p.face || 'open';
        if (face === 'open' && def.blink !== false) { const bt = (t + ph * 3.1) % (3.7 + (ph % 1.3)); if (bt < 0.14) face = 'closed'; }
        if (laugh > 0.5 && !p.face) face = 'laughing';
        const ang = (sn) => {
          let v = p[sn] || 0;
          if (sn === 'legL' || sn === 'legFL' || sn === 'legHR') v += walk * Math.sin(wt) * 22;
          if (sn === 'legR' || sn === 'legFR' || sn === 'legHL') v -= walk * Math.sin(wt) * 22;
          if (sn === 'armL') v += walk * Math.sin(wt) * -10 + laugh * Math.sin(t * 14) * 4;
          if (sn === 'armR') v += walk * Math.sin(wt) * 10 - laugh * Math.sin(t * 14) * 4;
          if (sn === 'head') v += talk * Math.sin(t * 9 + ph) * 2.5 + walk * Math.sin(wt * 2) * 1;
          if (sn === 'tail') v += Math.sin(t * 5 + ph) * 8 + walk * Math.sin(wt * 2) * 10;
          if (sn === 'scarf') v += Math.sin(t * 2.3 + ph) * 3 + walk * 4;
          if ((sn === 'wingL' || sn === 'wingR') && p.flap) v += (sn === 'wingL' ? 1 : -1) * Math.sin(t * (def.flapSpeed || 5) + ph) * 28 * p.flap;
          return v;
        };
        for (const sn in slots) {
          const s = slots[sn];
          let tr = `rotate(${ang(sn).toFixed(2)}deg)`;
          if ((sn === 'wingL' || sn === 'wingR') && p.flap) tr += ` scale(${(1 - 0.18 * p.flap * (0.5 + 0.5 * Math.sin(t * (def.flapSpeed || 5) + ph))).toFixed(3)},1)`;
          s.g.style.transform = tr;
          if (s.vars.length > 1) {
            let pick;
            if (sn === 'head') pick = `head_${face}`;
            else if (char === 'C2' && sn === 'face') pick = `face_${p.mood || 'sad'}`;
            else if (char === 'C2') pick = `${sn === 'wingL' ? 'wing_left' : 'wing_right'}_${p.wings || 'open'}`;
            else if (char === 'C3') pick = sn === 'armL' ? (p.wind ? 'arm_left_winding_clock' : 'arm_left_rest') : (p.wind ? 'arm_right_winding_key' : 'arm_right_rest');
            else if (char === 'C1' && sn === 'eyes') pick = 'eyes_' + (p.face === 'laughing' || laugh > 0.5 ? 'laugh' : p.face === 'closed' || face === 'closed' ? 'closed' : 'open');
            else if (char === 'C1' && sn === 'mouth') pick = 'mouth_' + (p.face === 'laughing' || laugh > 0.5 ? 'laugh' : (p.light ?? 1) < 0.45 ? 'tired' : 'smile');
            else if (char === 'C4' && sn === 'face') pick = `face_${p.mood || 'sad'}`;
            for (const v of s.vars) s.imgs[v].style.display = v === pick ? 'block' : 'none';
          }
        }
        if (char === 'C1') { // Pip: grey → pale → gold
          const L = clamp(p.light ?? 1);
          slots.grey.g.style.opacity = 1; slots.pale.g.style.opacity = ss(L * 2).toFixed(3); slots.bright.g.style.opacity = ss(L * 2 - 1).toFixed(3);
        }
        if (char === 'C4') slots.rain.g.style.opacity = (p.rain ?? 1).toFixed(3), slots.rain.g.style.transform = `translate(0px,${((t * 220) % 60).toFixed(1)}px)`;
      } else if (poses[pose]) {
        rigEl.style.display = 'none'; poseEl.style.display = 'block';
        if (propIm) propIm.style.display = 'none';
        for (const pn in poses) poses[pn].im.style.display = pn === pose ? 'block' : 'none';
        const P = poses[pose], [x0, y0, w, h] = P.b, k = (hgt * P.k) / h;
        const im = P.im; im.style.left = '0px'; im.style.top = '0px'; im.style.width = w + 'px'; im.style.height = h + 'px';
        const ax = (p.ax ?? 0.5) * w;
        inner.style.transform = `scale(${k.toFixed(5)},${(k * breath).toFixed(5)}) translate(${-ax}px,${-h}px)`;
      } else if (propIm) {
        rigEl.style.display = 'none'; poseEl.style.display = 'none'; propIm.style.display = 'block';
        const [iw, ih] = def.isize, k = hgt / ih;
        inner.style.transform = `scale(${k.toFixed(5)}) translate(${-def.anchor[0]}px,${-def.anchor[1]}px)`;
        propIm.style.width = iw + 'px'; propIm.style.height = ih + 'px';
      } else { rigEl.style.display = 'none'; poseEl.style.display = 'none'; inner.style.transform = `scale(${(p.s ?? 1) * (def.k ?? 1)})`; }
      if (glow) {
        const g = def.glow, L = p.glow ?? (p.light ?? 1);
        const r = (g.r || 1.6) * hgt * (0.55 + 0.45 * L) * (1 + 0.04 * Math.sin(t * 3 + ph));
        glow.style.width = glow.style.height = 2 * r + 'px';
        glow.style.left = (-r + (g.dx || 0) * hgt) + 'px'; glow.style.top = (-r + (g.dy || 0) * hgt) + 'px';
        glow.style.background = `radial-gradient(circle, ${g.c || 'rgba(255,214,120,.85)'} 0%, ${g.c2 || 'rgba(255,190,90,.35)'} 30%, rgba(255,170,60,0) 70%)`;
        glow.style.opacity = (L * (g.op ?? 1)).toFixed(3);
      }
      a.last = p;
    },
  };
  return a;
}

// ---------- effects (SVG, world or screen space) ----------
const NS = 'http://www.w3.org/2000/svg';
export const svg = (parent, tag, attrs = {}) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };

// twinkling stars scattered over a region (world px). returns draw(t, amount)
export function stars(parent, n, { x0 = 0, y0 = 0, x1 = 2880, y1 = 700, seed = 1, r = 2.2, color = '#fff6dc' } = {}) {
  const g = svg(parent, 'g'); const L = [];
  for (let i = 0; i < n; i++) {
    const c = svg(g, 'circle', { cx: lerp(x0, x1, hash(seed + i * 3.1)), cy: lerp(y0, y1, hash(seed + i * 7.7)), r: r * (0.5 + hash(i * 1.3 + seed)), fill: color });
    L.push({ c, ph: hash(i * 5.3) * 6.28, sp: 1 + hash(i * 2.9) * 3 });
  }
  return (t, amt = 1, laugh = 0) => { for (const s of L) s.c.setAttribute('opacity', (amt * clamp(0.45 + 0.4 * Math.sin(t * s.sp + s.ph) + laugh * 0.6 * Math.sin(t * 17 + s.ph * 3))).toFixed(3)); };
}
// soft glowing dot (for stars that matter, sparkles)
export function glowDot(parent, id, color = '#ffe9a8') {
  const defs = svg(parent, 'defs');
  const rg = svg(defs, 'radialGradient', { id });
  svg(rg, 'stop', { offset: '0', 'stop-color': '#fffef5', 'stop-opacity': 1 });
  svg(rg, 'stop', { offset: '0.25', 'stop-color': color, 'stop-opacity': 0.8 });
  svg(rg, 'stop', { offset: '1', 'stop-color': color, 'stop-opacity': 0 });
  return svg(parent, 'circle', { fill: `url(#${id})`, r: 0 });
}
// rain streaks over the frame (screen space)
export function rain(parent, n = 140, color = 'rgba(220,230,255,.55)') {
  const g = svg(parent, 'g', { stroke: color, 'stroke-width': 2, 'stroke-linecap': 'round' }); const L = [];
  for (let i = 0; i < n; i++) L.push({ l: svg(g, 'line'), x: hash(i * 3.3) * 2100 - 90, ph: hash(i * 9.1), sp: 900 + hash(i) * 500, len: 26 + hash(i * 4) * 26 });
  return (t, amt = 1) => {
    g.setAttribute('opacity', amt.toFixed(3));
    if (amt <= 0) return;
    for (const d of L) {
      const y = ((t * d.sp + d.ph * 900) % 900) - 60, x = d.x - y * 0.12;
      d.l.setAttribute('x1', x.toFixed(1)); d.l.setAttribute('y1', y.toFixed(1)); d.l.setAttribute('x2', (x - d.len * 0.12).toFixed(1)); d.l.setAttribute('y2', (y + d.len).toFixed(1));
    }
  };
}
// sparkles drifting up from a point (screen or world). returns draw(t, x, y, amt)
export function sparkles(parent, n = 24, color = '#ffe08a', seed = 2) {
  const g = svg(parent, 'g'); const L = [];
  for (let i = 0; i < n; i++) L.push({ c: svg(g, 'circle', { fill: color }), ph: hash(seed + i * 1.7), sp: 0.4 + hash(i * 3.7 + seed) * 0.8, dx: (hash(i * 5.1 + seed) - 0.5) * 2 });
  return (t, x, y, amt = 1, spread = 120) => {
    for (const s of L) {
      const u = (t * s.sp + s.ph) % 1;
      s.c.setAttribute('cx', (x + s.dx * spread * (0.3 + u)).toFixed(1)); s.c.setAttribute('cy', (y - u * spread * 1.6).toFixed(1));
      s.c.setAttribute('r', (2.5 + 3 * (1 - u)).toFixed(2)); s.c.setAttribute('opacity', (amt * Math.sin(u * Math.PI)).toFixed(3));
    }
  };
}
// a little flock of the boy's migratory birds, painted in two tones. draw(t, list of {x,y,s,flap})
const BIRD_P = (w) => `M${-60} ${-6 - w * 30} Q-30 ${-18 - w * 20} -6 -2 Q0 4 6 -2 Q30 ${-18 - w * 20} 60 ${-6 - w * 30} Q30 ${-4 - w * 10} 6 8 Q0 14 -6 8 Q-30 ${-4 - w * 10} -60 ${-6 - w * 30}Z`;
export function birds(parent, n = 5, { fill = '#f7efe3', stroke = '#6b4b38', k = 1.7 } = {}) {
  const L = [];
  for (let i = 0; i < n; i++) {
    const g = svg(parent, 'g');
    const p = svg(g, 'path', { fill, stroke, 'stroke-width': 3.5, 'stroke-linejoin': 'round' });
    const head = svg(g, 'circle', { cx: 0, cy: 2, r: 8, fill, stroke, 'stroke-width': 3 });
    const beak = svg(g, 'path', { d: 'M0 6 L-4 14 L4 14Z', fill: '#e2a04a', stroke, 'stroke-width': 1.5 });
    L.push({ g, p });
  }
  return (t, list) => L.forEach((b, i) => {
    const d = list[i]; if (!d) { b.g.setAttribute('opacity', 0); return; }
    const w = Math.sin(t * (d.speed || 9) + i * 1.9) * (d.flap ?? 1);
    b.p.setAttribute('d', BIRD_P(w));
    b.g.setAttribute('opacity', d.op ?? 1);
    b.g.setAttribute('transform', `translate(${d.x.toFixed(1)},${d.y.toFixed(1)}) scale(${((d.s || 1) * k).toFixed(3)})`);
  });
}
// string from (x1,y1) to (x2,y2) with a little sag
export const strand = (parent, color = 'rgba(80,60,50,.75)', w = 2) => { const p = svg(parent, 'path', { fill: 'none', stroke: color, 'stroke-width': w }); return (x1, y1, x2, y2, sag = 20, op = 1) => { p.setAttribute('d', `M${x1} ${y1} Q${(x1 + x2) / 2} ${(y1 + y2) / 2 + sag} ${x2} ${y2}`); p.setAttribute('opacity', op); }; };

// a star that matters: soft glow plus a four-point flare. draw(x, y, r, op)
export function flareStar(parent, id, color = '#ffe9a8') {
  const g = svg(parent, 'g'); const d = glowDot(g, id, color);
  const f = svg(g, 'path', { fill: '#fffbea' });
  return (x, y, r, op = 1) => {
    d.setAttribute('cx', x); d.setAttribute('cy', y); d.setAttribute('r', Math.max(0, r));
    const a = r * 1.6, b = r * 0.09;
    f.setAttribute('d', `M${x - a} ${y} L${x - b} ${y - b} L${x} ${y - a} L${x + b} ${y - b} L${x + a} ${y} L${x + b} ${y + b} L${x} ${y + a} L${x - b} ${y + b}Z`);
    g.setAttribute('opacity', op);
  };
}

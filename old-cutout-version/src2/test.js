import {makeScene} from './kit.js';
const BOY = 300;
export const {html, css, setup, SUB_TEXT, DURATION} = makeScene({ duration: 6, fades: {in: 0.01, out: 0.01}, subs: [[0, 6, 'Test line.', '测试。']],
  shots: [{ t0: 0, t1: 6, xf: 0, plate: 'B1_b612_day', cam: [[0, {x: 1440, y: 603, z: 1}]],
    actors: {
      boy: {char: 'C6', h: BOY, track: [[0, {x: 700, y: 900, walk: 0}], [3, {x: 700, y: 900, walk: 1}]]},
      boyA: {char: 'C6', h: BOY, track: [[0, {x: 950, y: 900, armL: -40, armR: 40}]]},
      sheep: {char: 'C5', h: BOY * 0.62, track: [[0, {x: 1250, y: 900}], [3, {x: 1250, y: 900, walk: 1}]]},
      pip: {char: 'C1', h: 60, glow: {}, track: [[0, {x: 1250, y: 650, light: 0}], [6, {light: 1}]]},
      moth: {char: 'C2', h: BOY * 1.4, track: [[0, {x: 1700, y: 500, mood: 'laughing', flap: 0}], [3, {flap: 1}]]},
      clock: {char: 'C3', h: BOY * 0.45, track: [[0, {x: 2050, y: 900, wind: 1}]]},
      cloud: {char: 'C4', h: 220, track: [[0, {x: 2300, y: 450, mood: 'sad'}]]},
      pilot: {char: 'C7', h: BOY * 1.5, track: [[0, {x: 450, y: 950}]]},
      sit: {char: 'C6', h: BOY, poses: ['sitting', 'sleeping'], track: [[0, {x: 1500, y: 1000, pose: 'sitting'}]]},
      sl: {char: 'C5', h: BOY * 0.62, poses: ['sleeping'], track: [[0, {x: 1900, y: 1050, pose: 'sleeping'}]]},
    }}]});

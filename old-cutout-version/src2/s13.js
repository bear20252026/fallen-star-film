// S13 — END CREDITS (1:20), for The Fallen Star. Same look as film 1's credits. Moments from the film appear as pencil sketches on paper, then fill in with watercolour,
// brushed in from left to right, one after another, each with a line of credits.
import gsap from 'gsap';
gsap.defaults({ lazy: false });

const D = 80;
const CARD = (D - 3.6) / 14;
const CARDS = [
  ['The Fallen Star', '坠落的星星'],
  ['Inspired by “The Little Prince” by Antoine de Saint-Exupéry', '灵感来自圣埃克苏佩里《小王子》'],
  ['Pip · The Sheep · The Boy', '皮皮 · 小羊 · 小王子'],
  ['Moth · The Clockmaker · The Little Cloud', '飞蛾 · 钟表匠 · 小云'],
  ['The Pilot · The Rose', '飞行员 · 玫瑰'],
  ['Story, animation and sound by Claude', '故事、动画与声音：Claude'],
  ['Paintings and characters by bear’s illustrators', '绘画与角色：bear 的插画师们'],
  ['Produced by bear', '出品：bear'],
  ['Made with Remotion', '使用 Remotion 制作'],
  ['Two birds who came back', '两只飞回来的小鸟'],
  ['and one very tired pair of wings', '还有一对很累的翅膀'],
  ['For everyone who needs a little light', '献给每一个需要一点光的人'],
  ['Laugh often. Somebody is looking up.', '常常笑吧。总有人在抬头看。'],
  ['Thank you for watching', '谢谢观看'],
];
export const DURATION = D;
export const SUB_TEXT = CARDS.map((c) => c[1]).join('');

export const css = `
#stage{position:relative;width:1920px;height:804px;overflow:hidden;background:#efe6d4}
.card{position:absolute;inset:0;opacity:0}
.card svg{position:absolute;inset:0;width:1920px;height:804px}
.card .col{position:absolute;inset:0;width:1920px;height:804px}
#paper{position:absolute;inset:0;width:100%;height:100%;mix-blend-mode:multiply;opacity:.55;pointer-events:none}
#band{position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(rgba(40,28,20,0),rgba(40,28,20,.55));pointer-events:none}
#cred{position:absolute;left:0;right:0;bottom:46px;text-align:center;pointer-events:none}
#cred .en{font:italic 46px/1.3 Lora,Georgia,serif;color:#fffaf0;text-shadow:0 0 8px rgba(30,20,10,.9),0 0 22px rgba(30,20,10,.6)}
#cred .zh{font:32px/1.6 "Noto Serif SC",serif;color:#fff3e0;text-shadow:0 0 8px rgba(30,20,10,.9)}
#fade{position:absolute;inset:0;background:#000}
`;

export const html = (IMG) => `
<div id="stage">
 <svg width="0" height="0" style="position:absolute"><defs>
  <filter id="pencil" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
   <feColorMatrix type="matrix" values="0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0 0 0 1 0" result="g"/>
   <feGaussianBlur in="g" stdDeviation="2.2" result="gb"/>
   <feConvolveMatrix order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1" preserveAlpha="true" in="gb" result="e"/>
   <feColorMatrix type="matrix" in="e" values="-9 0 0 0 1.05  -9 0 0 0 1.0  -9 0 0 0 0.94  0 0 0 1 0" result="lines"/>
   <feComponentTransfer in="g" result="tone"><feFuncR type="linear" slope=".35" intercept=".62"/><feFuncG type="linear" slope=".35" intercept=".6"/><feFuncB type="linear" slope=".35" intercept=".55"/></feComponentTransfer>
   <feBlend mode="multiply" in="lines" in2="tone"/>
  </filter></defs></svg>
 ${CARDS.map((_, i) => `<div class="card" id="card${i}">
   <svg viewBox="0 0 1920 804"><image href="${IMG}credits2/c${String(i + 1).padStart(2, '0')}.jpg" width="1920" height="804" filter="url(#pencil)"/></svg>
   <img class="col" id="col${i}" src="${IMG}credits2/c${String(i + 1).padStart(2, '0')}.jpg"></div>`).join('')}
 <img id="paper" src="${IMG}paper.jpg">
 <div id="band"></div>
 <div id="cred"><div class="en"></div><div class="zh"></div></div>
 <div id="fade"></div>
</div>`;

export function setup() {
  const $ = (s) => document.querySelector(s);
  const tl = gsap.timeline({ paused: true });
  tl.set('#fade', { opacity: 1 }, 0).to('#fade', { opacity: 0, duration: 1.5 }, 0);
  CARDS.forEach((_, i) => {
    const a = i * CARD;
    tl.set('#card' + i, { opacity: 0, scale: 1.0 }, 0);
    tl.to('#card' + i, { opacity: 1, duration: 0.8, ease: 'sine.inOut' }, a).to('#card' + i, { scale: 1.05, duration: CARD + 0.8, ease: 'none' }, a);
    if (i < CARDS.length - 1) tl.to('#card' + i, { opacity: 0, duration: 0.8, ease: 'sine.inOut' }, a + CARD);
  });
  tl.to('#fade', { opacity: 1, duration: 3 }, DURATION - 3.2);
  const ss = (u) => { u = Math.min(1, Math.max(0, u)); return u * u * (3 - 2 * u); };
  return {
    render: (t) => {
      tl.seek(t);
      // the colour is brushed in from left to right, a little after each sketch appears
      CARDS.forEach((_, i) => {
        const u = ss((t - i * CARD - 1.2) / 2.4), x = -25 + u * 150;
        const m = `linear-gradient(100deg,#000 ${(x - 20).toFixed(1)}%,rgba(0,0,0,0) ${x.toFixed(1)}%)`;
        const e = $('#col' + i); e.style.webkitMaskImage = m; e.style.maskImage = m;
      });
      const i = Math.min(CARDS.length - 1, Math.floor(t / CARD)), lt = t - i * CARD;
      $('#cred .en').textContent = CARDS[i][0]; $('#cred .zh').textContent = CARDS[i][1];
      let k = Math.min(1, (lt - 0.6) / 0.6); if (i < CARDS.length - 1) k = Math.min(k, (CARD + 0.3 - lt) / 0.5);
      $('#cred').style.opacity = Math.max(0, k).toFixed(3);
    },
  };
}
export const AUDIO = 'audio2/s13.wav';

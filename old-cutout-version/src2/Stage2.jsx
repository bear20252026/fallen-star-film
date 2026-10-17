import React, {useLayoutEffect, useRef, useState} from 'react';
import {useCurrentFrame, useVideoConfig, delayRender, continueRender, staticFile} from 'remotion';
import '@fontsource/lora/400.css';
import '@fontsource/lora/400-italic.css';
import '@fontsource/noto-serif-sc/400.css';

// Like Stage, but scenes build their puppets in setup(), so it waits for every image made there too.
export const Stage2 = ({part}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ref = useRef(null);
  const api = useRef(null);
  const [handle] = useState(() => delayRender('Loading art and fonts', {timeoutInMilliseconds: 120000}));
  const [html] = useState(() => part.html(staticFile('img/')));
  useLayoutEffect(() => {
    let cancelled = false;
    const text = part.SUB_TEXT || '';
    const fonts = [document.fonts.load('40px Lora', 'Ab'), document.fonts.load('italic 40px Lora', 'Ab'), document.fonts.load('31px "Noto Serif SC"', text || '羊')];
    api.current = part.setup();
    const imgs = [...ref.current.querySelectorAll('img')].map((i) => i.decode().catch(() => {}));
    Promise.all([...imgs, ...fonts]).then(() => document.fonts.ready).then(() => {
      if (cancelled) return;
      api.current.render(frame / fps);
      continueRender(handle);
    });
    return () => { cancelled = true; };
  }, []);
  useLayoutEffect(() => { if (api.current) api.current.render(frame / fps); }, [frame, fps]);
  return (
    <div style={{width: 1920, height: 804, background: '#000'}}>
      <style>{`#stage *{box-sizing:content-box}` + part.css}</style>
      <div ref={ref} dangerouslySetInnerHTML={{__html: html}} />
    </div>
  );
};

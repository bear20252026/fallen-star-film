#!/bin/bash
# Film 2 chunked render queue (restart-safe): 10 s video-only chunks, then join + mux with the scene's wav.
cd "$(dirname "$0")/.."
BR=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
CH=${CH:-240}; START=$(date +%s); BUDGET=${BUDGET:-0}
while read -r s; do
  [ -z "$s" ] && continue; [ -f render2/$s.mp4 ] && continue
  low=$(echo $s | tr 'S' 's')
  [ -f public/audio2/$low.wav ] || continue
  N=$(python3 -c "import re;print(round(float(re.search(r'^const D = ([0-9.]+);',open('src2/$low.js').read(),re.M).group(1))*24))" 2>/dev/null)
  [ -z "$N" ] && { echo "$(date +%T) no duration for $s" >> render2/queue.log; continue; }
  missing=0
  for ((a=0; a<N; a+=CH)); do
    b=$((a+CH-1)); [ $b -ge $N ] && b=$((N-1))
    tag=${s}_$(printf %05d $a); out=render2/chunks/$tag.mp4
    [ -f $out ] && continue
    if ! mkdir render2/chunks/$tag.lock 2>/dev/null; then missing=1; continue; fi
    if [ $BUDGET -gt 0 ] && [ $(( $(date +%s) - START )) -ge $BUDGET ]; then rmdir render2/chunks/$tag.lock; exit 0; fi
    echo "$(date +%T) $s $a-$b of $N" >> render2/queue.log
    if NOAUDIO=1 npx remotion render < /dev/null src2/index2.jsx $s render2/chunks/part_$$.mp4 --frames=$a-$b --muted --gl=swiftshader --browser-executable=$BR --concurrency=${CONC:-2} --crf=18 --log=error > render2/$s.$$.log 2>&1; then
      mv render2/chunks/part_$$.mp4 $out; rmdir render2/chunks/$tag.lock
    else rmdir render2/chunks/$tag.lock; echo "$(date +%T) FAILED $s $a" >> render2/queue.log; missing=1; continue; fi
  done
  [ $missing = 1 ] && continue
  ls render2/chunks/${s}_*.mp4 2>/dev/null | wc -l | grep -q "^$(( (N+CH-1)/CH ))$" || continue
  mkdir render2/chunks/${s}.joining 2>/dev/null || continue
  ls render2/chunks/${s}_*.mp4 | sort | sed "s#^render2/chunks/#file '#; s#\$#'#" > render2/chunks/$s.txt
  ffmpeg -nostdin -loglevel error -y -f concat -safe 0 -i render2/chunks/$s.txt -i public/audio2/$low.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest render2/$s.tmp.mp4 && mv render2/$s.tmp.mp4 render2/$s.mp4 && echo "$(date +%T) done $s" >> render2/queue.log
done < render2/queue.txt

#!/bin/bash
# Render the scenes listed in film/queue.txt one after another; re-reads the list after each scene, so scenes can be added while it runs.
cd "$(dirname "$0")/.."
while true; do
  next=""
  for s in $(cat film/queue.txt); do
    [ -f ${OUT_DIR:-../out/scenes}/${s^^}.mp4 ] && continue
    next=$s; break
  done
  if [ -z "$next" ]; then sleep 120; continue; fi
  while pgrep -f "render_scene.py" >/dev/null || pgrep -f "join_scene.py" >/dev/null; do sleep 30; done
  [ -f ${OUT_DIR:-../out/scenes}/${next^^}.mp4 ] && continue
  echo "$(date +%H:%M) start $next"
  mkdir -p film/chunks/$next
  bash film/par.sh $next 2 > film/chunks/$next.par.log 2>&1
  echo "$(date +%H:%M) done $next"
done

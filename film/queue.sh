#!/bin/bash
# Render scenes one after another (each waits for the previous scene's final file). Usage: bash film/queue.sh s02 s03 ...
cd "$(dirname "$0")/.."
for s in "$@"; do
  out=${OUT_DIR:-../out/scenes}/${s^^}.mp4
  [ -f "$out" ] && continue
  while pgrep -f "render_scene.py" >/dev/null || pgrep -f "join_scene.py" >/dev/null; do sleep 30; done
  mkdir -p film/chunks/$s
  bash film/par.sh $s 2 > film/chunks/$s.par.log 2>&1
done

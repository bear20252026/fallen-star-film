#!/bin/bash
# Keep 4 render workers busy across scenes (next scene starts as soon as a core is free), and join each scene when all its pieces are done.
# Scene list: film/queue.txt (re-read every loop).
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nchunks() { python3 -c "import re,math;d=float(re.search(r'DURATION = ([0-9.]+)',open('film/$1.py').read()).group(1));print(math.ceil(d/30-1e-6))"; }
while true; do
  for s in $(cat film/queue.txt); do
    out=${OUT_DIR:-../out/scenes}/${s^^}.mp4
    [ -f "$out" ] && continue
    n=$(nchunks $s); mkdir -p film/chunks/$s
    have=$(ls film/chunks/$s/c[0-9][0-9][0-9].mp4 2>/dev/null | wc -l)
    locks=$(ls -d film/chunks/$s/c*.lock 2>/dev/null | wc -l)
    if [ "$have" -ge "$n" ] && [ "$locks" -eq 0 ]; then
      if ! pgrep -f "join_scene.py $s" >/dev/null && ! pgrep -f "par.sh $s" >/dev/null; then
        echo "$(date +%H:%M) join $s"; python3 film/join_scene.py $s >> film/chunks/$s.join.log 2>&1 && echo "$(date +%H:%M) done $s"
      fi
      continue
    fi
    free=$(( have + locks < n ))
    w=$(pgrep -fc "render_scene.py")
    if [ "$free" -eq 1 ] && [ "$w" -lt 4 ]; then
      echo "$(date +%H:%M) worker for $s"
      (setsid python3 film/render_scene.py $s 2 >> film/chunks/$s.w.log 2>&1 < /dev/null &)
      sleep 5; break
    fi
  done
  sleep 20
done

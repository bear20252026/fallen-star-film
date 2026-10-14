#!/bin/bash
# One line: which scenes are finished, and how far the current scene is.
cd "$(dirname "$0")/.."
done_s=""; cur=""
for s in $(cat film/queue.txt); do
  if [ -f ${OUT_DIR:-../out/scenes}/${s^^}.mp4 ]; then done_s="$done_s ${s^^}"; elif [ -z "$cur" ]; then cur=$s; fi
done
n=$(ls film/chunks/$cur/c[0-9][0-9][0-9].mp4 2>/dev/null | wc -l)
w=$(pgrep -fc "render_scene.py") 
echo "done:${done_s:- none} | now: ${cur^^} $n/10 pieces | workers: $w"

#!/bin/bash
cd "$(dirname "$0")/.."
n=$(ls render2/chunks/*.mp4 2>/dev/null | grep -v part_ | wc -l); echo "chunks done: $n (= $(python3 -c "print(round($n*10/60,1))") min of film)"; ls render2/*.mp4 2>/dev/null; tail -3 render2/queue.log

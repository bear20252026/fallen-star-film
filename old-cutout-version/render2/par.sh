#!/bin/bash
# keep NW workers going, pass after pass, until everything in the queue is rendered or BUDGET runs out
cd "$(dirname "$0")/.."
while pgrep -f "^bash render2/runq.sh" > /dev/null; do sleep 15; done
NW=${NW:-2}; END=$(( $(date +%s) + ${BUDGET:-6600} ))
while [ $(date +%s) -lt $END ]; do
  for i in $(seq 1 $NW); do BUDGET=$(( END - $(date +%s) )) setsid bash render2/runq.sh >> render2/runq.out 2>&1 & sleep 3; done
  while pgrep -f "^bash render2/runq.sh" > /dev/null; do sleep 15; done
  todo=0; while read -r s; do [ -n "$s" ] && [ ! -f render2/$s.mp4 ] && todo=1; done < render2/queue.txt
  [ $todo = 0 ] && break
  sleep 20
done
echo "$(date +%T) workers finished" >> render2/queue.log

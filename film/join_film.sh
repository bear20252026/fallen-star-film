#!/bin/bash
# Join the 13 finished scenes (out/scenes/S01.mp4 ... S13.mp4) into the whole 60-minute film.
# Usage: bash film/join_film.sh        -> out/The_Fallen_Star.mp4
set -e
cd "$(dirname "$0")/.."; SC=${OUT_DIR:-$PWD/out/scenes}; OUT=$PWD/out; mkdir -p $OUT
rm -f $OUT/list.txt
for n in 01 02 03 04 05 06 07 08 09 10 11 12 13; do echo "file '$SC/S$n.mp4'" >> $OUT/list.txt; done
ffmpeg -y -v error -f concat -safe 0 -i $OUT/list.txt -c copy -movflags +faststart $OUT/The_Fallen_Star.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT/The_Fallen_Star.mp4

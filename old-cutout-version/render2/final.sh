#!/bin/bash
# Join all scenes (each already fades through black) into the 60:00 master, then cut 4 parts and a small whole film.
cd "$(dirname "$0")/.."
set -e
O=/mnt/project-files/sheep-film2/final; mkdir -p $O
: > render2/all.txt; while read -r s; do [ -n "$s" ] && echo "file '$PWD/render2/$s.mp4'" >> render2/all.txt; done < render2/queue.txt
ffmpeg -nostdin -loglevel error -y -f concat -safe 0 -i render2/all.txt -c copy render2/master.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 render2/master.mp4
for i in 0 1 2 3; do
  ffmpeg -nostdin -loglevel error -y -ss $((i*900)) -t 900 -i render2/master.mp4 -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$O/The_Fallen_Star_part$((i+1))_of_4.mp4"
done
ffmpeg -nostdin -loglevel error -y -i render2/master.mp4 -vf scale=1440:-2 -c:v libx264 -preset medium -crf 25 -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart "$O/The_Fallen_Star_whole_1440.mp4"
ls -la $O

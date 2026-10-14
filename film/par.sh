#!/bin/bash
# Run 4 render workers for a scene, then join it. Usage: bash film/par.sh s01
cd "$(dirname "$0")/.."
mkdir -p film/chunks/$1; rm -rf film/chunks/$1/*.lock film/chunks/$1/*.part.mp4 2>/dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for i in 1 2 3 4; do python3 film/render_scene.py $1 ${2:-2} > film/chunks/$1.w$i.log 2>&1 & done
wait
python3 film/join_scene.py $1

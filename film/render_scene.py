# Render one scene in 30-second chunks straight to mp4 (no frame files). Several workers can run at once:
# each claims a chunk with an atomic mkdir, so restarts and parallel runs never redo or clash.
# Usage: python3 film/render_scene.py s01 [SUBSAMPLES]     then: python3 film/join_scene.py s01
import sys, os, importlib, subprocess, time
import cv2; cv2.setNumThreads(1)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1]; sub = int(sys.argv[2]) if len(sys.argv) > 2 else 2
S = importlib.import_module(name).SCENE
from base import FPS, W, H
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chunks', name); os.makedirs(OUT, exist_ok=True)
CH = 30.0; n = int((S.DURATION + CH - 1e-6) // CH)
for c in range(n):
    done = os.path.join(OUT, f'c{c:03d}.mp4'); lock = os.path.join(OUT, f'c{c:03d}.lock')
    if os.path.exists(done): continue
    try: os.mkdir(lock)
    except FileExistsError: continue
    t0 = time.time(); f0 = int(c * CH * FPS); f1 = int(min(S.DURATION, (c + 1) * CH) * FPS)
    tmp = done + '.part.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(f0, f1):
        p.stdin.write(S.frame(i / FPS, sub).tobytes())
    p.stdin.close(); p.wait()
    os.rename(tmp, done); os.rmdir(lock)
    print(f'{name} chunk {c} done in {time.time() - t0:.0f}s', flush=True)

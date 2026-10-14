# Join a scene's chunks, add its music and sound, and save it to the project files.
import sys, os, importlib, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
name = sys.argv[1]
mod = importlib.import_module(name); S = mod.SCENE
import audio
D = os.path.dirname(os.path.abspath(__file__)); CH = os.path.join(D, 'chunks', name)
OUTD = os.environ.get('OUT_DIR', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'scenes')); os.makedirs(OUTD, exist_ok=True)
chunks = sorted(glob.glob(os.path.join(CH, 'c[0-9][0-9][0-9].mp4')))
need = int((S.DURATION + 30 - 1e-6) // 30)
if len(chunks) < need: sys.exit(f'{name}: only {len(chunks)}/{need} chunks')
lst = os.path.join(CH, 'list.txt'); open(lst, 'w').write(''.join(f"file '{c}'\n" for c in chunks))
wav = os.path.join(CH, 'audio.wav'); audio.build(wav, S.DURATION, mod.MUSIC, mod.SFX, seed=sum(map(ord, name)) % 1000)
out = os.path.join(OUTD, f'{name.upper()}.mp4')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                '-shortest', out], check=True)
print('saved', out, os.path.getsize(out) // 1e6, 'MB')

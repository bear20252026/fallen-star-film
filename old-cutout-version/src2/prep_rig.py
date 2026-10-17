# crop every rig part / pose to its content box and write src2/rig.json (canvas coords at half size)
import json,glob,os
from PIL import Image
A='public/art2'; out={}
for c in range(1,8):
    rig=json.load(open(f'{A}/parts/C{c}/Rig.json')); cid=f'C{c}'
    P={}
    for p in rig['parts']:
        src=f"{A}/{p['png']}"; im=Image.open(src); bb=im.getbbox()
        x0,y0,x1,y1=max(0,bb[0]-4),max(0,bb[1]-4),min(im.width,bb[2]+4),min(im.height,bb[3]+4)
        d=f'{A}/rig/{cid}'; os.makedirs(d,exist_ok=True)
        im.crop((x0,y0,x1,y1)).save(f"{d}/{p['name']}.png")
        P[p['name']]=[x0,y0,x1-x0,y1-y0]
    out[cid]={'parts':P,'states':{s['state']:s['layers'] for s in rig['states']},'scale':rig.get('scale_in_story')}
poses={}
for f in sorted(glob.glob(f'{A}/poses/*/*.png')):
    im=Image.open(f); bb=im.getbbox(); x0,y0,x1,y1=max(0,bb[0]-4),max(0,bb[1]-4),min(im.width,bb[2]+4),min(im.height,bb[3]+4)
    n=os.path.basename(f)[:-4]; d=f'{A}/rig/poses'; os.makedirs(d,exist_ok=True)
    im.crop((x0,y0,x1,y1)).save(f'{d}/{n}.png'); poses[n]=[x0,y0,x1-x0,y1-y0]
out['poses']=poses
json.dump(out,open('src2/rig.json','w'),indent=1)
print('ok')

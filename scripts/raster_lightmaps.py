"""Rasterize Cycles corner samples into padded RGB lightmap atlases."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter
ROOT=Path(__file__).resolve().parents[1];src=ROOT/'blender/lighting';out=ROOT/'public/lighting';out.mkdir(exist_ok=True,parents=True)
geo=np.load(src/'atlas-geometry.npz');uv=geo['uv'];tris=geo['triangles']
for name in ['ao','dawn','noon','dusk','night']:
    size=2048 if name=='ao' else 1024
    colors=np.load(src/(name+'.npy'))[:,:3]
    rgb=np.zeros((size,size,3),np.float32);mask=np.zeros((size,size),bool)
    coords=uv*np.array([size-1,size-1],dtype=np.float32);coords[:,1]=size-1-coords[:,1]
    for ids in tris:
        p=coords[ids];c=colors[ids]
        lo=np.maximum(np.floor(p.min(0)).astype(int),0);hi=np.minimum(np.ceil(p.max(0)).astype(int),size-1)
        if (hi<lo).any():continue
        den=(p[1,1]-p[2,1])*(p[0,0]-p[2,0])+(p[2,0]-p[1,0])*(p[0,1]-p[2,1])
        if abs(den)<1e-8:continue
        yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        a=((p[1,1]-p[2,1])*(xx-p[2,0])+(p[2,0]-p[1,0])*(yy-p[2,1]))/den
        b=((p[2,1]-p[0,1])*(xx-p[2,0])+(p[0,0]-p[2,0])*(yy-p[2,1]))/den;d=1-a-b
        hit=(a>=-.001)&(b>=-.001)&(d>=-.001)
        patch=rgb[lo[1]:hi[1]+1,lo[0]:hi[0]+1];patch[hit]=(a[...,None]*c[0]+b[...,None]*c[1]+d[...,None]*c[2])[hit]
        mask[lo[1]:hi[1]+1,lo[0]:hi[0]+1]|=hit
    coverage=float(mask.mean())
    for _ in range(5):
        pm=np.pad(mask,1);pc=np.pad(rgb,((1,1),(1,1),(0,0)));total=np.zeros_like(rgb);count=np.zeros_like(mask,dtype=np.float32)
        for sy,sx in [(0,1),(2,1),(1,0),(1,2)]:
            m=pm[sy:sy+size,sx:sx+size];total+=pc[sy:sy+size,sx:sx+size]*m[:,:,None];count+=m
        fill=(~mask)&(count>0);rgb[fill]=total[fill]/count[fill,None];mask|=fill
    if name=='ao':
        rgb[~mask]=1;encoded=np.clip(rgb[:,:,0],0,1)
        img=Image.fromarray(np.rint(encoded*255).astype(np.uint8),'L')
    else:
        # Square-root encoding preserves subtle shadow values, with linear range [0,4].
        encoded=np.sqrt(np.clip(rgb/4,0,1));img=Image.fromarray(np.rint(encoded*255).astype(np.uint8),'RGB')
    img=img.filter(ImageFilter.GaussianBlur(.65 if name=='ao' else 1.0))
    img.save(out/(name+'.png'),optimize=True)
    print('ATLAS_OK',name,size,'coverage',round(coverage,3),flush=True)
meta=json.loads((src/'bake.json').read_text());meta.update({'encoding':'sqrt-linear-range-4','aoSize':2048,'lightmapSize':1024,'paddingPixels':5,'gpuBytesWithMipmaps':44739243})
(out/'manifest.json').write_text(json.dumps(meta,indent=2))

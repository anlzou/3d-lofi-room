"""Retain the generated lightmaps inside the authoritative Blender source."""
import bpy,json
from pathlib import Path
ROOT=Path(bpy.data.filepath).resolve().parents[1]
for name in ['ao','dawn','noon','dusk','night']:
    im=bpy.data.images.get('P3_'+name)
    if im is None:
        im=bpy.data.images.load(str(ROOT/'public/lighting'/(name+'.png')),check_existing=False);im.name='P3_'+name
    else:im.filepath=str(ROOT/'public/lighting'/(name+'.png'));im.reload()
    im.colorspace_settings.name='Non-Color';im.use_fake_user=True;im.pack()
bpy.context.scene['phase3_baked']=True
bpy.context.scene['lightmap_manifest']=json.loads((ROOT/'public/lighting/manifest.json').read_text())
print('PHASE3_PACK_OK',flush=True)

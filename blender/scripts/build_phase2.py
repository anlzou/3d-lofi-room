"""Rebuild Phase 2 from its preserved Phase 1.5 source and authored materials.
Separate background Blender only. Default verifies; --save-export publishes source/GLB.
"""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert bpy.app.background, 'Do not reset a live desktop session.'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/lofi_room-phase15-backup.blend'))
with bpy.data.libraries.load(str(ROOT/'blender/materials/phase2-materials.blend'),link=False) as (source,target):
    target.materials=[n for n in source.materials if n.startswith('MAT_P2_') and 'Backup' not in n]
for name in ['phase2_refine','phase2_finish','phase2_contacts','phase2_final_assets','phase2_budget','phase2_last_contacts','phase2_slippers','phase2_prints','phase2_polish','phase2_flower_stems','phase2_cabinet_clock','phase2_user_feedback','phase2_feedback_budget','phase2_feedback_contacts']:
    p=ROOT/'blender/scripts'/(name+'.py');exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{'__file__':str(p)})
dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in bpy.context.scene.objects:
    assert min(o.scale)>0,o.name
    if o.type=='MESH':
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);ev.to_mesh_clear()
assert tri<80000,tri
print('PHASE2_REBUILD_OK',tri)
if '--save-export' in sys.argv:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/lofi_room.blend'))
    p=ROOT/'scripts/export_glb.py';exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'))

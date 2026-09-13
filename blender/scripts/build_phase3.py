"""Reproducible Phase 3 UV / Cycles bake / atlas / export pipeline.
--bake requires --raster-python pointing to Python with numpy and Pillow.
--save-export is the explicit source/GLB publish switch.
"""
import bpy,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert bpy.app.background
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/lofi_room-phase2-approved.blend'))
names=['MAT_P2_Fur','MAT_P2_FurLight','MAT_P2_Oak','MAT_P2_Sage']
old={n:bpy.data.materials[n] for n in names}
for n,m in old.items():m.name=n+'.Phase2Retained'
with bpy.data.libraries.load(str(ROOT/'blender/materials/phase3-materials.blend'),link=False) as (a,b):b.materials=names
for n,m in old.items():m.user_remap(bpy.data.materials[n])
def run(name):
    p=ROOT/'blender/scripts'/(name+'.py');exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'),{'__file__':str(p)})
run('phase3_uv')
if '--bake' in sys.argv:
    assert '--raster-python' in sys.argv,'Pass a Python executable with numpy and Pillow.'
    prepared=ROOT/'blender/phase3-prepared-cache.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(prepared),compress=True)
    run('phase3_bake')
    subprocess.run([sys.argv[sys.argv.index('--raster-python')+1],str(ROOT/'scripts/raster_lightmaps.py')],check=True)
    # The baking worker is deliberately disposable; restore the clean UV source before publishing.
    bpy.ops.wm.open_mainfile(filepath=str(prepared))
    run('phase3_pack')
elif '--save-export' in sys.argv:
    run('phase3_pack')
if '--save-export' in sys.argv:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/lofi_room.blend'),compress=True)
    p=ROOT/'scripts/export_glb.py';exec(compile(p.read_text(encoding='utf-8'),str(p),'exec'))
print('PHASE3_UV_REBUILD_OK')

"""Rebuild geometry using the authored, packed material library. Background only.
Default: verify without saving. --save-export: save canonical source and export.
"""
import bpy, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
assert bpy.app.background, 'Use a separate background Blender process.'
save = '--save-export' in sys.argv
sys.argv = [a for a in sys.argv if a != '--save-export']
bpy.ops.wm.read_homefile(use_empty=True)
def run(name):
    path = ROOT / 'blender/scripts' / name
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'), {'__file__': str(path)})
run('build_scene.py')
with bpy.data.libraries.load(str(ROOT / 'blender/materials/phase15-materials.blend'), link=False) as (source, target):
    target.materials = ['MAT_Graybox_Dark', 'MAT_TestCard']
    target.worlds = ['World_Night']
run('densify_scene.py')
run('refine_layout.py')
deps = bpy.context.evaluated_depsgraph_get()
triangles = 0
for obj in bpy.context.scene.objects:
    assert min(obj.scale) > 0, obj.name
    if obj.type == 'MESH':
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        triangles += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
assert triangles == 55408, triangles
print('PHASE15_REBUILD_OK', triangles)
if save:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'blender/lofi_room.blend'))
    path = ROOT / 'scripts/export_glb.py'
    exec(compile(path.read_text(encoding='utf-8'), str(path), 'exec'))

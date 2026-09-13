"""Pack existing bakes and publish the saved room without touching a GUI session."""
import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
assert bpy.app.background
assert Path(bpy.data.filepath).resolve()==(ROOT/'blender/lofi_room.blend').resolve()
assert bpy.context.scene.get('phase3_uv')
exec((ROOT/'blender/scripts/phase3_pack.py').read_text(encoding='utf-8'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/lofi_room.blend'),compress=True)
exec((ROOT/'scripts/export_glb.py').read_text(encoding='utf-8'))
assert len([i for i in bpy.data.images if i.name.startswith('P3_') and i.packed_file])==5
print('PHASE3_SOURCE_PACKED',bpy.data.filepath,flush=True)

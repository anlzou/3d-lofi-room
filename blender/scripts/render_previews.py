"""Render each Phase 1 composition; invoke after build and viewport inspection."""
import bpy
from pathlib import Path
root = Path(bpy.data.filepath).resolve().parents[1]
scene = bpy.context.scene
original_camera = scene.camera
try:
    for key in ['Room', 'Desk', 'Window']:
        scene.camera = bpy.data.objects['Camera_' + key]
        scene.render.filepath = str(root / 'blender' / 'renders' / ('phase1-' + key.lower() + '-2026-09-05.png'))
        bpy.ops.render.render(write_still=True)
        print('RENDER_OK', scene.render.filepath)
finally:
    scene.camera = original_camera

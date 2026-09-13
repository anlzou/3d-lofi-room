# Blender -> GLB exporter for blender-web-demo
#
# Usage (both work identically):
#   1. Live session via Blender MCP:
#      execute_blender_code: exec(open(r'<project>\scripts\export_glb.py', encoding='utf-8').read())
#   2. Headless CLI:
#      blender -b <project>\blender\demo.blend -P <project>\scripts\export_glb.py
#
# The project root is resolved from the open .blend file (blender/demo.blend),
# so the script never depends on a hardcoded absolute path or cwd.

import bpy
import os

EXCLUDE_COLLECTIONS = {"LIGHTS", "CAMERAS"}  # never shipped to the web runtime


def project_root():
    blend = bpy.data.filepath
    if blend:
        # <root>/blender/demo.blend -> <root>
        return os.path.dirname(os.path.dirname(os.path.abspath(blend)))
    return os.getcwd()


ROOT = project_root()
OUT_DIR = os.path.join(ROOT, "public", "models")
OUT_PATH = os.path.join(OUT_DIR, "demo.glb")

os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene

# Preserve named Empty interaction pivots and effect sockets, excluding actual lights/cameras.
bpy.ops.object.select_all(action="DESELECT")
exported = []
for obj in scene.objects:
    if obj.type not in {"MESH", "EMPTY"}:
        continue
    if any(c.name in EXCLUDE_COLLECTIONS for c in obj.users_collection):
        continue
    obj.select_set(True)
    exported.append(obj.name)
if exported:
    bpy.context.view_layer.objects.active = bpy.data.objects[exported[0]]

# Filter kwargs so the script survives glTF-exporter option changes across
# Blender versions.
wanted = {
    "filepath": OUT_PATH,
    "export_format": "GLB",
    "use_selection": True,          # only the picked meshes
    "export_apply": True,           # bake modifiers (Bevel) into the mesh
    "export_yup": True,             # glTF is Y-up, matching three.js
    "export_cameras": False,
    "export_lights": False,
    "export_animations": False,     # static demo model
    "export_skins": False,
    "export_extras": True,
}
if scene.get('phase3_uv'):
    wanted.update({
        'export_draco_mesh_compression_enable': True,
        'export_draco_mesh_compression_level': 6,
        'export_draco_position_quantization': 15,
        'export_draco_normal_quantization': 12,
        'export_draco_texcoord_quantization': 14,
    })
schema = bpy.ops.export_scene.gltf.get_rna_type().properties.keys()
kwargs = {k: v for k, v in wanted.items() if k in schema}
skipped = sorted(set(wanted) - set(kwargs))

bpy.ops.export_scene.gltf(**kwargs)

size = os.path.getsize(OUT_PATH) if os.path.isfile(OUT_PATH) else 0
with open(OUT_PATH, "rb") as f:
    magic = f.read(4)

print("EXPORTED_OBJECTS:", exported)
print("SKIPPED_KWARGS:", skipped)
print("GLB_PATH:", OUT_PATH)
print("GLB_SIZE_BYTES:", size)
print("GLB_MAGIC_OK:", magic == b"glTF")
assert size > 10000, "GLB suspiciously small - export likely failed"
assert magic == b"glTF", "not a valid GLB container"
print("EXPORT_OK")

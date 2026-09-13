"""Two street lamps on top of the exterior utility pole; canonical Blender source only.

Run once on the current source, then export with scripts/export_glb.py:

    blender -b blender/lofi_room.blend -P blender/scripts/street_lamps.py

House rules honoured here:
* geometry and materials come from this script, never from the GLB;
* every mesh keeps the two UV layers the exporter and web batcher rely on
  ('UVMap' at index 0, 'LightmapUV' at index 1);
* the lightmap atlas is NOT re-baked. The new parts copy the LightmapUV of the
  pole top they sit on, which keeps the existing four-time Cycles bake valid and
  gives them the same indirect bounce as the pole. A later full re-bake can
  replace this with real atlas islands.
"""
import bpy, ast, math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
scene = bpy.context.scene
assert not scene.get('street_lamps'), 'street lamps already present in this source'
assert bpy.data.objects.get('Exterior_UtilityPole'), 'exterior utility pole required'

COL = {n: bpy.data.collections[n] for n in ['ROOM_SHELL', 'FURNITURE', 'PROPS', 'LIGHTS', 'CAMERAS']}
M = {m.name[7:]: m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay = M['Cream']; dark = M['Charcoal']; card = M['Paper']; zone = 'exterior'

# Reuse the audited primitives instead of re-declaring them.
for f in ['densify_scene.py', 'phase2_refine.py']:
    t = ast.parse((ROOT / 'blender/scripts' / f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n, ast.FunctionDef)], type_ignores=[]), 'helpers', 'exec'))


def world_bounds(o):
    bpy.context.view_layer.update()
    ps = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [(min(v[i] for v in ps), max(v[i] for v in ps)) for i in range(3)]


# Remove a partial previous run so the script stays rerunnable after a crash.
for o in list(scene.objects):
    if o.name.startswith(('StreetLamp_', 'Exterior_StreetLamp_', 'LIGHT_street_lamp')):
        remove(o)

pole = bpy.data.objects['Exterior_UtilityPole']
bb = world_bounds(pole)
cx = (bb[0][0] + bb[0][1]) / 2          # pole axis
cy = (bb[1][0] + bb[1][1]) / 2
top = bb[2][1]                          # pole top, +Z up in Blender
ARM_Z = top + .035                      # arms clear the crossarm below
REACH = .34                             # heads hang one on each side of the pole
LM_UV = (.4675, .30)                    # LightmapUV sampled from the pole top
segments = 10

# Collar so the arms read as mounted hardware rather than floating boxes.
box('Exterior_StreetLamp_Collar', (cx, cy, top + .012), (.075, .075, .048), mat=dark, coll='ROOM_SHELL', bevel=0)

# The crossarm runs along X, so the lamp arms run along Y (F = window side) to keep the
# two heads clear of it instead of stacking another bar on top of the pole hardware.
for side, sign in (('F', -1), ('B', 1)):
    hy = cy + sign * REACH
    box(f'Exterior_StreetLamp_Arm_{side}', (cx, (cy + hy) / 2, ARM_Z), (.024, REACH, .024), mat=dark, coll='ROOM_SHELL', bevel=0)
    # Tapered head: wide rim at the bottom, narrow at the arm, open below for the lens.
    lathe(f'Exterior_StreetLamp_Head_{side}', (cx, hy, ARM_Z - .012),
          [(.006, .075), (.042, .058), (.076, .014), (.080, 0)], 'Charcoal', segments)
    lathe(f'Exterior_StreetLamp_Lens_{side}', (cx, hy, ARM_Z - .016),
          [(0, .006), (.062, .006), (.062, -.006), (0, -.006)], 'GlowWarm', segments)
    anchor = empty(f'LIGHT_street_lamp_{side}', (cx, hy, ARM_Z - .03), coll='PROPS')
    anchor['zone'] = 'lights'
    anchor['role'] = 'light'

# Keep the export/atlas contract: two UV layers on every new mesh, the second one
# pointing at the pole-top lightmap texels.
new_meshes = [o for o in scene.objects if o.name.startswith('Exterior_StreetLamp_')]
for o in new_meshes:
    o['zone'] = 'exterior'; o['phase'] = 2; o['lightmapUV'] = 1
    # Lathe parts are born in PROPS; the rest of the exterior lives in ROOM_SHELL.
    for c in list(o.users_collection):
        c.objects.unlink(o)
    COL['ROOM_SHELL'].objects.link(o)
    me = o.data
    if not me.uv_layers:
        me.uv_layers.new(name='UVMap')
    if len(me.uv_layers) < 2:
        me.uv_layers.new(name='LightmapUV')
    else:
        me.uv_layers[1].name = 'LightmapUV'
    for d in me.uv_layers[1].data:
        d.uv = LM_UV

# Budget guard: AGENTS.md keeps the room under 80k triangles after modifiers.
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
total = 0
for o in scene.objects:
    if o.type == 'MESH':
        e = o.evaluated_get(dg); m = e.to_mesh(); m.calc_loop_triangles()
        total += len(m.loop_triangles); e.to_mesh_clear()

scene['street_lamps'] = True
print('STREET_LAMPS', [o.name for o in new_meshes])
print('STREET_LAMP_ANCHORS', ['LIGHT_street_lamp_F', 'LIGHT_street_lamp_B'])
print('TOTAL_TRIANGLES', total)
assert total < 80000, f'triangle budget exceeded: {total}'
print('STREET_LAMPS_OK')

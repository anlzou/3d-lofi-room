"""Close-up findings: separate occupied desk footprints and sill bird/plant."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.get('phase2_finished') and not scene.get('phase2_contacts')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
for f in ['densify_scene.py','phase2_refine.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
move(['Windowsill_Figurine','Windowsill_FigurineHead'],(-.44,0,0))
for o in scene.objects:
    if o.name.startswith(('Floppy_Box','Floppy_Disk')):
        w=o.matrix_world.copy();w.translation+=Vector((.45,.07,-.09));o.matrix_world=w
    if o.name.startswith(('Modem_','EMIT_led_modem')):
        w=o.matrix_world.copy();w.translation+=Vector((.11,.09,0));o.matrix_world=w
    if o.name.startswith(('Mug_','SOCKET_steam_mug')):
        w=o.matrix_world.copy();w.translation+=Vector((-.27,-.33,0));o.matrix_world=w
    if o.name.startswith('Headphones_'):
        w=o.matrix_world.copy();w.translation+=Vector((.02,-.06,0));o.matrix_world=w
    if o.name.startswith('Walkman_'):
        w=o.matrix_world.copy();w.translation+=Vector((.05,.04,0));o.matrix_world=w
    if '_Midrib_' in o.name:
        for m in o.modifiers:
            if m.type=='DECIMATE':m.ratio=.12
move(['SEASON_summer_iceddrink'],(.13,.02,0))
move(['INT_calendar'],(.03,.17,0))
for i in range(4):bpy.data.objects['Sticky_Desk_%02d'%i].location=(-.41+i*.012,1.06+i*.008,.779+i*.003)
remove(bpy.data.objects['Cable_Headphone'])
cable('Cable_Headphone',[(-.08,.70,.745),(-.03,.73,.728),(-.015,.84,.728),(-.12,.89,.743)],.0023,M['Charcoal'])
# Smooth small-scale mouse and ceramic lamp shade, keeping their original names.
replace(bpy.data.objects['Mouse_Main'],uvball('MouseNew',(-.63,.76,.745),(.047,.068,.025),'Teal',24,12))
replace(bpy.data.objects['Lamp_Shade'],lathe('LampShadeNew',(-1.45,1.19,1.19),[(.104,0),(.047,.138),(.038,.138),(.094,.002),(.104,0)],'Teal',32))
# Spring blossoms receive petal silhouettes instead of polygonal balls.
for o in list(scene.objects):
    if o.name.startswith('Spring_Blossom'):
        p=o.matrix_world.translation.copy();replace(o,uvball('BlossomNew',p,(.026,.024,.025),'Rose',16,8))
        for i in range(5):
            a=i*math.tau/5;petal=uvball('Spring_Petal',(p.x+.028*math.cos(a),p.y+.028*math.sin(a),p.z),(.027,.023,.012),'Paper',12,6);parent(petal,bpy.data.objects['SEASON_spring_flowerpot'])
# Weighted normals retain flat hard-surface faces and soften bevel highlights.
for o in scene.objects:
    if o.type=='MESH' and any(m.type=='BEVEL' for m in o.modifiers):
        for f in o.data.polygons:f.use_smooth=True
        w=o.modifiers.new('CornerNormals','WEIGHTED_NORMAL');w.keep_sharp=True;w.weight=50
scene['phase2_contacts']=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);e.to_mesh_clear()
print('CONTACT_PASS',tri)  # Final gate is in phase2_budget.py and the GLB verifier.

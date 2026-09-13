"""One final visual pass: readable drawer contents, clean trim and embedded CRT controls."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
zone='phase2';clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard']
for f in ['densify_scene.py','phase2_refine.py']:
    t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
assert not scene.get('phase2_feedback_contacts')
box('Drawer_PhotoStorage',(.42,1.115,.414),(.272,.255,.070),mat=M['Walnut'],bevel=.004)
for o in list(scene.objects):
    if o.name.startswith(('Drawer_Tape','Drawer_Photo')) and o.name!='Drawer_PhotoStorage':
        w=o.matrix_world.copy();w.translation+=Vector((0,.075,.071));o.matrix_world=w
    if o.name.startswith('Cat_CheekTuft'):remove(o)
for name in ['Fumo_A_Hem','Fumo_B_Hem']:
    remove(bpy.data.objects[name])
w=bpy.data.objects['EMIT_screen_crt'].matrix_world.copy()
for o in scene.objects:
    if o.name.startswith(('Crt_ControlPanel','Crt_TuningKnob','Crt_SpeakerSlot','Crt_KnobMarker')):
        if o.name=='Crt_ControlPanel':
            for v in o.data.vertices:v.co.x*=.055/.073
        m=o.matrix_world.copy();m.translation+=w.to_3x3()@Vector((.025,0,0));o.matrix_world=m
    if o.name.startswith('Crt_Antenna'):
        o.visible_shadow=False;o['noShadow']=True
scene['phase2_feedback_contacts']=True

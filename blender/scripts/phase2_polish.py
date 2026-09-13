"""Persist final screen assignments, geographic globe art and prop placement."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name};zone='phase2';clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard']
for f in ['densify_scene.py','phase2_refine.py','phase2_final_assets.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
for o in scene.objects:
    if o.name.startswith(('Floppy_Box','Floppy_Disk')):
        w=o.matrix_world.copy();w.translation+=Vector((.10,0,0));o.matrix_world=w
    if o.name.startswith('PhotoFrame_'):
        w=o.matrix_world.copy();w.translation+=Vector((.58,.06,-.115));o.matrix_world=w
for name,key in [('EMIT_screen_mac','ScreenMac'),('EMIT_screen_crt','ScreenCRT')]:mat(bpy.data.objects[name],key)
o=bpy.data.objects['Globe_Sphere'];o.data.materials.append(M['Sage']);o.data.materials.append(M['Paper'])
for f in o.data.polygons:
    c=sum((o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);c.normalize();lon=math.atan2(c.y,c.x);lat=math.asin(c.z)
    if ((lon+.9)/.65)**2+((lat-.25)/.7)**2<1 or ((lon-1.5)/.7)**2+((lat-.4)/.45)**2<1 or ((lon-2)/.35)**2+((lat+.5)/.3)**2<1 or ((lon+2.1)/.55)**2+((lat-.3)/.7)**2<1:f.material_index=1
    if lat< -1.12:f.material_index=2
circle('Globe_Meridian',(1.86,.04,2.55),.167,.006,'Brass')

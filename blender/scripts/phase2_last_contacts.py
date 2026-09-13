"""Final close-view corrections and geometry manifest."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.get('phase2_budget') and not scene.get('phase2_last_contacts')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
for f in ['densify_scene.py','phase2_refine.py','phase2_final_assets.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
for o in scene.objects:
    if o.type=='MESH' and '_Leaf_' in o.name:
        for m in list(o.modifiers):
            if m.name=='SilhouetteBudget':o.modifiers.remove(m)
# All three machines fit inside the existing cabinet, stacked on its bottom panel.
R=Matrix.Rotation(math.radians(35),4,'Z');anchor=Vector((-1.72,-.79,0))
def at(x,y,z):return anchor+R.to_3x3()@Vector((x,y,z))
ps=bpy.data.objects['GameConsole_Body'];ps.matrix_world=Matrix.Translation(at(0,-.04,.106))@R
replace(bpy.data.objects['Vhs_Body'],box('VCRNew',at(0,-.02,.175),(.46,.28,.078),math.radians(35),M['Charcoal'],bevel=.01))
replace(bpy.data.objects['ANIM_vcr_door'],box('VCRDoorNew',at(-.03,-.163,.178),(.23,.005,.022),math.radians(35),M['Walnut'],bevel=.003))
replace(bpy.data.objects['Dvd_Body'],box('DVDNew',at(0,-.02,.243),(.46,.28,.056),math.radians(35),M['Cream'],bevel=.009))
replace(bpy.data.objects['ANIM_dvd_tray'],box('DVDTrayNew',at(-.04,-.163,.245),(.22,.008,.013),math.radians(35),M['Charcoal'],bevel=.002))
for z in [.174,.243]:
    for x in [.15,.18]:uvball('Media_Button',at(x,-.166,z),(.007,.005,.007),'Brass',12,6)
for n in ['Cable_GameController','PS1_TvCable']:
    if n in bpy.data.objects:remove(bpy.data.objects[n])
tube('Cable_GameController',[at(-.07,-.14,.105),at(-.06,-.23,.07),(-1.42,-1.17,.04),(-1.16,-1.15,.043),(-1.13,-1.23,.09)],.004)
tube('PS1_TvCable',[at(0,.055,.106),at(.25,.10,.16),at(.25,.13,.39),at(.14,.17,.66)],.004)
# Decorative glove-like ridge removed; tail cap remains part of the cat.
for o in scene.objects:
    if o.name.startswith('CatBed_Stitch'):
        b=bounds(o)
        print('CATBED_STITCH_BOUNDS',b)
# Make land masses visible from the locked camera side of the globe.
o=bpy.data.objects['Globe_Sphere']
for f in o.data.polygons:
    c=sum((o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices);c.normalize();lon=math.atan2(c.y,c.x);lat=math.asin(c.z)
    if ((lon+2.1)/.55)**2+((lat-.3)/.7)**2<1:f.material_index=1
# Two doll bases fully touch the shelf, not its bevel.
for o in scene.objects:
    if o.name.startswith('Fumo_'):
        w=o.matrix_world.copy();w.translation.z-=.006;o.matrix_world=w
scene['phase2_last_contacts']=True

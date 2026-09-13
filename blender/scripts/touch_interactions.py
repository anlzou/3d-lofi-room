import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert not scene.get('touch_interactions')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']};M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=M['Paper'];zone='interaction'
for f in ['densify_scene.py','phase2_refine.py']:
 t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
drawer=[o for o in scene.objects if o.name.startswith('Drawer_') or o.name in ['Nightstand_Drawer','Nightstand_DrawerBottom','Nightstand_DrawerSide','Nightstand_DrawerSide.001','Nightstand_DrawerBack']]
group('ANIM_drawer_upper',(.42,.91,.38),drawer)
phone=bpy.data.objects['INT_phone'];group('ANIM_phone',(-1.63,.83,.72),[phone]+[o for o in scene.objects if o.name.startswith('Phone_')])
group('INT_bedside_lamp',(.29,1.48,.64),[o for o in scene.objects if o.name.startswith('Nightlight_')])
for key in ['A','B']:group('INT_mecha_'+key,(-1.23 if key=='A' else -.57,1.54,1.0),[o for o in scene.objects if o.name.startswith('Mecha_'+key)])
group('ANIM_globe',(1.86,.04,2.55),[o for o in scene.objects if o.name=='Globe_Sphere' or o.name.startswith('Globe_Parallel')])
# Replace the solid bucket and inaccurate ribs with a hollow rolled-rim vessel.
old=bpy.data.objects['Wastebasket_Main']
for o in list(scene.objects):
 if o.name.startswith('Bin_Rib'):remove(o)
replace(old,lathe('Bin_New',(-1.86,.38,.035),[(0,0),(.085,0),(.118,.235),(.123,.24),(.121,.25),(.110,.25),(.108,.235),(.077,.013),(0,.013)],'Cream',20))
random.seed(77)
for i in range(3):
 o=bpy.data.objects['Paper_Crumpled_%02d'%i];p=(-1.64,.18,.071) if i==0 else (-1.83,.10,.068) if i==1 else (-1.86,.38,.235)
 n=ball('Paper_New',p,(.036,.032,.034),M['Paper'],sub=2)
 for v in n.data.vertices:v.co*=random.uniform(.76,1.12)
 replace(o,n)
 # Rest outside paper at floor height using actual geometry bounds.
 if i<2:o.location.z+=.034-bounds(o)[2][0]
binroot=group('ANIM_bin',(-1.86,.38,.035),[old]);paper=bpy.data.objects['Paper_Crumpled_02'];group('ANIM_bin_paper',(-1.86,.38,.22),[paper])
# Preserve the approved white pillow; shape the green cushion underside to its top.
old=bpy.data.objects['Bed_Cushion'];n=uvball('Green_Pillow_New',(1.52,1.12,.80),(.235,.15,.052),'Sage',20,10)
for v in n.data.vertices:
 x,y,z=v.co;white=.72+.072*math.sqrt(max(0,1-((x-1.31)/.405)**2-((y-1.16)/.21)**2));v.co.z=white+.004+(z-.748)*.8
replace(old,n)
# Keep additions within the realtime budget by simplifying distant exterior bevels.
def count():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();total=0
 for o in scene.objects:
  if o.type=='MESH':e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();total+=len(m.loop_triangles);e.to_mesh_clear()
 return total
if count()>=80000:
 for o in scene.objects:
  if o.type=='MESH' and o.name.startswith('Exterior_'):mod=o.modifiers.new('DistantDetailBudget','DECIMATE');mod.ratio=.65
assert count()<80000,count()
scene['touch_interactions']=True;print('TOUCH_ASSETS_OK',count())

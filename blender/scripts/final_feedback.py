"""Final feedback geometry; canonical Blender source only."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert not scene.get('final_feedback')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']};M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=M['Paper'];zone='final-feedback'
for f in ['densify_scene.py','phase2_refine.py']:
 t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
# Real contact against the untouched white pillow, not an approximate ellipsoid.
green=bpy.data.objects['Bed_Cushion'];white=bpy.data.objects['Bed_Pillow']
bvh=BVHTree.FromPolygons([white.matrix_world@v.co for v in white.data.vertices],[list(p.vertices) for p in white.data.polygons])
for j in range(11):
 for i in range(20):
  t=math.pi*j/10;a=math.tau*i/20;x=1.49+.18*math.sin(t)*math.cos(a);y=1.13+.12*math.sin(t)*math.sin(a)
  hit=bvh.ray_cast(Vector((x,y,1.5)),Vector((0,0,-1)))[0];assert hit is not None
  green.data.vertices[j*20+i].co=green.matrix_world.inverted()@Vector((x,y,hit.z+.002+.045*(1+math.cos(t))))
chime=bpy.data.objects['ANIM_windchime'];chime.location+=Vector((.30,-.10,0))
cylinder('Windchime_WallHook',(.20,1.63,2.4),(.20,1.45,2.4),.006,M['Brass'])
random.seed(451)
for i,(x,y,z,key) in enumerate([(-1.90,.40,.252,'Paper'),(-1.81,.39,.263,'Paper'),(-1.85,.33,.265,'Rose')]):
 o=ball('Bin_Content_%02d'%i,(x,y,z),(.027,.024,.033),M[key],sub=1)
 for v in o.data.vertices:v.co*=random.uniform(.7,1.15)
 parent(o,bpy.data.objects['ANIM_bin_paper'])
o=box('Bin_FoldedReceipt',(-1.90,.35,.249),(.045,.035,.004),rot=.5,mat=M['Paper'],bevel=0);o.rotation_euler.x=.4;parent(o,bpy.data.objects['ANIM_bin_paper'])
for name,p,r,h,key in [('Nightstand_Water',(-.01,1.20,.73),.037,.12,'Cream'),('SEASON_summer_iceddrink',(-.12,1.12,.73),.033,.14,'Glass')]:
 replace(bpy.data.objects[name],lathe('Cup_New',p,[(0,0),(r*.8,0),(r,h),(r-.004,h),(r-.004,.009),(0,.009)],key,12))
 if key=='Glass':
  cylinder('IcedDrink_Tea',(p[0],p[1],.741),(p[0],p[1],.824),r-.006,M['Terracotta'])
  cylinder('IcedDrink_Straw',(p[0]+.012,p[1],.81),(p[0]+.02,p[1],.903),.003,M['Cream'])
 else:
  cylinder('Water_Surface',(p[0],p[1],.811),(p[0],p[1],.813),r-.007,M['Blue'])
# Printed paper face, binder and modem vents make their functions readable.
box('Calendar_Paper',(-.02,1.000,.80),(.106,.003,.096),mat=M['Paper'],bevel=0)
box('Calendar_Header',(-.02,.997,.827),(.098,.002,.017),mat=M['Rose'],bevel=0)
for row in range(3):
 for col in range(5):box('Calendar_Day',(-.058+col*.019,.997,.802-row*.014),(.007,.002,.006),mat=M['Walnut'],bevel=0)
for i in range(4):box('Modem_Vent',(-.12+i*.04,1.32,.789),(.022,.07,.002),mat=M['Charcoal'],bevel=0)
box('Modem_RearJack',(.035,1.402,.757),(.025,.008,.016),mat=M['Charcoal'],bevel=0)
# Five cables terminate inside both the device casing and the plug strain relief.
def cord(name,points):
 pts=[Vector(p) for p in points];samples=[]
 for k in range(len(pts)-1):
  p0=pts[max(0,k-1)];p1=pts[k];p2=pts[k+1];p3=pts[min(len(pts)-1,k+2)]
  for n in range(5):
   t=n/5;samples.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
 samples.append(pts[-1]);vs=[];fs=[]
 for i,p in enumerate(samples):
  tangent=(samples[min(i+1,len(samples)-1)]-samples[max(i-1,0)]).normalized();u=tangent.cross(Vector((1,0,0))).normalized();v=tangent.cross(u)
  for j in range(6):vs.append(p+.006*(u*math.cos(j*math.tau/6)+v*math.sin(j*math.tau/6)))
 for i in range(len(samples)-1):
  for j in range(6):a=i*6+j;b=i*6+(j+1)%6;fs.append((a,b,b+6,a+6))
 return meshobj(name,vs,fs,'Charcoal',True)
anchors=[(-1.62,1.28,.732),(-1.38,1.38,.80),(-1.01,1.266,.81),(-.65,1.38,.80),(.035,1.401,.757)]
for i,p in enumerate(anchors):
 px=-.9+i*.1
 o=cord('NewCord',[p,(p[0],1.47,max(.76,p[2])),(p[0]+.02,1.54,.49),(px,1.53,.25),(px,1.45,.13)])
 replace(bpy.data.objects['Cable_Device_%02d'%i],o)
 cylinder('PowerStrip_StrainRelief_%02d'%i,(px,1.45,.128),(px,1.45,.157),.012,M['Charcoal'])
for o in list(scene.objects):
 if o.name.startswith('FlipClock_Print'):remove(o)
o=bpy.data.objects['EMIT_screen_flip'];w=o.matrix_world.copy();w.translation.y-=.010;o.matrix_world=w
# Reclaim triangles from distant silhouettes, never the foreground subjects.
def count():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();total=0
 for o in scene.objects:
  if o.type=='MESH':e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();total+=len(m.loop_triangles);e.to_mesh_clear()
 return total
if count()>=80000:
 for o in scene.objects:
  if o.type=='MESH' and o.name.startswith('Exterior_'):
   mod=o.modifiers.new('DistantBudget','DECIMATE');mod.ratio=.45
for o in scene.objects:
 if o.type=='MESH' and o.name.startswith(('LowBookshelf','Book','Nightstand','TvStand','Desk_','Exterior_','Floor_','Wall_')):
  mod=o.modifiers.new('MergeCoplanar','DECIMATE');mod.decimate_type='DISSOLVE';mod.angle_limit=.001
for name in ['Nightstand_Main','TvStand_Main','Bed_Frame','Cat_Bed','SEASON_autumn_blanket','Cactus_Body']:
 o=bpy.data.objects.get(name)
 if o:mod=o.modifiers.new('HiddenDetailBudget','DECIMATE');mod.ratio=.6
print('FINAL_GEOMETRY',count());assert count()<80000
scene['final_feedback']=True

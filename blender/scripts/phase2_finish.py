"""Second visual inspection pass: efficient fine tubes and finished paper/device details."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.get('phase2_refined') and not scene.get('phase2_finished')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
for f in ['densify_scene.py','phase2_refine.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
for o in list(scene.objects):
    if o.type!='MESH':continue
    ratio=None
    if o.name.startswith(('Speaker_Rim','Mug_Handle','Fan_Cage','CatBed_Stitch')):ratio=.16
    if '_Midrib_' in o.name:ratio=.20
    if o.name=='Cable_Phone_Coil':ratio=.25
    if ratio:
        m=o.modifiers.new('FineTubeBudget','DECIMATE');m.ratio=ratio
# Open wastebasket with rolled rim and visible paper, replacing closed placeholder.
replace(bpy.data.objects['Wastebasket_Main'],lathe('BinNew',(-1.86,.38,.028),[(0,0),(.095,0),(.135,.255),(.135,.27),(.123,.27),(.085,.013),(0,.013)],'Cream',24))
for i in range(10):
    a=i*math.tau/10
    cable('Bin_Rib',[(-1.86+.096*math.cos(a),.38+.096*math.sin(a),.05),(-1.86+.134*math.cos(a),.38+.134*math.sin(a),.28)],.002,M['Walnut'])
# Hero CRT details follow its face basis, without moving the screen.
sc=bpy.data.objects['EMIT_screen_crt'];bpy.context.view_layer.update();w=sc.matrix_world.copy();root=bpy.data.objects['INT_tv_crt']
for i in range(5):
    o=box('Crt_SpeakerSlot',(0,0,0),(.045,.003,.004),mat=M['Charcoal'],bevel=.001)
    o.matrix_world=w@Matrix.Translation(Vector((.207,-.012,-.075+i*.014)));parent(o,root)
for z in [.065,.022]:
    o=uvball('Crt_TuningKnob',(0,0,0),(.020,.009,.020),'Walnut',16,8)
    o.matrix_world=w@Matrix.Translation(Vector((.205,-.012,z)));parent(o,root)
o=label('Crt_Label','STEREO',(0,0,0),.015,'Walnut',(math.pi/2,0,0));o.matrix_world=w@Matrix.Translation(Vector((-.16,-.014,-.155)))@Matrix.Rotation(math.pi/2,4,'X');parent(o,root)
# Printed record-style poster art in place of extruded polygon blobs.
for i in range(3):
    p=bpy.data.objects['Poster_%02d'%i].location
    old=bpy.data.objects['Poster_Moon_%02d'%i]
    replace(old,cylinder('PosterDisc',(1.998,p.y,p.z+.08),(1.994,p.y,p.z+.08),.092,M['Paper']))
    for j in range(4):
        box('Poster_PrintRule',(1.988,p.y,p.z-.11-j*.018),(.002,.25-j*.032,.003),mat=M['Paper'],bevel=0)
    # One small landscape silhouette, intentionally simple graphic design.
    meshobj('Poster_Landscape',[(1.989,p.y-.14,p.z-.035),(1.989,p.y-.04,p.z+.045),(1.989,p.y+.04,p.z-.008),(1.989,p.y+.14,p.z+.055),(1.989,p.y+.14,p.z-.065),(1.989,p.y-.14,p.z-.065)],[(0,1,2,3,4,5)],['Terracotta','Blue','Sage'][i])
for i in range(6):
    o=bpy.data.objects['Corkboard_Photo_%02d'%i];p=o.location
    box('Photo_Print',(p.x-.005,p.y,p.z+.015),(.002,.108,.103),mat=M[['Blue','Sage','Terracotta'][i%3]],bevel=0)
    label('Photo_Date','99 / 09',(p.x-.008,p.y-.050,p.z-.064),.012,'Walnut',(math.pi/2,0,-math.pi/2))
# Globe parallels give the sphere an immediately readable identity.
g=bpy.data.objects['Globe_Sphere'];p=g.location
for z,r in [(-.07,.133),(0,.15),(.07,.133)]:
    o=ring('Globe_Parallel',(p.x,p.y,p.z+z),r,.002,'Paper');m=o.modifiers.new('FineTubeBudget','DECIMATE');m.ratio=.12
cylinder('Globe_Axis',(p.x,p.y,p.z-.18),(p.x,p.y,p.z+.18),.006,M['Brass'])
for o in scene.objects:
    if o.name.startswith('Corkboard_Pin'):mat(o,'Terracotta')
    if o.name.startswith(('ANIM_clock_','WallClock_Face')):mat(o,'Charcoal' if o.name.startswith('ANIM') else 'Paper')
# Clock markings on the actual right-wall dial plane.
for i in range(12):
    a=i*math.tau/12
    box('WallClock_Tick',(1.968,-1.47+.117*math.sin(a),2+.117*math.cos(a)),(.003,.009,.009),mat=M['Walnut'],bevel=0)
# Clear face on the curled cat: lower the head slightly and enlarge the ears subtly.
for o in scene.objects:
    if o.name.startswith('Cat_InnerEar'):mat(o,'Rose')
for o in scene.objects:
    if o.name.startswith('Noodles_'):
        w=o.matrix_world.copy();w.translation+=Vector((-.44,.13,0));o.matrix_world=w
scene['phase2_finished']=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);e.to_mesh_clear()
print('PHASE2_FINISH',len(scene.objects),tri)
assert tri<80000,tri

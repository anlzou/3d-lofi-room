import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert not scene.get('desk_life_update')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=M['Paper'];zone='desk'
for f in ['densify_scene.py','phase2_refine.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
remove(bpy.data.objects['UnderBed_Storage_00'])
# Open ceramic pencil holder, colored barrels and exposed graphite tips.
for o in list(scene.objects):
    if o.name.startswith(('Pencil_','Pencil_Cup')):remove(o)
p=(-1.79,1.35,.722)
lathe('Pencil_Cup',p,[(0,0),(.041,0),(.043,.12),(.045,.124),(.035,.124),(.033,.016),(0,.016)],'Teal',16)
for i,(dx,dy,h) in enumerate([(-.015,0,.19),(.011,.013,.175),(.013,-.012,.16),(-.009,-.014,.18)]):
    a=Vector((p[0]+dx,p[1]+dy,.745));b=Vector((a.x+dx*.6,a.y+dy*.5,.745+h))
    cylinder('Pencil_Barrel_%d'%i,a,b,.0038,M[['Rose','Brass','Blue','Walnut'][i]])
    tip=b+(b-a).normalized()*.012;cylinder('Pencil_WoodTip_%d'%i,b,tip,.0038,M['Cream'],top=.0006)
    cylinder('Pencil_Graphite_%d'%i,tip,tip+(b-a).normalized()*.004,.0009,M['Charcoal'],top=0)
# Compact film camera, separate lens rings, finder, shutter and a soft strap.
box('Camera_Body',(-.545,1.08,.767),(.15,.078,.09),mat=M['Charcoal'],bevel=.007)
box('Camera_Top',(-.545,1.08,.811),(.146,.072,.015),mat=M['Cream'],bevel=.003)
box('Camera_Grip',(-.602,1.035,.766),(.027,.015,.066),mat=M['Walnut'],bevel=.005)
cylinder('Camera_LensBarrel',(-.528,1.04,.767),(-.528,1.012,.767),.03,M['Charcoal'])
cylinder('Camera_LensRim',(-.528,1.015,.767),(-.528,1.006,.767),.027,M['Brass'])
cylinder('Camera_LensGlass',(-.528,1.005,.767),(-.528,1.003,.767),.022,M['Teal'])
box('Camera_Viewfinder',(-.514,1.037,.806),(.025,.009,.014),mat=M['Blue'],bevel=.002)
cylinder('Camera_Shutter',(-.594,1.07,.819),(-.594,1.07,.827),.009,M['Brass'])
cable('Camera_Strap',[(-.62,1.08,.78),(-.65,1.00,.737),(-.60,.958,.725),(-.53,.974,.725),(-.47,1.03,.745),(-.47,1.08,.78)],.003,M['Walnut'])
for i,(x,y,a) in enumerate([(-.29,.958,-.18),(-.235,.965,.21)]):
    box('Polaroid_Camera_%d'%i,(x,y,.724+i*.004),(.064,.083,.002),a,M['Paper'],bevel=0)
    box('Polaroid_Image_%d'%i,(x,y+.008,.7255+i*.004),(.050,.054,.001),a,M['Terracotta' if i==0 else 'Sage'],bevel=0)
# Small curled notes: Mac side, shelf edge, wall beside the desk.
for i,(x,y,z) in enumerate([(-1.13,1.012,.83),(-.70,1.602,1.44),(1.895,.72,1.48)]):
    w=.044;h=.052
    verts=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y+.001,z+h/2),(x-w/2,y+.001,z+h/2),(x+w/2,y-.006,z-h/2+.009)]
    if i==2:verts=[(x-(b-y),y+(a-x),c) for a,b,c in verts]
    meshobj('Sticky_LivedIn_%d'%i,verts,[(0,1,4,2,3)],'Paper')
# Group speakers around grounded pivots so runtime motion does not separate parts.
for i,x in enumerate([-1.38,-.65]):
    objs=[]
    for o in list(scene.objects):
        if o.type=='MESH' and o.name.startswith('Speaker_'):
            b=bounds(o)
            if abs((b[0][0]+b[0][1])/2-x)<.08:objs.append(o)
    group('ANIM_speaker_%d'%i,(x,1.32,.72),objs)
for name,p in [('SOCKET_steam_coffee',(-.43,.88,.813)),('SOCKET_steam_kettle',(.61,.38,.657))]:
    if name not in bpy.data.objects:empty(name,p)
# Keep new hard-surface bevels modest and measure the actual export topology.
for o in scene.objects:
    if o.name.startswith('Camera_'):
        for mod in o.modifiers:
            if mod.type=='BEVEL':mod.segments=1
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();count=0
for o in scene.objects:
    if o.type=='MESH':m=o.evaluated_get(dg).to_mesh();m.calc_loop_triangles();count+=len(m.loop_triangles);o.evaluated_get(dg).to_mesh_clear()
assert count<80000,count
scene['desk_life_update']=True
print('DESK_LIFE_OK',count)

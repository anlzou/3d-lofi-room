import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert not scene.get('gentle_motion_assets')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_P2_ScreenMac'];zone='motion'
for f in ['densify_scene.py','phase2_refine.py']:
    t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for prefix,p,name in [('Plant_Windowsill',(-1.58,1.58,1.08),'ANIM_plant_window'),('Spring_',(-.32,1.60,1.07),'ANIM_plant_flowers')]:
    objects=[o for o in scene.objects if o.type=='MESH' and o.name.startswith(prefix) and not any(k in o.name for k in ['Pot','Soil'])]
    group(name,p,objects)
group('ANIM_windchime',(-.10,1.55,2.40),[o for o in scene.objects if o.name.startswith('Windchime_')])
for i,o in enumerate([o for o in scene.objects if o.name.startswith('LavaLamp_Wax')]):o.name='ANIM_lava_wax_%d'%i
# Shift the complete heater and its kettle 8 cm toward the desk, maintaining contacts.
heater=bpy.data.objects['SEASON_winter_heater'];heater.location.x-=.08
socket=bpy.data.objects['SOCKET_steam_kettle'];socket.location.x-=.08
for name in ['SOCKET_kettle_steam','SOCKET_cat_heater']:
    o=bpy.data.objects.get(name)
    if o and o.parent!=heater:o.location.x-=.08
# Small bench oscilloscope at the clear right-hand edge of the desktop.
box('Scope_Body',(-.025,.855,.761),(.12,.085,.078),mat=M['Cream'],bevel=.004)
box('Scope_Bezel',(-.043,.810,.764),(.071,.006,.052),mat=M['Charcoal'],bevel=.002)
sc=surface('EMIT_screen_scope',(-.043,.806,.764),.059,.040,card)
for z in [.746,.774]:cylinder('Scope_Knob',(.021,.810,z),(.021,.799,z),.007,M['Walnut'])
# Restrained printed numbers and bindings on the upper row of books.
for i in [0,2,4,6]:
    o=bpy.data.objects['LowBookshelf_Book_01_%02d'%i];b=bounds(o);x=b[0][0]-.001;y=(b[1][0]+b[1][1])/2;z=(b[2][0]+b[2][1])/2
    lab=label('Book_Print_%d'%i,str(i+1),(x,y-.011,z+.025),.025,'Walnut',(math.pi/2,0,-math.pi/2))
    for h in [z-.07,z+.075]:box('Book_Binding_%d'%i,(x,y,h),(.001,max(.015,b[1][1]-b[1][0]-.008),.004),mat=M['Brass'],bevel=0)
scene['gentle_motion_assets']=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();tri+=len(m.loop_triangles);e.to_mesh_clear()
assert tri<80000,tri
print('MOTION_ASSETS_OK',tri)

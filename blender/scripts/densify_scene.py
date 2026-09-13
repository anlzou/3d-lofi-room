"""Phase 1.5 additive layout pass on Phase 1; never resets/deletes the scene.
Run once after build_scene.py, or on the existing Phase 1 .blend.
Materials were authored with validated MCP patches and packed in materials/phase15-materials.blend.
"""
import bpy, math, random, json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert not scene.get('phase15_layout'), 'Phase 1.5 is already applied; use the saved source for iteration.'
assert bpy.data.objects.get('Desk_Main'), 'Phase 1 required'
random.seed(1501999)
clay=bpy.data.materials['MAT_Graybox_Clay']
dark=bpy.data.materials['MAT_Graybox_Dark']
card=bpy.data.materials['MAT_TestCard']
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
records=[]
zone='desk'
def record(key,label,names,priority='P1',season='all'):
    records.append(dict(key=key,label=label,zone=zone,objects=[o.name if hasattr(o,'name') else o for o in names],priority=priority,season=season,layout='1.5',refine='2',runtime='4'))
def attach(obj,name,coll='PROPS',material=None):
    obj.name=name
    for c in list(obj.users_collection): c.objects.unlink(obj)
    COL[coll].objects.link(obj)
    if obj.type=='MESH': obj.data.materials.append(material or clay)
    obj['zone']=zone
    return obj
def box(name,p,s,rot=0,mat=None,coll='PROPS',bevel=.008):
    pre=set(bpy.data.objects); bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=(set(bpy.data.objects)-pre).pop(); o.scale=s
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.rotation_euler.z=rot
    attach(o,name,coll,mat)
    if bevel:
        m=o.modifiers.new('LayoutBevel','BEVEL'); m.width=min(bevel,min(s)*.35); m.segments=2
    return o
def ball(name,p,s,mat=None,sub=1):
    pre=set(bpy.data.objects); bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p)
    o=(set(bpy.data.objects)-pre).pop(); o.scale=s
    bpy.context.view_layer.objects.active=o; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    attach(o,name,material=mat)
    for poly in o.data.polygons: poly.use_smooth=True
    return o
def cylinder(name,a,b,r,mat=None,top=None,coll='PROPS'):
    a,b=Vector(a),Vector(b)
    pre=set(bpy.data.objects)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if top is None else top,depth=(b-a).length,location=(a+b)/2)
    o=(set(bpy.data.objects)-pre).pop(); o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    return attach(o,name,coll,mat)
def cable(name,pts,r=.008,mat=None,coll='PROPS'):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=6; cu.bevel_depth=r; cu.bevel_resolution=1
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for bp,p in zip(sp.bezier_points,pts): bp.co=p; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu); COL[coll].objects.link(o)
    # Convert only this new curve, keeping an exportable mesh and original source recipe.
    dg=bpy.context.evaluated_depsgraph_get(); mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    result=bpy.data.objects.new(name+'_Mesh',mesh); COL[coll].objects.link(result)
    bpy.context.view_layer.objects.active=bpy.data.objects['Desk_Main']
    bpy.data.objects.remove(o,do_unlink=True)
    result.name=name; result.data.materials.append(mat or dark); result['zone']=zone
    return result
def empty(name,p,coll='PROPS'):
    o=bpy.data.objects.new(name,None); COL[coll].objects.link(o); o.location=p; o.empty_display_size=.07; o['zone']=zone
    o['role']=name.split('_')[0].lower(); return o
def parent(obj,p):
    bpy.context.view_layer.update()
    world=obj.matrix_world.copy(); obj.parent=p; obj.matrix_world=world
def group(name,p,objs):
    g=empty(name,p); bpy.context.view_layer.update()
    for o in objs: parent(o,g)
    return g
def surface(name,p,w,h,material=card,rot=0):
    # Local front normal -Y, UV upright and one coherent test-card across the display.
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)])
    uv=mesh.uv_layers.new(name='UVMap')
    for d,co in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]): d.uv=co
    o=bpy.data.objects.new(name,mesh); COL['PROPS'].objects.link(o); o.location=p; o.rotation_euler.z=rot
    mesh.materials.append(material); o['zone']=zone; o['role']='emissive'; return o
def pot(name,p,r=.09,height=.18):
    x,y,z=p; objs=[cylinder(name+'_Pot',(x,y,z),(x,y,z+height),r,top=r*1.2)]
    for i in range(6):
        a=i*math.tau/6
        tip=(x+math.cos(a)*r*1.7,y+math.sin(a)*r*1.7,z+height+r*(2+random.random()))
        objs.append(cable(name+'_Stem_%02d'%i,[(x,y,z+height),((x+tip[0])/2,(y+tip[1])/2,tip[2]),tip],.004))
        objs.append(ball(name+'_Leaf_%02d'%i,tip,(r*.85,r*.35,r*.18),dark))
    return objs
def book(name,p,s=(.22,.29,.025),angle=0,mat=None):
    return box(name,p,s,angle,mat,bevel=.003)

# Authoritative dimensions and hierarchy migration for existing hero objects.
desk=bpy.data.objects['Desk_Main']; desk.location.z=.68  # tabletop top .72m
for o in list(scene.objects):
    if o.name.startswith('Desk_Leg'): o.scale.z=.92; o.location.z*=.92
    if o.name.startswith(('Lamp_','Keyboard_','Mouse_','Mug_','Notebook_')): o.location.z-=.07
for o in list(scene.objects):
    if o.name.startswith('Mac_'):
        o.location=Vector((-1.01,1.12,.72))+(o.location-Vector((-1.01,1.12,.79)))*(.34/.4975)
        o.scale*=.34/.4975
for o in list(scene.objects):
    if o.name.startswith('Chair_'):
        o.location.x=-.92+(o.location.x+.92)*1.14
        o.location.y=.18+(o.location.y-.24)*1.14
        o.scale.x*=1.14; o.scale.y*=1.14
        if o.name=='Chair_Back': o.scale.z*=1.1; o.location.z+=.02
    if o.name.startswith('Bed_'): o.location.z+=.08

zone='tv'
tvparts=[o for o in scene.objects if o.name.startswith(('TvStand_','Crt_','Vhs_'))]
old=Vector((-1.45,-.92,.03)); new=Vector((-1.72,-.79,.03)); rot=Matrix.Rotation(math.radians(45),4,'Z')
for o in tvparts:
    o.location=new+rot.to_3x3()@((o.location-old)*.82)
    o.rotation_euler.rotate(rot); o.scale*=.82
    o['zone']='tv'
tvroot=group('INT_tv_crt',new,tvparts)
def tvpoint(p): return new+rot.to_3x3()@(Vector(p)-old)*.82
def tvbox(name,p,s,angle=0,mat=None):
    o=box(name,tvpoint(p),tuple(v*.82 for v in s),math.radians(45)+angle,mat)
    parent(o,tvroot); return o
crt=bpy.data.objects['Crt_Screen']; crt.name='Crt_ScreenBacking'; crt.data.materials.clear(); crt.data.materials.append(dark)
bpy.context.view_layer.update()
sc=surface('EMIT_screen_crt',tvpoint((-1.55,-1.176,.91)),.435*.82,.295*.82,rot=math.radians(45)); parent(sc,tvroot)
tvbox('Dvd_Body',(-1.45,-1.0,.49),(.56,.30,.07),mat=dark)
tray=tvbox('ANIM_dvd_tray',(-1.45,-1.20,.49),(.28,.12,.015)); group('INT_dvd',tvpoint((-1.45,-1.0,.49)),[tray])
vcr=bpy.data.objects['Vhs_Body']; vcr.data.materials.clear(); vcr.data.materials.append(dark)
door=tvbox('ANIM_vcr_door',(-1.44,-1.18,.38),(.27,.012,.03),mat=dark)
group('INT_vcr',vcr.matrix_world.translation,[vcr,door])
for i in range(5):
    tvbox('Vhs_ExtraTape_%02d'%i,(-1.06,-.81,.70+i*.028),(.19,.12,.024),random.uniform(-.17,.17),dark)
    tvbox('Vhs_HandLabel_%02d'%i,(-1.06,-.81,.714+i*.028),(.13,.08,.002),random.uniform(-.1,.1))
for i in range(4): tvbox('Dvd_Case_%02d'%i,(-1.87,-.85,.67+i*.035),(.13,.19,.03),random.uniform(-.15,.15))
console=tvbox('GameConsole_Body',(-1.48,-.8,.64),(.26,.19,.06),mat=dark)
controller=box('Game_Controller',(-1.13,-1.23,.09),(.19,.10,.035),-.23,dark)
for dx in [-.055,.055]: ball('Game_ControllerGrip',(-1.13+dx,-1.27,.08),(.046,.05,.025),dark)
cable('Cable_GameController',[tuple(console.matrix_world.translation),(-1.42,-.7,.30),(-1.33,-1.08,.04),(-.96,-1.2,.04),(-1.13,-1.23,.1)],.006)
remote=box('Tv_Remote',(-1.0,-1.48,.055),(.055,.18,.025),.25,dark)
record('TV','CRT + tilted cabinet',tvparts+[sc],'P0')
record('VCR','VHS recorder / door',[vcr,door],'P0')
record('DVD','DVD player / tray',[tray,'Dvd_Body'],'P0')
record('TAPES','VHS labels / DVD cases',[o for o in scene.objects if o.name.startswith(('Vhs_Extra','Vhs_Hand','Dvd_Case'))])
record('GAME','Console / controller / cable / remote',[console,controller,remote,'Cable_GameController'])

zone='desk'
mac=bpy.data.objects['Mac_Screen']; mac.name='Mac_ScreenBacking'; mac.data.materials.clear(); mac.data.materials.append(dark)
bpy.context.view_layer.update()
mp=mac.matrix_world.translation
ms=surface('EMIT_screen_mac',(mp.x,mp.y-.012,mp.z),.275*.34/.4975,.202*.34/.4975)
group('INT_mac',(-1.01,1.12,.72),[o for o in scene.objects if o.name.startswith('Mac_')]+[ms])
group('INT_lamp_desk',(-1.62,1.19,.72),[o for o in scene.objects if o.name.startswith('Lamp_') and o.type=='MESH'])
record('DESK','Desk 0.72m / Mac 0.34m',[desk,ms,'INT_mac'],'P0')
record('KEYS','Keyboard / mouse',[o for o in scene.objects if o.name.startswith(('Keyboard_','Mouse_'))],'P0')
record('TASKLAMP','Task lamp',['INT_lamp_desk'])
cpu=box('Computer_Tower',(-.18,1.18,.30),(.23,.40,.54),mat=dark)
box('Computer_Drive',(-.18,.975,.46),(.17,.01,.06))
record('TOWER','Computer tower',[cpu,'Computer_Drive'])
modem=box('Modem_Body',(-.16,1.23,.76),(.24,.15,.055),.08)
for i in range(4): ball('EMIT_led_modem_%02d'%i,(-.24+i*.04,1.148,.77),(.009,.004,.006),dark)
phone=box('INT_phone',(-1.63,.83,.76),(.18,.23,.07),-.2)
box('Phone_Receiver',(-1.64,.84,.815),(.055,.20,.04),-.2,dark)
coilpts=[(-1.56+.025*math.cos(i*.6),.78-i*.006,.76+.025*math.sin(i*.6)) for i in range(65)]
coil=cable('Cable_Phone_Coil',coilpts,.004)
record('MODEM','Modem / coiled phone cable',[modem,phone,coil])
speakers=[]
for i,x in enumerate([-1.38,-.65]):
    speakers.append(box('Speaker_%s'%i,(x,1.32,.84),(.12,.13,.24),mat=dark))
    speakers.append(cylinder('Speaker_Cone_%s'%i,(x,1.248,.84),(x,1.24,.84),.04))
record('SPEAKERS','Pair of speakers',speakers)
flip=box('INT_clock_flip',(-.45,1.33,.78),(.17,.09,.10),mat=dark)
flipsc=surface('EMIT_screen_flip',(-.45,1.278,.78),.145,.07)
calendar=box('INT_calendar',(-.05,.88,.79),(.12,.045,.14),-.18)
calendar.rotation_euler.x=math.radians(-12)
record('CLOCK','Flip clock / calendar',[flip,flipsc,calendar])
bowl=cylinder('Noodles_Bowl',(-.40,.84,.73),(-.40,.84,.82),.055,top=.08)
cylinder('Noodles_ChopstickA',(-.46,.80,.83),(-.28,.83,.85),.003)
cylinder('Noodles_ChopstickB',(-.46,.82,.83),(-.28,.85,.85),.003)
penpot=cylinder('Pencil_Cup',(-1.79,1.35,.73),(-1.79,1.35,.86),.043)
for i in range(5):
    cylinder('Pencil_%02d'%i,(-1.81+i*.011,1.35,.79),(-1.84+i*.022,1.36,.97+random.random()*.04),.004,dark)
notes=[]
for i in range(4):
    n=book('Sticky_Desk_%02d'%i,(-.75+i*.13,.99,.727),(.065,.07,.003),random.uniform(-.5,.5)); n.rotation_euler.x=.07*i; notes.append(n)
for i in range(2):
    notes.append(box('Sticky_Mac_%02d'%i,(-1.095+i*.16,mp.y-.015,mp.z+.09),(.048,.002,.055),bevel=0))
record('SNACK','Noodles / mug / stationery',[bowl,penpot,'Mug_Main']+notes)
walkman=box('Walkman_Body',(-.13,.67,.75),(.11,.16,.045),.2,dark)
cable('Headphones_Band',[(-.25,.57,.75),(-.33,.55,.82),(-.31,.63,.84),(-.22,.64,.75)],.008)
for p in [(-.25,.57,.75),(-.22,.64,.75)]: ball('Headphones_Earcup',p,(.035,.025,.02),dark)
cable('Cable_Headphone',[(-.22,.64,.75),(-.34,.62,.735),(-.4,.68,.73),(-.13,.65,.76)],.003)
floppy=box('Floppy_Box',(-.07,1.36,.77),(.13,.13,.09))
for i in range(4): box('Floppy_Disk_%02d'%i,(-.12+i*.025,1.36,.84),(.015,.10,.09),random.uniform(-.1,.1),dark)
for i,p in enumerate([(-.6,.94,.735),(-.29,1.04,.735)]): cylinder('Cd_Loose_%02d'%i,p,(p[0],p[1],p[2]+.003),.055,dark)
record('AUDIO','Walkman / headphones / cable',[walkman,'Headphones_Band','Cable_Headphone'])
record('DISKS','Floppy box / loose CDs',[floppy,'Cd_Loose_00','Cd_Loose_01'])
strip=box('PowerStrip_Main',(-.64,1.45,.072),(.63,.10,.055),mat=dark)
wires=[]
for i,x in enumerate([-1.60,-1.20,-.89,-.63,-.37,-.13]):
    px=-.90+i*.1
    box('PowerStrip_Plug_%02d'%i,(px,1.45,.115),(.065,.07,.055))
    wires.append(cable('Cable_Device_%02d'%i,[(x,1.40,.77),(x,1.5,.60),(x+.05,1.58,.29),(px,1.52,.10),(px,1.45,.14)],.008))
cable('Cable_Mains',[(-.35,1.45,.10),(-.2,1.60,.06),(.10,1.62,.1),(.14,1.67,.24)],.01)
box('Wall_Outlet',(.14,1.67,.24),(.12,.025,.15),coll='ROOM_SHELL')
record('POWER','Power strip / six device cables / plugs',[strip]+wires)

zone='right-wall'
wallShelf=box('WallShelf_Long',(1.87,.20,2.30),(.33,2.74,.07),coll='FURNITURE')
shelfthings=[wallShelf]
for i in range(10): shelfthings.append(book('WallShelf_Cd_%02d'%i,(1.87,-.90+i*.045,2.45),(.17,.032,.24),random.uniform(-.06,.06)))
globe=ball('Globe_Sphere',(1.86,.04,2.55),(.15,.15,.15),sub=2)
cylinder('Globe_Stand',(1.86,.04,2.33),(1.86,.04,2.42),.055)
shelfthings.append(globe)
for j in range(2):
    y=.50+j*.30
    shelfthings.append(ball('Figurine_Head_%02d'%j,(1.85,y,2.59),(.065,.065,.065)))
    shelfthings.append(box('Figurine_Body_%02d'%j,(1.85,y,2.46),(.08,.08,.15)))
for i in range(4): shelfthings.append(box('Lego_Block_%02d'%i,(1.85,1.12,2.36+i*.055),(.14,.12,.05),random.uniform(-.15,.15)))
for i in range(3): shelfthings.append(book('Manual_Shelf_%02d'%i,(1.85,-.23,2.37+i*.022),(.20,.22,.018),random.uniform(-.1,.1)))
record('WALLSHELF','Long wall shelf / CD tower / globe / figures / Lego / manuals',shelfthings)
posters=[]
for i,(y,z,w,h) in enumerate([(-.95,1.74,.48,.62),(-.36,1.63,.40,.47),(.26,1.81,.44,.57)]):
    p=box('Poster_%02d'%i,(2.019,y,z),(.014,w,h),mat=dark,bevel=.002); p.rotation_euler.x=(-.10 if i==1 else .025*i); posters.append(p)
    # Raised graphic placeholder: a moon, horizontal rule and caption block.
    posters.append(ball('Poster_Moon_%02d'%i,(2.005,y,z+.08),(.008,w*.25,w*.25)))
    posters.append(box('Poster_Caption_%02d'%i,(1.996,y,z-h*.32),(.01,w*.68,.04),bevel=0))
record('POSTERS','Three skewed posters',posters)
board=box('Corkboard_Main',(2.01,.91,1.57),(.055,.66,.48))
boardnotes=[board]
for i in range(6):
    y=.69+(i%3)*.20; z=1.45+(i//3)*.23
    b=box('Corkboard_Photo_%02d'%i,(1.974,y,z),(.007,.14,.16),mat=dark,bevel=.001); b.rotation_euler.x=random.uniform(-.15,.15); boardnotes.append(b)
    boardnotes.append(ball('Corkboard_Pin_%02d'%i,(1.96,y,z+.06),(.014,.012,.012)))
record('NOTICE','Corkboard / photos / notes / tickets',boardnotes)
clock=cylinder('INT_clock_wall',(2.018,-1.47,2.0),(1.99,-1.47,2.0),.16,mat=dark)
cylinder('WallClock_Face',(1.985,-1.47,2),(1.977,-1.47,2),.14)
box('ANIM_clock_hour',(1.97,-1.44,2.025),(.008,.065,.012),bevel=0)
box('ANIM_clock_minute',(1.965,-1.47,2.05),(.008,.012,.1),bevel=0)
record('WALLCLOCK','Wall clock / hands',[clock,'ANIM_clock_hour','ANIM_clock_minute'])
lower=box('LowBookshelf_Main',(1.80,-1.26,.40),(.37,.91,.70),coll='FURNITURE',mat=dark)
for row in range(2):
    for i in range(8): book('LowBookshelf_Book_%02d_%02d'%(row,i),(1.58,-1.61+i*.088,.23+row*.31),(.22,.065,random.uniform(.20,.28)),random.uniform(-.05,.05))
skate=box('Skateboard_Deck',(1.53,-1.63,.35),(.17,.05,.62),-.12); skate.rotation_euler.x=.17
for z in [.15,.55]: cylinder('Skateboard_Axle',(1.43,-1.67,z),(1.63,-1.67,z),.025,dark)
record('LOWWALL','Low bookshelf / skateboard',[lower,skate])

zone='bed'
# Replace the flat blanket geometry in-place with a folded grid; keep name and source identity.
blanket=bpy.data.objects['Bed_Blanket']; mesh=bpy.data.meshes.new('Bed_Blanket_Folds')
verts=[]; faces=[]; nx,ny=24,24
for j in range(ny+1):
    for i in range(nx+1):
        u=i/nx; v=j/ny
        x=(u-.5)*1.26; y=(v-.5)*1.30
        z=.035*math.sin(u*math.pi*9+v*3)+.018*math.sin(v*math.pi*12)+.018*math.sin(u*17-v*8)
        if u<.06 or u>.94: z-=.12
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        k=j*(nx+1)+i; faces.append((k,k+1,k+nx+2,k+nx+1))
mesh.from_pydata(verts,[],faces); mesh.materials.append(clay); blanket.data=mesh
blanket.modifiers.clear(); sol=blanket.modifiers.new('ClothThickness','SOLIDIFY'); sol.thickness=.015
blanket.location.z=.735
for p in mesh.polygons:p.use_smooth=True
cushion=box('Bed_Cushion',(1.61,.99,.84),(.36,.35,.17),.28,bevel=.065)
comicA=book('Comic_OpenLeft',(1.15,.42,.78),(.22,.30,.025),-.2); comicA.rotation_euler.y=-.12
comicB=book('Comic_OpenRight',(1.37,.38,.78),(.22,.30,.025),-.2); comicB.rotation_euler.y=.12
for i in range(3): box('Comic_Panel_%02d'%i,(1.12,.33+i*.07,.805),(.13,.04,.003),-.2,dark,bevel=0)
record('BED','Raised bed / folded duvet / cushion / open comic',[blanket,cushion,comicA,comicB])
nightstand=box('Nightstand_Main',(.42,1.32,.34),(.38,.45,.59),coll='FURNITURE')
box('Nightstand_Drawer',(.42,1.086,.38),(.32,.025,.23),mat=dark)
alarm=box('Alarm_Body',(.39,1.24,.70),(.15,.085,.10),mat=dark)
alarmScreen=surface('EMIT_screen_alarm',(.39,1.192,.70),.12,.065)
cylinder('Nightstand_Water',(.53,1.40,.64),(.53,1.40,.76),.038)
cylinder('Nightlight_Stem',(.29,1.48,.64),(.29,1.48,.83),.012)
cylinder('Nightlight_Shade',(.29,1.48,.80),(.29,1.48,.93),.08,top=.05)
record('NIGHTSTAND','Nightstand / alarm / water / nightlight',[nightstand,alarm,alarmScreen,'Nightlight_Shade'])
slippers=[]
for i in range(2): slippers.append(ball('Slipper_%02d'%i,(.86+i*.21,-.71,.07),(.085,.16,.04),dark,sub=2))
record('SLIPPERS','Pair of slippers',slippers)

zone='floor'
trash=cylinder('Wastebasket_Main',(-1.86,.38,.04),(-1.86,.38,.30),.10,top=.14,mat=dark)
papers=[]
for i,p in enumerate([(-1.65,.18,.055),(-1.86,.08,.045),(-1.78,.41,.32)]): papers.append(ball('Paper_Crumpled_%02d'%i,p,(.05,.047,.05)))
catbed=ball('Cat_Bed',(.04,-1.17,.12),(.31,.26,.09),dark,sub=2)
cat=ball('Cat_Placeholder',(.04,-1.17,.23),(.22,.16,.13),sub=2)
ball('Cat_Head',(.18,-1.16,.29),(.085,.085,.075),sub=2)
for y in [-1.20,-1.12]: cylinder('Cat_Ear',(.18,y,.32),(.18,y,.43),.045,top=.005)
cable('Cat_Tail',[(-.12,-1.18,.20),(-.19,-1.30,.21),(.00,-1.35,.23),(.13,-1.28,.24)],.025)
group('INT_cat',(.04,-1.17,.23),[o for o in scene.objects if o.name.startswith('Cat_') and o!=catbed])
record('CAT','Cat bed / sleeping cat',[catbed,'INT_cat'])
record('TRASH','Bin / missed paper balls',[trash]+papers)
magazines=[]
for i in range(4): magazines.append(book('Magazine_Floor_%02d'%i,(.70+random.random()*.3,-1.22+i*.11,.045+i*.012),(.26,.34,.014),random.uniform(-.5,.5)))
record('MAGAZINES','Scattered magazines',magazines)
foreground=pot('Plant_Foreground',(-1.92,-1.62,.04),.20,.36)
crate=box('Box_Foreground',(1.45,-1.80,.22),(.62,.50,.40),-.10)
for i in range(5): book('Box_Record_%02d'%i,(1.28+i*.075,-1.8,.49),(.025,.34,.37),-.10,dark)
record('FOREGROUND','Foreground plant / record crate',foreground+[crate])

zone='window'
wp=pot('Plant_Windowsill',(-1.56,1.54,1.0),.065,.12)
bird=ball('Windowsill_Figurine',(-.34,1.55,1.09),(.09,.05,.07))
ball('Windowsill_FigurineHead',(-.29,1.55,1.15),(.045,.04,.04))
record('SILL','Sill plant / tiny bird figure',wp+[bird])
blindparts=[o for o in scene.objects if o.name.startswith('Window_Blind')]
for i,o in enumerate(blindparts): o.name='ANIM_blinds_slat_%02d'%i
window=group('INT_window',(-.9,1.7,1.7),blindparts)
for name,p in [('SOCKET_rain_window',(-.9,1.82,2.4)),('SOCKET_petals_window',(-.9,1.7,1.9)),('SOCKET_windchime',(-.10,1.55,2.35)),('SOCKET_steam_mug',(-.34,.96,.86))]: empty(name,p)
cable('Windchime_Cord',[(-.10,1.55,2.4),(-.10,1.55,2.10)],.003)
for i in range(3): cylinder('Windchime_Tube_%02d'%i,(-.15+i*.05,1.55,2.12),(-.15+i*.05,1.55,1.92-i*.025),.008)
record('WINDOW','Movable blinds / weather sockets / chime',[window,'SOCKET_rain_window','SOCKET_petals_window','SOCKET_windchime'])

zone='seasonal'
fanparts=[cylinder('Fan_Base',(.19,-.37,.06),(.19,-.37,.10),.17),cylinder('Fan_Stem',(.19,-.37,.1),(.19,-.37,.44),.025)]
head=empty('ANIM_fan_head',(.19,-.37,.50))
guard=cylinder('Fan_Guard',(.19,-.40,.53),(.19,-.30,.53),.19,dark)
parent(guard,head)
for i in range(3):
    a=i*math.tau/3
    blade=ball('ANIM_fan_blade_%02d'%i,(.19+math.cos(a)*.08,-.415,.53+math.sin(a)*.08),(.085,.015,.04));parent(blade,head)
fangroup=group('SEASON_summer_fan',(.19,-.37,.05),fanparts+[head])
heater=box('SEASON_winter_heater',(.45,.38,.25),(.32,.30,.43),mat=dark)
for i in range(5):box('Heater_Grille_%02d'%i,(.32+i*.065,.217,.25),(.025,.01,.30))
cylinder('Kettle_Body',(.45,.38,.47),(.45,.38,.61),.09)
cable('Kettle_Handle',[(.36,.38,.59),(.36,.38,.73),(.54,.38,.73),(.54,.38,.59)],.012)
cylinder('Kettle_Spout',(.53,.38,.56),(.61,.38,.65),.022,top=.015)
empty('SOCKET_kettle_steam',(.61,.38,.65))
flower=pot('Spring_Flowers',(-.32,1.60,1.00),.06,.12)
flowergroup=group('SEASON_spring_flowerpot',(-.32,1.60,1),flower)
for p in [(-.39,1.59,1.29),(-.24,1.64,1.3)]:ball('Spring_Blossom',p,(.045,.04,.035))
throw=box('SEASON_autumn_blanket',(-.92,-.01,.77),(.42,.10,.39),-.04,bevel=.025)
scarf=box('SEASON_winter_scarf',(1.83,1.58,.98),(.16,.15,.43),.12,bevel=.035)
ice=cylinder('SEASON_summer_iceddrink',(-.25,1.1,.73),(-.25,1.1,.87),.035)
sock=[]
for name,p in [('SOCKET_cat_bed',(1.60,.70,.82)),('SOCKET_cat_heater',(.65,.10,.12)),('SOCKET_cat_windowsill',(-.68,1.56,1.03)),('SOCKET_cat_fan',(.22,-.70,.10))]:sock.append(empty(name,p))
for o,season in [(fangroup,'summer'),(heater,'winter'),(flowergroup,'spring'),(throw,'autumn'),(scarf,'winter'),(ice,'summer')]:o['season']=season
record('SEASONS','Fan / heater / kettle / spring flowers / throw / scarf / iced drink',[fangroup,heater,flowergroup,throw,scarf,ice,'SOCKET_kettle_steam'])
record('CATSOCKETS','Four cat destinations',sock)

zone='lights'
lampAnchor=empty('LIGHT_desk_lamp',(-1.45,1.18,1.18))
for name,p in [('LIGHT_ceiling',(.2,.5,2.52)),('LIGHT_heater',(.45,.2,.3)),('LIGHT_string_lights',(-.9,1.58,2.48)),('LIGHT_lava_lamp',(1.76,-1.18,1.1))]:empty(name,p)
ceiling=cylinder('Ceiling_Shade',(.2,.5,2.47),(.2,.5,2.66),.25,top=.1)
cable('Ceiling_Suspension',[(.2,.5,2.65),(.2,.5,2.95)],.013)
cable('INT_ceiling_pullcord',[(.40,.5,2.54),(.40,.5,1.97)],.003)
ball('Ceiling_PullWeight',(.4,.5,1.96),(.017,.017,.026),dark)
string=cable('StringLights_Wire',[(-1.83,1.53,1.1),(-1.82,1.53,2.51),(-.96,1.52,2.56),(.00,1.53,2.5),(.1,1.54,1.17)],.007)
for i in range(14):ball('StringLights_Bulb_%02d'%i,(-1.81+i*.14,1.51,2.51-.08*math.sin(i*.7)),(.024,.024,.035))
cylinder('LavaLamp_Base',(1.76,-1.18,.77),(1.76,-1.18,.89),.075,dark,top=.05)
lava=cylinder('INT_lava_lamp',(1.76,-1.18,.89),(1.76,-1.18,1.15),.05,top=.02)
record('LIGHTS','Ceiling / pullcord / string path / lava lamp / five anchors',[ceiling,string,lava,lampAnchor,'LIGHT_ceiling','LIGHT_heater','LIGHT_string_lights','LIGHT_lava_lamp'])

zone='exterior'
ext=[]
for i,(x,y,h) in enumerate([(-2.7,6.2,1.0),(-.5,6.6,1.3),(1.4,6.4,.95)]):
    ext.append(box('Exterior_House_%02d'%i,(x,y,h/2),(1.4,1.1,h),coll='ROOM_SHELL'))
    roof=box('Exterior_Roof_%02d'%i,(x,y,h+.12),(1.55,1.22,.22),coll='ROOM_SHELL',mat=dark); ext.append(roof)
    for j in range(2):ext.append(box('Exterior_Window_%02d_%02d'%(i,j),(x-.35+j*.7,y-.558,h*.65),(.24,.012,.30),coll='ROOM_SHELL',mat=dark))
pole=cylinder('Exterior_UtilityPole',(-1.75,4.5,-1),(-1.75,4.5,3.0),.055,coll='ROOM_SHELL')
ext.append(pole); ext.append(box('Exterior_Crossarm',(-1.75,4.5,2.85),(.70,.08,.07),coll='ROOM_SHELL'))
for i in range(2):ext.append(cable('Exterior_Powerline_%02d'%i,[(-4,4.6+i*.2,3),(-1.75,4.5+i*.2,2.85),(1,4.6+i*.2,2.45),(4,4.5+i*.2,2.85)],.009,coll='ROOM_SHELL'))
for i in range(16):ext.append(box('Exterior_Fence_%02d'%i,(-3+i*.32,4.15,-.15),(.10,.08,.95),coll='ROOM_SHELL'))
for z in [-.3,.15]:ext.append(box('Exterior_FenceRail',(-.6,4.19,z),(5,.06,.065),coll='ROOM_SHELL'))
record('OUTSIDE','Utility pole / wires / houses / fence',ext)

zone='extras'
for i in range(3):book('UnderBed_Storage_%02d'%i,(1.0+i*.30,-.51,.18),(.24,.35,.15),random.uniform(-.05,.05),dark)
cable('Rug_FrayedEdge',[(-.6,-1.30,.06),(-.55,-1.35,.06),(-.50,-1.3,.06)],.006)
record('EXTRAS','Underbed boxes / frayed rug edge',['UnderBed_Storage_00','UnderBed_Storage_01','UnderBed_Storage_02','Rug_FrayedEdge'])

# Close framing: retain the established view direction and move 12% toward target.
cam=bpy.data.objects['Camera_Room']; target=Vector((0,.25,1.1)); cam.location=target+(cam.location-target)*.88
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
scene.camera=cam
bpy.ops.object.select_all(action='DESELECT')
for o in scene.objects:
    if o.type=='MESH':
        bpy.context.view_layer.objects.active=o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.select_set(False)
        for poly in o.data.polygons:
            if len(poly.vertices)==4 and o.name.startswith(('Bed_','Mac_','Crt_')): pass

# Emissive area sources approximate screen bounce in Eevee. They are screen lights only.
def areaLight(name,screen,energy,color,size):
    d=bpy.data.lights.new(name,'AREA'); d.energy=energy;d.color=color;d.shape='RECTANGLE';d.size=size;d.size_y=size*.7
    o=bpy.data.objects.new(name,d);COL['LIGHTS'].objects.link(o)
    bpy.context.view_layer.update(); world=screen.matrix_world
    normal=world.to_3x3()@Vector((0,-1,0));o.location=world.translation+normal*.035
    o.rotation_euler=normal.to_track_quat('-Z','Y').to_euler();return o
areaLight('ScreenBounce_Mac',ms,5,(.60,.80,1),.24)
areaLight('ScreenBounce_Crt',sc,9,(.70,.83,1),.36)
bpy.data.objects['Lamp_Warm'].location.z-=.07
bpy.data.objects['Lamp_Warm'].data.energy=16

scene['phase15_layout']=True
scene['layout_inventory']=json.dumps(records,ensure_ascii=False)
(ROOT/'docs'/'layout-inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':
        ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);ev.to_mesh_clear()
assert tri<80000,tri
assert all(min(o.scale)>0 for o in scene.objects)
print('DENSITY_OK',len(scene.objects),'objects',tri,'triangles',len(records),'asset groups')

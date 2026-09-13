"""User's unified Phase 2 completion list. No furniture/camera relocation."""
import bpy,ast,math,random,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert scene.get('phase2_contacts') and not scene.get('phase2_final_assets')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
for f in ['densify_scene.py','phase2_refine.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
def tube(name,points,r,key='Charcoal',sides=6):
    points=[Vector(p) for p in points];vs=[];fs=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        ref=Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((0,1,0))
        u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized()
        for k in range(sides):a=k*math.tau/sides;vs.append(p+r*(math.cos(a)*u+math.sin(a)*v))
    for i in range(len(points)-1):
        for k in range(sides):a=i*sides+k;b=i*sides+(k+1)%sides;fs.append((a,b,b+sides,a+sides))
    fs.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+k for k in range(sides))])
    return meshobj(name,vs,fs,key,True)
def circle(name,p,r,thick,key='Cream',axis='Y'):
    pts=[]
    for i in range(25):
        a=i*math.tau/24;pts.append((p[0]+r*math.cos(a),p[1]+(r*math.sin(a) if axis=='Z' else 0),p[2]+(r*math.sin(a) if axis=='Y' else 0)))
    return tube(name,pts,thick,key)
# Spend bevel segments on heroes, not tiny distant shelf blocks.
for o in scene.objects:
    if o.type!='MESH':continue
    if o.name.startswith(('WallShelf_','Shelf_Book','Manual_','Keyboard_Key','Floor_','Exterior_','LowBookshelf_Book','Box_Record','Vhs_','Dvd_Case','UnderBed_','Poster_','Corkboard_','Comic_','Pencil_','PowerStrip_','Sticky_')):
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
    if o.name.startswith(('Cable_Device','Plant_','Spring_')) and not any(m.type=='DECIMATE' for m in o.modifiers):
        if o.name.startswith('Cable_') or '_Stem_' in o.name:
            m=o.modifiers.new('SmallTubeBudget','DECIMATE');m.ratio=.4

# Fan's original semantic head pivot remains. Cage depth encloses twisted blades.
head=bpy.data.objects['ANIM_fan_head']
for o in list(head.children):remove(o)
for y in [-.455,-.335]:
    for r in [.065,.12,.18]:parent(circle('Fan_Cage',(.19,y,.53),r,.003),head)
    for i in range(12):
        a=i*math.tau/12
        parent(tube('Fan_Spoke',[(.19,y+(-.012 if y<-.4 else .012),.53),(.19+.10*math.cos(a),y,.53+.10*math.sin(a)),(.19+.18*math.cos(a),y,.53+.18*math.sin(a))],.0024,'Cream'),head)
for i in range(8):
    a=i*math.tau/8
    parent(tube('Fan_CageDepth',[(.19+.18*math.cos(a),-.455,.53+.18*math.sin(a)),(.19+.187*math.cos(a),-.395,.53+.187*math.sin(a)),(.19+.18*math.cos(a),-.335,.53+.18*math.sin(a))],.003,'Teal'),head)
motor=cylinder('Fan_Motor',(.19,-.38,.53),(.19,-.29,.53),.047,M['Teal']);parent(motor,head)
hub=uvball('Fan_Hub',(.19,-.469,.53),(.029,.018,.029),'Brass',16,8);parent(hub,head)
pivot=empty('ANIM_fan_blades',(.19,-.395,.53));parent(pivot,head);pivot['axis']='Y'
for i in range(3):
    a=i*math.tau/3;vs=[];fs=[]
    for j in range(7):
        t=j/6;rad=.025+.13*t;ang=a+t*.72
        for side in [-1,1]:
            b=ang+side*.30*math.sin(t*math.pi*.85)
            vs.append((.19+rad*math.cos(b),-.395+side*.016*math.sin(t*math.pi),.53+rad*math.sin(b)))
    for j in range(6):q=j*2;fs.append((q,q+1,q+3,q+2))
    o=meshobj('Fan_Blade',vs,fs,'Teal',True);sol=o.modifiers.new('BladeThickness','SOLIDIFY');sol.thickness=.005;parent(o,pivot)
joint=cylinder('Fan_TiltJoint',(.145,-.36,.44),(.235,-.36,.44),.035,M['Brass']);parent(joint,head)
for i in range(3):box('Fan_BaseButton',(.13+i*.055,-.45,.112),(.035,.04,.013),mat=M[['Cream','Cream','Terracotta'][i]],bevel=.004)

# Compact Macintosh: taper upper rear housing; add recessed handle and rounded screen glass.
body=bpy.data.objects['Mac_Body'];bpy.context.view_layer.update()
for v in body.data.vertices:
    if v.co.z>0:v.co.x*=.91;v.co.y*=.95
handle=box('Mac_HandleRecess',(-1.01,1.19,1.058),(.10,.05,.003),mat=M['Charcoal'],bevel=.008);parent(handle,bpy.data.objects['INT_mac'])
for name in ['Keyboard_Base','Mouse_Main']:mat(bpy.data.objects[name],'Jelly')
box('Keyboard_Circuit',(-1,.76,.733),(.39,.16,.005),mat=M['Leaf'],bevel=.004)
for x in [-1.16,-1.12]:uvball('Keyboard_LED',(x,.834,.744),(.005,.005,.003),'GlowWarm',12,6)
for i in range(3):box('Keyboard_CircuitTrace',(-1.01,.72+i*.04,.737),(.29,.002,.001),mat=M['Brass'],bevel=0)
box('Mouse_Circuit',(-.63,.76,.73),(.045,.065,.006),mat=M['Leaf'],bevel=.003)
for name in ['EMIT_screen_mac','EMIT_screen_crt']:
    sc=bpy.data.objects[name];bpy.context.view_layer.update();w=sc.matrix_world.copy();bw=max(v.co.x for v in sc.data.vertices)*2;bh=max(v.co.z for v in sc.data.vertices)*2
    verts=[];faces=[];nx,ny=12,8
    for j in range(ny+1):
        z=(j/ny-.5)*bh
        for i in range(nx+1):
            x=(i/nx-.5)*bw;y=-.004-.009*(1-(x/(bw/2))**2)*(1-(z/(bh/2))**2);verts.append(w@Vector((x,y,z)))
    for j in range(ny):
        for i in range(nx):q=j*(nx+1)+i;faces.append((q,q+1,q+nx+2,q+nx+1))
    glass=meshobj('Crt_Glass' if name.endswith('crt') else 'Mac_Glass',verts,faces,'Glass',True);parent(glass,sc.parent)

# Phone buttons align to the tilted body frame as one 3x4 keypad.
for o in list(scene.objects):
    if o.name.startswith('Phone_Key'):remove(o)
angle=-.2;center=Vector((-1.63,.83,.802));rot=Matrix.Rotation(angle,4,'Z')
for row in range(4):
    for col in range(3):
        p=center+rot.to_3x3()@Vector((.028+col*.025,-.058+row*.031,0))
        box('Phone_Key_%d_%d'%(row,col),p,(.018,.024,.005),angle,M['Paper'],bevel=.002)
for y in [.76,.92]:box('Phone_Cradle',(-1.69,y,.803),(.075,.022,.025),-.2,M['Teal'],bevel=.006)

# Pillows: padded surface with a shallow pressure depression, stitched perimeter.
for name in ['Bed_Pillow','Bed_Cushion']:
    old=bpy.data.objects[name];bb=bounds(old);c=Vector([(b[0]+b[1])/2 for b in bb]);sx=(bb[0][1]-bb[0][0])*.5;sy=(bb[1][1]-bb[1][0])*.5
    n=uvball(name+'_New',c,(sx,sy,.082),'Paper' if name=='Bed_Pillow' else 'Sage',24,12)
    for v in n.data.vertices:
        if v.co.z>c.z:
            d=((v.co.x-c.x)/(.6*sx))**2+((v.co.y-c.y)/(.6*sy))**2;v.co.z-=.035*math.exp(-d*2)
    replace(old,n)
for i in range(2):
    old=bpy.data.objects['Slipper_%02d'%i];p=old.matrix_world.translation.copy()
    replace(old,uvball('SlipperSole',p,(.074,.145,.016),'Lilac',20,8))
    o=lathe('Slipper_Upper',(0,0,0),[(.05,0),(.08,.02),(.07,.05),(.045,.055)],'Sage',16)
    for v in o.data.vertices:
        x,y,z=v.co;v.co=(p.x+x,p.y+y*.85+.025,p.z+z+.012)
    uvball('Slipper_Opening',(p.x,p.y-.065,p.z+.027),(.052,.055,.006),'Walnut',16,6)
    uvball('Slipper_Lining',(p.x,p.y-.095,p.z+.023),(.045,.032,.006),'Paper',16,6)
# Kettle gets a real lid, rim, knob, open spout and attachment pivots.
p=(.45,.38,.47)
replace(bpy.data.objects['Kettle_Body'],lathe('KettleNew',p,[(0,0),(.062,0),(.095,.045),(.087,.115),(.062,.137),(.05,.137),(.05,.12)],'Cream',24))
lid=lathe('Kettle_Lid',(.45,.38,.603),[(0,.012),(.063,0),(.065,.008),(.025,.026),(0,.026)],'Brass',24);parent(lid,bpy.data.objects['SEASON_winter_heater'])
knob=uvball('Kettle_LidKnob',(.45,.38,.64),(.018,.018,.012),'Walnut',16,8);parent(knob,bpy.data.objects['SEASON_winter_heater'])
sp=bpy.data.objects['Kettle_Spout'];mat(sp,'Cream')
mouth=uvball('Kettle_SpoutOpening',(.61,.38,.652),(.012,.013,.003),'Charcoal',12,6);parent(mouth,bpy.data.objects['SEASON_winter_heater'])

# Cat: paint stripes onto the fur instead of leaving raised floating strips.
for o in list(scene.objects):
    if o.name.startswith('Cat_BackStripe'):remove(o)
o=bpy.data.objects['Cat_Body'];o.data.materials.append(M['Walnut'])
for f in o.data.polygons:
    p=sum((o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices)
    if p.z>.325 and any(abs(p.y-y)<.012 for y in [-1.09,-1.15,-1.21]):f.material_index=1
tip=uvball('Cat_TailTip',(-.035,-1.36,.177),(.037,.037,.037),'Fur',16,8);parent(tip,bpy.data.objects['INT_cat'])
socket=empty('SOCKET_emoji_cat',(-.10,-1.18,.62));parent(socket,bpy.data.objects['INT_cat'])

# PS1 in the TV stand, with visible controller ports and original controller silhouette.
old=bpy.data.objects['GameConsole_Body'];p=old.matrix_world.translation.copy()
replace(old,box('PS1New',p,(.28,.19,.06),mat=M['Cream'],bevel=.014))
lid=cylinder('PS1_DiscLid',(p.x,p.y,p.z+.029),(p.x,p.y,p.z+.035),.073,M['Paper']);parent(lid,old)
for x in [-.095,.095]:
    b=cylinder('PS1_Button',(p.x+x,p.y-.045,p.z+.030),(p.x+x,p.y-.045,p.z+.036),.016,M['Sage']);parent(b,old)
for x in [-.07,.07]:
    b=box('PS1_ControllerPort',(p.x+x,p.y-.098,p.z-.006),(.055,.006,.019),mat=M['Charcoal'],bevel=.004);parent(b,old)
con=bpy.data.objects['Game_Controller'];mat(con,'Cream')
for o in scene.objects:
    if o.name.startswith('Game_ControllerGrip'):mat(o,'Cream')
for p2,s2 in [((-1.182,-1.237,.113),(.012,.045,.004)),((-1.182,-1.237,.115),(.041,.012,.004))]:box('PS1_Dpad',p2,s2,mat=M['Charcoal'],bevel=.001)
for i in range(4):
    a=i*math.tau/4;uvball('PS1_FaceButton',(-1.082+.017*math.cos(a),-1.23+.017*math.sin(a),.111),(.006,.006,.003),['Rose','Blue','Sage','Lilac'][i],12,6)
tube('PS1_TvCable',[p+Vector((0,.10,0)),p+Vector((.15,.15,-.05)),p+Vector((.13,.19,.22))],.004)

# Two 1/144-style original mecha silhouettes, kept below window sightline.
def mecha(name,x,y,z,key,pose):
    objs=[]
    for dx in [-.03,.03]:
        objs.append(box(name+'_Foot',(x+dx,y-.012,z+.012),(.037,.058,.023),mat=M['Charcoal'],bevel=.005))
        objs.append(box(name+'_Shin',(x+dx,y,z+.050),(.023,.025,.06),mat=M['Paper'],bevel=.004))
        objs.append(box(name+'_Knee',(x+dx,y-.017,z+.079),(.028,.022,.024),mat=M[key],bevel=.004))
        objs.append(box(name+'_Thigh',(x+dx,y+.004,z+.098),(.028,.027,.04),mat=M['Paper'],bevel=.004))
    objs.append(box(name+'_Waist',(x,y,z+.13),(.06,.036,.04),mat=M[key],bevel=.004))
    objs.append(box(name+'_Chest',(x,y,z+.168),(.071,.045,.055),mat=M[key],bevel=.008))
    objs.append(box(name+'_Head',(x,y,z+.216),(.042,.037,.039),mat=M['Paper'],bevel=.006))
    objs.append(box(name+'_Visor',(x,y-.020,z+.218),(.031,.003,.006),mat=M['Teal'],bevel=0))
    for dx in [-.055,.055]:
        objs.append(box(name+'_Shoulder',(x+dx,y,z+.178),(.038,.041,.029),mat=M['Paper'],bevel=.007))
        objs.append(box(name+'_Arm',(x+dx,y-.005,z+.139),(.023,.026,.055),mat=M[key],bevel=.005))
        objs.append(box(name+'_Hand',(x+dx,y-.009,z+.11),(.022,.024,.024),mat=M['Charcoal'],bevel=.004))
    objs.append(tube(name+'_Crest',[(x-.028,y-.021,z+.252),(x,y-.023,z+.234),(x+.028,y-.021,z+.252)],.003,'Brass'))
    return objs
mecha('Mecha_A',-1.23,1.54,1.002,'Blue',0)
mecha('Mecha_B',-.57,1.55,1.002,'Terracotta',1)

# Two seated cloth dolls: shoes, skirt, hands, hair silhouette, hat and face.
def fumo(name,p,key,hair):
    x,y,z=p
    for dx in [-.037,.037]:
        uvball(name+'_Shoe',(x+dx,y-.045,z+.021),(.032,.045,.021),'Walnut',16,8)
    uvball(name+'_Skirt',(x,y,z+.075),(.09,.07,.055),key,20,10)
    uvball(name+'_Torso',(x,y,z+.13),(.055,.046,.064),key,16,8)
    uvball(name+'_Hair',(x,y+.006,z+.23),(.092,.072,.091),hair,20,10)
    uvball(name+'_Face',(x,y-.035,z+.226),(.071,.048,.063),'FurLight',20,10)
    for dx in [-.030,.030]:
        uvball(name+'_Eye',(x+dx,y-.081,z+.237),(.007,.003,.011),'Charcoal',12,6)
        uvball(name+'_Hand',(x+dx*2.3,y-.031,z+.115),(.023,.025,.025),'FurLight',12,6)
        uvball(name+'_HairLock',(x+dx*2.35,y-.022,z+.194),(.024,.04,.076),hair,16,8)
    tube(name+'_Mouth',[(x-.011,y-.084,z+.210),(x,y-.086,z+.208),(x+.011,y-.084,z+.210)],.0018,'Rose')
    hat=lathe(name+'_Hat',(x,y,z+.287),[(0,0),(.105,0),(.10,.013),(.065,.025),(.055,.06),(0,.065)],key,20)
    box(name+'_HatRibbon',(x,y-.058,z+.322),(.057,.015,.022),mat=M['Paper'],bevel=.003)
fumo('Fumo_A',(1.79,-1.43,.756),'Lilac','Walnut')
fumo('Fumo_B',(1.79,-1.03,.756),'Blue','Fur')
# Relocate the lava lamp along the same shelf so the dolls do not intersect it.
move(['LavaLamp_Base','INT_lava_lamp','LIGHT_lava_lamp'],(0,.36,0))

# One clustered Lego build and Game Boy beside the cat, not across the whole rug.
for i in range(6):
    x=.43+(i%3)*.085;y=-.91+(i//3)*.07;z=.079
    if i==5:z=.115;x=.515;y=-.91
    key=['Terracotta','Blue','Cream'][i%3]
    box('Lego_FloorBrick',(x,y,z),(.072,.052,.032),mat=M[key],bevel=.003)
    for dx in [-.018,.018]:cylinder('Lego_Stud',(x+dx,y,z+.016),(x+dx,y,z+.022),.009,M[key])
box('GameBoy_Body',(.40,-1.28,.079),(.15,.235,.034),-.18,M['Cream'],bevel=.012)
box('GameBoy_Bezel',(.40,-1.235,.098),(.12,.105,.006),-.18,M['Charcoal'],bevel=.006)
box('GameBoy_Screen',(.40,-1.235,.102),(.084,.068,.002),-.18,M['Sage'],bevel=.002)
box('GameBoy_Dpad',(.36,-1.335,.099),(.038,.010,.006),mat=M['Charcoal'],bevel=.002)
box('GameBoy_Dpad',(.36,-1.335,.100),(.010,.038,.006),mat=M['Charcoal'],bevel=.002)
for x in [.425,.457]:cylinder('GameBoy_Button',(x,-1.34,.098),(x,-1.34,.104),.008,M['Rose'])
box('GameBoy_Cartridge',(.40,-1.145,.091),(.09,.047,.019),-.18,M['Walnut'],bevel=.003)

# Bedside: clear upper surface, partly open drawer, photo edge and small frame.
move([o.name for o in scene.objects if o.name.startswith(('Floppy_','Nightstand_Water'))],(0,0,0))
# Move floppies to the existing back wall shelf, in place of one book stack footprint.
move([o.name for o in scene.objects if o.name.startswith(('Floppy_Box','Floppy_Disk'))],(.43,.15,1.43))
move(['Nightstand_Water'],(-.54,-.20,.09))
dr=bpy.data.objects['Nightstand_Drawer'];dr.location.y-=.045
box('Nightstand_PhotoEdge',(.42,1.03,.501),(.13,.08,.004),mat=M['Paper'],bevel=.001)
box('PhotoFrame_Back',(-.06,1.37,.82),(.115,.022,.14),mat=M['Walnut'],bevel=.007)
box('PhotoFrame_Print',(-.06,1.356,.82),(.09,.003,.112),mat=M['Rose'],bevel=.001)
uvball('PhotoFrame_Silhouette',(-.06,1.352,.83),(.025,.002,.037),'Terracotta',16,8)
# Clock fits on top, faces toward main camera, all seven segments retain runtime IDs.
clock=bpy.data.objects['Alarm_Body'];replace(clock,box('AlarmNew',(.39,1.24,.70),(.23,.105,.112),-.30,M['Charcoal'],bevel=.015))
back=bpy.data.objects['EMIT_screen_alarm'];mat(back,'Charcoal');back.location=(.39,1.18,.70);back.rotation_euler.z=-.30
digits=empty('EMIT_clock_digits',(.39,1.175,.70));digits.rotation_euler.z=-.30
segments={'a':(0,.034,.023,.005),'b':(.014,.018,.005,.024),'c':(.014,-.018,.005,.024),'d':(0,-.034,.023,.005),'e':(-.014,-.018,.005,.024),'f':(-.014,.018,.005,.024),'g':(0,0,.023,.005)}
patterns={'0':'abcdef','1':'bc','2':'abdeg','3':'abcdg','4':'bcfg','5':'acdfg','6':'acdefg','7':'abc','8':'abcdefg','9':'abcdfg'}
for i,num in enumerate('1720'):
    for seg,(x,z,w,h) in segments.items():
        o=box('EMIT_clock_segment_%d_%s'%(i,seg),(0,0,0),(w,.002,h),mat=M['GlowRed' if seg in patterns[num] else 'Charcoal'],bevel=.001)
        o.parent=digits;o.location=(-.072+i*.046+x,-.002,z);o['digit_index']=i;o['segment']=seg
for z in [-.012,.012]:
    o=box('EMIT_clock_colon',(0,0,0),(.005,.002,.005),mat=M['GlowRed'],bevel=.001);o.parent=digits;o.location=(-.002,-.002,z)
# Exposed heater tubes behind its guard.
heater=bpy.data.objects['SEASON_winter_heater']
for i in range(3):
    points=[]
    for k in range(33):points.append((.32+k*.008,.205,.16+i*.085+.009*math.sin(k*math.pi/2)))
    o=tube('EMIT_heater_coil' if i==0 else 'EMIT_heater_coil_%d'%i,points,.004,'GlowRed');parent(o,heater)
for n in ['StringLights_Bulb','Nightlight_Shade']:
    for o in scene.objects:
        if o.name.startswith(n):mat(o,'Cream')
# Two CDs beside the lamp, thin discs with center holes and rainbow vertex bands.
for i in range(2):
    old=bpy.data.objects['Cd_Loose_%02d'%i]
    p=(-1.39+i*.068,1.04-i*.027,.724+i*.004)
    replace(old,lathe('CDNew',p,[(.008,0),(.055,0),(.055,.0015),(.008,.0015),(.008,0)],'Brass',32))
    for key in ['Teal','Lilac','Rose']:old.data.materials.append(M[key])
    for f in old.data.polygons:f.material_index=(f.index//8)%4
# Only five power drops; keep a single cable gently crossing the foundation edge.
remove(bpy.data.objects['Cable_Device_05'])
scene['phase2_final_assets']=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);e.to_mesh_clear()
print('FINAL_ASSETS',len(scene.objects),tri)

"""User acceptance corrections: supported props, soft cables and seated plush silhouettes."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
assert not scene.get('phase2_user_feedback')
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
zone='phase2';clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard']
for f in ['densify_scene.py','phase2_refine.py','phase2_final_assets.py']:
    t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))

def clear_prefix(*prefixes):
    for o in list(scene.objects):
        if o.name.startswith(prefixes):remove(o)

def curved(name,points,r,key='Charcoal',steps=8):
    p=[Vector(x) for x in points];q=[p[0]]+p+[p[-1]];out=[]
    for i in range(1,len(q)-2):
        a,b,c,d=q[i-1:i+3]
        for j in range(steps):
            t=j/steps;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    out.append(p[-1]);return tube(name,out,r,key)

def place_group(objects,w,owner=None):
    for o in objects:
        o.matrix_world=w@o.matrix_world
        if owner:parent(o,owner)

def cassette(name,p,angle=0):
    pre=set(scene.objects)
    box(name+'_Shell',(0,0,.008),(.10,.064,.016),mat=M['Charcoal'],bevel=.004)
    box(name+'_Label',(0,.005,.0165),(.084,.042,.002),mat=M['Cream'],bevel=.001)
    box(name+'_Window',(0,.007,.018),(.062,.018,.001),mat=M['Walnut'],bevel=.001)
    for x in [-.023,.023]:
        cylinder(name+'_Reel',(x,.007,.018),(x,.007,.020),.007,M['Paper'])
        cylinder(name+'_Hub',(x,.007,.020),(x,.007,.0205),.003,M['Charcoal'])
    box(name+'_Stripe',(0,.020,.018),(.065,.004,.001),mat=M['Terracotta'],bevel=0)
    place_group(set(scene.objects)-pre,Matrix.Translation(Vector(p))@Matrix.Rotation(angle,4,'Z'))

# Two real drawers; the upper one opens 18 cm and reveals tapes and photographs.
clear_prefix('Nightstand_DrawerBottom','Nightstand_DrawerSide','Nightstand_PhotoEdge','Nightstand_Handle')
frame_replace('Nightstand_Main',[
    ((.42,1.32,.622),(.38,.45,.026)),((.42,1.32,.058),(.38,.45,.026)),
    ((.243,1.32,.34),(.026,.45,.59)),((.597,1.32,.34),(.026,.45,.59)),
    ((.42,1.532,.34),(.33,.026,.55)),((.42,1.32,.35),(.33,.42,.018))])
replace(bpy.data.objects['Nightstand_Drawer'],box('UpperDrawerNew',(.42,.910,.48),(.32,.024,.232),mat=M['Oak'],bevel=.005))
box('Nightstand_LowerDrawer',(.42,1.078,.212),(.32,.024,.25),mat=M['Oak'],bevel=.005)
for y,z in [(.893,.48),(1.061,.212)]:box('Nightstand_Handle',(.42,y,z),(.085,.024,.015),mat=M['Brass'],bevel=.004)
box('Nightstand_DrawerBottom',(.42,1.13,.370),(.295,.43,.016),mat=M['Walnut'],bevel=.003)
for x in [.28,.56]:box('Nightstand_DrawerSide',(x,1.13,.46),(.012,.42,.17),mat=M['Oak'],bevel=.003)
box('Nightstand_DrawerBack',(.42,1.335,.46),(.28,.012,.17),mat=M['Oak'],bevel=.003)
cassette('Drawer_TapeA',(.345,1.015,.382),-.12)
cassette('Drawer_TapeB',(.49,1.13,.383),.16)
for i in range(3):
    box('Drawer_Photo',(.47,1.00+i*.025,.383+i*.003),(.075,.074,.002),-.2+i*.12,M['Paper'],bevel=0)
    box('Drawer_PhotoPrint',(.47,1.00+i*.025,.385+i*.003),(.059,.051,.001),-.2+i*.12,M[['Rose','Sage','Terracotta'][i]],bevel=0)
cassette('Desk_TapeA',(-1.37,.75,.724),-.12)
cassette('Desk_TapeB',(-1.40,.67,.724),.13)

# Both phone cups face downward together; the grip arches above the cradle.
clear_prefix('Phone_Receiver','Phone_Cradle','Cable_Phone_Coil')
pre=set(scene.objects)
curved('Phone_Receiver',[(0,-.083,.028),(0,-.065,.043),(0,0,.047),(0,.065,.043),(0,.083,.028)],.020,steps=6)
for y in [-.083,.083]:
    uvball('Phone_ReceiverCup',(0,y,.028),(.037,.039,.025),'Charcoal',20,10)
    box('Phone_Cradle',(0,y,.001),(.044,.019,.018),mat=M['Teal'],bevel=.005)
w=Matrix.Translation(Vector((-1.69,.84,.813)))@Matrix.Rotation(-.2,4,'Z')
place_group(set(scene.objects)-pre,w)
pts=[w@Vector((-.02,-.108,.020)),Vector((-1.754,.731,.775))]
for j in range(81):
    a=j*math.tau/8;pts.append(Vector((-1.750+.006*math.cos(a),.742+j*.00125,.755+.006*math.sin(a))))
pts.append(Vector((-1.716,.868,.767)));tube('Cable_Phone_Coil',pts,.0021)

# First-generation controller: one continuous case with two rounded grips, no analogue sticks.
clear_prefix('Game_ControllerGrip','PS1_Dpad','PS1_FaceButton','Cable_GameController','PS1_TvCable')
outline=[(-.089,.043),(-.057,.057),(-.029,.034),(.029,.034),(.057,.057),(.089,.043),(.104,.014),(.089,-.036),(.068,-.072),(.043,-.074),(.021,-.012),(-.021,-.012),(-.043,-.074),(-.068,-.072),(-.089,-.036),(-.104,.014)]
vv=[];ff=[]
for scale,z in [(.93,-.017),(1,-.010),(1,.010),(.93,.017)]:vv.extend([(x*scale,y*scale,z) for x,y in outline])
N=len(outline)
for j in range(3):
    for i in range(N):a=j*N+i;b=j*N+(i+1)%N;ff.append((a,b,b+N,a+N))
ff += [tuple(reversed(range(N))),tuple(3*N+i for i in range(N))]
case=meshobj('ControllerNew',vv,ff,'Cream');be=case.modifiers.new('GripRoundover','BEVEL');be.width=.007;be.segments=2
old=bpy.data.objects['Game_Controller'];replace(old,case)
cw=Matrix.Translation(Vector((-1.13,-1.24,.047)))@Matrix.Rotation(-.20,4,'Z');old.matrix_world=cw
pre=set(scene.objects)
for p,s in [((-.058,0,.019),(.041,.012,.006)),((-.058,0,.020),(.012,.041,.006))]:box('PS1_Dpad',p,s,mat=M['Charcoal'],bevel=.002)
for i in range(4):
    a=i*math.tau/4;x=.058+.017*math.cos(a);y=.017*math.sin(a)
    cylinder('PS1_FaceButton',(x,y,.016),(x,y,.021),.007,M[['Rose','Blue','Sage','Lilac'][i]])
for x in [-.016,.016]:box('PS1_StartSelect',(x,-.001,.018),(.017,.005,.004),.2,M['Charcoal'],bevel=.001)
for x in [-.062,.062]:box('PS1_ShoulderButton',(x,.047,.013),(.046,.011,.015),mat=M['Charcoal'],bevel=.003)
place_group(set(scene.objects)-pre,cw,old)
R=Matrix.Rotation(math.radians(35),4,'Z');anchor=Vector((-1.72,-.79,0))
def tvp(p):return anchor+R.to_3x3()@Vector(p)
curved('Cable_GameController',[tvp((-.07,-.141,.105)),tvp((-.07,-.22,.080)),(-1.42,-1.18,.034),(-1.38,-1.37,.033),(-1.21,-1.39,.034),cw@Vector((0,.058,.044)),cw@Vector((0,.038,.004))],.0032,steps=8)
curved('PS1_TvCable',[tvp((0,.060,.107)),tvp((-.20,.13,.12)),tvp((-.25,.16,.32)),tvp((-.20,.18,.56)),tvp((-.13,.18,.67))],.003,steps=7)

# Game Boy: all details are authored in the body's own tilted frame, attached to its top.
clear_prefix('GameBoy_')
pre=set(scene.objects)
box('GameBoy_Body',(0,0,0),(.15,.235,.034),mat=M['Cream'],bevel=.012)
box('GameBoy_BatterySeam',(0,-.003,-.015),(.12,.18,.003),mat=M['Walnut'],bevel=.005)
box('GameBoy_Bezel',(0,.043,.018),(.121,.106,.006),mat=M['Charcoal'],bevel=.007)
box('GameBoy_Screen',(0,.043,.0215),(.084,.068,.002),mat=M['Sage'],bevel=.002)
for p,s in [((-.039,-.056,.018),(.038,.011,.006)),((-.039,-.056,.019),(.011,.038,.006))]:box('GameBoy_Dpad',p,s,mat=M['Charcoal'],bevel=.002)
for x,y in [(.028,-.067),(.054,-.055)]:cylinder('GameBoy_Button',(x,y,.015),(x,y,.021),.008,M['Rose'])
for x in [-.010,.017]:box('GameBoy_StartSelect',(x,-.090,.017),(.018,.004,.003),.22,M['Charcoal'],bevel=.001)
for i in range(4):box('GameBoy_SpeakerSlot',(.042+i*.006,-.094+i*.003,.0175),(.002,.014,.002),.25,M['Walnut'],bevel=0)
box('GameBoy_Cartridge',(0,.117,.003),(.091,.041,.020),mat=M['Walnut'],bevel=.003)
box('GameBoy_CartridgeLabel',(0,.125,.014),(.069,.022,.001),mat=M['Paper'],bevel=0)
place_group(set(scene.objects)-pre,Matrix.Translation(Vector((.40,-1.28,.079)))@Matrix.Rotation(-.18,4,'Z'))

# Fumo: large soft head, flat embroidered face, forward legs and a compressed seated body.
clear_prefix('Fumo_')
def plush(name,p,key,hair,angle,bow):
    pre=set(scene.objects)
    for dx in [-.038,.038]:
        uvball(name+'_Sock',(dx,-.051,.032),(.029,.044,.029),'Paper',16,8)
        uvball(name+'_Shoe',(dx,-.085,.025),(.032,.047,.025),'Walnut',16,8)
    lathe(name+'_Skirt',(0,0,.035),[(0,0),(.079,0),(.087,.021),(.065,.064),(.041,.075),(0,.075)],key,20)
    lathe(name+'_Hem',(0,0,.039),[(.079,0),(.084,.007),(.082,.013)],'Paper',20)
    uvball(name+'_Torso',(0,0,.12),(.052,.042,.055),key,16,8)
    uvball(name+'_Hair',(0,.01,.204),(.101,.071,.086),hair,20,10)
    uvball(name+'_Face',(0,-.024,.194),(.079,.048,.064),'FurLight',20,10)
    for dx in [-.034,.034]:
        uvball(name+'_Eye',(dx,-.068,.197),(.008,.003,.014),'Charcoal',12,6)
        uvball(name+'_EyeGlint',(dx-.002,-.071,.203),(.002,.001,.003),'Paper',8,4)
        uvball(name+'_Blush',(dx*1.42,-.064,.18),(.010,.0015,.004),'Rose',12,6)
        uvball(name+'_Hand',(dx*1.9,-.031,.095),(.021,.021,.027),'FurLight',12,6)
        uvball(name+'_Sleeve',(dx*1.8,-.017,.121),(.026,.026,.038),key,12,6)
        uvball(name+'_SideHair',(dx*2.2,-.002,.174),(.025,.036,.066),hair,16,8)
    curved(name+'_Mouth',[(-.010,-.072,.175),(0,-.073,.171),(.010,-.072,.175)],.0016,'Charcoal',4)
    for i in range(5):
        x=(i-2)*.025;z=.244+.008*math.cos(i)
        o=meshobj(name+'_Bang',[(x-.018,-.061,z+.025),(x+.018,-.061,z+.025),(x+.012,-.075,z-.02),(x-.010,-.074,z-.030),(x,-.041,z+.028)],[(0,1,2,3),(0,4,1),(1,4,2),(2,4,3),(3,4,0)],hair,True)
        be=o.modifiers.new('SoftHairEdge','BEVEL');be.width=.003;be.segments=2
    if bow:
        for dx in [-.044,.044]:
            uvball(name+'_Bow',(dx,0,.285),(.047,.024,.026),key,16,8)
            box(name+'_BowEdge',(dx,-.020,.286),(.063,.004,.010),mat=M['Paper'],bevel=.002)
        uvball(name+'_BowKnot',(0,-.01,.282),(.018,.023,.022),key,12,6)
    else:
        uvball(name+'_Beret',(.005,.006,.275),(.102,.075,.027),key,20,8)
        uvball(name+'_BeretButton',(.020,.010,.302),(.010,.010,.009),'Paper',12,6)
        box(name+'_Ribbon',(-.057,-.054,.277),(.042,.007,.017),mat=M['Paper'],bevel=.003)
    box(name+'_Collar',(0,-.044,.131),(.057,.007,.020),mat=M['Paper'],bevel=.003)
    place_group(set(scene.objects)-pre,Matrix.Translation(Vector(p))@Matrix.Rotation(math.radians(angle),4,'Z'))
plush('Fumo_A',(1.79,-1.46,.75),'Lilac','Walnut',-101,True)
plush('Fumo_B',(1.79,-1.105,.75),'Blue','Fur',-79,False)

# Seat the lava lamp wholly on the top shelf; its bottle remains attached to its base.
move([o.name for o in scene.objects if o.name.startswith(('LavaLamp_','INT_lava_lamp','LIGHT_lava_lamp'))],(0,-.07,-.02))
# Green cushion rests on the mattress beside the good white pillow, with a slight lean.
o=bpy.data.objects['Bed_Cushion'];b=bounds(o);center=Vector([(a+c)/2 for a,c in b])
w=Matrix.Translation(Vector((1.66,1.10,.708)))@Matrix.Rotation(.11,4,'X')@Matrix.Translation(-center);o.matrix_world=w@o.matrix_world
# Clear the rectangular pile over the slippers; keep two readable magazines beside the rug.
clear_prefix('Magazine_Floor_02','Magazine_Floor_03')
for i in range(2):
    o=bpy.data.objects['Magazine_Floor_%02d'%i];replace(o,box('MagazineNew',(.95+i*.02,-1.38+i*.035,.040+i*.014),(.25,.30,.012),-.12+i*.20,M[['Blue','Terracotta'][i]],bevel=.002))
    box('Magazine_PageBlock',(.95+i*.02,-1.38+i*.035,.040+i*.014),(.239,.289,.008),-.12+i*.20,M['Paper'],bevel=0)
    box('Magazine_CoverBand',(.95+i*.02,-1.43+i*.035,.047+i*.014),(.20,.032,.001),-.12+i*.20,M['Cream'],bevel=0)

# CRT knobs sit in a moulded control panel with real depth back into the casing.
clear_prefix('Crt_TuningKnob','Crt_SpeakerSlot')
sc=bpy.data.objects['EMIT_screen_crt'];w=sc.matrix_world.copy();pre=set(scene.objects)
box('Crt_ControlPanel',(.203,.018,0),(.073,.067,.261),mat=M['Cream'],bevel=.008)
for z in [.065,.022]:
    cylinder('Crt_TuningKnob',(.203,-.015,z),(.203,-.033,z),.019,M['Walnut'])
    box('Crt_KnobMarker',(.203,-.034,z+.009),(.002,.001,.009),mat=M['Cream'],bevel=0)
for i in range(5):box('Crt_SpeakerSlot',(.203,-.016,-.075+i*.014),(.042,.004,.003),mat=M['Charcoal'],bevel=.001)
place_group(set(scene.objects)-pre,w,bpy.data.objects['INT_tv_crt'])

# Smoothly join the orange masses; keep a painted muzzle and a few soft cheek tufts.
merge_names=['Cat_Body','Cat_Haunch','Cat_Head','Cat_Tail','Cat_TailTip'];verts=[];faces=[]
for n in merge_names:
    o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();st=len(verts)
    verts.extend(o.matrix_world@v.co for v in me.vertices);faces.extend(tuple(st+i for i in f.vertices) for f in me.polygons);ev.to_mesh_clear()
unified=meshobj('CatSoftNew',verts,faces,'Fur',True)
rem=unified.modifiers.new('ContinuousSilhouette','REMESH');rem.mode='VOXEL';rem.voxel_size=.007;rem.use_smooth_shade=True
sm=unified.modifiers.new('SoftPadding','SMOOTH');sm.factor=.65;sm.iterations=3
dec=unified.modifiers.new('RealtimeCat','DECIMATE');dec.ratio=.22
bpy.context.view_layer.update();ev=unified.evaluated_get(bpy.context.evaluated_depsgraph_get());me=bpy.data.meshes.new_from_object(ev)
unified.modifiers.clear();unified.data=me;mat(unified,'Fur')
replace(bpy.data.objects['Cat_Body'],unified)
for n in merge_names[1:]:remove(bpy.data.objects[n])
cat=bpy.data.objects['Cat_Body'];cat.data.materials.append(M['Terracotta'])
for f in cat.data.polygons:
    c=f.center
    if c.z>.30 and c.y>-1.27 and any(abs(c.y-y+.010*math.sin(c.x*25))<.009 for y in [-1.08,-1.15,-1.215]):f.material_index=1
    f.use_smooth=True
for o in list(scene.objects):
    if o.name.startswith('Cat_Cheek'):
        c=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
        for v in o.data.vertices:
            d=v.co-c;v.co=c+Vector((d.x*.9,d.y*.48-.020,d.z*.76+.003))
    if o.name.startswith('Cat_Whisker'):
        m=o.modifiers.new('SmallWhisker','DECIMATE');m.ratio=.45
for side in [-1,1]:
    x=-.155+side*.085
    for j in range(2):uvball('Cat_CheekTuft',(x+side*j*.010,-1.297,.244+j*.014),(.021,.022,.010),'FurLight',12,6)

# A small ribbed cactus beside the pale mecha, rooted in a tiny terracotta pot.
p=(-1.39,1.56,1.002)
lathe('Cactus_Pot',p,[(0,0),(.031,0),(.041,.055),(.044,.055),(.044,.064),(.037,.064),(.035,.014),(0,.014)],'Terracotta',20)
cylinder('Cactus_Soil',(p[0],p[1],1.057),(p[0],p[1],1.059),.036,M['Soil'])
o=uvball('Cactus_Body',(p[0],p[1],1.095),(.038,.038,.045),'Leaf',24,12)
for v in o.data.vertices:
    d=v.co-Vector((p[0],p[1],1.095));a=math.atan2(d.y,d.x);scale=1+.065*math.cos(8*a);v.co.x=p[0]+d.x*scale;v.co.y=p[1]+d.y*scale
for i in range(8):
    a=i*math.tau/8
    for z in [1.085,1.105]:uvball('Cactus_Areole',(p[0]+.038*math.cos(a),p[1]+.038*math.sin(a),z),(.002,.002,.002),'Cream',6,4)
uvball('Cactus_Flower',(p[0],p[1],1.142),(.009,.009,.006),'Rose',12,6)

# Reclaim triangles from distant trim and tiny repeated parts, never from the fan/white pillow.
for o in scene.objects:
    if o.type!='MESH':continue
    if o.name.startswith(('Drawer_','Desk_Tape','Fumo_','GameBoy_','Nightstand_','Cactus_')):
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
    if o.name.startswith(('Manual_','WallShelf_Cd_','LowBookshelf_Book_','Exterior_','Book_SpineBand','Corkboard_','Photo_','Tower_Vent','Keyboard_Key','Vhs_','Dvd_Case')):
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
        if not any(m.name=='DistantBudget' for m in o.modifiers):
            m=o.modifiers.new('DistantBudget','DECIMATE');m.ratio=.55
scene['phase2_user_feedback']=True
bpy.context.view_layer.update()
print('USER_FEEDBACK_GEOMETRY_DONE')

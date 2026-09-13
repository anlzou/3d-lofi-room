"""Phase 2 geometry and material assignment. Run once on Phase 1.5 source.
Node materials are authored with validated MCP patches, never edited here.
"""
import bpy, math, random, ast, json
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.get('phase15_refined') and not scene.get('phase2_refined')
random.seed(20906)
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={n:bpy.data.materials['MAT_P2_'+n] for n in ['Cream','Paper','Oak','Walnut','Sage','Leaf','LeafLight','Terracotta','Charcoal','Teal','Brass','Rose','Blue','Lilac','Fur','FurLight','Soil']}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
# Reuse audited geometry primitives without replaying the Phase 1.5 scene mutations.
tree=ast.parse((ROOT/'blender/scripts/densify_scene.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'primitives','exec'))
def mat(o,key):
    o.data.materials.clear();o.data.materials.append(M[key]);return o
def remove(o):
    bpy.context.view_layer.objects.active=bpy.data.objects['Desk_Main']
    o.select_set(False);bpy.data.objects.remove(o,do_unlink=True)
def replace(old,new):
    # Preserve the original object's semantic identity, parent, and child transforms.
    bpy.context.view_layer.update()
    children=[(c,c.matrix_world.copy()) for c in old.children]
    old.data=new.data;old.modifiers.clear();old.matrix_world=new.matrix_world.copy()
    for mod in new.modifiers:
        if mod.type=='BEVEL':
            m=old.modifiers.new(mod.name,'BEVEL');m.width=mod.width;m.segments=mod.segments
        if mod.type=='SOLIDIFY':
            m=old.modifiers.new(mod.name,'SOLIDIFY');m.thickness=mod.thickness
    for c,w in children:c.matrix_world=w
    remove(new);return old
def meshobj(name,verts,faces,key='Cream',smooth=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);COL['PROPS'].objects.link(o);mat(o,key)
    for p in me.polygons:p.use_smooth=smooth
    o['phase']=2;return o
def uvball(name,p,size,key='Cream',segs=24,rings=12):
    verts=[];faces=[]
    for j in range(rings+1):
        t=math.pi*j/rings
        for i in range(segs):
            a=math.tau*i/segs
            verts.append((p[0]+size[0]*math.sin(t)*math.cos(a),p[1]+size[1]*math.sin(t)*math.sin(a),p[2]+size[2]*math.cos(t)))
    for j in range(rings):
        for i in range(segs):
            k=j*segs+i;l=j*segs+(i+1)%segs
            faces.append((k,l,l+segs,k+segs))
    return meshobj(name,verts,faces,key,True)
def lathe(name,p,profile,key='Cream',segments=32):
    verts=[];faces=[]
    for r,z in profile:
        verts.extend([(p[0]+r*math.cos(i*math.tau/segments),p[1]+r*math.sin(i*math.tau/segments),p[2]+z) for i in range(segments)])
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
    return meshobj(name,verts,faces,key,True)
def ring(name,p,r,t,key='Cream',axis='Z'):
    points=[]
    for i in range(33):
        a=i*math.tau/32
        points.append((p[0]+r*math.cos(a),p[1]+(r*math.sin(a) if axis=='Z' else 0),p[2]+(r*math.sin(a) if axis=='Y' else 0)))
    return cable(name,points,t,M[key])
def label(name,text,p,size,key='Charcoal',rot=(0,0,0)):
    cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size;cu.extrude=0;cu.resolution_u=2
    o=bpy.data.objects.new(name,cu);COL['PROPS'].objects.link(o);o.location=p;o.rotation_euler=rot
    bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    n=bpy.data.objects.new(name+'_Mesh',me);COL['PROPS'].objects.link(n);n.matrix_world=o.matrix_world.copy();mat(n,key);remove(o);n.name=name;return n
def move(names,delta):
    for n in names:
        o=bpy.data.objects.get(n)
        if o:
            w=o.matrix_world.copy();w.translation+=Vector(delta);o.matrix_world=w
def bounds(o):
    bpy.context.view_layer.update();ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [(min(v[i] for v in ps),max(v[i] for v in ps)) for i in range(3)]

# Assign a restrained palette to every existing mesh.
for o in list(scene.objects):
    if o.type!='MESH' or o.name.startswith('EMIT_screen_'):continue
    n=o.name;key='Cream'
    if n.startswith(('Wall_','Ceiling_Shade','Bed_Mattress','Bed_Pillow','Nightlight_Shade','Window_Sill')):key='Paper'
    if n.startswith(('Floor_','Desk_','Window_Frame','Window_Mullion','Shelf_','WallShelf_Long','LowBookshelf_Main','Nightstand_Main','TvStand_','Bed_Frame','Bed_Headboard','Skirting_','Chair_Leg')):key='Oak'
    if n.startswith(('Room_','Tree_Trunk','Tree_Branch','Exterior_Utility','Box_Foreground','UnderBed_','Corkboard_Main')):key='Walnut'
    if n.startswith(('Bed_Blanket','Bed_Cushion','Chair_','Rug_','Cat_Bed')):key='Sage'
    if n.startswith(('Cable_','Headphones_','Speaker_','Walkman_','Vhs_','Dvd_','Game_','Tv_Remote','Computer_','Mac_Drive','Mac_Screen','Crt_Screen','Crt_Bezel','Floppy_Disk','PowerStrip_','StringLights_Wire','Exterior_Window','Exterior_Powerline','Heater_','SEASON_winter_heater')):key='Charcoal'
    if n.startswith(('Lamp_','Fan_','SEASON_summer_fan','Keyboard_Base','Mouse_','INT_phone','Phone_','Windowsill_Figurine')):key='Teal'
    if n.startswith(('Plant_','Spring_Flowers')):key='Leaf' if ('Leaf' in n or 'Stem' in n) else 'Terracotta'
    if n.startswith(('Tree_Canopy','Mug_','Noodles_','SEASON_autumn','Poster_00')):key='Terracotta'
    if n.startswith(('Windchime_Tube','Crt_Antenna','Kettle_','Skateboard_Axle')):key='Brass'
    if n.startswith(('Exterior_House','Globe_Sphere','Poster_02')):key='Blue'
    if n.startswith(('Poster_01','SEASON_winter_scarf','Slipper_')):key='Lilac'
    if n.startswith(('Paper_','Sticky_','Notebook_','Comic_','Vhs_HandLabel','Corkboard_Photo','Poster_Caption','Poster_Moon')):key='Paper'
    if 'Book' in n or n.startswith(('WallShelf_Cd','Manual_','Dvd_Case','Box_Record','Magazine_')):key=random.choice(['Terracotta','Blue','Sage','Cream','Lilac'])
    mat(o,key)
    for m in o.modifiers:
        if m.type=='BEVEL':m.segments=2

# Plant geometry: all pots now physically supported; broad curved leaves with midribs.
def plant(prefix,p,r,h,oldnames):
    for n in oldnames:
        if n in bpy.data.objects:remove(bpy.data.objects[n])
    objs=[]
    objs.append(lathe(prefix+'_Pot',p,[(0,0),(r*.73,0),(r,.035),(r*1.05,h-.025),(r*1.10,h-.018),(r*1.10,h),(r*.94,h),(r*.88,h-.045),(0,h-.045)],'Terracotta'))
    objs.append(cylinder(prefix+'_Soil',(p[0],p[1],p[2]+h-.045),(p[0],p[1],p[2]+h-.04),r*.88,M['Soil']))
    for i in range(7):
        a=i*2.399;length=r*(1.9+random.random()*.65);width=length*.31
        base=Vector((p[0]+r*.13*math.cos(a),p[1]+r*.13*math.sin(a),p[2]+h-.035))
        start=base+Vector((r*.50*math.cos(a),r*.50*math.sin(a),r*(1.0+i*.14)))
        end=start+Vector((length*math.cos(a),length*math.sin(a),r*(.55 if i%2 else -.1)))
        objs.append(cable(prefix+'_Stem_%02d'%i,[base,base.lerp(start,.65)+Vector((0,0,r*.2)),start],r*.023,M['Leaf']))
        verts=[];faces=[];ridge=[]
        side=Vector((-math.sin(a),math.cos(a),0))
        for j in range(9):
            t=j/8;center=start.lerp(end,t)+Vector((0,0,math.sin(t*math.pi)*r*.36));ridge.append(center)
            w=math.sin(math.pi*t)**.75*width
            for k in [-1,0,1]:verts.append(center+side*w*k-Vector((0,0,abs(k)*w*.30)))
        for j in range(8):
            for k in range(2):q=j*3+k;faces.append((q,q+1,q+4,q+3))
        leaf=meshobj(prefix+'_Leaf_%02d'%i,verts,faces,'LeafLight' if i%3==0 else 'Leaf',True)
        sol=leaf.modifiers.new('LeafThickness','SOLIDIFY');sol.thickness=.0015;objs.append(leaf)
        objs.append(cable(prefix+'_Midrib_%02d'%i,ridge,r*.012,M['LeafLight']))
    return objs
plant('Plant_Foreground',(-1.78,-1.48,.028),.145,.27,[o.name for o in scene.objects if o.name.startswith('Plant_Foreground')])
plant('Plant_Windowsill',(-1.58,1.58,1.001),.058,.115,[o.name for o in scene.objects if o.name.startswith('Plant_Windowsill')])
plant('Plant_Shelf',(1.11,1.59,2.068),.076,.17,[o.name for o in scene.objects if o.name in ['Plant_Pot'] or o.name.startswith(('Plant_Stem','Plant_Leaf'))])
spring=plant('Spring_Flowers',(-.32,1.60,1.001),.055,.11,[o.name for o in scene.objects if o.name.startswith('Spring_Flowers')])
for o in spring:parent(o,bpy.data.objects['SEASON_spring_flowerpot'])

# Sleeping tabby: soft body silhouette, cheeks, muzzle, tucked paws and curled tail.
catroot=bpy.data.objects['INT_cat']
for o in list(catroot.children):remove(o)
catparts=[]
catparts.append(uvball('Cat_Body',(-.01,-1.16,.235),(.235,.16,.155),'Fur'))
catparts.append(uvball('Cat_Haunch',(.14,-1.12,.205),(.115,.135,.11),'Fur'))
catparts.append(uvball('Cat_Head',(-.145,-1.26,.287),(.108,.087,.093),'Fur'))
for x in [-.197,-.115]:
    catparts.append(uvball('Cat_Cheek',(x,-1.315,.25),(.048,.048,.038),'FurLight',16,8))
    # Rounded triangular ears, facing the main camera.
    vv=[(x-.033,-1.27,.34),(x+.033,-1.27,.34),(x-.006,-1.265,.419),(x,-1.225,.346)]
    ear=meshobj('Cat_Ear',vv,[(0,1,2),(0,3,1),(1,3,2),(2,3,0)],'Fur')
    be=ear.modifiers.new('EarSoftness','BEVEL');be.width=.006;be.segments=2;catparts.append(ear)
    catparts.append(meshobj('Cat_InnerEar',[(x-.022,-1.277,.35),(x+.02,-1.277,.35),(x-.005,-1.273,.399)],[(0,1,2)],'Rose'))
for x in [-.18,-.085]:catparts.append(uvball('Cat_Paw',(x,-1.305,.175),(.052,.066,.035),'FurLight',16,8))
catparts.append(uvball('Cat_Nose',(-.155,-1.362,.26),(.014,.009,.009),'Rose',12,6))
for x in [-.195,-.12]:
    catparts.append(cable('Cat_ClosedEye',[(x-.018,-1.337,.29),(x,-1.342,.281),(x+.017,-1.337,.29)],.003,M['Charcoal']))
for dx in [-1,1]:
    catparts.append(cable('Cat_Mouth',[(-.155,-1.362,.252),(-.155+dx*.009,-1.358,.242),(-.155+dx*.019,-1.351,.245)],.0017,M['Charcoal']))
    for j in range(2):catparts.append(cable('Cat_Whisker',[(-.155+dx*.024,-1.352,.25+j*.009),(-.155+dx*.084,-1.369,.247+j*.019)],.0013,M['FurLight']))
catparts.append(cable('Cat_Tail',[(.17,-1.08,.21),(.24,-1.18,.16),(.18,-1.34,.145),(.045,-1.385,.155),(-.035,-1.36,.177)],.037,M['Fur']))
for i in range(3):
    y=-1.085-i*.048
    catparts.append(cable('Cat_BackStripe',[(-.10,y,.363),(-.03,y-.006,.388),(.055,y-.005,.375)],.012,M['Walnut']))
for o in catparts:parent(o,catroot)
replace(bpy.data.objects['Cat_Bed'],lathe('CatBedNew',(.04,-1.17,.029),[(0,0),(.27,0),(.30,.03),(.31,.08),(.29,.115),(.26,.11),(.24,.045),(0,.045)],'Sage'))
ring('CatBed_Stitch',(.04,-1.17,.122),.274,.003,'Paper')

# Work surface zoning. Right-hand writing/audio area gets clear space.
move(['Notebook_Main'],(.03,-.06,-.005))
move(['Mug_Main'],(.18,.25,0))
move(['Noodles_Bowl','Noodles_ChopstickA','Noodles_ChopstickB'],(.04,.28,0))
for i in range(4):
    o=bpy.data.objects['Sticky_Desk_%02d'%i];o.location=(-.45+i*.015,.92+i*.008,.724+i*.003);o.rotation_euler=(0,0,-.17+i*.08)
move(['Cd_Loose_00'],(.24,.12,0));move(['Cd_Loose_01'],(.02,.15,0))
move(['Walkman_Body'],(-.04,.23,0))
for n in ['Headphones_Band','Headphones_Earcup','Headphones_Earcup.001','Cable_Headphone','Cable_Phone_Coil','Phone_Receiver']:
    if n in bpy.data.objects:remove(bpy.data.objects[n])
# Compact phone receiver and dial buttons. The coil now connects both ends.
phone=bpy.data.objects['INT_phone'];mat(phone,'Teal')
recv=box('Phone_Receiver',(-1.69,.84,.817),(.065,.22,.035),-.2,M['Charcoal'],bevel=.013)
for y in [.755,.925]:uvball('Phone_ReceiverCap',(-1.69,y,.813),(.046,.043,.026),'Charcoal',16,8)
for j in range(4):
    for i in range(3):box('Phone_Key',(-1.605+i*.025,.775+j*.032,.799),(.018,.025,.009),-.2,M['Paper'],bevel=.003)
pts=[(-1.68,.74,.814),(-1.74,.71,.76)]
pts +=[(-1.73+.010*math.cos(i*.8),.715+i*.0015,.741+.010*math.sin(i*.8)) for i in range(60)]
pts +=[(-1.73,.82,.744),(-1.715,.86,.768)]
cable('Cable_Phone_Coil',pts,.0026,M['Charcoal'])
# Full-sized headphones lying on the clear front-right corner, connected to the Walkman.
cx,cy=-.17,.78
cable('Headphones_Band',[(cx-.07,cy,.758),(cx-.085,cy+.06,.765),(cx,cy+.105,.766),(cx+.085,cy+.06,.765),(cx+.07,cy,.758)],.008,M['Charcoal'])
for dx in [-.068,.068]:
    uvball('Headphones_Earcup',(cx+dx,cy,.749),(.039,.044,.025),'Charcoal',20,10)
    uvball('Headphones_Cushion',(cx+dx,cy,.769),(.028,.032,.010),'Walnut',16,8)
    box('Headphones_Hinge',(cx+dx,cy+.029,.763),(.016,.025,.014),mat=M['Brass'],bevel=.003)
cable('Cable_Headphone',[(cx+.07,cy-.02,.745),(-.07,.70,.728),(-.035,.79,.728),(-.12,.87,.737)],.0023,M['Charcoal'])
box('Walkman_Window',(-.17,.90,.777),(.073,.083,.004),.2,M['Blue'],bevel=.006)
for x in [-.19,-.15]:cylinder('Walkman_Reel',(x,.90,.78),(x,.90,.783),.012,M['Paper'])
label('Walkman_Label','STEREO',(-.205,.954,.78),.011,'Paper')

# Hollow ceramic vessels instead of closed cylinders.
mug=bpy.data.objects['Mug_Main'];p=mug.matrix_world.translation.copy();p.z=.72
replace(mug,lathe('MugNew',p,[(0,0),(.037,0),(.046,.009),(.046,.11),(.038,.11),(.037,.018),(0,.018)],'Terracotta'))
ring('Mug_Handle',(p.x+.049,p.y,.781),.033,.008,'Terracotta','Y')
cylinder('Mug_Coffee',(p.x,p.y,.808),(p.x,p.y,.809),.037,M['Soil'])
bpy.data.objects['SOCKET_steam_mug'].location=(p.x,p.y,.835)
bowl=bpy.data.objects['Noodles_Bowl'];p=bowl.matrix_world.translation.copy();p.z=.72
replace(bowl,lathe('BowlNew',p,[(0,0),(.042,0),(.078,.08),(.079,.09),(.071,.09),(.038,.013),(0,.013)],'Cream'))
cylinder('Noodles_Broth',(p.x,p.y,.782),(p.x,p.y,.783),.065,M['Terracotta'])
for i in range(5):cable('Noodles_Strand',[(p.x-.045,p.y-.024+i*.01,.787),(p.x-.012,p.y-.014+i*.01,.789),(p.x+.037,p.y-.024+i*.01,.787)],.002,M['Paper'])
label('Notebook_Title','NIGHT NOTES',(-.42,1.22,.777),.018,'Charcoal')
for i in range(6):box('Notebook_Rule',(-.33,1.10+i*.014,.777),(.15,.001,.001),mat=M['Blue'],bevel=0)

# Hero device seams, vents, speaker grille, labels and mouse split.
macroot=bpy.data.objects['INT_mac']
for i in range(8):
    o=box('Mac_Vent',(-1.145,1.11+i*.015,.875),(.002,.008,.07),mat=M['Charcoal'],bevel=.001);parent(o,macroot)
o=label('Mac_Badge','Macintosh',(-1.105,1.025,.801),.012,'Walnut',(math.pi/2,0,0));parent(o,macroot)
for x in [-1.12,-.905]:
    o=uvball('Mac_Screw',(x,1.025,.787),(.004,.002,.004),'Brass',12,6);parent(o,macroot)
for i in range(2):
    x=[-1.38,-.65][i]
    for z,r in [(.88,.038),(.78,.018)]:
        ring('Speaker_Rim',(x,1.238,z),r,.003,'Walnut','Y')
        uvball('Speaker_Dome',(x,1.234,z),(r*.48,.006,r*.48),'Charcoal',16,8)
for i in range(9):box('Tower_Vent',(-.18,.968,.22+i*.016),(.15,.003,.005),mat=M['Walnut'],bevel=0)
uvball('Tower_Power',(-.18,.964,.39),(.009,.003,.009),'Teal',12,6)
cable('Mouse_Split',[(-.63,.70,.751),(-.63,.74,.771),(-.63,.775,.769)],.0015,M['Charcoal'])
cable('Mouse_Wire',[(-.63,.817,.745),(-.53,.91,.73),(-.60,1.04,.73),(-.78,1.32,.73)],.0025,M['Charcoal'])

# Furniture shells: replace solid cabinet blocks that intersected their stored devices.
def frame_replace(name,pieces,key='Oak'):
    parts=[box('FramePart',p,s,mat=M[key],bevel=.008) for p,s in pieces]
    verts=[];faces=[]
    for o in parts:
        bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();start=len(verts)
        verts.extend([o.matrix_world@v.co for v in me.vertices]);faces.extend([tuple(start+i for i in f.vertices) for f in me.polygons]);ev.to_mesh_clear();remove(o)
    replace(bpy.data.objects[name],meshobj(name+'_New',verts,faces,key))
frame_replace('Bed_Frame',[((1.31,.54,.40),(1.32,2.13,.10)),((.69,.54,.29),(.08,2.13,.22)),((1.93,.54,.29),(.08,2.13,.22)),((1.31,1.56,.24),(1.26,.08,.35))])
# Existing TV is rotated. Build cabinet panels in its exact local frame.
cab=bpy.data.objects['TvStand_Main'];world=cab.matrix_world.copy();dim=Vector(cab.dimensions)
verts=[];faces=[]
for p,size in [((0,0,dim.z/2-.022),(dim.x,dim.y,.044)),((0,0,-dim.z/2+.022),(dim.x,dim.y,.044)),((-dim.x/2+.022,0,0),(.044,dim.y,dim.z)),((dim.x/2-.022,0,0),(.044,dim.y,dim.z)),((0,dim.y/2-.012,0),(dim.x,.024,dim.z))]:
    o=box('CabPart',p,size,mat=M['Oak'],bevel=.008);bpy.context.view_layer.update();ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();st=len(verts)
    verts.extend([world@(o.matrix_world@v.co) for v in me.vertices]);faces.extend([tuple(st+i for i in f.vertices) for f in me.polygons]);ev.to_mesh_clear();remove(o)
replace(cab,meshobj('TvCabinetNew',verts,faces,'Oak'))
# The old inset represented a solid door; make it a thin shelf below the recorder.
shelf=bpy.data.objects['TvStand_Shelf'];shelf.scale.z=.10;mat(shelf,'Walnut')

# Correct duvet contact: top sits on mattress, edges fall outside its footprint.
blanket=bpy.data.objects['Bed_Blanket'];verts=[];faces=[];nx,ny=30,24
for j in range(ny+1):
    t=j/ny;y=-.54+t*1.36
    for i in range(nx+1):
        u=i/nx;x=.625+u*1.37
        edge=max(0,(.72-x)/.095,(x-1.90)/.095)
        z=.692+.021*math.sin(u*15+t*4)+.01*math.sin(t*18-u*3)-.13*edge
        if y<-.47:z-=.10*(-.47-y)/.07
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):q=j*(nx+1)+i;faces.append((q,q+1,q+nx+2,q+nx+1))
new=meshobj('DuvetNew',verts,faces,'Sage',True);sol=new.modifiers.new('FabricThickness','SOLIDIFY');sol.thickness=.012;replace(blanket,new)
# Comic rests on the duvet rather than hovering above it.
move(['Comic_OpenLeft','Comic_OpenRight','Comic_Panel_00','Comic_Panel_01','Comic_Panel_02'],(0,0,-.065))
for o in list(scene.objects):
    if o.name.startswith('Comic_Panel'):mat(o,'Charcoal')
for x in [.75,1.87]:cable('Duvet_Seam',[(x,-.43,.71),(x,.0,.71),(x,.4,.71),(x,.79,.70)],.002,M['Paper'])
# Throw lies on the backrest front surface and folds over the top, no embedded slab.
throw=bpy.data.objects['SEASON_autumn_blanket']
vv=[];ff=[]
path=[(-.13,.71),(-.135,.88),(-.13,1.04),(-.11,1.085),(-.04,1.085),(-.018,1.05),(-.015,.92)]
for j,(y,z) in enumerate(path):
    for i in range(13):u=i/12;vv.append((-.92+(u-.5)*.39,y+.012*math.sin(u*16),z+.009*math.sin(u*12+j)))
for j in range(len(path)-1):
    for i in range(12):q=j*13+i;ff.append((q,q+1,q+14,q+13))
new=meshobj('ThrowNew',vv,ff,'Terracotta',True);sol=new.modifiers.new('FabricThickness','SOLIDIFY');sol.thickness=.006;replace(throw,new)
for i in range(12):cable('Throw_Fringe',[(-1.10+i*.032,-.13,.72),(-1.10+i*.032,-.13,.67)],.002,M['Paper'])

# Bedside clock was floating above its nightstand; put its bottom on the top.
move(['Alarm_Body','EMIT_screen_alarm'],(0,0,-.015))
box('Nightstand_Handle',(.42,1.064,.40),(.09,.024,.018),mat=M['Brass'],bevel=.005)
# Fan: replace the solid shield with actual open wire cage.
guard=bpy.data.objects['Fan_Guard'];remove(guard)
head=bpy.data.objects['ANIM_fan_head']
for r in [.07,.12,.18]:parent(ring('Fan_Cage',(.19,-.43,.53),r,.003,'Cream','Y'),head)
for i in range(12):
    a=i*math.tau/12
    parent(cable('Fan_Spoke',[(.19,-.442,.53),(.19+.18*math.cos(a),-.43,.53+.18*math.sin(a))],.0024,M['Cream']),head)
parent(uvball('Fan_Hub',(.19,-.448,.53),(.029,.017,.029),'Brass',16,8),head)

# Printed paper details, bindings, shelf supports and rug border.
for i in range(3):
    p=bpy.data.objects['Poster_%02d'%i].location
    label('Poster_Title_%d'%i,['SLOW RADIO','MOON / 99','SUNDAY CLUB'][i],(1.985,p.y-.18,p.z-.20),.036,'Paper',(math.pi/2,0,-math.pi/2))
for o in list(scene.objects):
    if o.name.startswith(('Shelf_Book','WallShelf_Cd')):
        b=bounds(o);x=(b[0][0]+b[0][1])/2;y=b[1][0]-.001;z=b[2][0]+.055
        if o.name.startswith('Shelf_Book'):box('Book_SpineBand',(x,y,z),(.045,.002,.012),mat=M['Paper'],bevel=0)
for y in [-.9,.3,1.25]:
    cable('Shelf_Bracket',[(2.015,y,2.10),(1.73,y,2.26),(2.015,y,2.26)],.013,M['Brass'])
for x in [-.69,.93]:cable('Rug_Border',[(x,-1.20,.058),(x,-.60,.058),(x,.15,.058)],.006,M['Cream'])
for i in range(20):
    x=-.68+i*.084
    cable('Rug_Tassel',[(x,-1.29,.054),(x-.007,-1.35,.045)],.003,M['Cream'])
# Main objects keep stable names; mark added mesh assets for the manifest.
for o in scene.objects:
    if o.type=='MESH':o['phase']=2
scene['phase2_refined']=True
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in scene.objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);e.to_mesh_clear()
print('PHASE2_GEOMETRY',len(scene.objects),'objects',tri,'triangles')
# Final budget gate follows the cable optimization in phase2_finish.py.

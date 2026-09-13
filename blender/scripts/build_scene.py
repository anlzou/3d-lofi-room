"""Phase 1 graybox. Run in an empty Blender scene through MCP.
CLI: blender --background --python blender/scripts/build_scene.py -- --save-export
"""
import bpy
import math
import random
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
if '--save-export' in sys.argv:
    bpy.ops.wm.read_homefile(use_empty=True)
if len(bpy.data.objects):
    raise RuntimeError('Build requires an empty scene; preserve existing work before resetting.')

random.seed(1999)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
collections = {}
for name in ['ROOM_SHELL', 'FURNITURE', 'PROPS', 'LIGHTS', 'CAMERAS']:
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    collections[name] = c

# Default Principled is deliberately neutral: this phase judges geometry and light.
clay = bpy.data.materials.new('MAT_Graybox_Clay')
clay.use_nodes = True

def place(obj, name, collection, mat=True):
    obj.name = name
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collections[collection].objects.link(obj)
    if mat:
        obj.data.materials.append(clay)
    return obj

def cube(name, pos, size, collection='PROPS', bevel=0.015):
    before = set(bpy.data.objects)
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = (set(bpy.data.objects) - before).pop()
    obj.scale = size
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    place(obj, name, collection)
    if bevel:
        mod = obj.modifiers.new('SoftEdges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    return obj

def sphere(name, pos, size, collection='PROPS', sub=2):
    before = set(bpy.data.objects)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=pos)
    obj = (set(bpy.data.objects) - before).pop()
    obj.scale = size
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return place(obj, name, collection)

def rod(name, a, b, radius, collection='PROPS', top=None):
    mid = (Vector(a) + Vector(b)) / 2
    before = set(bpy.data.objects)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=radius, radius2=radius if top is None else top,
                                  depth=(Vector(b)-Vector(a)).length, location=mid)
    obj = (set(bpy.data.objects) - before).pop()
    obj.rotation_euler = (Vector(b)-Vector(a)).to_track_quat('Z', 'Y').to_euler()
    return place(obj, name, collection)

# Open-front room. A real hole in the rear wall gives natural window shadows.
cube('Room_Foundation', (0, 0, -.14), (4.3, 3.7, .25), 'ROOM_SHELL', .04)
for i in range(18):
    cube('Floor_Plank_%02d' % i, (-2.0+i*.235, 0, .005), (.229, 3.6, .045), 'ROOM_SHELL', .004)
cube('Wall_Right', (2.1, 0, 1.4), (.13, 3.6, 2.8), 'ROOM_SHELL')
cube('Wall_BackLower', (0, 1.8, .49), (4.2, .13, .98), 'ROOM_SHELL')
cube('Wall_BackUpper', (0, 1.8, 2.62), (4.2, .13, .36), 'ROOM_SHELL')
cube('Wall_BackLeft', (-1.94, 1.8, 1.71), (.32, .13, 1.46), 'ROOM_SHELL')
cube('Wall_BackRight', (1.04, 1.8, 1.71), (2.12, .13, 1.46), 'ROOM_SHELL')
for x in [-1.77, -.03]:
    cube('Window_FrameSide', (x, 1.70, 1.71), (.065, .17, 1.5), 'ROOM_SHELL')
for z in [.98, 2.44]:
    cube('Window_FrameRail', (-.9, 1.70, z), (1.8, .17, .07), 'ROOM_SHELL')
cube('Window_Mullion', (-.9, 1.70, 1.71), (.04, .08, 1.44), 'ROOM_SHELL', .005)
cube('Window_Sill', (-.9, 1.61, .96), (1.94, .42, .08), 'ROOM_SHELL')
for i in range(5):
    slat = cube('Window_Blind_%02d' % i, (-.9, 1.59, 2.35-i*.09), (1.73, .14, .025), 'ROOM_SHELL', .005)
    slat.rotation_euler.x = -.25
cube('Skirting_Back', (0, 1.70, .09), (4.15, .055, .13), 'ROOM_SHELL', .006)
cube('Skirting_Right', (2.0, 0, .09), (.055, 3.5, .13), 'ROOM_SHELL', .006)

# Desk and recognizable silhouette props, deliberately no fine texturing yet.
cube('Desk_Main', (-.9, 1.03, .75), (1.92, .78, .08), 'FURNITURE', .025)
for x in [-1.69, -.11]:
    for y in [.74, 1.29]:
        cube('Desk_Leg', (x, y, .365), (.07, .07, .73), 'FURNITURE')
cube('Mac_Foot', (-1.01, 1.12, .82), (.40, .31, .065))
cube('Mac_Body', (-1.01, 1.17, 1.06), (.39, .34, .45), bevel=.035)
cube('Mac_ScreenInset', (-1.01, .993, 1.10), (.31, .015, .24), bevel=.02)
cube('Mac_Screen', (-1.01, .981, 1.10), (.275, .012, .202), bevel=.018)
cube('Mac_DriveSlot', (-1.0, .991, .91), (.15, .015, .017), bevel=.003)
cube('Keyboard_Base', (-1.0, .76, .811), (.47, .20, .035), bevel=.012)
for row in range(3):
    for col in range(10):
        cube('Keyboard_Key_%02d_%02d' % (row,col), (-1.20+col*.044, .70+row*.05, .835), (.036, .039, .012), bevel=.003)
sphere('Mouse_Main', (-.63, .76, .815), (.047, .068, .025))
rod('Lamp_Base', (-1.62,1.19,.79), (-1.62,1.19,.815), .10)
rod('Lamp_LowerArm', (-1.62,1.19,.82), (-1.64,1.19,1.12), .015)
rod('Lamp_UpperArm', (-1.64,1.19,1.12), (-1.47,1.19,1.35), .014)
rod('Lamp_Shade', (-1.45,1.19,1.26), (-1.45,1.19,1.40), .105, top=.045)
rod('Mug_Main', (-.34,.96,.79), (-.34,.96,.90), .045)
cube('Notebook_Main', (-.36,1.22,.81), (.23,.27,.04), bevel=.006)

cube('Chair_Seat', (-.92,.24,.45), (.46,.44,.09), 'FURNITURE', .045)
cube('Chair_Back', (-.92,.02,.76), (.46,.07,.53), 'FURNITURE', .045)
for x in [-1.09,-.75]:
    for y in [.07,.39]:
        rod('Chair_Leg', (x,y,.03), (x,y,.42), .026, 'FURNITURE')

# TV cabinet lies at left foreground; front faces viewer, clear of chair.
cube('TvStand_Main', (-1.45,-.92,.32), (1.05,.55,.58), 'FURNITURE', .03)
cube('TvStand_Shelf', (-1.45,-1.205,.29), (.90,.025,.23), 'FURNITURE', .008)
cube('Crt_Body', (-1.53,-.89,.89), (.65,.46,.52), bevel=.055)
cube('Crt_Bezel', (-1.55,-1.135,.91), (.52,.035,.38), bevel=.04)
cube('Crt_Screen', (-1.55,-1.158,.91), (.45,.025,.31), bevel=.04)
rod('Crt_AntennaLeft', (-1.53,-.86,1.15), (-1.78,-.86,1.47), .007)
rod('Crt_AntennaRight', (-1.53,-.86,1.15), (-1.27,-.86,1.43), .007)
cube('Vhs_Body', (-1.44,-1.0,.38), (.58,.34,.095), bevel=.012)
for i in range(3):
    cube('Vhs_Tape_%02d' % i, (-1.01,-.89,.64+i*.028), (.19,.12,.025), bevel=.004)

cube('Bed_Frame', (1.31,.54,.24), (1.27,2.13,.34), 'FURNITURE', .035)
cube('Bed_Headboard', (1.31,1.59,.56), (1.28,.11,.90), 'FURNITURE', .035)
cube('Bed_Mattress', (1.31,.51,.47), (1.21,1.96,.21), 'FURNITURE', .085)
cube('Bed_Blanket', (1.31,.19,.60), (1.22,1.28,.08), 'FURNITURE', .035)
cube('Bed_Pillow', (1.31,1.16,.65), (.81,.42,.17), 'PROPS', .065)
cube('Rug_Main', (.12,-.53,.044), (1.75,1.53,.022), 'PROPS', .06)
cube('Shelf_Main', (.78,1.61,2.04), (1.16,.26,.055), 'FURNITURE')
for i in range(7):
    h = random.uniform(.18,.32)
    cube('Shelf_Book_%02d'%i, (.31+i*.073,1.60,2.08+h/2), (.055,.16,h), bevel=.005)
rod('Plant_Pot', (1.11,1.60,2.07), (1.11,1.60,2.25), .075, top=.10)
for i in range(6):
    angle=i*math.tau/6
    end=(1.11+math.cos(angle)*.14,1.6+math.sin(angle)*.10,2.36+random.random()*.10)
    rod('Plant_Stem', (1.11,1.6,2.24), end, .007)
    sphere('Plant_Leaf', end, (.075,.04,.025), sub=1)

# Outdoor tree visible through window, separate from room framing bounds.
rod('Tree_Trunk', (-.90,3.3,-1.0), (-.80,3.3,1.25), .14, 'ROOM_SHELL', top=.075)
for i, p in enumerate([(-1.4,3.25,1.4),(-.3,3.3,1.6),(-.8,3.4,2.0),(-1.6,3.5,2.0),(.05,3.5,2.0)]):
    rod('Tree_Branch_%02d'%i,(-.82,3.3,.6),p,.055,'ROOM_SHELL',top=.023)
    sphere('Tree_Canopy_%02d'%i,p,(.61,.40,.50),'ROOM_SHELL')

def camera(name, pos, target, lens):
    data=bpy.data.cameras.new(name)
    obj=bpy.data.objects.new(name,data)
    collections['CAMERAS'].objects.link(obj)
    obj.location=pos
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.lens=lens
    return obj

camera('Camera_Room', (-6.5,-9.0,6.2), (0,.25,1.10), 48)
camera('Camera_Desk', (-3.5,-3.0,2.9), (-.72,1.06,1.28), 52)
camera('Camera_Window', (-3.6,-4.7,3.1), (-.25,.95,1.45), 48)

def light(name, kind, pos, target, power, color, size=3):
    data=bpy.data.lights.new(name,kind)
    data.energy=power
    data.color=color
    if kind=='AREA': data.shape='DISK'; data.size=size
    if kind=='SUN': data.angle=.07
    obj=bpy.data.objects.new(name,data)
    collections['LIGHTS'].objects.link(obj)
    obj.location=pos
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

light('Sun_Evening','SUN',(-3,5,4),(0,0,0),2.1,(1,.70,.42))
light('Window_Soft','AREA',(-.9,1.6,2),(-.5,-.5,.5),110,(1,.78,.57),1.5)
light('Room_Fill','AREA',(-3,-3,4),(0,.4,1),210,(.65,.76,1),5)
light('Lamp_Warm','POINT',(-1.45,1.18,1.25),(0,0,0),5,(1,.53,.22))
scene.world=bpy.data.worlds.new('World_Graybox')
scene.world.color=(.13,.13,.13)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1440
scene.render.resolution_y=1080
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.camera=bpy.data.objects['Camera_Room']
scene.view_settings.view_transform='AgX'
for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'

deps=bpy.context.evaluated_depsgraph_get()
triangles=0
for obj in scene.objects:
    if obj.type=='MESH':
        ev=obj.evaluated_get(deps)
        mesh=ev.to_mesh()
        mesh.calc_loop_triangles()
        triangles+=len(mesh.loop_triangles)
        ev.to_mesh_clear()
assert triangles < 80000, triangles
assert all(min(o.scale)>0 for o in scene.objects)
print('GRAYBOX_OK', 'objects',len(scene.objects),'triangles',triangles)
if '--save-export' in sys.argv:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender'/'lofi_room.blend'))
    exec(compile((ROOT/'scripts'/'export_glb.py').read_text(encoding='utf-8'),str(ROOT/'scripts'/'export_glb.py'),'exec'))

"""Second inspection pass for Phase 1.5. Execute once after densify_scene.py."""
import bpy, math
from mathutils import Vector, Matrix
s=bpy.context.scene
assert s.get('phase15_layout') and not s.get('phase15_refined')
# 35 degrees retains a small positive screen-facing angle to the bed and improves camera readability.
root=bpy.data.objects['INT_tv_crt'];root.rotation_euler.z=math.radians(-10)
for o in list(s.objects):
    if o.name.startswith('Plant_Foreground'):o.location.x-=.58;o.location.y+=.48
    if o.name.startswith(('Exterior_House','Exterior_Roof','Exterior_Window')):
        o.location.x=(o.location.x+.9)*.45+.6
        o.location.y=4.8+(o.location.y-6.4)*.45
        o.scale.x*=.45;o.scale.y*=.45;o.scale.z*=.60;o.location.z*=.60
    if o.name.startswith('Exterior_Fence'):
        o.location.x=.75+(o.location.x+.6)*.55;o.scale.x*=.55
    if o.name.startswith(('Exterior_Utility','Exterior_Crossarm')):
        o.location.x+=2.35;o.location.z-=.75
    if o.name.startswith('Exterior_Powerline'):
        for v in o.data.vertices:
            v.co.x=(v.co.x+1.75)*.4+.60;v.co.z-=1.15
# Softer irregular blanket folds, avoiding a waffle-like pattern.
me=bpy.data.objects['Bed_Blanket'].data
for v in me.vertices:
    u=v.co.x/1.26+.5; t=v.co.y/1.30+.5
    v.co.z=.028*math.sin(u*11+t*4)+.009*math.sin(t*16-u*3)+.012*math.cos(u*23+t*5)
    if u<.06 or u>.94:v.co.z-=.12
# Cat and seasonal pivots are kept; children move together when seasons are wired later.
def adopt(obj,par):
    bpy.context.view_layer.update(); world=obj.matrix_world.copy();obj.parent=par;obj.matrix_world=world
heater=bpy.data.objects['SEASON_winter_heater']
for o in list(s.objects):
    if o.name.startswith(('Heater_','Kettle_')) or o.name=='SOCKET_kettle_steam':adopt(o,heater)
for o in s.objects:
    if o.name.startswith('Spring_Blossom'):adopt(o,bpy.data.objects['SEASON_spring_flowerpot'])
# Promote fan interaction while preserving the pivot and seasonal parent.
fan=bpy.data.objects['SEASON_summer_fan'];fan['interaction']='fan'
heater['interaction']='heater'
# All category names have stable semantic roles and survive glTF extras.
for o in s.objects:
    prefix=o.name.split('_')[0]
    if prefix in {'INT','ANIM','EMIT','SOCKET','SEASON','LIGHT'}:o['role']=prefix.lower()
bpy.context.view_layer.update()
sc=bpy.data.objects['EMIT_screen_crt'];light=bpy.data.objects['ScreenBounce_Crt']
normal=sc.matrix_world.to_3x3()@Vector((0,-1,0));light.location=sc.matrix_world.translation+normal*.035
light.rotation_euler=normal.to_track_quat('-Z','Y').to_euler()
# Shadow-casting ceiling exists but is intentionally switched off in night inspection.
for a in bpy.context.screen.areas if bpy.context.screen else []:
    if a.type=='VIEW_3D':a.spaces.active.shading.type='SOLID';a.spaces.active.overlay.show_overlays=False
s['phase15_refined']=True
print('REFINEMENT_OK')

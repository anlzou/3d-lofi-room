"""Three Phase 1.5 acceptance views and complete scene manifest; restores all lighting."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(bpy.data.filepath).resolve().parents[1]
s=bpy.context.scene
mode=globals().get('RENDER_MODE','dusk')
cam=bpy.data.objects['Camera_Room']
energies={o.name:o.data.energy for o in s.objects if o.type=='LIGHT'}
originalWorld=s.world
engine=s.render.engine
hidden={o.name:o.hide_render for o in s.objects}
try:
    s.camera=cam;s.render.resolution_x=1600;s.render.resolution_y=1400;s.render.resolution_percentage=100
    s.render.engine='BLENDER_EEVEE'
    if mode=='night':
        # Path tracing uses actual screen emission and lamp bounce, with no ambient fill.
        s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=6
        s.world=bpy.data.worlds['World_Night']
        assert s.world.node_tree.nodes['Background'].inputs['Strength'].default_value==0
        for o in s.objects:
            if o.type=='LIGHT' and o.name!='Lamp_Warm':o.data.energy=0
    if mode=='plan':
        if 'Camera_Plan' not in bpy.data.objects:
            data=bpy.data.cameras.new('Camera_Plan'); pc=bpy.data.objects.new('Camera_Plan',data);bpy.data.collections['CAMERAS'].objects.link(pc)
        pc=bpy.data.objects['Camera_Plan'];pc.location=(.25,1.4,15);pc.rotation_euler=(0,0,0);pc.data.type='ORTHO';pc.data.ortho_scale=9.2
        s.camera=pc;s.render.resolution_x=2000;s.render.resolution_y=2000
        for o in s.objects:
            if o.name.startswith(('Ceiling_','INT_ceiling_')):o.hide_render=True
        bpy.context.view_layer.update()
        groups=json.loads(s['layout_inventory'])
        for g in groups:
            p=[]
            for name in g['objects']:
                if name in bpy.data.objects:p.append(bpy.data.objects[name].matrix_world.translation.copy())
            center=sum(p,Vector())/max(1,len(p));uv=world_to_camera_view(s,pc,center)
            g['plan_uv']=[uv.x,1-uv.y]
        objects=[]
        for o in sorted(s.objects,key=lambda o:o.name):
            objects.append({'name':o.name,'type':o.type,'zone':o.get('zone','base'),'parent':o.parent.name if o.parent else None,'position':list(o.matrix_world.translation),'role':o.get('role','static')})
        (ROOT/'docs'/'scene-manifest.json').write_text(json.dumps({'groups':groups,'objects':objects},indent=2,ensure_ascii=False),encoding='utf-8')
    s.render.filepath=str(ROOT/'blender'/'renders'/('phase15-'+mode+'-2026-09-05.png'))
    bpy.ops.render.render(write_still=True)
    print('RENDER_OK',mode,s.render.filepath)
finally:
    for n,power in energies.items():bpy.data.objects[n].data.energy=power
    for n,value in hidden.items():bpy.data.objects[n].hide_render=value
    s.world=originalWorld;s.render.engine=engine;s.camera=cam
    s.render.resolution_x=1600;s.render.resolution_y=1400

"""Phase 2 full and close acceptance renders, preserving source lighting."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parents[1]
s=bpy.context.scene
mode=globals().get('RENDER_MODE','dusk')
presets={'desk':((-2.7,-1.6,2.5),(-.90,1.03,.88),58),
         'tv':((-.35,-3.3,1.35),(-1.62,-.76,.42),58),
         'cat':((-.85,-2.8,1.2),(.015,-1.20,.24),62),
         'plant':((-3.0,-2.9,1.35),(-1.78,-1.48,.40),60)}
oldcam=s.camera;world=s.world;engine=s.render.engine
energy={o.name:o.data.energy for o in s.objects if o.type=='LIGHT'}
hidden={o.name:o.hide_render for o in s.objects}
try:
    s.camera=bpy.data.objects['Camera_Room']
    if mode in presets:
        name='Camera_P2_'+mode
        if name not in bpy.data.objects:
            d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.data.collections['CAMERAS'].objects.link(o)
        cam=bpy.data.objects[name];pos,target,lens=presets[mode];cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;s.camera=cam
        if mode=='desk':
            for o in s.objects:
                if o.name.startswith(('Chair_','SEASON_autumn_blanket','Throw_Fringe','Ceiling_','INT_ceiling_')):o.hide_render=True
        if mode=='plant':
            for o in s.objects:
                if o.name.startswith(('Crt_','TvStand_','Vhs_','Dvd_','EMIT_screen_crt')):o.hide_render=True
    if mode=='night':
        s.world=bpy.data.worlds['World_Night']
        for o in s.objects:
            if o.type=='LIGHT' and o.name!='Lamp_Warm':o.data.energy=0
    s.render.engine='CYCLES';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.max_bounces=6
    s.render.resolution_x=1600;s.render.resolution_y=1400 if mode in ['dusk','night'] else 1100;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.render.filepath=str(ROOT/'blender/renders'/('phase2-'+mode+'-2026-09-06.png'))
    bpy.ops.render.render(write_still=True)
    print('RENDER_OK',s.render.filepath)
finally:
    for n,v in energy.items():bpy.data.objects[n].data.energy=v
    for n,v in hidden.items():bpy.data.objects[n].hide_render=v
    s.camera=oldcam;s.world=world;s.render.engine=engine

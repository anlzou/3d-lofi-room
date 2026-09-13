"""Fast acceptance views from the saved revision, no source mutation."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parents[1];s=bpy.context.scene
assert bpy.app.background
cam=bpy.data.objects['Camera_Room'];s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.max_bounces=5
s.render.resolution_x=1200;s.render.resolution_y=950;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
views={
 'bedside':((-.50,.12,1.98),(.46,1.10,.48),60),
 'plush':((-.50,-2.3,1.6),(1.75,-1.17,.89),70),
 'cat':((-.65,-2.3,.95),(.03,-1.18,.22),60),
 'desk':((-2.7,-1.6,2.5),(-.90,1.03,.88),58),
 'tv':((-.35,-3.3,1.35),(-1.62,-.76,.42),58)}
for mode,(p,target,lens) in views.items():
 if globals().get('FEEDBACK_VIEWS') and mode not in FEEDBACK_VIEWS:continue
 cam.location=p;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
 hidden=[]
 if mode in ['desk','bedside']:
  for o in s.objects:
   if o.name.startswith(('Chair_','SEASON_autumn_blanket','Throw_Fringe','Ceiling_','INT_ceiling_')) and not o.hide_render:o.hide_render=True;hidden.append(o)
 s.render.filepath=str(ROOT/'blender/renders'/('phase2-feedback-'+mode+'.png'));bpy.ops.render.render(write_still=True)
 for o in hidden:o.hide_render=False
 print('FEEDBACK_RENDER_OK',mode,flush=True)

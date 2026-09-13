"""Original printed posters and finished lava lamp; remove redundant gray props."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard'];zone='phase2'
for f in ['densify_scene.py','phase2_refine.py']:
    tree=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
for o in list(scene.objects):
    if o.name.startswith(('Poster_Moon','Poster_Caption','Poster_Title','Poster_PrintRule','Poster_Landscape','Figurine_','Lego_Block')):remove(o)
for i in range(3):
    o=bpy.data.objects['Poster_%02d'%i];bpy.context.view_layer.update();w=o.matrix_world.copy()
    halfy=max(abs(v.co.y) for v in o.data.vertices);halfz=max(abs(v.co.z) for v in o.data.vertices)
    vs=[w@Vector((-.010,-halfy,-halfz)),w@Vector((-.010,halfy,-halfz)),w@Vector((-.010,halfy,halfz)),w@Vector((-.010,-halfy,halfz))]
    if i==1:vs[0].x-=.014
    p=meshobj('Poster_PrintSurface_%02d'%i,vs,[(3,2,1,0)],'Paper');p.data.materials.clear();p.data.materials.append(bpy.data.materials['MAT_P2_PosterArt'])
    uv=p.data.uv_layers.new(name='UVMap');coords={0:((i+1)/3,0),1:(i/3,0),2:(i/3,1),3:((i+1)/3,1)}
    for loop in p.data.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
lava=bpy.data.objects['INT_lava_lamp'];p=Vector((1.76,-.82,.89))
replace(lava,lathe('LavaBottle',p,[(.046,0),(.058,.055),(.053,.16),(.022,.26),(.015,.265)],'Glass',24))
cylinder('LavaLamp_Cap',(p.x,p.y,1.15),(p.x,p.y,1.185),.025,M['Brass'])
for j,(dx,z,r) in enumerate([(-.015,.94,.025),(.012,1.00,.031),(-.005,1.07,.018)]):uvball('LavaLamp_Wax',(p.x+dx,p.y,z),(r,r,r*1.3),'Terracotta',16,8)
scene['phase2_prints']=True
print('PRINTS_AND_LAVA_DONE')

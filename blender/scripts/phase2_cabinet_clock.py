"""Remove the last blocking cabinet panel and finish readable flip-clock plates."""
import bpy,ast,math,random
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];scene=bpy.context.scene
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
zone='phase2';clay=M['Cream'];dark=M['Charcoal'];card=bpy.data.materials['MAT_TestCard']
for f in ['densify_scene.py','phase2_refine.py']:
    t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
assert not scene.get('phase2_cabinet_clock')
# Full-depth shelf above the three stacked devices, wholly inside the existing cabinet.
replace(bpy.data.objects['TvStand_Shelf'],box('ShelfNew',(-1.72,-.79,.322),(.76,.45,.018),math.radians(35),M['Walnut'],bevel=.004))
# Keep the bedside cabinet's outer dimensions; make the upper cubby and drawer cavity real.
frame_replace('Nightstand_Main',[
    ((.42,1.32,.622),(.38,.45,.026)),
    ((.42,1.32,.058),(.38,.45,.026)),
    ((.243,1.32,.34),(.026,.45,.59)),
    ((.597,1.32,.34),(.026,.45,.59)),
    ((.42,1.532,.34),(.33,.026,.55)),
    ((.42,1.32,.512),(.33,.42,.02))])
box('Nightstand_DrawerBottom',(.42,1.26,.274),(.30,.42,.015),mat=M['Walnut'],bevel=.003)
for x in [.277,.563]:box('Nightstand_DrawerSide',(x,1.26,.38),(.015,.40,.215),mat=M['Oak'],bevel=.003)
# The flip clock is a non-emissive mechanical face; the separate red bedside clock is live.
mat(bpy.data.objects['EMIT_screen_flip'],'Charcoal')
for i,text in enumerate(['17','20']):
    x=-.488+i*.071
    box('FlipClock_Plate',(x,1.275,.78),(.064,.004,.061),mat=M['Charcoal'],bevel=.002)
    label('FlipClock_Print',text,(x-.026,1.271,.759),.046,'Paper',(math.pi/2,0,0))
    box('FlipClock_HingeLine',(x,1.269,.781),(.063,.0015,.0015),mat=M['Walnut'],bevel=0)
scene['phase2_cabinet_clock']=True

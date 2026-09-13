"""Explicit stalks connect both flowers to the soil; preserve the existing leaves."""
import bpy, ast, math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
COL={n:bpy.data.collections[n] for n in ['ROOM_SHELL','FURNITURE','PROPS','LIGHTS','CAMERAS']}
M={m.name[7:]:m for m in bpy.data.materials if m.name.startswith('MAT_P2_') and 'Backup' not in m.name}
zone='phase2'
for f in ['phase2_refine.py','phase2_final_assets.py']:
    t=ast.parse((ROOT/'blender/scripts'/f).read_text(encoding='utf-8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),f,'exec'))
for i,o in enumerate([o for o in bpy.context.scene.objects if o.name.startswith('Spring_Blossom')]):
    p=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
    tube('Spring_FlowerStalk_%02d'%i,[(-.32,1.60,1.06),(-.32+(p.x+.32)*.5,1.60+(p.y-1.60)*.5,1.16),p],.0025,'Leaf')

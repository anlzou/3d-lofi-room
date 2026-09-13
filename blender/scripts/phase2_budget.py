"""Final LOD budget: protect hero silhouette; reduce distant detail only."""
import bpy
s=bpy.context.scene
assert s.get('phase2_final_assets') and not s.get('phase2_budget')
for o in s.objects:
    if o.type!='MESH':continue
    n=o.name;ratio=None
    if n.startswith(('Plant_','Spring_')):ratio=.55 if 'Leaf' not in n else .7
    if n.startswith('Fumo_'):ratio=.75
    if n=='Bed_Blanket':ratio=.6
    if n.startswith(('Rug_','Throw_Fringe','Bin_Rib')):ratio=.4
    if n.startswith(('Mecha_','GameBoy_','Lego_','Photo','EMIT_clock_segment')):
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
    if ratio:
        m=o.modifiers.new('SilhouetteBudget','DECIMATE');m.ratio=ratio
    if n.startswith(('Nightstand_','PowerStrip_','Corkboard_','WallClock_','Poster_','Vhs_','Dvd_','UnderBed_','Ceiling_','Shelf_','WallShelf_','LowBookshelf_','Skirting_','Wall_')):
        for m in o.modifiers:
            if m.type=='BEVEL':m.segments=1
s['phase2_budget']=True
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();tri=0
for o in s.objects:
    if o.type=='MESH':
        e=o.evaluated_get(dg);me=e.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);e.to_mesh_clear()
print('FINAL_TRIANGLES',tri)
assert tri<80000,tri

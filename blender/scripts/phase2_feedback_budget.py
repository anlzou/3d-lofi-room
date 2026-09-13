"""Preserve hero shapes while compressing supporting geometry after the feedback pass."""
import bpy
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    ratio=None
    if o.name=='Cat_Body':ratio=.42
    elif o.name.startswith('Fumo_') and not any(s in o.name for s in ['_Face','_Hair','_Eye','_Bang']):ratio=.48
    elif o.name.startswith('Fumo_'):ratio=.78
    elif o.name.startswith(('Rug_','Throw_Fringe','CatBed_Stitch','Mug_Handle','Speaker_Rim','Bin_Rib','Cable_Phone_Coil','Globe_Parallel')):ratio=.55
    elif o.name=='Bed_Blanket':ratio=.65
    elif o.name.startswith(('Drawer_','Desk_Tape')):ratio=.65
    if ratio and not o.modifiers.get('FeedbackBudget'):
        m=o.modifiers.new('FeedbackBudget','DECIMATE');m.ratio=ratio
bpy.context.view_layer.update()
def count():
    dg=bpy.context.evaluated_depsgraph_get();total=0
    for o in bpy.context.scene.objects:
        if o.type=='MESH':
            e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();total+=len(m.loop_triangles);e.to_mesh_clear()
    return total
print('FEEDBACK_BUDGET',count())

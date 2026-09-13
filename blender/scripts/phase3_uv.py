"""Global, non-overlapping lightmap UVs without changing approved silhouettes.
Modifiers are evaluated once; the untouched editable Phase 2 source is retained.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parents[1];s=bpy.context.scene
assert not s.get('phase3_uv')
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
objects=sorted([o for o in s.objects if o.type=='MESH'],key=lambda o:o.name)
evaluated=[(o,bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)) for o in objects]
verts=[];faces=[];ranges=[]
for o,me in evaluated:
    o.data=me;o.modifiers.clear()
    if not me.uv_layers:me.uv_layers.new(name='UVMap')
    st=len(verts);loopstart=sum(len(f) for f in faces) if not ranges else ranges[-1][1]+ranges[-1][2]
    verts.extend(o.matrix_world@v.co for v in me.vertices)
    faces.extend(tuple(st+i for i in p.vertices) for p in me.polygons)
    ranges.append((o,loopstart,len(me.loops)))
me=bpy.data.meshes.new('LightmapAtlasPacking');me.from_pydata(verts,[],faces);me.update()
proxy=bpy.data.objects.new('LightmapAtlasPacking',me);s.collection.objects.link(proxy)
bpy.ops.object.select_all(action='DESELECT');proxy.select_set(True);bpy.context.view_layer.objects.active=proxy
me.uv_layers.new(name='LightmapUV')
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.0015,area_weight=.5,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
for o,start,count in ranges:
    uv=o.data.uv_layers.get('LightmapUV') or o.data.uv_layers.new(name='LightmapUV')
    for i in range(count):uv.data[i].uv=me.uv_layers.active.data[start+i].uv
    o.data.uv_layers.active_index=0;o['lightmapUV']=1
bpy.context.view_layer.objects.active=bpy.data.objects['Desk_Main'];proxy.select_set(False);bpy.data.objects.remove(proxy,do_unlink=True)
s['phase3_uv']=True;s['phase3_lightmap_method']='Cycles diffuse indirect / corner bake rasterized to shared UV atlas'
print('PHASE3_UV_OK',len(objects),'meshes',len(faces),'faces',flush=True)

"""Cycles corner-attribute baking, rasterized into shared lightmap UVs.
This uses Blender's supported VERTEX_COLORS bake target; no temporary shader nodes.
Only the bake proxy is subdivided. Exported source topology and pivots stay intact.
"""
import bpy,math,json,time
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(bpy.data.filepath).resolve().parents[1];s=bpy.context.scene
assert bpy.app.background and s.get('phase3_uv')
OUT=ROOT/'blender/lighting';OUT.mkdir(exist_ok=True,parents=True)
verts=[];faces=[];uvs=[];base_uvs=[];mats=[];mi=[];hidden=[]
for o in list(s.objects):
    if o.type!='MESH':continue
    # Keep source materials on the proxy so bounced light retains their colors.
    st=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    local=[]
    for m in o.data.materials:
        if m not in mats:mats.append(m)
        local.append(mats.index(m))
    for p in o.data.polygons:faces.append(tuple(st+i for i in p.vertices));mi.append(local[p.material_index] if local else 0)
    uvs.extend(tuple(x.uv) for x in o.data.uv_layers['LightmapUV'].data)
    base_uvs.extend(tuple(x.uv) for x in o.data.uv_layers[0].data)
    hidden.append((o,o.hide_render));o.hide_render=True
me=bpy.data.meshes.new('BakeProxy');me.from_pydata(verts,[],faces);me.update()
for m in mats:me.materials.append(m)
for p,i in zip(me.polygons,mi):p.material_index=i;p.use_smooth=False
base=me.uv_layers.new(name='UVMap')
for x,c in zip(base.data,base_uvs):x.uv=c
uv=me.uv_layers.new(name='LightmapUV')
for x,c in zip(uv.data,uvs):x.uv=c
me.uv_layers.active_index=0
proxy=bpy.data.objects.new('BakeProxy',me);s.collection.objects.link(proxy)
bpy.ops.object.select_all(action='DESELECT');proxy.select_set(True);bpy.context.view_layer.objects.active=proxy
# Subdivide long polygons only, producing spatial samples on walls and floor.
import bmesh
bm=bmesh.new();bm.from_mesh(me)
for step in range(5):
    edges=[e for e in bm.edges if e.calc_length()>.13]
    if not edges:break
    bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True)
bm.to_mesh(me);bm.free();me.update()
color=me.color_attributes.new(name='BakedIrradiance',type='FLOAT_COLOR',domain='CORNER');me.color_attributes.active_color=color
me.calc_loop_triangles()
s.render.engine='CYCLES';s.cycles.samples=128;s.cycles.max_bounces=5;s.cycles.diffuse_bounces=3
s.render.bake.use_clear=True;s.render.bake.target='VERTEX_COLORS'
print('BAKE_PROXY_READY',len(me.vertices),len(me.loop_triangles),flush=True)
# Disable photographic fill; these bakes contain bounce light only, no direct pass.
for o in s.objects:
    if o.type=='LIGHT' and o.name!='Sun_Evening' and o.name!='Lamp_Warm':o.data.energy=0
s.world=bpy.data.worlds['World_Night']
sun=bpy.data.objects['Sun_Evening'];lamp=bpy.data.objects['Lamp_Warm']
presets=[('dawn',7.0),('noon',12.0),('dusk',17+20/60),('night',0.0)]
uv_array=np.array([x.uv[:] for x in me.uv_layers['LightmapUV'].data],dtype=np.float32)
tri_loops=np.array([t.loops[:] for t in me.loop_triangles],dtype=np.int32)
np.savez_compressed(OUT/'atlas-geometry.npz',uv=uv_array,triangles=tri_loops)
for name,hour in [('ao',0)]+presets:
    if name=='ao':bpy.ops.object.bake(type='AO',target='VERTEX_COLORS')
    else:
        angle=(hour-6)/12*math.pi;height=math.sin(angle)
        daylight=max(0,min(1,(height+.12)/.37));daylight=daylight*daylight*(3-2*daylight)
        sun.location=(math.cos(angle)*4,5,1+max(.13,abs(height))*6)
        sun.rotation_euler=(Vector((0,0,.7))-sun.location).to_track_quat('-Z','Y').to_euler()
        sun.data.energy=daylight*(1.8+max(0,height));sun.data.color=(1,.73,.45) if name in ['dusk','dawn'] else (1,.93,.84)
        lamp.data.energy=2.5+(1-daylight)*3.5
        bpy.ops.object.bake(type='DIFFUSE',pass_filter={'INDIRECT'},target='VERTEX_COLORS')
    data=np.empty(len(color.data)*4,dtype=np.float32);color.data.foreach_get('color',data);data=data.reshape(-1,4)
    assert np.isfinite(data).all()
    np.save(OUT/(name+'.npy'),data)
    print('BAKE_OK',name,'max',float(data[:,:3].max()),'mean',float(data[:,:3].mean()),flush=True)
(OUT/'bake.json').write_text(json.dumps({'engine':'Cycles','samples':128,'directIncluded':False,'colorIncluded':False,'times':dict(presets),'proxyTriangles':len(me.loop_triangles),'sourceTriangles':sum(len(f)-2 for f in faces)},indent=2))


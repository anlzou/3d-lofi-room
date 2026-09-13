import bpy
from mathutils import Vector
s=bpy.context.scene
assert not s.get('finish_touch_assets')
root=bpy.data.objects['ANIM_drawer_upper']
for name in ['Nightstand_Handle','Nightstand_Handle.001']:
 o=bpy.data.objects[name];p=[o.matrix_world@Vector(v) for v in o.bound_box]
 if sum(v.z for v in p)/8>.35:
  w=o.matrix_world.copy();o.parent=root;o.matrix_world=w
# Ten slim slats fit the existing opening; lower five use twelve-triangle geometry.
first=bpy.data.objects['ANIM_blinds_slat_00']
for i in range(5,10):
 me=bpy.data.meshes.new('BlindSlatSimple')
 me.from_pydata([(x*.865,y*.07,z*.0125) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 me.materials.append(first.data.materials[0]);o=bpy.data.objects.new('ANIM_blinds_slat_%02d'%i,me);bpy.data.collections['PROPS'].objects.link(o);o.location=(-.9,1.59,2.35-i*.045)
for i in range(10):
 o=bpy.data.objects['ANIM_blinds_slat_%02d'%i];w=o.matrix_world.copy();w.translation=Vector((-.9,1.59,2.35-i*.045));o.matrix_world=w
s['finish_touch_assets']=True
print('SLATS_AND_DRAWER_HANDLE_OK')

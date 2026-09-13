"""Correct explicit slipper attachment positions; closed textile toe, open heel."""
import bpy,math
from mathutils import Vector
for i in range(2):
    p=Vector((.86+i*.21,-.71,.07));suffix='' if i==0 else '.001'
    old=bpy.data.objects['Slipper_Upper'+suffix];vs=[];fs=[]
    for j in range(9):
        t=j/8;width=.07*math.sqrt(max(.0001,1-t*t));height=.063*math.sqrt(max(.0001,1-t*t));y=p.y-.035+t*.17
        for k in range(13):
            a=k*math.pi/12;vs.append((p.x+math.cos(a)*width,y,p.z+.015+math.sin(a)*height))
    for j in range(8):
        for k in range(12):q=j*13+k;fs.append((q,q+1,q+14,q+13))
    me=bpy.data.meshes.new('Slipper_TextileHood');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['MAT_P2_Sage']);old.data=me;old.matrix_world.identity();old.modifiers.clear()
    m=old.modifiers.new('PaddedThickness','SOLIDIFY');m.thickness=.005
    for f in me.polygons:f.use_smooth=True
    for prefix in ['Slipper_Opening','Slipper_Lining']:
        o=bpy.data.objects[prefix+suffix]
        center=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
        target=p+Vector((0,-.065,.027) if prefix=='Slipper_Opening' else (0,-.095,.023))
        w=o.matrix_world.copy();w.translation+=target-center;o.matrix_world=w
print('SLIPPER_CONTACTS_FIXED')

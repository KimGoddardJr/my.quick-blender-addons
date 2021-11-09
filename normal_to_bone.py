import bpy
import mathutils
import math
import numpy as np


# get the index of the selected vertex or face

ob = bpy.context.object
count = len(ob.data.vertices)
sel = np.zeros(count, dtype=np.bool)

ob.data.vertices.foreach_get('select', sel)

print(sel)


# get the normal of selected vertex or face or edge
def get_normal(obj, mode):
    # Get the selected object
    me = obj.data
    print(me)
    # Get the selected mode
    if mode == 'VERTEX':
        # Get the selected vertex index
        index = obj.data.vertices.active_index
        # index = obj.data.vertices.active.index
        # Get the normal of the selected vertex
        normal = me.vertices[index].normal
    elif mode == 'FACE':
        # Get the selected face
        index = me.polygons.active.index
        # Get the normal of the selected face
        normal = me.polygons[index].normal
        print(normal)
    elif mode == 'EDGE':
        # Get the selected edge
        index = me.edges.active.index
        # Get the normal of the selected edge
        normal = me.edges[index].normal
    # Return the normal

# Convert the normal of a vertex to a rotational value
def normal_to_bone(normal):
    # Get the angle between the normal and the z-axis
    angle = math.atan2(normal.y, normal.x)
    # Convert the angle to a value between 0 and 1
    bone_value = angle / (2 * math.pi)
    # Return the bone value
    return bone_value
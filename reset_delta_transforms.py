# the general idea is to reset the deltas of all objects to their original values

import bpy
import numpy as np
import mathutils
import math


bl_info = {
    "name": "Delta Reset",
    "author": "King Goddard Jr",
    "version": (1, 0, 0),
    "blender": (2, 93, 5),
    "location": "3D View",
    "description": "reset the delta to 0 on many objects",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}


class reset_deltas(bpy.types.Operator):
    """Cleanup your object deltas"""

    bl_idname = "transform.reset_deltas"
    bl_label = "Cleans up all the deltas"
    bl_options = {"REGISTER", "UNDO"}

    def __init__(self):
        self.mode = bpy.context.object.rotation_mode

    def execute(self, context):
        for obj in context.selected_objects:
            # raw location data
            obj_L = obj.location
            obj_R = obj.rotation_euler.copy()
            obj_S = obj.scale

            obj_deltaL = obj.delta_location
            obj_deltaR = obj.delta_rotation_euler.copy()
            obj_deltaS = obj.delta_scale

            # convert to np array for quick math
            obj_L_np = np.asarray(obj_L)
            obj_R_np = np.asarray(obj_R)
            obj_S_np = np.asarray(obj_S)

            # obj_S_compensator = np.asarray((-1,-1,-1))

            obj_deltaL_np = np.asarray(obj_deltaL)
            obj_deltaR_np = np.asarray(obj_deltaR)
            obj_deltaS_np = np.asarray(obj_deltaS)

            # sum up location
            obj_L_new = obj_deltaL_np.__add__(obj_L_np)
            # multiply scale
            obj_S_new = np.multiply(obj_deltaS_np, obj_S_np)

            if self.mode != "QUATERNION" or self.mode != "AXIS_ANGLE":

                cur_or = bpy.context.scene.transform_orientation_slots[0].type

                bpy.context.scene.transform_orientation_slots[0].type = "GLOBAL"

                # Assign new values to transforms as tuples
                obj.location = tuple(obj_L_new)
                obj.delta_location = (0, 0, 0)

                obj.rotation_euler.rotate(obj_deltaR)
                obj.delta_rotation_euler = (0, 0, 0)

                obj.scale = tuple(obj_S_new)
                obj.delta_scale = (1, 1, 1)

                bpy.context.scene.transform_orientation_slots[0].type = cur_or

            return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(reset_deltas.bl_idname, text="HSLU - Reset Deltas")


def register():
    bpy.utils.register_class(reset_deltas)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)


def unregister():
    bpy.utils.unregister_class(reset_deltas)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)


if __name__ == "__main__":
    register()

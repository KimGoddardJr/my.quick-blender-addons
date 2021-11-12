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

    def execute(self, context):
        for obj in context.selected_objects:
            # raw location data
            obj_L = obj.location
            obj_R = obj.rotation_euler
            obj_S = obj.scale

            obj_deltaL = obj.delta_location
            obj_deltaR = obj.delta_rotation_euler
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

            # Get the axis of obj_R
            print("-----------")
            print(obj_R_np)
            print("-----------")
            print(obj_deltaR_np)
            print("-----------")

            # convert back to tuple
            obj_R_conv = obj_R_np.tolist()
            obj_deltaR_conv = obj_deltaR_np.tolist()

            obj_R_axis = mathutils.Vector.to_track_quat(
                obj_R_conv[0], obj_R_conv[1], obj_R_conv[2], "Z", "Y"
            )
            # Get the axis of obj_deltaR
            obj_deltaR_axis = mathutils.Vector.to_track_quat(
                obj_deltaR_conv[0], obj_deltaR_conv[1], obj_deltaR_conv[2], "Z", "Y"
            )
            # Add obj_deltaR_axis to obj_R_axis
            obj_R_new = obj_R_axis.__add__(obj_deltaR_axis)
            # Convert back to euler
            obj_R_new = obj_R_new.to_euler()

            # obj_S_compensated = obj_S_new.__add__(obj_S_compensator)

            # Assign new values to transforms as tuples
            obj.location = tuple(obj_L_new)
            obj.delta_location = (0, 0, 0)
            obj.rotation_euler = obj_R_new
            obj.delta_rotation_euler = (0, 0, 0)
            obj.scale = tuple(obj_S_new)
            obj.delta_scale = (1, 1, 1)

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

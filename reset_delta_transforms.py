import bpy


bl_info = {
    "name": "Delta Reset",
    "author": "King Goddard Jr",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "3D View",
    "description": "reset the delta to 0 on many objects",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}



class reset_deltas(bpy.types.Operator):
    """Cleanup your object deltas"""
    bl_idname = "transform.reset_deltas"
    bl_label = "Cleans up all the deltas"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self,context):
        for obj in bpy.context.selected_objects:
            #raw location data
            bpy.ops.object.transforms_to_deltas(mode='ALL')

            obj_deltaL = obj.delta_location
            obj_deltaR = obj.delta_rotation_euler
            obj_deltaS = obj.delta_scale

            # Assign new values to transforms as tuples           
            obj.location = obj_deltaL
            obj.delta_location = (0,0,0)
            obj.rotation_euler = obj_deltaR
            obj.delta_rotation_euler = (0,0,0)
            obj.scale = obj_deltaS
            obj.delta_scale = (1,1,1)

        return {'FINISHED'}



def menu_func(self, context):
    self.layout.operator(reset_deltas.bl_idname, text = "Reset Deltas")



def register():
    bpy.utils.register_class(reset_deltas)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)

def unregister():
    bpy.utils.unregister_class(reset_deltas)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)


if __name__ == "__main__":
    register()

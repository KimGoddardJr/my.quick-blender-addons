import bpy
import mathutils
import math
import numpy as np


#Blender Enum Widget showing all available Armatures in the scene
#Blender Menu Tab with bl_options
class ArmatureSelector(bpy.types.MenuItem):
    bl_idname = "OBJECT_MT_armature_selector"
    bl_label = "Armature Selector"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(self.ArmatureLister.bl_idname, text="Armature List")
        layout.operator(ArmatureSelector.bl_idname, text="Armature Selector")


    def ArmatureLister(self):
        # Get the list of all Armatures in the scene
        armature_list = bpy.data.armatures
        # Get the list of all Armatures in the scene
        for armature in armature_list:
            print(armature.name)

class NormalToBone(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.normal_to_bone"
    bl_label = "Normal to Bone"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.SetBoneNormal(context.active_object, context.mode)
        return {'FINISHED'}

    def GetNormal(self,mesh_components):
        # Get the component index
        normals = []
        num_verts = len(mesh_components)
        sel = np.zeros(num_verts, dtype=np.bool)
        mesh_components.foreach_get('select', sel)

        for component in sel:
            if component:
                normal = mesh_components[component].normal
                normals.append(normal)
        print(normals)
                
        return normals

    # get the normal of selected vertex or face or edge
    def SetBoneNormal(self,obj, mode):
        # Get the selected object
        me = obj.data
        print(me)
        # Get the selected mode
        if mode == 'VERTEX':
            normals = self.GetNormal(me.vertices)
        elif mode == 'FACE':
            # Get the selected face
            normals = self.GetNormal(me.polygons)
        elif mode == 'EDGE':
            # switch to Vertices mode
            raise NotImplementedError("Edge mode not implemented")

    # Convert the normal of a vertex to a rotational value
    def NormalToRotation(self,normal):
        # Get the normal of the component
        normal = normal.normalized()
        # Get the angle between the normal and the Z axis
        angle = math.acos(normal.z)
        # Get the rotation matrix
        rot_mat = mathutils.Matrix.Rotation(angle, 4, 'Z')
        # Get the rotation quaternion
        rot_quat = rot_mat.to_quaternion()
        # Get the rotation euler
        rot_euler = rot_quat.to_euler()
        
        return rot_euler

    def CreateBoneAlignedToNormal(self,armature,normal):
        # Get the rotation euler
        rot_euler = self.NormalToRotation(normal)
        # Create the bone
        bone = armature.edit_bones.new("Bone")
        # Set the bone's rotation
        bone.rotation_euler = rot_euler
        # Set the bone's length
        bone.tail = bone.head + mathutils.Vector((0,0,1))
        # Set the bone's roll
        bone.roll = 0
        # Set the bone's parent
        bone.parent = armature.edit_bones[0]
        # Set the bone's name
        bone.name = "Bone"
        # Set the bone's head
        bone.head = mathutils.Vector((0,0,0))
        # Set the bone's tail
        bone.tail = mathutils.Vector((0,0,1))
        # Set the bone's roll
        bone.roll = 0
        # Set the bone's parent
        bone.parent = armature.edit_bones[0]
        # Set the bone's name




def register():
    bpy.utils.register_class(NormalToBone)

def unregister():
    bpy.utils.unregister_class(NormalToBone)

if __name__ == "__main__":
    register()
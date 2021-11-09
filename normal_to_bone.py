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

    def GetLocationAndNormals(self,mesh,mesh_components):
        # Get the component index
        loc_and_norms = []
        num_verts = len(mesh_components)
        sel = np.zeros(num_verts, dtype=np.bool)
        mesh_components.foreach_get('select', sel)

        for component in sel:
            if component:
                normal = mesh_components[component].normal
                if mesh_components.bl_rna.name == 'Mesh Vertices':
                    location = mesh_components[component].co
                elif mesh_components.bl_rna.name == 'Mesh Edges':
                    # the normal is the average of the two vertex normals of the edge
                    v1 = mesh_components[component].vertices[0]
                    v2 = mesh_components[component].vertices[1]
                    normal = (mesh.vertices[v1].normal + mesh.vertices[v2].normal) / 2
                    location = mesh.vertices[v1].co + mesh.vertices[v2].co
                elif mesh_components.bl_rna.name == 'Mesh Polygons':
                    location = mesh_components[component].center
                
                loc_and_norm = (location,normal)
    
        loc_and_norms.append(loc_and_norm)
        print(loc_and_norms)
                
        return loc_and_norms

    # get the normal of selected vertex or face or edge
    def SetBoneNormal(self,obj, mode):
        # Get the selected object
        me = obj.data
        print(me)
        # Get the selected mode
        if mode == 'VERTEX':
            pos_dirs = self.GetLocationAndNormals(me,me.vertices)
        elif mode == 'FACE':
            pos_dirs = self.GetLocationAndNormals(me,me.polygons)
        elif mode == 'EDGE':
            pos_dirs = self.GetLocationAndNormals(me,me.edges)

        for pos, dir in pos_dirs:
            rot_euler = self.NormalToRotation(dir)
            self.CreateBoneAlignedToNormal(armature,pos,rot_euler)


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

    def CreateBoneAlignedToNormal(self,armature,pos,rot):
        
        bone = armature.edit_bones.new("Bone")
        # Set the bone's length
        bone.head = pos
        bone.tail = pos + (bone.vector.normalized() * 0.5)

        bone.rotation_euler = rot
        # Set the bone's roll
        bone.roll = 0




def register():
    bpy.utils.register_class(NormalToBone)

def unregister():
    bpy.utils.unregister_class(NormalToBone)

if __name__ == "__main__":
    register()
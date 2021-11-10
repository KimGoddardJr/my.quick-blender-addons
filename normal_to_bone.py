import bpy
from bpy.props import (
    IntProperty,
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty,
)
import mathutils
import math
import numpy as np

bl_info = {
    "name": "Bone from Normal",
    "author": "King Goddard Jr",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "3D View",
    "description": "creates a Bone in an Armature aligned to the normals of selected mesh component",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
}


def ArmatureLister():
    list_of_armatures = []
    # Get the list of all Armatures in the scene
    armature_list = bpy.data.armatures
    # Get the list of all Armatures in the scene
    for i, armature in enumerate(armature_list):
        new_armature = (armature.name, armature.name, armature.name, i)
        list_of_armatures.append(new_armature)
        print(armature.name)
    return list_of_armatures


# Get the list of all Armatures in the scene
armature_list = [
    ("Armature", "Armature", "All Blades", 0),
    ("Armature.001", "Armature.001", "Blades with D300 GPU", 1),
    ("Armature.002", "Armature.002", "Blades with D500 GPU", 2),
]

bpy.types.Scene.armature_list = EnumProperty(
    name="Armatures To Place Bones",
    items=armature_list,
    description="Armatures",
    default=armature_list[0][0],
)

# Blender Enum Widget showing all available Armatures in the scene
# Blender Menu Tab with bl_options
class ArmatureSelector(bpy.types.Panel):

    bl_idname = "HSLUCUSTOMPLUGINS_PT_plugins"
    bl_label = "HSLU Normal To Bone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):

        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        box.label(text="Select Armature")
        box.prop(context.scene, "armature_list")


class NormalToBone(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "object.normal_to_bone"
    bl_label = "Normal to Bone"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print(context.active_object)
        print(context.active_object.mode)
        # find out wether is in face selection, vertex selection or edge selection
        # find out if vertices, faces or edges are selected in editmode
        # if context.active_object.mode == "EDIT":

        if context.active_object.mode == "EDIT":
            if context.active_object.type == "MESH":
                self.SetBoneNormal(context.active_object, "FACE")

        if context.active_object.mode == "EDIT":
            self.SetBoneNormal(context.active_object, "FACE")
        elif context.active_object.mode == "OBJECT":
            self.SetBoneNormal(context.active_object, "VERTEX")
        elif context.active_object.mode == "EDIT_MESH":
            self.SetBoneNormal(context.active_object, "EDGE")
        return {"FINISHED"}

    def GetLocationAndNormals(self, mesh, mesh_components):
        # Get the component index
        loc_and_norms = []
        num_verts = len(mesh_components)
        sel = np.zeros(num_verts, dtype=np.bool)
        mesh_components.foreach_get("select", sel)

        for component in sel:
            if component:
                normal = mesh_components[component].normal
                if mesh_components.bl_rna.name == "Mesh Vertices":
                    location = mesh_components[component].co
                elif mesh_components.bl_rna.name == "Mesh Edges":
                    # the normal is the average of the two vertex normals of the edge
                    v1 = mesh_components[component].vertices[0]
                    v2 = mesh_components[component].vertices[1]
                    normal = (mesh.vertices[v1].normal + mesh.vertices[v2].normal) / 2
                    location = mesh.vertices[v1].co + mesh.vertices[v2].co
                elif mesh_components.bl_rna.name == "Mesh Polygons":
                    location = mesh_components[component].center

                loc_and_norm = (location, normal)

        loc_and_norms.append(loc_and_norm)
        print(loc_and_norms)

        return loc_and_norms

    # get the normal of selected vertex or face or edge
    def SetBoneNormal(self, obj, mode):
        # Cur value of enum
        armature = bpy.data.armatures[bpy.context.scene.armature_list]
        # Get the selected object
        me = obj.data
        print(me)
        # Get the selected mode
        if mode == "VERTEX":
            pos_dirs = self.GetLocationAndNormals(me, me.vertices)
        elif mode == "FACE":
            pos_dirs = self.GetLocationAndNormals(me, me.polygons)
        elif mode == "EDGE":
            pos_dirs = self.GetLocationAndNormals(me, me.edges)

        self.CreateBoneAlignedToNormal(armature, pos_dirs)

    # Convert the normal of a vertex to a rotational value
    def NormalToRotation(self, normal):
        # Get the normal of the component
        normal = normal.normalized()
        # Get the angle between the normal and the Z axis
        angle = math.acos(normal.z)
        # Get the rotation matrix
        rot_mat = mathutils.Matrix.Rotation(angle, 4, "Z")
        # Get the rotation quaternion
        rot_quat = rot_mat.to_quaternion()
        # Get the rotation euler
        rot_euler = rot_quat.to_euler()

        return rot_euler

    def CreateBoneAlignedToNormal(self, armature, pos_dirs):

        for pos, normal in pos_dirs:
            # normal,rot_euler,angle = self.NormalToRotation(dir)
            bone = armature.edit_bones.new("Aligned-Bone")
            # Set the bone's length
            bone.head = pos
            # bone.tail = pos + (bone.vector.normalized() * 0.5)
            bone.tail = pos + (normal.normalized() * 0.5)

            # Rotate the whole bone aligned
            # bone.matrix.rotate(rot_euler)
            # Set the bone's roll
            bone.roll = 0


# Add the Normal To Bone Operator to a Pie Menu
class NormalToBonePie(bpy.types.Menu):
    bl_idname = "object.normal_to_bone_pie"
    bl_label = "Normal to Bone"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("object.normal_to_bone", text="Vertex", icon="VERTEXSEL")
        pie.operator("object.normal_to_bone", text="Face", icon="FACESEL")
        pie.operator("object.normal_to_bone", text="Edge", icon="EDGESEL")


classes = [NormalToBone, ArmatureSelector, NormalToBonePie]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

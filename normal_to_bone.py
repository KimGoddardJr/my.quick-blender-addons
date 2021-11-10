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


# Get the list of all Armatures in the scene
armature_list = [
    ("Armature", "Armature", "All Blades", 0),
    ("Armature.001", "Armature.001", "Blades with D300 GPU", 1),
    ("Armature.002", "Armature.002", "Blades with D500 GPU", 2),
]


# Blender Enum Widget showing all available Armatures in the scene
# Blender Menu Tab with bl_options
class ArmatureSelector(bpy.types.Panel):

    bl_idname = "HSLUCUSTOMPLUGINS_PT_plugins"
    bl_label = "HSLU Normal To Bone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}

    def __init__(self):

        armature_list = self.ArmatureLister()

        bpy.types.Scene.armature_list = EnumProperty(
            name="Rigs",
            items=armature_list,
            description="Armatures",
            default=armature_list[0][0],
        )

    def draw(self, context):

        layout = self.layout
        # layout.use_property_split = True

        box = layout.box()
        box.scale_y = 1.75
        box.label(text="Select Armature")
        box.prop(context.scene, "armature_list")
        box.separator()
        box.operator("object.normal_to_bone", text="Create Bone")

    def ArmatureLister(self):
        list_of_armatures = []
        # Get the list of all Armatures in the scene
        armature_list = bpy.data.armatures
        # Get the list of all Armatures in the scene
        for i, armature in enumerate(armature_list):
            new_armature = (armature.name, armature.name, f"Choose {armature.name}", i)
            list_of_armatures.append(new_armature)
            print(armature.name)
        return list_of_armatures


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
            self.SetBoneNormal(context.active_object)

        return {"FINISHED"}

    def GetLocationAndNormals(self, mesh, mesh_components):
        # Get the component index
        loc_and_norms = []
        print(mesh_components)
        num_components = len(mesh_components)
        sel = np.zeros(num_components, dtype=np.bool)
        mesh_components.foreach_get("select", sel)

        print(sel)
        for i, component in enumerate(sel):
            if component:
                print(i)

                if mesh_components.bl_rna.name == "Mesh Vertices":
                    location = mesh_components[i].co
                    normal = mesh_components[i].normal

                elif mesh_components.bl_rna.name == "Mesh Edges":
                    # the normal is the average of the two vertex normals of the edge
                    v1 = mesh_components[i].vertices[0]
                    v2 = mesh_components[i].vertices[1]
                    normal = (mesh.vertices[v1].normal + mesh.vertices[v2].normal) / 2
                    # the position between two vertices
                    location = (mesh.vertices[v1].co + mesh.vertices[v2].co) / 2

                elif mesh_components.bl_rna.name == "Mesh Polygons":
                    location = mesh_components[i].center
                    normal = mesh_components[i].normal

                loc_and_norm = (location, normal)

                loc_and_norms.append(loc_and_norm)

        print(loc_and_norms)

        return loc_and_norms

    # get the normal of selected vertex or face or edge
    def SetBoneNormal(self, obj):
        # Cur value of enum
        sel_modes = bpy.context.tool_settings.mesh_select_mode
        VERTEX = sel_modes[0]
        EDGES = sel_modes[1]
        FACES = sel_modes[2]

        armature = bpy.data.armatures[bpy.context.scene.armature_list]
        # Get the selected object
        me = obj.data
        print(me)
        # Get the selected mode
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        if VERTEX:
            pos_dirs = self.GetLocationAndNormals(me, me.vertices)
        elif FACES:
            pos_dirs = self.GetLocationAndNormals(me, me.polygons)
        elif EDGES:
            pos_dirs = self.GetLocationAndNormals(me, me.edges)

        self.CreateBoneAlignedToNormal(obj, armature, pos_dirs)

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

    def CreateBoneAlignedToNormal(self, ob, armature, pos_dirs):
        # switch armature to edit mode

        cur_obj = bpy.data.objects[ob.name]

        cur_armature_obj = [
            obj
            for obj in bpy.data.objects
            if obj.data.rna_type.name == "Armature" and obj.data.name == armature.name
        ][0]

        bpy.ops.object.mode_set(mode="OBJECT")
        cur_obj.select_set(False)
        #
        bpy.context.view_layer.objects.active = cur_armature_obj
        cur_armature_obj.select_set(True)

        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        print("HAPPENING")

        edit_armature = bpy.context.active_object.data
        print(edit_armature)

        # if bpy.data.armatures[armature.name].edit_bones.active:

        for pos_dir in pos_dirs:
            # normal,rot_euler,angle = self.NormalToRotation(dir)
            bone = edit_armature.edit_bones.new("Aligned-Bone")
            # Set the bone's length
            pos = pos_dir[0]
            normal = pos_dir[1]

            bone.head = pos
            # bone.tail = pos + (bone.vector.normalized() * 0.5)
            bone.tail = pos + (normal.normalized() * 0.5)

            # Rotate the whole bone aligned
            # bone.matrix.rotate(rot_euler)
            # Set the bone's roll
            bone.roll = 0

        # bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        cur_armature_obj.select_set(False)
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

        bpy.context.view_layer.objects.active = cur_obj
        cur_obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT", toggle=False)


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

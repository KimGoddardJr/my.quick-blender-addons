# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####



bl_info = {
    "name": "Grease to Mesh",
    "author": "King Goddard Jr",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "3D View",
    "description": "make a mesh out of grease Pencil",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"}



import bpy
import math
import pdb
from mathutils import Euler, Matrix, Quaternion, Vector
import numpy



def sel():
    return bpy.context.view_layer.objects.selected

def GPframe_set(input=0):
    return bpy.context.scene.frame_set(input)

def Linker(context,index,col_name = "empty"):
    col_child = bpy.context.scene.collection.children
    col_obj = bpy.context.scene.collection.objects
    col_child_obj = col_child[col_name].objects
    assets = [col_child,col_obj,col_child_obj]
    return assets[index].link(context)

def ContextSel(self,type):
    for obj in selection:
        if obj.type == 'GPENCIL' and selection.data.active:
            return obj


def CurveNew(name="EmptyCurveData"):
    CurveData = bpy.data.curves.new(type='CURVE',name=name)
    CurveData.dimensions = '3D'
    CurveData.resolution_u = 2
    return CurveData

def ObjectNew(name="EmptyObjectData",data = None):
    object_info = bpy.data.objects.new(name,data)
    return object_info

def CollectionNew(name = "NewCollection"):
    newcol = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(newcol)
    return newcol

"""
CLASSES
"""

class convert_GP_CV(bpy.types.Operator):
    
    """Add a simple box mesh"""
    bl_idname = "gpencil.convert_to_cv"
    bl_label = "Create an Array of Meshes from a GP-Layer Timeline"
    bl_options = {'REGISTER', 'UNDO'}
    
    """
    vars
    """
    def execute(self,context):
        for obj in bpy.context.selected_objects:
            
            if obj.type == 'GPENCIL':
                current_gp = bpy.data.grease_pencils[obj.data.name]
                
                active_layer = current_gp.layers.active
                GP_frames = current_gp.layers.active.frames
                """
                Create a Collection to store the Grease Conversions in.
                """
                GP_coll = CollectionNew("{}_Collection".format(active_layer.info))
                
                """
                Start the Loop
                """
        
                for i,GP_frame in enumerate(GP_frames,0):   
                    """
                    add a new curve data of each frame in seq
                    """
                    f = GP_frames[i].frame_number
                    GPframe_set(f)
                    
                    cur = CurveNew("GreaseCurve")
                    cur.name = "00{}_{}_{}_{}".format(i+1,active_layer.info,cur.name,f)

                    for GP_stroke in GP_frames[i].strokes:
                        
                        polyline = cur.splines.new('POLY')
                        cur_points = polyline.points 
                        cur_points.add(len(GP_stroke.points)-1)
                        
                        """
                        for each separate stroke of the grasepencil on a 
                        frame,add a new polyline, 
                        and assign points to it corresponding with the amount 
                        of points on the stroke.
                        
                        """
                        for n,GP_point in enumerate(GP_stroke.points,0):
                            """
                            Iterate through all the curve points and place
                            them where the grease points are placed.
                            Also add a radius to the points corresponding with
                            the pressure.      
                            """  
                            x,y,z = GP_point.co
                                
                            cur_points[n].co = (x,y,z,1)
                            cur_points[n].radius = GP_point.pressure
                    
                    """
                    Returning back to the initial per frame loop, 
                    we bind the curves to an object and then link them
                    to the new collection.

                    we also add a curve bevel.            
                    """
                    cur.bevel_depth = 0.1
                    cur_obj = ObjectNew(cur.name,cur)
                    Linker(cur_obj,2,GP_coll.name)
        
        return {'FINISHED'}
                    
                
class HSLU_menu_items(bpy.types.Panel):
        
    bl_idname = "HSLUCUSTOMPLUGINS_PT_plugins"
    bl_label = "HSLU Custom Plugins"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    def draw(self, context):
        
        layout = self.layout
        layout.use_property_split = True
        
        box = layout.box()
        col = box.column(align=True)
        col.operator("gpencil.convert_to_cv", text="Make GP-Layer Mesh List")
        
classes = (convert_GP_CV,HSLU_menu_items)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
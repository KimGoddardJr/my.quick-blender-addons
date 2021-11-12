import bpy


class TransferAllShapeKeys(bpy.types.Operator):
    """Tooltip"""

    bl_idname = "object.transfer_all_shape_keys"
    bl_label = "Transfer All Shape Keys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        self.copy_all_shape_keys()
        return {"FINISHED"}

    def copy_all_shape_keys(self):
        if len(bpy.context.selected_objects) == 2:
            source = bpy.context.selected_objects[1]
            dest = bpy.context.active_object
            for v in bpy.context.selected_objects:
                if v is not dest:
                    source = v
                    break

            print("Source: ", source.name)
            print("Destination: ", dest.name)

            if source.data.shape_keys is None:
                print("Source object has no shape keys!")
            else:
                for idx in range(1, len(source.data.shape_keys.key_blocks)):
                    source.active_shape_key_index = idx
                    print("Copying Shape Key - ", source.active_shape_key.name)
                    bpy.ops.object.shape_key_transfer()


class TransferAllShapeKeysPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""

    bl_idname = "HSLUCUSTOMPLUGINS_PT_TransferAllShapes"
    bl_label = "HSLU Transfer All Shape Keys"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.scale_y = 1.75
        box.label(text="Transfer All Shapekeys")
        box.operator(TransferAllShapeKeys.bl_idname)
        box.separator()


classes = [TransferAllShapeKeys, TransferAllShapeKeysPanel]


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()

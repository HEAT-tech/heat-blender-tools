import bpy

class HEAT_PT_dev_inspector_panel(bpy.types.Panel):
    bl_idname = "heat_pt_dev_inspector_panel"
    bl_label = "Bone Matrix Inspector"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Heat Dev Inspector"

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_ARMATURE' or context.mode == 'POSE')

    def draw(self, context):
        layout = self.layout

        layout.label(text='Select bones to inspect...', icon='BORDERMOVE')
        layout.separator()

        selected_bones = bpy.context.selected_bones
        if selected_bones is None:
            selected_bones = bpy.context.selected_pose_bones

        for armature in bpy.context.selected_objects:
            box = layout.box()
            if armature.type != 'ARMATURE':
                continue
            box.label(text=armature.name, icon="ARMATURE_DATA")

            for bone in selected_bones:
                if not bone.id_data.name == armature.name:
                    continue
                box.label(text=bone.name, icon='BONE_DATA')
                box.prop(bone, 'location')
                box.prop(bone, 'rotation_quaternion')
                box.prop(bone, 'scale')

            layout.separator()





    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)

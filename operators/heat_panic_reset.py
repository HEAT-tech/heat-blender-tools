import bpy


class HeatPanicResetOperator(bpy.types.Operator):
    """Reset Heat properties"""
    bl_idname = "heat.panic_reset"
    bl_label = "Reset HEAT"

    def execute(self, context):
        context.scene.heat_animation_id_downloading = False
        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)

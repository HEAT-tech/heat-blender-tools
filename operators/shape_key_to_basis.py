import bpy
from .. import lib

class ShapeKeyApplier(bpy.types.Operator):
    # Replace the 'Basis' shape key with the currently selected shape key
    bl_idname = "heat.shape_key_to_basis"
    bl_label = 'Shape Key to Basis'
    bl_description = 'ShapeKeyApplier.desc'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object.active_shape_key and bpy.context.object.active_shape_key_index > 0

    def execute(self, context):
        mesh = lib.common.get_active()
        print('shape key apply on mesh:' and mesh)

        # Get shapekey which will be the new basis
        new_basis_shapekey = mesh.active_shape_key
        new_basis_shapekey_name = new_basis_shapekey.name
        new_basis_shapekey_value = new_basis_shapekey.value

        # Check for reverted shape keys
        if ' - Reverted' in new_basis_shapekey_name and new_basis_shapekey.relative_key.name != 'Basis':
            for shapekey in mesh.data.shape_keys.key_blocks:
                if ' - Reverted' in shapekey.name and shapekey.relative_key.name == 'Basis':
                    self.report({'ERROR'}, 'ShapeKeyApplier.error.revert')
                    return {'FINISHED'}

            self.report({'ERROR'}, 'ShapeKeyApplier.error.revert')
            return {'FINISHED'}

        # Set up shape keys
        mesh.show_only_shape_key = False
        bpy.ops.object.shape_key_clear()

        # Create a copy of the new basis shapekey to make it's current value stay as it is
        new_basis_shapekey.value = new_basis_shapekey_value
        if new_basis_shapekey_value == 0:
            new_basis_shapekey.value = 1
        new_basis_shapekey.name = new_basis_shapekey_name + '--Old'

        # Replace old new basis with new new basis
        new_basis_shapekey = mesh.shape_key_add(name=new_basis_shapekey_name, from_mix=True)
        new_basis_shapekey.value = 1

        # Delete the old one
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey.name == new_basis_shapekey_name + '--Old':
                bpy.ops.object.shape_key_remove(all=False)
                break

        # Find old basis and rename it
        old_basis_shapekey = mesh.data.shape_keys.key_blocks[0]
        old_basis_shapekey.name = new_basis_shapekey_name + ' - Reverted'
        old_basis_shapekey.relative_key = new_basis_shapekey

        # Rename new basis after old basis was renamed
        new_basis_shapekey.name = 'Basis'

        # Mix every shape keys with the new basis
        for index in range(0, len(mesh.data.shape_keys.key_blocks)):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and shapekey.name != 'Basis' and ' - Reverted' not in shapekey.name:
                shapekey.value = 1
                mesh.shape_key_add(name=shapekey.name + '-New', from_mix=True)
                shapekey.value = 0

        # Remove all the unmixed shape keys except basis and the reverted ones
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and not shapekey.name.endswith('-New') and shapekey.name != 'Basis' and ' - Reverted' not in shapekey.name:
                bpy.ops.object.shape_key_remove(all=False)

        # Fix the names and the relative shape key
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey and shapekey.name.endswith('-New'):
                shapekey.name = shapekey.name[:-4]
                shapekey.relative_key = new_basis_shapekey

        # Repair important shape key order
        lib.common.sort_shape_keys(mesh.name)

        # Correctly apply the new basis as basis (important step, doesn't work otherwise)
        lib.common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        lib.common.switch('OBJECT')

        # If a reversed shapekey was applied as basis, fix the name
        if ' - Reverted - Reverted' in old_basis_shapekey.name:
            old_basis_shapekey.name = old_basis_shapekey.name.replace(' - Reverted - Reverted', '')
            self.report({'INFO'}, 'ShapeKeyApplier.successRemoved')
        else:
            self.report({'INFO'}, 'ShapeKeyApplier.successSet')
        return {'FINISHED'}


def addToShapekeyMenu(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeyApplier.bl_idname, text='addToShapekeyMenu.ShapeKeyApplier.label', icon="KEY_HLT")

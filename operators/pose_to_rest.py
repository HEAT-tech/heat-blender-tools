import bpy

class PoseToRest(bpy.types.Operator):
    bl_idname = 'heat.pose_to_rest'
    bl_label = 'Pose to Rest'
    bl_description = 'Pose to rest description'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        saved_data = SavedData()

        armature = get_armature()
        set_active(armature)
        scales = {}

        # Find out how much each bone is scaled
        for bone in armature.pose.bones:
            scale_x = bone.scale[0]
            scale_y = bone.scale[1]
            scale_z = bone.scale[2]

            if armature.data.bones.get(bone.name).use_inherit_scale:
                def check_parent(child, scale_x_tmp, scale_y_tmp, scale_z_tmp):
                    if child.parent:
                        parent = child.parent
                        scale_x_tmp *= parent.scale[0]
                        scale_y_tmp *= parent.scale[1]
                        scale_z_tmp *= parent.scale[2]

                        if armature.data.bones.get(parent.name).use_inherit_scale:
                            scale_x_tmp, scale_y_tmp, scale_z_tmp = check_parent(parent, scale_x_tmp, scale_y_tmp,
                                                                                 scale_z_tmp)

                    return scale_x_tmp, scale_y_tmp, scale_z_tmp

                scale_x, scale_y, scale_z = check_parent(bone, scale_x, scale_y, scale_z)

            if scale_x == scale_y == scale_z != 1:
                scales[bone.name] = scale_x

        pose_to_shapekey('PoseToRest')

        bpy.ops.pose.armature_apply()

        for mesh in get_meshes_objects():
            unselect_all()
            set_active(mesh)

            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.cats_shapekey.shape_key_to_basis()

            # Remove old basis shape key from shape_key_to_basis operation
            for index in range(len(mesh.data.shape_keys.key_blocks) - 1, 0, -1):
                mesh.active_shape_key_index = index
                if 'PoseToRest - Reverted' in mesh.active_shape_key.name:
                    bpy.ops.object.shape_key_remove(all=False)

            mesh.active_shape_key_index = 0

            # Find out which bones scale which shapekeys and set it to the highest scale
            print('\nSCALED BONES:')
            shapekey_scales = {}
            for bone_name, scale in scales.items():
                print(bone_name, scale)
                vg = mesh.vertex_groups.get(bone_name)
                if not vg:
                    continue

                for vertex in mesh.data.vertices:
                    for g in vertex.groups:
                        if g.group == vg.index and g.weight == 1:
                            for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                                if i == 0:
                                    continue

                                if shapekey.data[vertex.index].co != mesh.data.shape_keys.key_blocks[0].data[
                                    vertex.index].co:
                                    if shapekey.name in shapekey_scales:
                                        shapekey_scales[shapekey.name] = max(shapekey_scales[shapekey.name], scale)
                                    else:
                                        shapekey_scales[shapekey.name] = scale
                            break

            # Mix every shape keys with itself with the slider set to the new scale
            for index in range(0, len(mesh.data.shape_keys.key_blocks)):
                mesh.active_shape_key_index = index
                shapekey = mesh.active_shape_key
                if shapekey.name in shapekey_scales:
                    print('Fixed shapekey', shapekey.name)
                    shapekey.slider_max = min(shapekey_scales[shapekey.name], 10)
                    shapekey.value = shapekey.slider_max
                    mesh.shape_key_add(name=shapekey.name + '-New', from_mix=True)
                    shapekey.value = 0

            # Remove all the old shapekeys
            for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
                mesh.active_shape_key_index = index
                shapekey = mesh.active_shape_key
                if shapekey.name in shapekey_scales:
                    bpy.ops.object.shape_key_remove(all=False)

            # Fix the names of the new shapekeys
            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if shapekey and shapekey.name.endswith('-New'):
                    shapekey.name = shapekey.name[:-4]

            # Repair important shape key order
            repair_shapekey_order(mesh.name)

        # Stop pose mode after operation
        # bpy.ops.cats_manual.stop_pose_mode()

        saved_data.load(hide_only=True)

        self.report({'INFO'}, 'PoseToRest.success')
        return {'FINISHED'}


def get_armature(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    for obj in get_objects():
        if obj.type == 'ARMATURE':
            if (armature_name and obj.name == armature_name) or not armature_name:
                return obj
    return None


class SavedData:
    __object_properties = {}
    __active_object = None

    def __init__(self):
        # initialize as instance attributes rather than class attributes
        self.__object_properties = {}
        self.__active_object = None

        for obj in get_objects():
            mode = obj.mode
            selected = is_selected(obj)
            hidden = is_hidden(obj)
            pose = None
            if obj.type == 'ARMATURE':
                pose = obj.data.pose_position
            self.__object_properties[obj.name] = [mode, selected, hidden, pose]

            active = get_active()
            if active:
                self.__active_object = active.name

    def load(self, ignore=None, load_mode=True, load_select=True, load_hide=True, load_active=True, hide_only=False):
        if not ignore:
            ignore = []
        if hide_only:
            load_mode = False
            load_select = False
            load_active = False

        for obj_name, values in self.__object_properties.items():
            # print(obj_name, ignore)
            if obj_name in ignore:
                continue

            obj = get_objects().get(obj_name)
            if not obj:
                continue

            mode, selected, hidden, pose = values
            # print(obj_name, mode, selected, hidden)
            print(obj_name, pose)

            if load_mode and obj.mode != mode:
                set_active(obj, skip_sel=True)
                switch(mode, check_mode=False)
                if pose:
                    obj.data.pose_position = pose

            if load_select:
                select(obj, selected)
            if load_hide:
                hide(obj, hidden)

        # Set the active object
        if load_active and self.__active_object and get_objects().get(self.__active_object):
            if self.__active_object not in ignore and self.__active_object != get_active():
                set_active(get_objects().get(self.__active_object), skip_sel=True)



def set_active(obj, skip_sel=False):
    if not skip_sel:
        select(obj)
    bpy.context.view_layer.objects.active = obj


def get_active():
    return bpy.context.view_layer.objects.active


def get_objects():
    return bpy.context.scene.objects


def select(obj, sel=True):
    if sel:
        hide(obj, False)
    obj.select_set(sel)


def is_selected(obj):
    return obj.select_get()


def unselect_all():
    for obj in get_objects():
        select(obj, False)


def hide(obj, val=True):
    if hasattr(obj, 'hide'):
        obj.hide = val
    obj.hide_set(val)


def is_hidden(obj):
    return obj.hide_get()


def switch(new_mode, check_mode=True):
    if check_mode and get_active() and get_active().mode == new_mode:
        return
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)


def delete(obj):
    if obj.parent:
        for child in obj.children:
            child.parent = obj.parent

    objs = bpy.data.objects
    objs.remove(objs[obj.name], do_unlink=True)


def get_meshes_objects(armature_name=None, mode=0, check=True, visible_only=False):
    # Modes:
    # 0 = With armatures only
    # 1 = Top level only
    # 2 = All meshes
    # 3 = Selected only

    if not armature_name:
        armature = get_armature()
        if armature:
            armature_name = armature.name

    meshes = []
    for ob in get_objects():
        if ob.type == 'MESH':
            if mode == 0 or mode == 5:
                if ob.parent:
                    if ob.parent.type == 'ARMATURE' and ob.parent.name == armature_name:
                        meshes.append(ob)
                    elif ob.parent.parent and ob.parent.parent.type == 'ARMATURE' and ob.parent.parent.name == armature_name:
                        meshes.append(ob)

            elif mode == 1:
                if not ob.parent:
                    meshes.append(ob)

            elif mode == 2:
                meshes.append(ob)

            elif mode == 3:
                if is_selected(ob):
                    meshes.append(ob)

    if visible_only:
        for mesh in meshes:
            if is_hidden(mesh):
                meshes.remove(mesh)

    # Check for broken meshes and delete them
    if check:
        current_active = get_active()
        to_remove = []
        for mesh in meshes:
            selected = is_selected(mesh)
            # print(mesh.name, mesh.users)
            set_active(mesh)

            if not get_active():
                to_remove.append(mesh)

            if not selected:
                select(mesh, False)

        for mesh in to_remove:
            print('DELETED CORRUPTED MESH:', mesh.name, mesh.users)
            meshes.remove(mesh)
            delete(mesh)

        if current_active:
            set_active(current_active)

    return meshes


def pose_to_shapekey(name):
    saved_data = SavedData()

    for mesh in get_meshes_objects():
        unselect_all()
        set_active(mesh)

        switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        switch('OBJECT')

        # Apply armature mod
        mod = mesh.modifiers.new(name, 'ARMATURE')
        mod.object = get_armature()
        apply_modifier(mod, as_shapekey=True)

    armature = set_default_stage()
    switch('POSE')
    armature.data.pose_position = 'POSE'

    saved_data.load(ignore=armature.name)
    return armature


def repair_shapekey_order(mesh_name):
    # Get current custom data
    armature = get_armature()
    custom_data = armature.get('CUSTOM')
    if not custom_data:
        custom_data = {}

    # Extract shape keys from string
    shape_key_order = custom_data.get('shape_key_order')
    if not shape_key_order:
        custom_data['shape_key_order'] = []
        armature['CUSTOM'] = custom_data

    if type(shape_key_order) is str:
        shape_key_order_temp = []
        for shape_name in shape_key_order.split(',,,'):
            shape_key_order_temp.append(shape_name)
        custom_data['shape_key_order'] = shape_key_order_temp
        armature['CUSTOM'] = custom_data

    sort_shape_keys(mesh_name, custom_data['shape_key_order'])


def set_default_stage():
    """

    Selects the armature, unhides everything and sets the modes of every object to object mode

    :return: the armature
    """

    # Remove rigidbody collections, as they cause issues if they are not in the view_layer
    if bpy.context.scene.remove_rigidbodies_joints:
        print('Collections:')
        for collection in bpy.data.collections:
            print(' ' + collection.name, collection.name.lower())
            if 'rigidbody' in collection.name.lower():
                print('DELETE')
                for obj in collection.objects:
                    delete(obj)
                bpy.data.collections.remove(collection)

    unhide_all()
    unselect_all()

    for obj in get_objects():
        set_active(obj)
        switch('OBJECT')
        if obj.type == 'ARMATURE':
            # obj.data.pose_position = 'REST'
            pass

        select(obj, False)

    armature = get_armature()
    if armature:
        set_active(armature)

    # Fix broken armatures
    if not bpy.context.scene.armature:
        bpy.context.scene.armature = armature.name

    return armature

def apply_modifier(mod, as_shapekey=False):
    if bpy.app.version < (2, 90):
        bpy.ops.object.modifier_apply(apply_as='SHAPE' if as_shapekey else 'DATA', modifier=mod.name)
        return

    if as_shapekey:
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=mod.name)
    else:
        bpy.ops.object.modifier_apply(modifier=mod.name)


def unhide_all():
    for obj in get_objects():
        hide(obj, False)
        set_unselectable(obj, False)

    unhide_all_unnecessary()


def sort_shape_keys(mesh_name, shape_key_order=None):
    mesh = get_objects()[mesh_name]
    if not has_shapekeys(mesh):
        return
    set_active(mesh)

    if not shape_key_order:
        shape_key_order = []

    order = [
        'Basis',
        'vrc.blink_left',
        'vrc.blink_right',
        'vrc.lowerlid_left',
        'vrc.lowerlid_right',
        'vrc.v_aa',
        'vrc.v_ch',
        'vrc.v_dd',
        'vrc.v_e',
        'vrc.v_ff',
        'vrc.v_ih',
        'vrc.v_kk',
        'vrc.v_nn',
        'vrc.v_oh',
        'vrc.v_ou',
        'vrc.v_pp',
        'vrc.v_rr',
        'vrc.v_sil',
        'vrc.v_ss',
        'vrc.v_th',
        'Basis Original'
    ]

    for shape in shape_key_order:
        if shape not in order:
            order.append(shape)

    wm = bpy.context.window_manager
    current_step = 0
    wm.progress_begin(current_step, len(order))

    i = 0
    for name in order:
        if name == 'Basis' and 'Basis' not in mesh.data.shape_keys.key_blocks:
            i += 1
            current_step += 1
            wm.progress_update(current_step)
            continue

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey.name == name:

                mesh.active_shape_key_index = index
                new_index = i
                index_diff = (index - new_index)

                if new_index >= len(mesh.data.shape_keys.key_blocks):
                    bpy.ops.object.shape_key_move(type='BOTTOM')
                    break

                position_correct = False
                if 0 <= index_diff <= (new_index - 1):
                    while position_correct is False:
                        if mesh.active_shape_key_index != new_index:
                            bpy.ops.object.shape_key_move(type='UP')
                        else:
                            position_correct = True
                else:
                    if mesh.active_shape_key_index > new_index:
                        bpy.ops.object.shape_key_move(type='TOP')

                    position_correct = False
                    while position_correct is False:
                        if mesh.active_shape_key_index != new_index:
                            bpy.ops.object.shape_key_move(type='DOWN')
                        else:
                            position_correct = True

                i += 1
                break

        current_step += 1
        wm.progress_update(current_step)

    mesh.active_shape_key_index = 0

    wm.progress_end()


def set_unselectable(obj, val=True):
    obj.hide_select = val


def unhide_all_unnecessary():
    # TODO: Documentation? What does "unnecessary" mean?
    try:
        bpy.ops.object.hide_view_clear()
    except RuntimeError:
        pass

    for collection in bpy.data.collections:
        collection.hide_select = False
        collection.hide_viewport = False



def has_shapekeys(mesh):
    if not hasattr(mesh.data, 'shape_keys'):
        return False
    return hasattr(mesh.data.shape_keys, 'key_blocks')

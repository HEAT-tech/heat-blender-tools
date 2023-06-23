import bpy
from mathutils import Quaternion
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty


class IMPORT_SCENE_OT_vrm_as_gltf(bpy.types.Operator, ImportHelper):
    """Import VRM file as GLTF/GLB (extra properties excluded)"""
    bl_idname = "import_scene.vrm_as_gltf"
    bl_label = "Import VRM"

    # ImportHelper mixin class uses this
    filename_ext = ".vrm"

    filter_glob: StringProperty(
        default="*.vrm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # GLTF import properties
    pack_images: BoolProperty(
        name="Pack Images",
        description="Pack all images into the .blend file",
        default=True,
    )

    merge_vertices: BoolProperty(
        name="Merge Vertices",
        description="Merge vertices",
        default=False,
    )

    shading: EnumProperty(
        name="Shading",
        description="How normals are computed during import",
        items=[
            ('NORMALS', "Use Normal Data", "Use Normal Data"),
            ('FLAT', "Flat Shading", "Flat Shading"),
            ('SMOOTH', "Smooth Shading", "Smooth Shading"),
        ],
        default='NORMALS',
    )

    guess_original_bind_pose: BoolProperty(
        name="Guess Original Bind Pose",
        description="Try to guess the original bind pose for skinned meshes from the inverse bind matrices. When off, use default/rest pose as bind pose",
        default=True,
    )

    bone_dir: EnumProperty(
        name="Bone Dir",
        description="Bone Dir, Heuristic for placing bones. Tries to make bones pretty",
        items=[
            ('BLENDER', 'Blender (best for re-importing)',
             'Good for re-importing glTFs exported from Blender. Bone tips are placed on their local +Y axis (in glTF space)'),
            ('TEMPERANCE', 'Temperance (average)',
             'Decent all-around strategy. A bone with one child has its tip placed on the local axis closest to its child.'),
            ('FORTUNE', 'Fortune (may look better, less accurate)',
             'Might look better than Temperance, but also might have errors. A bone with one child has its tip placed at its child’s root. Non-uniform scalings may get messed up though, so beware.')
        ],
        default='TEMPERANCE',
    )

    flip_forwards: BoolProperty(
        name="Flip Forwards Direction",
        description="Flip direction character is facing after import (+/-Y)",
        default=True,
    )

    def execute(self, context):
        bpy.ops.import_scene.gltf(
            filepath=self.filepath,
            import_pack_images=self.pack_images,
            merge_vertices=self.merge_vertices,
            import_shading=self.shading,
            guess_original_bind_pose=self.guess_original_bind_pose,
            bone_heuristic=self.bone_dir
        )

        if self.flip_forwards:
            obj = self.get_highest_parent_of_active_object()
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = Quaternion((0, 0, 0, 1))

        return {'FINISHED'}

    def menu_func_import(self, context):
        self.layout.operator(
            IMPORT_SCENE_OT_vrm_as_gltf.bl_idname,
            text="VRM as GLTF/GLB (*.vrm)",
            icon="ARMATURE_DATA"
        )

    def get_highest_parent_of_active_object(self):
        active_object = bpy.context.active_object

        if active_object:
            highest_parent = active_object
            while highest_parent.parent:
                highest_parent = highest_parent.parent

            return highest_parent

        return active_object

    @classmethod
    def register(cls):
        bpy.types.TOPBAR_MT_file_import.append(cls.menu_func_import)
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        bpy.types.TOPBAR_MT_file_import.remove(cls.menu_func_import)
        print("Unregistered: %s" % cls.bl_label)

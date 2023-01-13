import bpy
import os


class ProcessBatchOperator(bpy.types.Operator):
    """Execute batch commands on import directory"""
    bl_idname = "heat.process_batch"
    bl_label = "Process Batch"

    def execute(self, context):
        use_lookin_dir = context.scene.heat_export_use_lookin_directory_prop
        export_dir = context.scene.heat_export_directory_prop
        import_dir = context.scene.heat_import_directory_prop
        if use_lookin_dir:
            export_dir = import_dir

        export_fbx = context.scene.heat_multiexporter_export_fbx
        export_gltf = context.scene.heat_multiexporter_export_gltf

        for file in os.listdir(import_dir):
            # cleanup between files
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

            # import file
            print(file)
            file_path = import_dir + file
            if file.lower().endswith('.fbx'):
                print('processing fbx...')
                bpy.ops.import_scene.fbx(filepath=file_path)
            elif file.lower().endswith('.gltf') or file.lower().endswith('.glb'):
                print('processing gltf...')
                bpy.ops.import_scene.gltf(filepath=file_path)
            else:
                continue

            # run sanitization on files
            bpy.ops.object.uniform_scale_armature()
            bpy.ops.object.zero_armature_location()
            bpy.ops.object.zero_root()

            # export to export directory
            filename = os.path.splitext(file)[0]
            export_filepath = export_dir + filename
            if export_fbx:
                print('exporting fbx...')
                bpy.ops.export_scene.fbx(filepath=export_filepath+'.fbx', add_leaf_bones=False)
            if export_gltf:
                print('exporting gltf...')
                bpy.ops.export_scene.gltf(filepath=export_filepath)

            # cleanup between files
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=False)

        return {'FINISHED'}


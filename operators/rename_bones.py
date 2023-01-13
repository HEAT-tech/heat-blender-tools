import bpy
import csv
import os


class RenameBonesOperator(bpy.types.Operator):
    bl_idname = "object.rename_bones"
    bl_label = "Rename Bones"

    def execute(self, context):
        armature = bpy.data.armatures['Armature']

        this_dir = os.path.dirname(os.path.realpath(__file__))
        heat_bone_mappings_file = os.path.join(this_dir, '../heat_bone_mappings.csv')

        with open(heat_bone_mappings_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')

            from_schema_index = -1
            to_schema_index = -1
            if("AUTODETECT" in context.scene.rename_bones_from):
                from_schema = self.detect_armature_schema(armature, reader)
                csvfile.seek(0)
                from_schema_index = self.get_schema_csv_column_index_from_name(reader, from_schema)
            else:
                from_schema_index = self.get_schema_csv_column_index_from_name(reader, context.scene.rename_bones_from)
            csvfile.seek(0)
            to_schema_index = self.get_schema_csv_column_index_from_name(reader, context.scene.rename_bones_to)

            if from_schema_index == -1 or to_schema_index == -1:
                raise Exception("Invalid schema.")

            csvfile.seek(0)
            self.rename_armature_to_schema(armature, reader, from_schema_index, to_schema_index)

        return {'FINISHED'}


    def detect_armature_schema(self, armature, schema_list):
        schemas = ()
        for index, row in enumerate(schema_list):
            if index == 0:
                schemas = row
                continue
            if index > 5:
                break
            for col, bone_name in enumerate(row):
                if self.is_bone_in_armature(armature, bone_name):
                    return schemas[col]
        raise Exception("Armature schema could not be detected.")


    def rename_armature_to_schema(self, armature, schema_list, from_schema_index, to_schema_index):
        for index, row in enumerate(schema_list):
            if index == 0:
                continue
            if row[from_schema_index] == '' or row[to_schema_index] == '':
                continue

            self.rename_bone_in_armature(armature, row[from_schema_index], row[to_schema_index])
        print(from_schema_index)


    def is_bone_in_armature(self, armature, bone_name):
        for bone in armature.bones:
            if bone_name in bone.name:
                return True
        return False


    def rename_bone_in_armature(self, armature, bone_name, bone_rename_to, die_if_not_found=False):
        for bone in armature.bones:
            if bone_name in bone.name:
                bone.name = bone_rename_to
                return
        if die_if_not_found:
            raise Exception("Bone ({}) not found in armature.".format(bone_name))


    def get_schema_csv_column_index_from_name(self, schema_list, schema_name):
        for index, row in enumerate(schema_list):
            if index > 0:
                 raise Exception("Armature schema ({}) index not found.".format(schema_name))
            for col, schema in enumerate(row):
                if schema_name in schema:
                    return col


    @classmethod
    def register(cls):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        heat_bone_mappings_file = os.path.join(this_dir, '../heat_bone_mappings.csv')

        bone_schemas = ()
        with open(heat_bone_mappings_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            bone_schemas = next(reader)
            bone_schemas = tuple(map(lambda s: (s, s, s), bone_schemas))

        from_bone_schemas = (("AUTODETECT", "AUTODETECT", "AUTODETECT"),) + bone_schemas
        bpy.types.Scene.rename_bones_from = bpy.props.EnumProperty (
            name="From",
            description="Rename bones from the specified schema",
            items=from_bone_schemas,
            default=from_bone_schemas[0][0]
        )
        bpy.types.Scene.rename_bones_to = bpy.props.EnumProperty (
            name="To",
            description="Rename bones to the specified schema",
            items=bone_schemas,
            default=bone_schemas[0][0]
        )
        print("Registered: %s" % cls.bl_label)


    @classmethod
    def unregister(cls):
        del bpy.types.Scene.rename_bones_from
        del bpy.types.Scene.rename_bones_to
        print("Unregistered: %s" % cls.bl_label)

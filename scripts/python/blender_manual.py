# coding=utf-8
import bpy
import tempfile
from pathlib import Path, PurePath

TEMP_PATH = Path(tempfile.gettempdir(), 'houdini_blender')
BLEND_IMPORT_FILE = Path(TEMP_PATH, 'blend_import')
HOU_IMPORT_FILE = Path(TEMP_PATH, 'hou_import')

class HoudiniImportOp(bpy.types.Operator):
    bl_idname = "houdini.import"
    bl_label = "Paste"
    bl_description = 'Pastes yanked objects into the scene.'

    def execute(self, context):
        self.report({'INFO'}, f'This is {self.bl_idname}')
        file_present = file_exists(BLEND_IMPORT_FILE)
        if file_present == 1:
            self.report({'INFO'}, 'Nothing to import.')
            return {'CANCELLED'}
        if file_present == 2:
            self.report({'ERROR'}, 'List file is a directory.')
            return {'CANCELLED'}
        blender_import()

        file_paths = []
        missing = False

        with BLEND_IMPORT_FILE.open('r', encoding='utf-8') as source_file:
            for index, line in enumerate(source_file.readlines()):
                if not Path(line.strip()).exists():
                    missing = True
                else:
                    file_paths.append(line.strip())

        if len(file_paths) == 0:
            self.report({'WARNING'}, 'The import list appears to be empty.')
            return {'CANCELLED'}

        # Start the import process.
        for path in file_paths:
            bpy.ops.wm.alembic_import(filepath=path, relative_path=False, set_frame_range=False)

        return {'FINISHED'}


class HoudiniExportOp(bpy.types.Operator):
    bl_idname = "houdini.export"
    bl_label = "Yank"
    bl_description = 'Yanks selected objects to temporary directory.'

    def execute(self, context):
        print("HOUDINI_EXPORT")
        self.report({'INFO'}, f'This is {self.bl_idname}')
        return {'FINISHED'}


class HoudiniClipboardPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_Houdini'
    bl_label = 'Houdini'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Houdini'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(HoudiniImportOp.bl_idname, icon='PASTEDOWN')
        row.operator(HoudiniExportOp.bl_idname, icon='COPYDOWN')


classes = (
    HoudiniClipboardPanel,
    HoudiniImportOp,
    HoudiniExportOp,
)


def file_exists(file_path):
    if not file_path.exists():
        return 1
    if file_path.is_dir():
        return 2
    return 0


def blender_import():
    """Reads the list from file and imports it into the scene."""
    # Read blend_file
    pass


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()

# blender_manual.py
# Copyright (C) 2022  Artur J. Żarek (ajz3d)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import bpy
import tempfile
from pathlib import Path, PurePath
from uuid import uuid1
from . import common


TEMP_PATH = Path(tempfile.gettempdir(), 'houdini_blender')
BLEND_IMPORT_FILE = Path(TEMP_PATH, 'blend_import')
HOU_IMPORT_FILE = Path(TEMP_PATH, 'hou_import')

class HoudiniImportOp(bpy.types.Operator):
    bl_idname = "houdini.import"
    bl_label = "Paste"
    bl_description = 'Pastes yanked objects into the scene.'

    def execute(self, context):
        # Check if temporary directory exists and is not a file.
        if not common.temp_path_exists(common.TEMP_PATH):
            self.report({'INFO'}, 'Temp path is a file. Aborting.')
            return {'CANCELLED'}

        # Check if import file exists.
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

        if missing:
            self.report({'INFO'}, 'Done, but some files were missing.')

        return {'FINISHED'}


class HoudiniExportOp(bpy.types.Operator):
    bl_idname = "houdini.export"
    bl_label = "Yank"
    bl_description = 'Yanks selected objects to temporary directory.'

    def execute(self, context):
        # Check for temporary directory.
        if not common.temp_path_exists(common.TEMP_PATH):
            self.report({'INFO'}, 'Temp path is a file. Aborting.')
            return {'CANCELLED'}

        selection = bpy.context.selected_objects
        # Ignore objects that are not MESH.
        for obj in list(selection):
            if not obj.type == 'MESH':
                selection.remove(obj)

        if len(selection) == 0:
            self.report({'INFO'}, 'Nothing to export.')
            return {'FINISHED'}

        # Remove files specified in existing Houdini import list.
        if not common.purge_old_files(common.HOU_IMPORT_FILE):
            self.report({'ERROR'}, 'List file is a directory.')
            return {'CANCELLED'}

        # First, the file containing Alembics for Houdini import
        # needs do be removed and recreated.
        common.remove_file(common.HOU_IMPORT_FILE)

        # Construct path for exported Alembic file.
        filename = str(Path(common.TEMP_PATH, f'hou_{uuid1().hex}.abc').resolve())

        # Export selected objects.
        bpy.ops.wm.alembic_export(
            filepath=filename,
            selected=True,
            subdiv_schema=True
        )

        # Write exported path to Houdini import file.
        with common.HOU_IMPORT_FILE.open('a', encoding='utf-8') as target_file:
            target_file.write(f'{filename}\n')

        self.report({'INFO'}, 'Done exporting.')
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
        # TODO: Add a toggle that enables replacement of existing objects.
        # I'm not sure if it's possible as there seems to be no way of
        # knowing what objects reside in Alembic files.
        # TODO: Add a toggle which enables exporting objects to separate files.
        row.operator(HoudiniImportOp.bl_idname, icon='PASTEDOWN')
        row.operator(HoudiniExportOp.bl_idname, icon='COPYDOWN')


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


classes = (
    HoudiniClipboardPanel,
    HoudiniImportOp,
    HoudiniExportOp,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

# houdini_manual.py
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

import sys
from pathlib import Path
from uuid import uuid1
import hou
import common


def houdini_export():
    """Exports selected SOPs to Alembic files
    in operating system's temp path."""
    if not common.temp_path_exists(common.TEMP_PATH):
        hou.ui.setStatusMessage('Temp path is a file. Aborting.',
                                severity=hou.severityType.Error)
        return
    sops = hou.selectedNodes()

    if len(sops) == 0:
        hou.ui.setStatusMessage('Nothing to export.',
                                severity=hou.severityType.ImportantMessage)
        sys.exit(1)

    # Remove files specified in existing Blender import list.
    if not common.purge_old_files(common.BLEND_IMPORT_FILE):
        hou.ui.setStatusMessage('List file is a directory!',
                                severity=hou.severityType.Error)
        return

    # First, the file containing Alembics for Blender import
    # needs to be removed and recreated.
    common.remove_file(common.BLEND_IMPORT_FILE)

    # Configure and export selected SOPs.
    for sop in sops:
        abc_rop = sop.parent().createNode('rop_alembic')
        abc_rop.setFirstInput(sop)

        filename = sop.name() + '_' + uuid1().hex + '.abc'
        filepath = Path(common.TEMP_PATH, filename).resolve()

        abc_rop.setParms({
            'filename': str(filepath),
            'build_from_path': 1,
            'path_attrib': 'name'
        })

        hou.ui.setStatusMessage(f'Exporting {sop.name()}...')
        abc_rop.parm('execute').pressButton()
        abc_rop.destroy()

        # Write output file path to a file containing Blender's import list.
        with common.BLEND_IMPORT_FILE.open('a', encoding='utf-8') as target_file:
            target_file.write(f'{filepath}\n')

    hou.ui.setStatusMessage('Done exporting.')


def houdini_import():
    """Imports Alembic files to Houdini."""
    if not common.HOU_IMPORT_FILE.exists():
        hou.ui.setStatusMessage('Nothing to import.',
                                severity=hou.severityType.ImportantMessage)
        sys.exit(0)

    sops = hou.selectedNodes()

    # TODO: Allow for importing without the requirement of selecting a SOP.
    if len(sops) == 0:
        hou.ui.setStatusMessage('Select exactly one SOP',
                                severity=hou.severityType.Error)
        sys.exit(1)

    # Geometry will be imported near the first SOP. We don't need the rest.
    sop = sops[0]
    file_paths = []
    missing = False

    if common.HOU_IMPORT_FILE.is_dir():
        hou.ui.setStatusMessage('The import list is a directory!',
                                severity=hou.severityType.Error)
        return

    with common.HOU_IMPORT_FILE.open('r', encoding='utf-8') as source_file:
        for index, line in enumerate(source_file.readlines()):
            if not Path(line.strip()).exists():
                missing = True
            else:
                file_paths.append(line.strip())

    if len(file_paths) == 0:
        hou.ui.setStatusMessage('The import list appears to be empty.',
                                severity=hou.severityType.Error)
        return

    # Stores instances of nodes. Used in automatic layout.
    instances = []

    # Construct the network.
    # Special case for selected Alembic SOP and only one geometry file
    # to import. Replace filename with path to the new one.
    if sop.type().name() == 'alembic' and len(file_paths) == 1:
        abc = sop
        abc.setHardLocked(False)
        abc.setParms({
            'fileName': file_paths[0]
        })
        abc.parm('reload').pressButton()
        abc.setHardLocked(True)

    # Otherwise, create the whole network.
    else:
        for path in file_paths:
            abc = sop.parent().createNode('alembic')
            abc.setParms({
                'fileName': path
            })
            abc.setHardLocked(True)
            abc.setFirstInput(sop)
            instances.append(abc)

            unpack = sop.parent().createNode('unpack')
            unpack.setFirstInput(abc)
            instances.append(unpack)

            convert = sop.parent().createNode('convert')
            convert.setFirstInput(unpack)
            instances.append(convert)

            for node in instances:
                node.moveToGoodPosition(
                    move_inputs=False,
                    move_unconnected=False
                )

            abc.setFirstInput(None)

    if missing:
        hou.ui.setStatusMessage('Done, but one or more files were missing.',
                                severity=hou.severityType.Warning)
        return

    hou.ui.setStatusMessage('Done importing files.',
                            severity=hou.severityType.Message)


if __name__ == '__main__':
    print('Script must be launched from inside Houdini.')

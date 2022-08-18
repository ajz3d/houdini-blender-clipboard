import sys
from pathlib import PurePath, Path
import tempfile
from uuid import uuid1
import hou


TEMP_PATH = Path(tempfile.gettempdir(), 'houdini_blender')
BLEND_IMPORT_FILE = Path(TEMP_PATH, 'blend_import')
HOU_IMPORT_FILE = Path(TEMP_PATH, 'hou_import')


def houdini_export():
    """Exports selected SOPs to Alembic files
    in operating system's temp path."""
    verify_temp_path()

    sops = hou.selectedNodes()

    if len(sops) == 0:
        hou.ui.setStatusMessage('Nothing to export.',
                                severity=hou.severityType.Warning)
        sys.exit(1)

    # Remove files specified in existing Blender import list.
    purge_old_files()
    # First, the file containing Alembics for Blender import
    # needs to be removed and recreated.
    remove_file(BLEND_IMPORT_FILE)

    # Configure and export selected SOPs.
    for sop in sops:
        abc_rop = sop.parent().createNode('rop_alembic')
        abc_rop.setFirstInput(sop)

        filename = sop.name() + '_' + uuid1().hex + '.abc'
        filepath = Path(TEMP_PATH, filename).resolve()

        abc_rop.setParms({
            'filename': str(filepath),
            'build_from_path': 1,
            'path_attrib': 'name'
        })

        hou.ui.setStatusMessage(f'Exporting {sop.name()}...')
        abc_rop.parm('execute').pressButton()
        abc_rop.destroy()

        # Write output file path to a file containing Blender's import list.
        with BLEND_IMPORT_FILE.open('a', encoding='utf-8') as target_file:
            target_file.write(f'{filepath}\n')

    hou.ui.setStatusMessage('Done exporting.')


def houdini_import():
    """Imports Alembic files to Houdini."""
    if not Path.exists(HOU_IMPORT_FILE):
        hou.ui.setStatusMessage('Nothing to import.',
                                severity=hou.severityType.ImportantMessage)
        sys.exit(0)

    sops = hou.selectedNodes()

    # TODO: Allow for importing without the requirement of selecting a SOP.
    if len(sops) == 0:
        hou.ui.setStatusMessage('Select exactly one SOP',
                                severity=hou.severityType.Error)
        sys.exit(1)

    sop = sops[0]
    file_paths = []
    missing = False

    with HOU_IMPORT_FILE.open('r', encoding='utf-8') as source_file:
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
            node.moveToGoodPosition(move_inputs=False, move_unconnected=False)

        abc.setFirstInput(None)

    if missing:
        hou.ui.setStatusMessage('Done, but one or more files were missing.',
                                severity=hou.severityType.Warning)
        return

    hou.ui.setStatusMessage('Done importing files.',
                            severity=hou.severityType.Message)


def verify_temp_path():
    """Checks if temporary directory exists. Creates it if it doesn't."""
    if TEMP_PATH.exists():
        if TEMP_PATH.is_dir():
            return
        hou.ui.setStatusMessage('Temp path exists, but is a file.',
                                severity=hou.severityType.Error)
        sys.exit(1)
    else:
        TEMP_PATH.mkdir()


def purge_old_files():
    """Removes all files listed in BLEND_FILE."""
    if not BLEND_IMPORT_FILE.exists():
        return
    if BLEND_IMPORT_FILE.is_dir():
        hou.ui.setStatusMessage('File "blend_import" is a directory.',
                                severity=hou.severityType.Error)
        sys.exit(2)
    with BLEND_IMPORT_FILE.open('r', encoding='utf-8') as source_file:
        lines = source_file.readlines()
        for index, line in enumerate(lines):
            pure_path = PurePath(line.strip())
            # Safeguard which ensures that nothing
            # outside of system's tempdir is removed.
            if PurePath(tempfile.gettempdir()) in pure_path.parents:
                Path(pure_path).unlink(missing_ok=True)


def remove_file(file_path):
    """Removes a specific file or directory. Accepts pathlib.Path objects."""
    if file_path.exists():
        if file_path.is_dir():
            file_path.rmdir()
        else:
            file_path.unlink()


if __name__ == '__main__':
    print('Script must be launched from inside Houdini.')

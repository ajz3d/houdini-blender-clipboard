import sys
from pathlib import PurePath, Path
import tempfile
from uuid import uuid1
import hou


def houdini_export():
    """Exports selected SOPs to Alembic files
    in operating system's temp path."""

    temp_path = Path(tempfile.gettempdir(), 'houdini_blender')
    verify_temp_path(temp_path)

    sops = hou.selectedNodes()

    if len(sops) == 0:
        hou.ui.setStatusMessage('Nothing to export.',
                                severity=hou.severityType.Warning)
        sys.exit(1)

    blend_import_file = Path(temp_path, 'blend_import')

    # Remove files specified in existing Blender import list.
    purge_old_files(blend_import_file)
    # First, the file containing Alembics for Blender import
    # needs to be removed and recreated.
    remove_file(blend_import_file)

    # Configure and export selected SOPs.
    for sop in sops:
        abc_rop = sop.parent().createNode('rop_alembic')
        abc_rop.setFirstInput(sop)

        filename = sop.name() + '_' + uuid1().hex + '.abc'
        filepath = Path(temp_path, filename).resolve()

        abc_rop.setParms({
            'filename': str(filepath),
            'build_from_path': 1,
            'path_attrib': 'name'
        })

        hou.ui.setStatusMessage(f'Exporting {sop.name()}...')
        abc_rop.parm('execute').pressButton()
        abc_rop.destroy()

        # Write output file path to a file containing Blender's import list.
        blend_import_file = Path(temp_path, 'blend_import')
        with blend_import_file.open('a', encoding='utf-8') as target_file:
            target_file.write(f'{filepath}\n')

    hou.ui.setStatusMessage('Done exporting.')


def verify_temp_path(temp_path):
    """Checks if temporary directory exists. Creates it if it doesn't."""
    if Path.exists(temp_path):
        if Path.is_dir(temp_path):
            return
        hou.ui.setStatusMessage('Temp path exists, but is a file.',
                                severity=hou.severityType.Error)
        sys.exit(1)
    else:
        Path.mkdir(temp_path)


def purge_old_files(list_file):
    """Removes all files specified in a file passed as argument.
    Provided path must be absolute."""
    if not Path.exists(list_file):
        return

    with list_file.open('r', encoding='utf-8') as source_file:
        lines = source_file.readlines()
        for index, line in enumerate(lines):
            pure_path = PurePath(line.strip())
            # Safeguard which ensures that nothing
            # outside of system's tempdir is removed.
            if PurePath(tempfile.gettempdir()) in pure_path.parents:
                Path(pure_path).unlink()


def remove_file(file_path):
    """Removes a specific file or directory."""
    if Path.exists(file_path):
        if Path.is_dir(file_path):
            Path.rmdir(file_path)
        else:
            Path.unlink(file_path)


if __name__ == '__main__':
    houdini_export()

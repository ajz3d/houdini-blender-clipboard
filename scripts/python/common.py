# coding=utf-8
import tempfile
from pathlib import Path, PurePath


TEMP_PATH = Path(tempfile.gettempdir(), 'houdini_blender')
BLEND_IMPORT_FILE = Path(TEMP_PATH, 'blend_import')
HOU_IMPORT_FILE = Path(TEMP_PATH, 'hou_import')


def temp_path_exists(path: Path) -> bool:
    """Checks if temporary directory exists.

    Returns True if it does.
    Returns True if it doesn't, but first it creates the path.
    Returns False if path is a file."""
    # Old name was: verify_temp_path
    if path.exists():
        if not path.is_dir():
            return False
        return True
    else:
        path.mkdir()
        return True


def purge_old_files(path: Path) -> bool:
    """Removes all files listed in a file specified by path.

    Returns 0 if path exists and is a file or when it doesn't exist.
    Returns False if path is a directory."""
    if not path.exists():
        return True

    if path.is_dir():
        return False

    with path.open('r', encoding='utf-8') as source_file:
        lines = source_file.readlines()
        for index, line in enumerate(lines):
            pure_path = PurePath(line.strip())
            # Safeguard which ensures that nothing outside of system's tempdir
            # is removed. This is to prevent hypothetical malicious actors
            # from tampering with contents of files containing alembic paths
            # in such way, that files from outside of temp directory are
            # removed.
            if PurePath(tempfile.gettempdir()) in pure_path.parents:
                Path(pure_path).unlink(missing_ok=True)
    return True


def remove_file(path: Path) -> None:
    """Removes a specific file or directory."""
    if path.exists():
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()

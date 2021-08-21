import sys
from pathlib import Path
from typing import List
from autopdf.logs import get_logger
import os
import subprocess
from send2trash import send2trash, TrashPermissionError

log = get_logger(__name__)


def get_directories(root: Path) -> List[Path]:
    paths = []
    for path in Path(root).rglob('*/'):
        if path.is_file():
            continue
        paths.append(path)
    paths.reverse()
    return paths


def make_directories(paths: List[Path]):
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def substitute_root(x: List[Path], root: Path, new_root: Path) -> List[Path]:
    substituted = []
    for path in x:
        substituted.append(substitute_single_path(path, root, new_root))
    return substituted


def substitute_single_path(x: Path, root: Path, new_root: Path) -> Path:
    return new_root.joinpath(x.relative_to(root))


def create_env(persistence_root: Path, temporary_root: Path):
    """
    Env describes a replicate of the actual folder-structure where the newly converted pdfs are going to be stored.
    The OfficeFiles should be pasted inside the env and wherever it is located on the env (replica) the pdfs will be
    copied to the real location.
    :param persistence_root: Where the PDFs are stored
    :param temporary_root: Where the persistence_root folder structure should be replicated
    :return:
    """
    log.info('Creating ENV')
    autopdf_env_path = temporary_root.joinpath('.autopdf_env')
    is_resync = False
    if temporary_root.exists():
        if temporary_root.is_file():
            log.critical('temporary-root must be an empty directory, not a file')
            exit('Tried creating env in file')
        if autopdf_env_path.exists():
            log.info('Using existing env, resyncing...')
            is_resync = True
            delete_env(is_resync, temporary_root)
        else:
            if any(temporary_root.iterdir()):
                # Directory is not empty
                log.critical(f'Temporary-Root must be empty: {temporary_root}')
                exit('Tried creating env in non-empty directory')

    paths = get_directories(persistence_root)
    paths = substitute_root(paths, persistence_root, temporary_root)
    make_directories(paths)
    temporary_root.joinpath('.autopdf_env').touch(exist_ok=True)
    if is_resync:
        log.info(f'Resynced env: {temporary_root}')
    else:
        log.info(f'Created env: {temporary_root}')
    open_explorer(str(temporary_root))


def delete_env(is_resync: bool = False, path: Path = None):
    if not is_resync:
        if path is None:
            path = Path(sys.argv[2])
        log.info('Deleting Env')
    try:
        send2trash(path)
    except TrashPermissionError:
        log.warning(f'Could not delete temporary-root: {path}. Please remove by yourself')


def open_explorer(path):
    log.info(f'Opening filebrowser on {path}')
    # explorer would choke on forward slashes
    path = os.path.normpath(path)
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

    if os.path.isdir(path):
        subprocess.run([FILEBROWSER_PATH, path])
    elif os.path.isfile(path):
        subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])

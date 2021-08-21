import queue
import shutil
import subprocess
import time
from pathlib import Path
from queue import Queue
from typing import Union

from send2trash import send2trash, TrashPermissionError
from win10toast_click import ToastNotifier

import autopdf.config as config
from ..logs import get_logger
from ..sync import substitute_single_path, delete_env

log = get_logger(__name__)


class Converter:
    queue: Queue
    origin_root_path: Path
    target_root_path: Path
    file_types: list = [
        '.doc', '.dot', '.docx', '.dotx', '.docm', '.dotm', '.rtf', '.wpd',  # Word
        '.xls', '.xlsx', '.xlsm', '.xlsb', '.xlt', '.xltx', '.xltm', '.csv',  # Excel
        '.ppt', '.pptx', '.pptm', '.pps', '.ppsx', '.ppsm', '.pot', '.potx', '.potm',  # Powerpoint
        '.vsd', '.vsdx', '.vsdm', '.svg'  # Visio [Requires >= Visio 2013 for .svg, .vsdx and .vsdm support]
                                  '.pub',  # Publisher
        '.msg', '.vcf', '.ics',  # Outlook
        '.mpp'  # Project  [Requires Project >= 2010 for .mpp support]
        '.odt', 'odp', '.ods',  # OpenOffice
        '.pdf'  # Will just be copied
    ]
    error_codes: dict = {
        # Directly from 'https://github.com/cognidox/OfficeToPDF'
        0: 'Success',
        1: 'Failure',
        2: 'Unknown Error',
        4: 'File protected by password',
        8: 'Invalid arguments',
        16: 'Unable to open the source file',
        32: 'Unsupported file format',
        64: 'Source file not found',
        128: 'Output directory not found',
        256: 'The requested worksheet was not found',
        512: 'Unable to use an emtpy worksheet',
        1024: 'Unable to modify or open a protected PDF',
        2048: 'There is a problem calling an Office application',
        4096: 'There are no printers installed, so Office conversion can not proceed'
    }

    def __init__(self, queue: Queue, target_root_path: Path, origin_root_path: Path):
        self.queue = queue
        self.target_root_path = target_root_path
        self.origin_root_path = origin_root_path

    def __del__(self):
        def cleanup(path):
            def clup():
                delete_env(path=path)
            return clup
        self.toast('AutoPDF: Clean Up', 'Click here to clean up the env', duration=5,
                   callback_on_click=cleanup(self.origin_root_path), threaded=False)

    def handle(self):
        file_path: Path
        try:
            file_path = self.queue.get(block=False)
        except queue.Empty:
            time.sleep(config.queue_polling_interval)
            return

        if not file_path.exists():
            log.warning(f'Filepath does not exist anymore, must have been a temporary file')
            return

        if not self._verify_file_type(file_path):
            log.warning(f'Unsupported file type: {file_path}')
            self.toast('AutoPDF: Error', f'Unsupported File Type: {file_path.name}', duration=None)
            return
        success = self._convert(file_path)
        if not success:
            time.sleep(config.short_waiting_interval)
            return
        try:
            self._delete_file(file_path)
        except TrashPermissionError:
            log.warning(f"Couldn't move {file_path} to recycling bin")
            self.toast('AutoPDF: Error', f"Couldn't move {file_path.name} to recycling bin", duration=None)
        time.sleep(config.short_waiting_interval)

    def _convert(self, path: Path) -> bool:
        target_path = substitute_single_path(path, self.origin_root_path, self.target_root_path).with_suffix('.pdf')
        if target_path.exists():
            log.warning(f'File already exists: {target_path}')
            self.toast('AutoPDF: Warning / Error', f'File does already exist: {target_path.name}')
            return True

        if path.suffix == '.pdf':
            log.info(f'File already PDF: copying to {target_path}')
            self.toast('AutoPDF: already PDF', f'{path.name} does not need conversion - copying')
            shutil.copy2(path, target_path)
            return True

        log.info(f'Converting {path} to {target_path}')
        process = subprocess.run(
            [str(config.package_file_path.absolute()), f'/working_dir', f"{config.package_path.absolute()}",
             f"{path.absolute()}", f"{target_path.absolute()}"],
            stdout=subprocess.PIPE, universal_newlines=True
        )
        if process.returncode == 0:
            # TODO decide on duration
            log.info(f'Successfully converted: {path} to {target_path}')
            self.toast('Successfully converted', f'{path.name} to {target_path.name}')
            return True
        if process.returncode in self.error_codes.keys():
            log.warning(f'Error converting {path}: {self.error_codes[process.returncode]}')
            self.toast(f'AutoPDF: Error {process.returncode}', self.error_codes[process.returncode], duration=None)
            return False
        log.debug(f"{process.stdout}")

    @staticmethod
    def _delete_file(path: Path):
        log.info(f'Moving {path} to trash')
        send2trash(path)

    @staticmethod
    def toast(title: str, msg: str, duration: Union[int, None] = 5, callback_on_click=None, threaded: bool = True):
        # TODO add icon
        toaster = ToastNotifier()
        toaster.show_toast(
            title=title, msg=msg, icon_path=None, duration=duration, threaded=threaded,
            callback_on_click=callback_on_click
        )

    def _verify_file_type(self, path: Path) -> bool:
        if path.suffix in self.file_types:
            return True
        return False

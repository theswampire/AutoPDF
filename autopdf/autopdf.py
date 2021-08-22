import json
import signal
import sys
from pathlib import Path
from queue import Queue

import autopdf.config as config
from .convert import Converter
from .installer import install_app, check_package_existence
from .logs import get_logger
from .sync import create_env, FileSysListener

log = get_logger(__name__)


class AutoPDF:
    path_persistence_root: Path = None
    path_temp_root: Path = None

    queue: Queue
    fsl: FileSysListener
    converter: Converter

    def __init__(self, persistence_path: Path = None, temporary_path: Path = None, no_input: bool = False):
        log.info('Initializing AutoPDF')
        if not all((persistence_path, temporary_path)):
            self._load_config(no_input)
        success = install_app()
        if not success and not check_package_existence():
            log.critical('Vital package "OfficeToPDF" could not be installed')
            exit(1)

        signal.signal(signal.SIGINT, self.signal_handler)

        log.info(f'{self.path_persistence_root=}, {self.path_temp_root=}')

        create_env(self.path_persistence_root, self.path_temp_root)

        self.queue = Queue()
        self.fsl = FileSysListener(queue=self.queue, path=self.path_temp_root)
        self.converter = Converter(
            queue=self.queue, target_root_path=self.path_persistence_root, origin_root_path=self.path_temp_root
        )

        self.main_loop()

    def _load_config(self, no_input: bool = False):
        if config.config_path.exists():
            try:
                with open(config.config_path, 'r', encoding='UTF-8') as file:
                    data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = {}
            self.path_persistence_root = data.get('persistence_path', None)
            self.path_temp_root = data.get('temporary_path', None)

        if self.path_persistence_root is None:
            if no_input:
                raise ValueError('Configuration incomplete: persistence_path missing')
            self.path_persistence_root = Path(self._get_input('Root directory of your documents'))
        else:
            self.path_persistence_root = Path(self.path_persistence_root)

        if self.path_temp_root is None:
            if no_input:
                raise ValueError('Configuration incomplete: temporary_path missing')
            self.path_temp_root = Path(self._get_input('Root directory for temporary replica'))
        else:
            self.path_temp_root = Path(self.path_temp_root)

        with open(config.config_path, 'w', encoding='UTF-8') as file:
            json.dump({
                'persistence_path': str(self.path_persistence_root),
                'temporary_path': str(self.path_temp_root)
            }, file)

    @staticmethod
    def _get_input(prompt: str) -> str:
        print(prompt)
        while True:
            uip = input('\r > ')
            if uip != '':
                print()
                return uip

    @staticmethod
    def signal_handler(s, f):
        log.info('Shutting down')
        sys.exit(0)

    def main_loop(self):
        while True:
            self.converter.handle()

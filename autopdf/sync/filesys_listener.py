import time
from pathlib import Path
from queue import Queue
from typing import Union

from watchdog.events import FileSystemEventHandler, FileSystemEvent, EVENT_TYPE_CREATED
from watchdog.observers import Observer


class EventHandler(FileSystemEventHandler):
    queue: Queue

    def __init__(self, queue: Queue):
        super(EventHandler, self).__init__()
        self.queue = queue

    @staticmethod
    def _is_file(event: FileSystemEvent):
        path = Path(event.src_path)
        return path.is_file()

    def dispatch(self, event: FileSystemEvent):
        if event.event_type != EVENT_TYPE_CREATED:
            return
        if not self._is_file(event):
            return
        time.sleep(0.2)
        self.queue.put(Path(event.src_path))


class FileSysListener:
    observer: Observer
    event_handler: FileSystemEventHandler
    queue: Queue
    path: Path

    def __init__(self, queue: Queue, path: Union[Path, str]):
        if type(path) is str:
            path = Path(path)
        self.path = path
        self.queue = queue
        self.observer = Observer()
        self.event_handler = EventHandler(queue)

        self.observer.schedule(self.event_handler, str(self.path), recursive=True)
        self.observer.start()

    def __del__(self):
        self.observer.stop()
        self.observer.join()

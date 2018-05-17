import asyncio
import logging
import os
import sys

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

logger = logging.getLogger('reloader')
root_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class FileWatcher(PatternMatchingEventHandler):
    def __init__(self, patterns):
        super().__init__(patterns=patterns)

    def on_any_event(self, event):
        logger.info('File changed ({}) - reloading WatchGhost '.format(
            event.src_path))
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except OSError:
            logger.error('Error during WatchGhost restart')


class WatchdogObserver:
    def __init__(self, path):
        self.path = path
        self.patterns = (['*.conf', '*.css', '*.html', '*.py']
                         if self.path == root_path
                         else ['*'])
        self.event_handler = FileWatcher(self.patterns)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)

    async def observe(self):
        self.observer.start()
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


async def start_file_watcher(options):
    observers_list = []
    if options.debug:
        logger.info(
            'WatchGhost will be reloaded '
            'when Python, HTML and CSS files are modified')
        file_observer = WatchdogObserver(root_path)
        observers_list.append(file_observer.observe())
    if options.reload:
        logger.info(
            'WatchGhost will be reloaded '
            'when configuration files are modified')
        conf_observer = WatchdogObserver(options.config)
        observers_list.append(conf_observer.observe())
    await asyncio.wait(observers_list)

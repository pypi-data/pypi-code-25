from multiprocessing import Process,Lock
from queue import Queue

class FileManager(object):
    def __init__(self,file_name):
        self._queue = Queue()
        self._lock = Lock()
        self._file = open(file_name,'wb+')
        self._process = Process(targer=self._worker)
        self._process.start()
    def _worker(self):
        while True:
            data,pos = self._queue.get()
            self._lock.acquire()
            self._file.seek(pos)
            self._file.write()

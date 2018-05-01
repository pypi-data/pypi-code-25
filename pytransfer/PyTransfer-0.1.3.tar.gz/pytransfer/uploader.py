import os
from collections import deque

from pytransfer.progressbar import AdvancedTqdm


class FileStreamUploader:
    progressbar = None
    queue = deque()

    def __init__(self, filename, order):
        self.curr_tell = 0
        self.last = 0
        self.filename = filename
        self.order = order
        self.base_filename = os.path.basename(filename)
        self.file_size = os.stat(self.filename).st_size

        if self.queue_http_start:
            self.queue_http_start()

        if self.queue_file:
            self.queue_file()

        if self.queue_http_end:
            self.queue_http_end()

    def __iter__(self):
        return self

    def __next__(self):
        output = b''
        remaining_buffer_size = 8192

        if len(self.queue) == 0:
            raise StopIteration

        while remaining_buffer_size != 0:
            try:
                fragment = self.queue[0]
                if isinstance(fragment, bytes):
                    chunk = fragment[:remaining_buffer_size]
                    output += chunk
                    self.queue[0] = fragment[remaining_buffer_size:]

                    remaining_buffer_size -= len(chunk)

                    if len(self.queue[0]) == 0:
                        self.queue.popleft()
                else:
                    data = fragment.read(remaining_buffer_size)
                    if self.update_progress:
                        self.update_progress(len(data))
                        # self.curr_tell = fragment.tell()

                    if len(data) < remaining_buffer_size:
                        self.queue.popleft()

                    remaining_buffer_size -= len(data)
                    output += data
            except IndexError:
                return output
        return output

    def update_progress(self, buffer_size):
        if self.progressbar is None:
            self.progressbar = AdvancedTqdm(total=self.file_size, desc=self.base_filename, position=self.order, unit='B', unit_scale=True)

        self.progressbar.update(buffer_size)

        if self.progressbar.n == self.file_size:
            self.progressbar.refresh()

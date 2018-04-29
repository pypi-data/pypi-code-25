"""
Opens and reads in a thread, fills a local buffer with data
to avoid too many / limit thread calls.

This should avoid twisted blocking.
"""
import os

from twisted.internet import defer, threads


class TwistedIOBuffer(object):
    buffer_fill_increments = 5 * 1024 * 1024

    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.data = BytesIO()
        self.data_lock = defer.DeferredLock()

    @defer.inlineCallbacks
    def fill_buffer(self):
        current_buffer_obj = self.data
        data = yield threads.deferToThread(fileObject.read, self.buffer_fill_increments)

        yield self.data_lock.acquire()

        if current_buffer_obj == self.data:
            # we can avoid locking while reading
            # and not create a race condition with "seek"
            current_pos = self.data.tell()
            self.data.seek(0, SEEK_END)
            self.data.write(data)
            self.data.seek(current_pos)

        yield self.data_lock.release()

    @defer.inlineCallbacks
    def seek(self, offset, whence=os.SEEK_SET):
        yield self.data_lock.acquire()

        self.data = BytesIO()
        self.fileObject.seek(offset, whence)

        yield self.data_lock.release()


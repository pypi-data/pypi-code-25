import tempfile

from greenwich.io import MemFileIO


class SpooledCacheFile(tempfile.SpooledTemporaryFile):
    # cachedir = os.path.join('CACHE', 'images')
    cachedir = 'CACHE'

    # FIXME: Should duplicate constructor to avoid StringIO creation
    def __init__(self, dir=None, *args, **kwargs):
        dir = dir or self.cachedir
        super(SpooledCacheFile, self).__init__(dir=dir, *args, **kwargs)
        self._file = MemFileIO()


class SpooledFileIO(tempfile.SpooledTemporaryFile):
    """Temporary file wrapper switches from MemFileIO to an actual file when
    the maximum size is exceeded.
    """

    # def __init__(self, max_size=10 * 1024, *args, **kwargs):
    def __init__(self, max_size=10 * 2 ** 20, *args, **kwargs):
        tempfile.SpooledTemporaryFile.__init__(
            self, max_size=max_size, *args, **kwargs)
        self._file = MemFileIO()

    def _check(self, file):
        if self._rolled:
            return
        max_size = self._max_size
        # Seek to the end to be sure we really have a 0-length file.
        # if file.tell() == 0:
        if not file.tell():
            file.seek(0, 2)
        if max_size and file.tell() > max_size:
            self.rollover()

    def check_rollover(self):
    # def check_size(self):
        self._check(self._file)
        print('ROLLED:', self._rolled, self.name)

    def is_rolled(self):
        return self._rolled

    # FIXME: Drop this when MemFileIO has .getvalue() or not since we are
    # switching to NamedTemporaryFile.
    def rollover(self):
        if self._rolled:
            return
        file = self._file
        # newfile = self._file = tempfile.TemporaryFile(
        newfile = self._file = tempfile.NamedTemporaryFile(
            *self._TemporaryFileArgs)
        del self._TemporaryFileArgs
        # newfile.write(file.getvalue())
        # Seek first in absence of .getvalue()
        file.seek(0)
        newfile.write(file.read())
        # Why would the default implementation seek to the end? position is
        # already at the end after calling .write(), right?
        # newfile.seek(file.tell(), 0)
        # print 'NEWFILE:', newfile.tell()
        self._rolled = True

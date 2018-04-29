import os
import sys
from pathlib import Path
from iohandler import AbstractHandler, IOBridge
from typing import Iterable


class IOFileHandler(AbstractHandler):
    def read(self, reader):
        _reader = self._read_from_buffer_or_raw(reader)
        if self.validate_reader_type(_reader):
            return _reader.read()
        else:
            try:
                return reader.read()
            except AttributeError:
                sys.exit("ERR904:Invalid Stream.")

    def readlines(self, reader):
        _reader = self._read_from_buffer_or_raw(reader)
        if self.validate_reader_type(_reader):
            return _reader.readlines()
        else:
            raise AttributeError("ERR904:Invalid Stream.")

    @staticmethod
    def _read_from_buffer_or_raw(reader=None):
        if hasattr(reader, 'buffer'):
            return reader.buffer
        elif hasattr(reader, 'raw'):
            return reader.raw
        else:
            return False

    def write(self, file_object, data):
        """
        Thin wrapper for the IO write behaviour
        :rtype: bool
        """
        assert isinstance(data, Iterable)
        result = IOBridge.IOWriteBridge(file_object).write(data=data)
        return result

    def _open_(self, full_file_path_and_name, mode='rb'):
        f = Path(full_file_path_and_name)
        try:
            x = f.open(mode)
        except Exception as e:
            sys.exit("{1}:_open ops | ERR9_903. Open File Error.\nMessage: {0}".format(
                e.args[-1], type(self).__name__))
        if self.validate_reader_type(x):
            return x
        else:
            raise TypeError(type(x))
        pass

    def check_if_file_exists(self, full_file_path):
        f = Path(full_file_path)
        return f.is_file()

    def create_file(self, full_file_path_and_name):
        f = Path(full_file_path_and_name)
        f.touch(mode=0o777)

    def create_file_path(self, full_file_path, create_package=False):
        p = Path(full_file_path)
        if not p.exists():
            try:
                p.mkdir(mode=0o777, parents=True)
            except IOError as e:
                sys.exit("{1}:new_file | ERR9_901. Create DIR Error.\nMessage: {0}".format(
                    e.args[1], type(self).__name__))
        if create_package:
            try:
                f = Path(full_file_path + os.sep + '__init__.py')
                f.touch(mode=0o777)
            except IOError as e:
                sys.exit("{1}:new_file | ERR9_902. Create Package Error.\nMessage: {0}".format(
                    e.args[1], type(self).__name__))

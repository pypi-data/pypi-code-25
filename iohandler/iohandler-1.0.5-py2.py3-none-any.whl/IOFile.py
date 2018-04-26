import os
import sys

import io
from pathlib import Path
from iohandler import AbstractHandler, IOBridge
from typing import Iterable


class IOFileHandler(AbstractHandler):
    def read(self, reader):
        # type: (io.RawIOBase or io.BufferedIOBase or io.TextIOBase) -> object
        """
        Same interface as the _write below. Specifies
        """
        _reader = self._read_from_buffer(reader)
        if _reader:
            return _reader.read()
        else:
            try:
                return reader.read()
            except AttributeError:
                sys.exit("ERR904:Invalid Stream.")

    def readlines(self, reader):
        # type: (io.RawIOBase or io.BufferedIOBase or io.TextIOBase) -> object
        _reader = self._read_from_buffer(reader)
        if _reader:
            return _reader.readlines()
        else:
            raise AttributeError("ERR904:Invalid Stream.")
        pass

    @staticmethod
    def _read_from_buffer(reader=None):

        """
        :rtype: io.RawIOBase
        """
        if hasattr(reader, 'buffer'):
            return reader.buffer
        elif hasattr(reader, 'raw'):
            return reader.raw
        else:
            return False
        pass

    def write(self, file_object, data):
        """
        Thin wrapper for the IO write behaviour
        :type file_object: _io.
        :type data: Iterable
        :param file_object:
        :param data:
        :rtype: bool
        :return:
        """
        writer = IOBridge.IOWriteBridge(file_object).write(data=data)
        # file_object.writelines(data)
        return writer
        pass

    def _open_(self, full_file_path_and_name, mode='rb'):
        # type: (str, str) -> io.RawIOBase or io.BufferedIOBase or io.TextIOBase
        f = Path(full_file_path_and_name)
        try:
            x = f.open(mode)
        except Exception as e:
            sys.exit("{1}:_open ops | ERR9_903. Open File Error.\nMessage: {0}".format(
                e.args[-1], type(self).__name__))
        return x
        pass

    def check_if_file_exists(self, full_file_path):
        f = Path(full_file_path)
        return f.is_file()
        pass

    def check_if_path_exists(self, full_file_path):
        p = Path(full_file_path)
        return p.is_dir()
        pass

    def create_file(self, full_file_path_and_name):
        f = Path(full_file_path_and_name)
        f.touch(mode=0o777)
        pass

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
        pass

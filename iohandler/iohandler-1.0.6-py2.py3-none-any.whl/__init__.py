from abc import ABCMeta, abstractmethod
import sys
import os
import io


class AbstractHandler(object):
    """
    Interface defining shared behaviour of various IO handlers.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        super(AbstractHandler, self).__init__()

    @staticmethod
    def validate_reader_type(reader):
        if reader and (isinstance(reader, io.RawIOBase)
                       or isinstance(reader, io.BufferedIOBase)
                       or isinstance(reader, io.TextIOBase)):
            return True
        else:
            return False

    def open(self, file_name, file_path, create_file_if_none=True, create_package=False, mode='w'):
        # type: (str, str, bool, bool) -> [io.RawIOBase, io.BufferedIOBase,io.TextIOBase]
        if not self.check_if_file_exists(full_file_path=file_path + os.sep + file_name):
            if create_file_if_none:
                ret = self.new_file(file_name, file_path, create_package, mode)
            else:
                # print IOError("File Not Found. Not Instructed to create new.")
                sys.exit("{0}:open | ERR901. File Not Found. Not Instructed to create new.".format(
                    type(self).__name__))
        else:
            ret = self.open_existing_file(file_name=file_name, file_path=file_path, mode=mode)
        if self.validate_reader_type(ret):
            return ret
        else:
            raise TypeError()

    @abstractmethod
    def read(self, reader):
        # type: (io.RawIOBase or io.BufferedIOBase or io.TextIOBase) -> object
        """

        :param reader:
        :return:
        """

    @abstractmethod
    def readlines(self, reader):
        # type: (io.RawIOBase or io.BufferedIOBase or io.TextIOBase) -> object
        """
                Same interface as the _write below. Specifies
                :rtype: object
                :param reader: The IO object to read data from
                :type reader:_io.RawIOBase
        """

    @abstractmethod
    def write(self, file_object, data):
        # type: ([io.RawIOBase, io.BufferedIOBase, io.TextIOBase],any) -> bool
        """
        Thin wrapper for the IO write behaviour
        """

    def new_file(self, file_name, file_path, create_package=False, mode='w'):
        # type: (str, str, bool) -> [io.RawIOBase, io.BufferedIOBase, io.TextIOBase]
        try:
            self.create_file_path(file_path, create_package)
        except IOError as e:
            sys.exit("{1}:new_file | ERR902. Create File Path Error.\nMessage: {0}".format(
                e.args, type(self).__name__))
        try:
            self.create_file(file_path + file_name)
        except IOError as e:
            sys.exit("{1}:new_file | ERR903. Create File Error.\nMessage: {0}".format(
                e.args, type(self).__name__))

        result = self.open_existing_file(file_path, file_name, mode)
        if self.validate_reader_type(result):
            return result
        else:
            raise TypeError(result)

    def open_existing_file(self, file_path, file_name, mode='w'):
        # type: (str, str) -> [io.RawIOBase, io.BufferedIOBase, io.TextIOBase]
        """

        :rtype: _io.
        """
        try:
            return self._open_(file_path + os.sep + file_name, mode)
        except Exception as e:
            sys.exit("{1}:open_existing__file | ERR904. File Open Error.\nMessage: {0}".format(
                e.args, type(self).__name__))

    @abstractmethod
    def _open_(self, full_file_path_and_name, mode='w'):
        # type: (str, str) -> [io.RawIOBase, io.BufferedIOBase, io.TextIOBase]
        """

        :rtype: _io.
        """

    @abstractmethod
    def create_file_path(self, full_file_path, create_package=False):
        # type: (str) -> ()
        """

        :param full_file_path:
        :param create_package:
        :return:
        """

    @abstractmethod
    def create_file(self, full_file_path_and_name):
        # type: (str) -> ()
        """

        :param full_file_path_and_name:
        :return:
        """

    @abstractmethod
    def check_if_file_exists(self, full_file_path):
        # type: (str) -> bool

        """

        :rtype: bool
        """

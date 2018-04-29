"""
Decouple an abstraction from its implementation so that the two can vary
independently.
"""

import abc
import sys


class IOWriteBridge:
    """
    Define the abstraction's interface. Hold an implementor property that
    """

    def __init__(self, writer):
        """
        :param writer: The IO object to write data to
        :type writer:_io.IOBase
        """
        self._writer = writer
        if sys.version_info.major == 2:
            self._implementor = VerTwoWriteImplementor()
        else:
            self._implementor = VerThreeWriteImplementor()

    def write(self, data=None, ):
        """
        :param data:The data to be written
        :type data:object
        """
        try:
            return self._implementor.write(data=data, writer=self._writer)
        except IOError:
            sys.exit("E9700|Implementor Failure.")


class WriteImplementor(object):
    """
    Define the interface for implementation classes. This interface
    doesn't have to correspond exactly to Abstraction's interface; in
    fact the two interfaces can be quite different. Typically the
    Implementor interface provides only primitive operations, and
    Abstraction defines higher-level operations based on these
    primitives.
    """
    __metaclass__ = abc.ABCMeta

    def write(self, data=None, writer=None):
        """
        Same interface as the _write below. Specifies
        :rtype: bool
        :param data:The data to be written
        :type data:object
        :param writer: The IO object to write data to
        :type writer:_io.IOBase
        """
        if not writer.closed:
            try:
                return self._write(data=data, writer=writer)
            except Exception as e:
                sys.exit("E9701|Concrete Implementer Exception\n{}".format(e.args[-1]))
        else:
            sys.exit("E9702|Object lacks support for Write Operation(s)")

    @abc.abstractmethod
    def _write(self, data=None, writer=None):
        """
        :param data:The data to be written
        :type data:object
        :param writer: The IO object to write data to
        :type writer:_io.IOBase
        """


class VerTwoWriteImplementor(WriteImplementor):
    """
    Implement the Implementor interface and define its concrete
    implementation.
    """

    def _write(self, data=None, writer=None):
        """
        :param data:The data to be written
        :type data:object
        :param writer: The IO object to write data to
        :type writer:_io.IOBase
        """
        new_line = '\n'
        try:
            writer.writelines(str(data) + new_line)
            return True
        except IOError as e:
            sys.exit("E9703|Write Failure {}".format(e.args[-1]))


class VerThreeWriteImplementor(WriteImplementor):
    """
    Implement the Implementor interface and define its concrete
    implementation.
    """

    def _write(self, data=None, writer=None):
        """
        :param data:The data to be written
        :type data:object
        :param writer: The IO object to write data to
        :type writer:_io.IOBase
        """
        new_line = b'\n'
        if isinstance(data, str):
            v = data.encode(encoding='utf-8')
        elif isinstance(data, bytes):
            v = data
        else:
            v = bytes(str(data), encoding='utf-8')
        try:
            writer.writelines([v.rstrip(new_line) + new_line])
            return True
        except Exception as e:
            sys.exit("E9703|Write Failure {}".format(e.args[-1]))

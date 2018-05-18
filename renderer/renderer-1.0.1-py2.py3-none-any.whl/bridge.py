"""
Decouple an abstraction from its implementation so that the two can vary
independently.
"""

import abc
import sys
from datetime import datetime

if sys.version_info.major == 2:
    try:
        from singledispatch import singledispatch
    except ImportError:
        singledispatch = None
        sys.stderr.write("E:909. singledispatch module missing. Run `pip install singledispatch`")
        sys.exit(1)
else:
    try:
        from functools import singledispatch
    except ImportError:
        singledispatch = None
        sys.stderr.write("E:909. singledispatch module missing. Run `pip install singledispatch`")
        sys.exit(1)


class Renderer(object):
    """
    Define the abstraction's interface.
    Maintain a reference to an object of type Implementor.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, target='code', imp=None):
        """

        """
        super(Renderer, self).__init__()
        self._target = target
        self._imp = imp
        pass

    @abc.abstractmethod
    def _file(self, val):
        pass

    @abc.abstractmethod
    def _code(self, val):
        pass

    @abc.abstractmethod
    def _db(self, val):
        pass

    @abc.abstractmethod
    def _stdout(self, val):
        pass

    def render(self, val):
        try:
            probable_op = getattr(self, "_{}".format(self._target.lstrip('_')))
        except AttributeError:
            probable_op = getattr(self, "_file")
        if not callable(probable_op):
            invert_op = '_code'
        else:
            invert_op = probable_op
        result = invert_op.__call__(self._imp.serialize(val))
        return result


class Implementor(object):
    """
    Define the interface for implementation classes. This interface
    doesn't have to correspond exactly to Abstraction's interface; in
    fact the two interfaces can be quite different. Typically the
    Implementor interface provides only primitive operations, and
    Abstraction defines higher-level operations based on these
    primitives.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Implementor, self).__init__()
        self.version_specific_registrations()
        self.serialize.register(datetime, self._datetime)
        self.serialize.register(list, self._list)
        self.serialize.register(dict, self._dict)

    @abc.abstractmethod
    def serialize(self, data):
        """

        :rtype: any
        """
        pass

    @abc.abstractmethod
    def version_specific_registrations(self):
        pass

    def _datetime(self, val):
        """
         datetime obj to byte(str) conversion.
        :type val: datetime
        :return String representation of the datetime object
        :rtype :str
        """
        return val.isoformat() + "Z"

    def _list(self, val):
        """
        list to byte(str) conversion
        :type val:list
        :return String representation of the list object
        :rtype :str
        """
        result = "["
        result += ",".join(self.serialize(v) for v in val)
        result += "]"
        return result
        pass

    def _dict(self, val):
        """
        dict to byte(str) conversion
        :type val:dict
        :return String representation of the dict object
        :rtype :str
        """
        import json
        dump = " ".join(
            k + "=" + json.dumps(v, ensure_ascii=False, default=self.serialize) for k, v in
            (val.items()))
        return self.serialize(dump)


def main():
    # print(result)
    pass


if __name__ == "__main__":
    main()

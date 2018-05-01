#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division

__version__ = "$Revision: 1.6 $"

# Copyright 2005-2007 Michael M. Hoffman <hoffman+software@ebi.ac.uk>
try:
    from exceptions import AttributeError
except ImportError:
    from builtins import AttributeError
import csv
from functools import partial
import sys

import textinput

class SurrogateNotInitedError(AttributeError):
    pass

class Surrogate(object):
    """
    the data is stored in _data

    >>> list1 = [0, 1, 2, 3]
    >>> list2 = [4, 5, 6, 7]
    >>> surrogate = Surrogate(list1)
    >>> surrogate.reverse()
    >>> list1
    [3, 2, 1, 0]
    >>> surrogate._data = list2
    >>> surrogate.append(8)
    >>> list2
    [4, 5, 6, 7, 8]
    """
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        if name == "_data":
            raise SurrogateNotInitedError(name)
        else:
            try:
                return getattr(self._data, name)
            except SurrogateNotInitedError:
                raise SurrogateNotInitedError(name)

def _update_not_None(src, dest, *args):
    for key in args:
        value = src[key]
        if value is not None:
            dest[key] = value

    return dest

class _UnixTabDialect(csv.excel_tab):
    """
    just like excel-tab, but line terminator is "\n" not "\r\n"
    """
    lineterminator = "\n"
csv.register_dialect("unix-tab", _UnixTabDialect)

#### both list and dict

class _ReaderWriter(object):
    def __init__(self, *args, **kwargs):
        self._started = False
        self.set_reader(*args, **kwargs)
        self.set_writer()

    def set_reader(self, *args, **kwargs):
        if self._started:
            raise RuntimeError("iteration already started")

        self._reader_args = args
        self._reader_kwargs = kwargs

    def set_writer(self, *args, **kwargs):
        if self._started:
            raise RuntimeError("iteration already started")

        self._writer_args = args
        self._writer_kwargs = kwargs

    def __iter__(self):
        if self._started:
            raise RuntimeError("iteration already started")

        self._started = True

        reader = self._reader_factory(*self._reader_args,
                                      **self._reader_kwargs)
        writer = reader.writer(*self._writer_args, **self._writer_kwargs)

        for row in reader:
            yield row
            writer.writerow(row)

def io(readerwriter_factory, filenames=None, inplace=None, backup=None,
       *args, **kwargs):
    input_kwargs = _update_not_None(locals(), {},
                                    "filenames", "inplace", "backup")

    f = textinput.lines(**input_kwargs)
    return readerwriter_factory(f, *args, **kwargs)

#### list versions

class ListReader(Surrogate):
    def __init__(self, csvfile, dialect=None, *args, **kwargs):
        self.dialect = dialect

        if dialect is None:
            dialect = "excel-tab"

        data = csv.reader(csvfile, dialect, *args, **kwargs)
        Surrogate.__init__(self, data)

    def __iter__(self):
        return iter(self._data)

    def writer(self, csvfile=sys.stdout, dialect=None, *args, **kwargs):
        if dialect is None:
            dialect = self.dialect

        if dialect is None:
            dialect = "unix-tab"

        return ListWriter(csvfile, dialect, *args, **kwargs)

def ListWriter(csvfile=sys.stdout, dialect="unix-tab", *args, **kwargs):
    "factory function"
    return csv.writer(csvfile, dialect, *args, **kwargs)

class ListReaderWriter(_ReaderWriter):
    _reader_factory = ListReader

listio = partial(io, ListReaderWriter)
listinput = partial(io, ListReader)

#### dict versions

class DictReader(csv.DictReader):
    """
    >>> text = "foodstuff source\n" \
    ... "ham pigs\n" \
    ... "spam factories\n"
    >>> reader = DictReader(text, delimiter=" ")
    >>> row = reader.next()
    >>> row["source"]
    'pigs'
    >>> row["foodstuff"]
    'ham'
    """
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect=None, *args, **kwargs):
        self.dialect = dialect

        if dialect is None:
            dialect = "excel-tab"

        iterator = iter(f)
        if fieldnames is None:
            self.header = True
            fieldnames = next(csv.reader(iterator, dialect, *args, **kwargs))
        else:
            self.header = False

        csv.DictReader.__init__(self, iterator, fieldnames,
                                restkey, restval, dialect, *args, **kwargs)

    def writer(self, f=sys.stdout, fieldnames=None, restval=None,
               extrasaction="raise", dialect=None, header=None,
               prepend=[], append=[], *args, **kwargs):
        if fieldnames is None:
            fieldnames = self.fieldnames

        fieldnames = prepend + fieldnames + append

        if restval is None:
            restval = self.restval
            if restval is None:
                restval = ""

        if dialect is None:
            dialect = self.dialect

        if dialect is None:
            dialect = "unix-tab"

        if header is None:
            header = self.header

        return DictWriter(f, fieldnames, restval, extrasaction,
                          dialect, header, *args, **kwargs)

class DictWriter(csv.DictWriter):
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="unix-tab", header=True, *args, **kwargs):
        csv.DictWriter.__init__(self, f, fieldnames, restval, extrasaction,
                                dialect, *args, **kwargs)

        if header:
            self.writeheader()

    def writeheader(self):
        self.writerow(dict((fieldname, fieldname)
                           for fieldname in self.fieldnames))

class DictReaderWriter(_ReaderWriter):
    _reader_factory = DictReader

    def __init__(self, f=None, fieldnames=None, restkey=None, restval=None,
                 extrasaction=None, dialect=None, header=None, prepend=None,
                 append=None, *args, **kwargs):
        super(DictReaderWriter, self).__init__(*args, **kwargs)

        _update_not_None(locals(), self._reader_kwargs,
                         "f", "fieldnames", "restkey", "restval", "dialect")
        _update_not_None(locals(), self._writer_kwargs,
                         "extrasaction", "header", "prepend", "append")

dictio = partial(io, DictReaderWriter)
dictinput = partial(io, DictReader)

def dictoutput(f=sys.stdout, *args, **kwargs):
    """
    can create as many as necessary
    """
    return DictWriter(f, *args, **kwargs)

#### __main__

def main(args):
    pass

def _test(*args, **kwargs):
    import doctest
    doctest.testmod(sys.modules[__name__], *args, **kwargs)

if __name__ == "__main__":
    if __debug__:
        _test()
    sys.exit(main(sys.argv[1:]))
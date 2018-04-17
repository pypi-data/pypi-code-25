from __future__ import absolute_import, division, print_function, unicode_literals

from six import BytesIO

from ._formats import ImageFormat


class Tile(object):
    def __init__(self, coordinates, indices, tile_shape=None, sha256=None, extras=None):
        self.coordinates = dictvalues_to_tuples(coordinates)
        self.indices = dictvalues_to_tuples(indices)
        self.tile_shape = tile_shape
        self.sha256 = sha256
        self.extras = {} if extras is None else extras

        self.tile_format = None
        self._source_fh_callable = None
        self._numpy_array = None
        self._name_or_url = None

    def _load(self):
        if self._source_fh_callable is not None:
            assert self._numpy_array is None
            with self._source_fh_callable() as src_fh:
                self._numpy_array = self.tile_format.reader_func(src_fh)
            self._source_fh_callable = None
            self.tile_format = ImageFormat.NUMPY

    @property
    def numpy_array(self):
        self._load()
        return self._numpy_array

    @numpy_array.setter
    def numpy_array(self, numpy_array):
        if self.tile_shape is not None:
            assert self.tile_shape == numpy_array.shape

        self._source_fh_callable = None
        self._numpy_array = numpy_array
        self.tile_format = ImageFormat.NUMPY

    def set_source_fh_callable(self, source_fh_callable, tile_format):
        self._source_fh_callable = source_fh_callable
        self._numpy_array = None
        self.tile_format = tile_format

    def write(self, dst_fh):
        """
        Write the contents of this tile out to a given file handle.
        """
        import numpy

        self._load()

        numpy.save(dst_fh, self._numpy_array)

    def copy(self, dst_fh):
        """
        Write the contents of this tile out to a given file handle, in the original file format provided.
        """
        if self._source_fh_callable is not None:
            assert self._numpy_array is None
            with self._source_fh_callable() as src_fh:
                data = src_fh.read()
                self._numpy_array = self.tile_format.reader_func(BytesIO(data))
                dst_fh.write(data)
            self._source_fh_callable = None
            self.tile_format = ImageFormat.NUMPY
        else:
            raise RuntimeError("copy can only be called on a tile that hasn't been decoded.")


def dictvalues_to_tuples(d):
    """
    Given a dictionary mapping names to values that may either be iterables or not, return a new dictionary with the
    same contents, except the values that are iterables are converted to tuples.
    """
    result = dict()
    for name, value in d.items():
        try:
            iter(value)
            result[name] = tuple(value)
        except TypeError:
            result[name] = value
    return result

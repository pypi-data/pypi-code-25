import datetime
import typing

import numpy  # type: ignore

from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('ndarray', 'matrix')

# This implementation is based on these guidelines:
# https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html

N = typing.TypeVar('N', bound='ndarray')
M = typing.TypeVar('M', bound='matrix')


# TODO: We could implement also __array_ufunc__ and adapt metadata as well after in-place changes to data?
class ndarray(numpy.ndarray):
    """
    Extended `numpy.ndarray` with the ``metadata`` attribute.

    Parameters
    ----------
    input_array : Sequence
        Anything array-like to create an instance from. Including lists and standard numpy arrays.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the array, or top-level metadata to be updated
        if ``input_array`` is another instance of this array class.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the array.
    """

    def __new__(cls: typing.Type[N], input_array: typing.Sequence, metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> N:
        array = numpy.asarray(input_array).view(cls)

        # If "input_array" was already our ndarray, we copy input metadata over here because
        # "__array_finalize__" has no access to input metadata and we cannot do it there.
        if isinstance(input_array, ndarray):
            array.metadata = input_array.metadata.set_for_value(array)

        if metadata is not None:
            array.metadata = array.metadata.update((), metadata, source=source, timestamp=timestamp)

        return array

    def __array_finalize__(self, obj: typing.Any) -> None:
        # If metadata attribute already exists.
        if hasattr(self, 'metadata'):
            return

        # During "matrix" construction this method is called with "obj" an instance of "ndarray" but
        # without "metadata" attribute yet set, so we fall through to else clause and just
        # temporary set an empty metadata object.
        if obj is not None and isinstance(obj, ndarray) and hasattr(obj, 'metadata'):
            # TODO: We could adapt (if this is after a slice) metadata instead of just copying?
            self.metadata: metadata_base.DataMetadata = obj.metadata.set_for_value(self)
        else:
            self.metadata = metadata_base.DataMetadata(for_value=self)

    def __reduce__(self) -> typing.Tuple:
        reduced = list(super().__reduce__())

        reduced[2] = {
            'numpy': reduced[2],
            'metadata': self.metadata,
        }

        return tuple(reduced)

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state['numpy'])

        self.metadata = state['metadata'].set_for_value(self)


class matrix(numpy.matrix, ndarray):
    """
    Extended `numpy.matrix` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Union[Sequence, str]
        Anything array-like to create an instance from. Including lists and standard numpy arrays and matrices.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the matrix, or top-level metadata to be updated
        if ``data`` is another instance of this matrix class.
    dtype : Union[dtype, str]
         Data type of the output matrix.
    copy : bool
       If ``data`` is already an ``ndarray``, then this flag determines
       whether the data is copied (the default), or whether a view is
       constructed.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the matrix.
    """

    def __new__(cls: typing.Type[M], data: typing.Union[typing.Sequence, str], metadata: typing.Dict[str, typing.Any] = None,
                dtype: typing.Union[numpy.dtype, str] = None, copy: bool = True, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> M:
        mx = numpy.matrix.__new__(cls, data=data, dtype=dtype, copy=copy)

        if not isinstance(mx, cls):
            mx = mx.view(cls)

        # mx seems to always have "metadata" attribute at this point.
        if metadata is not None:
            mx.metadata = mx.metadata.update((), metadata, source=source, timestamp=timestamp)

        return mx

    def __array_finalize__(self, obj: typing.Any) -> None:
        numpy.matrix.__array_finalize__(self, obj)
        ndarray.__array_finalize__(self, obj)


typing.Sequence.register(numpy.ndarray)  # type: ignore


def ndarray_serializer(obj: ndarray) -> dict:
    data = {
        'metadata': obj.metadata,
        'numpy': obj.view(numpy.ndarray),
    }

    if type(obj) is not ndarray:
        data['type'] = type(obj)

    return data


def ndarray_deserializer(data: dict) -> ndarray:
    array = data['numpy'].view(data.get('type', ndarray))
    array.metadata = data['metadata'].set_for_value(array)
    return array


def matrix_serializer(obj: matrix) -> dict:
    data = {
        'metadata': obj.metadata,
        'numpy': obj.view(numpy.matrix),
    }

    if type(obj) is not matrix:
        data['type'] = type(obj)

    return data


def matrix_deserializer(data: dict) -> matrix:
    mx = data['numpy'].view(data.get('type', matrix))
    mx.metadata = data['metadata'].set_for_value(mx)
    return mx


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        ndarray, 'd3m.ndarray',
        custom_serializer=ndarray_serializer,
        custom_deserializer=ndarray_deserializer,
    )

    pyarrow_lib._default_serialization_context.register_type(
        matrix, 'd3m.matrix',
        custom_serializer=matrix_serializer,
        custom_deserializer=matrix_deserializer,
    )

import datetime
import typing

import numpy  # type: ignore
import pandas  # type: ignore
from pandas.core.dtypes import common as pandas_common  # type: ignore

from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('DataFrame', 'SparseDataFrame')

# This implementation is based on these guidelines:
# https://pandas.pydata.org/pandas-docs/stable/internals.html#subclassing-pandas-data-structures

D = typing.TypeVar('D', bound='DataFrame')


class DataFrame(pandas.DataFrame):
    """
    Extended `pandas.DataFrame` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Sequence
        Anything array-like to create an instance from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the data frame, or top-level metadata to be updated
        if ``data`` is another instance of this data frame class.
    index : Union[Index, Sequence]
        Index to use for resulting frame.
    columns : Union[Index, Sequence]
        Column labels to use for resulting frame.
    dtype : Union[dtype, str, ExtensionDtype]
        Data type to force.
    copy : bool
        Copy data from inputs.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the data frame.
    """

    @property
    def _constructor(self) -> type:
        return DataFrame

    def __init__(self, data: typing.Sequence = None, metadata: typing.Dict[str, typing.Any] = None, index: typing.Union[pandas.Index, typing.Sequence] = None,
                 columns: typing.Union[pandas.Index, typing.Sequence] = None, dtype: typing.Union[numpy.dtype, str, pandas_common.ExtensionDtype] = None, copy: bool = False,
                 *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        # If not a constructor call to this exact class, then a child constructor
        # is responsible to call a pandas constructor.
        if type(self) is DataFrame:
            pandas.DataFrame.__init__(self, data=data, index=index, columns=columns, dtype=dtype, copy=copy)

        if isinstance(data, DataFrame):
            self.metadata: metadata_base.DataMetadata = data.metadata.set_for_value(self)

            if metadata is not None:
                self.metadata: metadata_base.DataMetadata = self.metadata.update((), metadata, source=source, timestamp=timestamp)
        else:
            self.metadata: metadata_base.DataMetadata = metadata_base.DataMetadata(metadata, for_value=self, source=source, timestamp=timestamp)

    def __finalize__(self: D, other: typing.Any, method: str = None, **kwargs: typing.Any) -> D:
        self = super().__finalize__(other, method, **kwargs)

        # Merge operation: using metadata of the left object.
        if method == 'merge':
            obj = other.left
        # Concat operation: using metadata of the first object.
        elif method == 'concat':
            obj = other.objs[0]
        else:
            obj = other

        if isinstance(obj, DataFrame):
            # TODO: We could adapt (if this is after a slice) metadata instead of just copying?
            self.metadata: metadata_base.DataMetadata = obj.metadata.set_for_value(self)
        # "metadata" attribute should already be set in "__init__",
        # but if we got here without it, let's set it now.
        elif not hasattr(self, 'metadata'):
            self.metadata: metadata_base.DataMetadata = metadata_base.DataMetadata(for_value=self)

        return self

    def __getstate__(self) -> dict:
        state = super().__getstate__()

        state['metadata'] = self.metadata

        return state

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)

        self.metadata = state['metadata'].set_for_value(self)


class SparseDataFrame(pandas.SparseDataFrame, DataFrame):
    """
    Extended `pandas.SparseDataFrame` with the ``metadata`` attribute.

    Parameters
    ----------
    data : Sequence
        Anything array-like to create an instance from.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the sparse data frame, or top-level metadata to be updated
        if ``data`` is another instance of this sparse data frame class.
    index : Union[Index, Sequence]
        Index to use for resulting frame.
    columns : Union[Index, Sequence]
        Column labels to use for resulting frame.
    default_kind : str
        Default sparse kind for converting `Series` to `SparseSeries`.
    default_fill_value : float
        Default fill_value for converting `Series` to `SparseSeries`.
    dtype : Union[dtype, str, ExtensionDtype]
        Data type to force.
    copy : bool
        Copy data from inputs.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the sparse data frame.
    """

    @property
    def _constructor(self) -> type:
        return SparseDataFrame

    def __init__(self, data: typing.Sequence = None, metadata: typing.Dict[str, typing.Any] = None, index: typing.Union[pandas.Index, typing.Sequence] = None,
                 columns: typing.Union[pandas.Index, typing.Sequence] = None, default_kind: str = None, default_fill_value: float = None,
                 dtype: typing.Union[numpy.dtype, str, pandas_common.ExtensionDtype] = None, copy: bool = False,
                 *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        pandas.SparseDataFrame.__init__(self, data=data, index=index, columns=columns, default_kind=default_kind, default_fill_value=default_fill_value, dtype=dtype, copy=copy)
        DataFrame.__init__(self, data=data, metadata=metadata, index=index, columns=columns, source=source, timestamp=timestamp)

    # We have to define "__getstate__" because "SparseDataFrame" defines it as well,
    # so our "__getstate__" in "DataFrame" is not called.
    def __getstate__(self) -> dict:
        state = super().__getstate__()

        state['metadata'] = self.metadata

        return state


typing.Sequence.register(pandas.DataFrame)  # type: ignore


def dataframe_serializer(obj: DataFrame) -> dict:
    data = {
        'metadata': obj.metadata,
        'pandas': pandas.DataFrame(obj),
    }

    if type(obj) is not DataFrame:
        data['type'] = type(obj)

    return data


def dataframe_deserializer(data: dict) -> DataFrame:
    df = data.get('type', DataFrame)(data['pandas'])
    df.metadata = data['metadata'].set_for_value(df)
    return df


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        DataFrame, 'd3m.dataframe',
        custom_serializer=dataframe_serializer,
        custom_deserializer=dataframe_deserializer,
    )

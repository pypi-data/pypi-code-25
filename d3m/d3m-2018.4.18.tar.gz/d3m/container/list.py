import datetime
import typing

from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('List',)

# We see "List" as immutable for the purpose of inputs and outputs and this is why covariance is
# a reasonable choice here. Callers should make "List" immutable before passing it as inputs.
# See: PEP 484 and 483 for more details about immutability and covariance
# See: https://github.com/Stewori/pytypes/issues/21
# See: https://gitlab.com/datadrivendiscovery/metadata/issues/1
T = typing.TypeVar('T', covariant=True)
L = typing.TypeVar('L', bound='List')

# Workaround for Python 3.6.3 and older. This allows copy.copying generics.
# See: https://github.com/python/typing/commit/cca58eeb2d257e200bee37baeae80c29a49f0106
if hasattr(typing.GenericMeta, '__copy__'):
    del typing.GenericMeta.__copy__


class List(typing.List[T]):
    """
    Extended Python standard `typing.List` with the ``metadata`` attribute.

    You can provide a type of elements. One way is as a subclass::

        class IntList(List[int]):
            ...

        l = IntList(...)

    Another is inline::

        l = List[int](...)

    If you do not provide a type, type is assumed to be `typing.Any`.

    You should use only standard data and container types as its elements.

    Metadata attribute is immutable, so if you ``update`` it, you should reassign it back::

        l.metadata = l.metadata.update(...)

    `List` is mutable, but this can introduce issues during runtime if a primitive
    modifies its inputs directly. Callers of primitives are encouraged
    to make it immutable to assure such behavior is detected/prevented,
    and primitives should copy inputs to a mutable `List` before modifying it.

    Parameters
    ----------
    iterable : Iterable
        Optional initial values for the list.
    metadata : typing.Dict[str, typing.Any]
        Optional initial metadata for the top-level of the list, or top-level metadata to be updated
        if ``iterable`` is another instance of this list class.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference.
    timestamp : datetime
        A timestamp of initial metadata.

    Attributes
    ----------
    metadata : DataMetadata
        Metadata associated with the list.
    """

    def __init__(self, iterable: typing.Iterable = (), metadata: typing.Dict[str, typing.Any] = None, *, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        super().__init__(iterable)

        if isinstance(iterable, List):
            self.metadata = iterable.metadata.set_for_value(self)

            if metadata is not None:
                self.metadata = self.metadata.update((), metadata, source=source, timestamp=timestamp)
        else:
            self.metadata = metadata_base.DataMetadata(metadata, for_value=self, source=source, timestamp=timestamp)

    def copy(self: L) -> L:
        # Metadata is copied from provided iterable.
        return type(self)(iterable=self)

    @typing.overload  # type: ignore
    def __getitem__(self, i: int) -> T:
        ...

    def __getitem__(self: L, s: slice) -> L:  # type: ignore
        if isinstance(s, slice):
            lst = type(self)(iterable=super().__getitem__(s))
            # TODO: We could do a slice in metadata as well?
            #       Update dimensions. Slice per-element metadata.
            lst.metadata = self.metadata.set_for_value(lst)
            return lst
        else:
            return super().__getitem__(s)

    def __add__(self: L, x: typing.List[T]) -> L:
        lst = type(self)(iterable=super().__add__(x))
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        lst.metadata = self.metadata.set_for_value(lst)
        return lst

    def __iadd__(self: L, x: typing.Iterable[T]) -> L:
        super().__iadd__(x)
        # TODO: We could do add in metadata as well?
        #       Update dimensions. Maybe x is List and has metadata.
        #       What to do if both have conflicting ALL_ELEMENTS metadata?
        return self

    def __mul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__mul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.set_for_value(lst)
        return lst

    def __rmul__(self: L, n: int) -> L:
        lst = type(self)(iterable=super().__rmul__(n))
        # TODO: We could do multiply in metadata as well?
        #       Update dimensions. Multiplicate per-element metadata.
        lst.metadata = self.metadata.set_for_value(lst)
        return lst

    def __setstate__(self, state: dict) -> None:
        self.__dict__ = state

        # During deep-copying metadata is not available in state in all calls to this method.
        if hasattr(self, 'metadata'):
            self.metadata = self.metadata.set_for_value(self)

    def __reduce__(self) -> typing.Tuple[typing.Callable, typing.Tuple, dict]:
        reduced = super().__reduce__()
        return reduced


def list_serializer(obj: List) -> dict:
    data = {
        'metadata': obj.metadata,
        'list': list(obj),
    }

    if type(obj) is not List:
        data['type'] = type(obj)

    return data


def list_deserializer(data: dict) -> List:
    data_list = data.get('type', List)(data['list'])
    data_list.metadata = data['metadata'].set_for_value(data_list)
    return data_list


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        List, 'd3m.list',
        custom_serializer=list_serializer,
        custom_deserializer=list_deserializer,
    )

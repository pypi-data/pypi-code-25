#!/usr/bin/env
# encoding: utf-8
"""
Author:     Daniel Boeckenhoff
Mail:       daniel.boeckenhoff@ipp.mpg.de

core of tfields library
contains numpy ndarray derived bases of the tfields package
"""
import tfields.bases
import numpy as np
from contextlib import contextmanager
from collections import Counter
np.seterr(all='warn', over='raise')


def rank(tensor):
    """
    Tensor rank
    """
    return len(tensor.shape) - 1


def dim(tensor):
    """
    Manifold dimension
    """
    if rank(tensor) == 0:
        return 1
    return tensor.shape[1]


class AbstractNdarray(np.ndarray):
    """
    All tensors and subclasses should derive from AbstractNdarray.
    AbstractNdarray implements all the inheritance specifics for np.ndarray
    Whene inheriting, three attributes are of interest:
        __slots__ (list of str): If you want to add attributes to
            your AbstractNdarray subclass, add the attribute name to __slots__
        __slotDefaults__ (list): if __slotDefaults__ is None, the
            defaults for the attributes in __slots__ will be None
            other values will be treaded as defaults to the corresponding
            arg at the same position in the __slots__ list.
        __slotDtype__ (list of types): for the conversion of the
            args in __slots__ to numpy arrays. None values mean no
            conversion.

    Args:
        array (array-like): input array
        **kwargs: arguments corresponding to __slots__
    TODO:
        equality check
    """
    __slots__ = []
    __slotDefaults__ = []
    __slotDtypes__ = []
    __slotSetters__ = []

    def __new__(cls, array, **kwargs):  # pragma: no cover
        raise NotImplementedError("{clsType} type must implement '__new__'"
                                  .format(clsType=type(cls)))

    def __array_finalize__(self, obj):
        if obj is None:
            return
        for attr in self._iterSlots():
            setattr(self, attr, getattr(obj, attr, None))

    def __array_wrap__(self, out_arr, context=None):
        return np.ndarray.__array_wrap__(self, out_arr, context)

    @classmethod
    def _iterSlots(cls, skipCache=True):
        return [att for att in cls.__slots__ if att != '_cache']

    @classmethod
    def _updateSlotKwargs(cls, kwargs, skipCache=True):
        """
        set the defaults in kwargs according to __slotDefaults__
        and convert the kwargs according to __slotDtypes__
        """
        slotDefaults = cls.__slotDefaults__ + \
            [None] * (len(cls.__slots__) - len(cls.__slotDefaults__))
        slotDtypes = cls.__slotDtypes__ + \
            [None] * (len(cls.__slots__) - len(cls.__slotDtypes__))
        for attr, default, dtype in zip(cls.__slots__, slotDefaults, slotDtypes):
            if attr == '_cache':
                continue
            if attr not in kwargs:
                kwargs[attr] = default
            if dtype is not None:
                kwargs[attr] = np.array(kwargs[attr], dtype=dtype)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            index = self.__slots__.index(name)
            try:
                setter = self.__slotSetters__[index]
            except IndexError:
                setter = None
            if setter is not None:
                value = setter(value)
        super(AbstractNdarray, self).__setattr__(name, value)

    def __reduce__(self):
        """
        important for pickling
        Examples:
            >>> from tempfile import NamedTemporaryFile
            >>> import pickle
            >>> import tfields

            Build a dummy scalar field
            >>> from tfields import Tensors, TensorFields
            >>> scalars = Tensors([0, 1, 2])
            >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
            >>> scalarField = TensorFields(vectors, scalars, coordSys='cylinder')

            Save it and restore it
            >>> outFile = NamedTemporaryFile(suffix='.pickle')

            >>> pickle.dump(scalarField,
            ...             outFile)
            >>> _ = outFile.seek(0)

            >>> sf = pickle.load(outFile)
            >>> sf.coordSys == 'cylinder'
            True
            >>> sf.fields[0][2] == 2.
            True

        """
        # Get the parent's __reduce__ tuple
        pickled_state = super(AbstractNdarray, self).__reduce__()

        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + tuple([getattr(self, slot) for slot in
                                              self._iterSlots()])

        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        """
        important for unpickling
        """
        # Call the parent's __setstate__ with the other tuple elements.
        super(AbstractNdarray, self).__setstate__(state[0:-len(self._iterSlots())])

        # set the __slot__ attributes
        for i, slot in enumerate(reversed(self._iterSlots())):
            index = -(i + 1)
            setattr(self, slot, state[index])


class Tensors(AbstractNdarray):
    """
    Set of tensors with the same basis.
    TODO:
        all slot args should be protected -> _base
    Args:
        tensors: np.ndarray or AbstractNdarray subclass
    Examples:
        >>> from tfields import Tensors
        >>> import numpy as np

        Initialize a scalar range
        >>> scalars = Tensors([0, 1, 2])
        >>> scalars.rank == 0
        True

        Initialize vectors
        >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> vectors.rank == 1
        True
        >>> vectors.dim == 3
        True
        >>> assert vectors.coordSys == 'cartesian'

        Initialize the Levi-Zivita Tensor
        >>> matrices = Tensors([[[0, 0, 0], [0, 0, 1], [0, -1, 0]],
        ...                     [[0, 0, -1], [0, 0, 0], [1, 0, 0]],
        ...                     [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]])
        >>> matrices.shape == (3, 3, 3)
        True
        >>> matrices.rank == 2
        True
        >>> matrices.dim == 3
        True

        Initializing in different start coordinate system
        >>> cyl = Tensors([[5, np.arctan(4. / 3.), 42]], coordSys='cylinder')
        >>> assert cyl.coordSys == 'cylinder'
        >>> cyl.coordinateTransform('cartesian')
        >>> assert cyl.coordSys == 'cartesian'
        >>> cart = cyl
        >>> assert round(cart[0, 0], 10) == 3.
        >>> assert round(cart[0, 1], 10) == 4.
        >>> assert cart[0, 2] == 42

        Initialize with copy constructor keeps the coordinate system
        >>> with vectors.tempCoordSys('cylinder'):
        ...     vectCyl = Tensors(vectors)
        ...     assert vectCyl.coordSys == vectors.coordSys
        >>> assert vectCyl.coordSys == 'cylinder'

        You can demand a special dimension.
        >>> _ = Tensors([[1, 2, 3]], dim=3)
        >>> _ = Tensors([[1, 2, 3]], dim=2)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Incorrect dimension: 3 given, 2 demanded.

        The dimension argument (dim) becomes necessary if you want to initialize
        an empty array
        >>> _ = Tensors([])  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Empty tensors need dimension parameter 'dim'.
        >>> Tensors([], dim=7)
        Tensors([], shape=(0, 7), dtype=float64)

    """
    __slots__ = ['coordSys']
    __slotDefaults__ = ['cartesian']
    __slotSetters__ = [tfields.bases.getCoordSystemName]

    def __new__(cls, tensors, **kwargs):
        ''' copy constructor '''
        if issubclass(type(tensors), cls):
            obj = tensors.copy()
            coordSys = kwargs.pop('coordSys', None)
            if kwargs:
                raise AttributeError("In copy constructor only 'coordSys' "
                                     "attribute is supported. Kwargs {kwargs} "
                                     "are not consumed"
                                     .format(**locals()))
            if coordSys is not None:
                obj.coordinateTransform(coordSys)
            return obj

        dtype = kwargs.pop('dtype', np.float64)
        order = kwargs.pop('order', None)
        dim = kwargs.pop('dim', None)

        ''' process empty inputs '''
        if len(tensors) == 0:
            if dim is not None:
                tensors = np.empty((0, dim))
            else:
                raise ValueError("Empty tensors need dimension "
                                 "parameter 'dim'.")

        tensors = np.asarray(tensors, dtype=dtype, order=order)
        obj = tensors.view(cls)

        ''' check dimension(s) '''
        for d in obj.shape[1:]:
            if not d == obj.dim:
                raise ValueError("Dimensions are inconstistent.")
        if dim is not None:
            if dim != obj.dim:
                raise ValueError("Incorrect dimension: {obj.dim} given,"
                                 " {dim} demanded."
                                 .format(**locals()))

        ''' update kwargs with defaults from slots '''
        cls._updateSlotKwargs(kwargs)

        ''' set kwargs to slots attributes '''
        for attr in kwargs:
            if attr not in cls._iterSlots():
                raise AttributeError("Keywordargument {attr} not accepted "
                                     "for class {cls}".format(**locals()))
            setattr(obj, attr, kwargs[attr])

        return obj

    @classmethod
    def merged(cls, *objects, **kwargs):
        """
        Factory method
        Merges all tensor inputs to one tensor

        Examples:
            >>> import numpy as np
            >>> from tfields import Tensors
            >>> import tfields.bases
            >>> vecA = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
            >>> vecB = Tensors([[5, 4, 1]], coordSys=tfields.bases.cylinder)
            >>> vecC = Tensors([[5, 4, 1]], coordSys=tfields.bases.cylinder)
            >>> merge = Tensors.merged(vecA, vecB, vecC, [[2, 0, 1]])
            >>> assert merge.coordSys == 'cylinder'

        """

        ''' get most frequent coordSys or predefined coordSys '''
        coordSys = kwargs.get('coordSys', None)
        if coordSys is None:
            bases = []
            for t in objects:
                try:
                    bases.append(t.coordSys)
                except:
                    pass
            # get most frequent coordSys
            coordSys = sorted(bases, key=Counter(bases).get, reverse=True)[0]
            kwargs['coordSys'] = coordSys

        ''' transform all raw inputs to cls type with correct coordSys. Also
        automatically make a copy of those instances that are of the correct
        type already.'''
        objects = [cls(t, **kwargs) for t in objects]

        ''' check rank and dimension equality '''
        if not len(set([t.rank for t in objects])) == 1:
            raise TypeError("Tensors must have the same rank for merging.")
        if not len(set([t.dim for t in objects])) == 1:
            raise TypeError("Tensors must have the same dimension for merging.")

        ''' merge all objects '''
        remainingObjects = objects[1:] or []
        tensors = objects[0]

        for i, obj in enumerate(remainingObjects):
            tensors = np.append(tensors, obj, axis=0)
        return cls.__new__(cls, tensors, **kwargs)

    @property
    def rank(self):
        """
        Tensor rank
        """
        return rank(self)

    @property
    def dim(self):
        """
        Manifold dimension
        """
        return dim(self)

    def coordinateTransform(self, coordSys):
        """
        Args:
            coordSys (str)

        Examples:
            >>> import numpy as np
            >>> from tfields import Tensors

            CARTESIAN to SPHERICAL
            >>> t = Tensors([[1, 2, 2], [1, 0, 0], [0, 0, -1], [0, 0, 1], [0, 0, 0]])
            >>> t.coordinateTransform('spherical')

            r
            >>> assert t[0, 0] == 3

            phi
            >>> assert t[1, 1] == 0.
            >>> assert t[2, 1] == 0.

            theta is 0 at (0, 0, 1) and pi at (0, 0, -1)
            >>> assert round(t[1, 2], 10) == round(np.pi / 2, 10)
            >>> assert t[2, 2] == np.pi
            >>> assert t[3, 2] == 0.

            theta is defined 0 for R == 0
            >>> assert t[4, 0] == 0.
            >>> assert t[4, 2] == 0.


            CARTESIAN to CYLINDER
            >>> tCart = Tensors([[3, 4, 42], [1, 0, 0], [0, 1, -1], [-1, 0, 1], [0, 0, 0]])
            >>> tCyl = tCart.copy()
            >>> tCyl.coordinateTransform('cylinder')
            >>> assert tCyl.coordSys == 'cylinder'

            R
            >>> assert tCyl[0, 0] == 5
            >>> assert tCyl[1, 0] == 1
            >>> assert tCyl[2, 0] == 1
            >>> assert tCyl[4, 0] == 0

            Phi
            >>> assert round(tCyl[0, 1], 10) == round(np.arctan(4. / 3), 10)
            >>> assert tCyl[1, 1] == 0
            >>> assert round(tCyl[2, 1], 10) == round(np.pi / 2, 10)
            >>> assert tCyl[1, 1] == 0

            Z
            >>> assert tCyl[0, 2] == 42
            >>> assert tCyl[2, 2] == -1

            >>> tCyl.coordinateTransform('cartesian')
            >>> assert tCyl.coordSys == 'cartesian'
            >>> assert tCyl[0, 0] == 3

        """
        #           scalars                 empty             already there
        if self.rank == 0 or self.shape[0] == 0 or self.coordSys == coordSys:
            self.coordSys = coordSys
            return

        self[:] = tfields.bases.transform(self, self.coordSys, coordSys)
        self.coordSys = coordSys

    @contextmanager
    def tempCoordSys(self, coordSys):
        """
        Temporarily change the coordSys to another coordSys and change it back at exit
        This method is for cleaner code only.
        No speed improvements go with this.
        Args:
            see coordinateTransform
        Examples:
            >>> import tfields
            >>> p = tfields.Tensors([[1,2,3]], coordSys=tfields.bases.SPHERICAL)
            >>> with p.tempCoordSys(tfields.bases.CYLINDER):
            ...     assert p.coordSys == tfields.bases.CYLINDER
            >>> assert p.coordSys == tfields.bases.SPHERICAL

        """
        baseBefore = self.coordSys
        if baseBefore == coordSys:
            yield
        else:
            self.coordinateTransform(coordSys)

            yield

            self.coordinateTransform(baseBefore)


class TensorFields(Tensors):
    """
    Discrete Tensor Field

    Examples:
        >>> from tfields import Tensors, TensorFields
        >>> scalars = Tensors([0, 1, 2])
        >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> scalarField = TensorFields(vectors, scalars)
        >>> scalarField.rank
        1
        >>> scalarField.fields[0].rank
        0
        >>> vectorField = TensorFields(vectors, vectors)
        >>> vectorField.fields[0].rank
        1
        >>> vectorField.fields[0].dim
        3
        >>> multiField = TensorFields(vectors, scalars, vectors)
        >>> multiField.fields[0].dim
        1
        >>> multiField.fields[1].dim
        3

    """
    __slots__ = ['coordSys', 'fields']

    def __new__(cls, tensors, *fields, **kwargs):
        obj = super(TensorFields, cls).__new__(cls, tensors, **kwargs)
        obj.fields = list(fields)
        return obj

    def coordinateTransform(self, coordSys):
        super(TensorFields, self).coordinateTransform(coordSys)
        for field in self.fields:
            field.coordinateTransform(coordSys)
        

class TensorMaps(TensorFields):
    """
    Args:
        tensors: see Tensors class
        *fields (Tensors): see TensorFields class
        **kwargs:
            coordSys ('str'): see Tensors class
            maps (array-like): indices indicating a connection between the
                tensors at the respective index positions
    Examples:
        >>> from tfields import Tensors, TensorMaps
        >>> scalars = Tensors([0, 1, 2])
        >>> vectors = Tensors([[0, 0, 0], [0, 0, 1], [0, -1, 0]])
        >>> mesh = TensorMaps(vectors, scalars, maps=[[[0, 1, 2], [0, 1, 2]],
        ...                                           [[1, 1, 1], [2, 2, 2]]])
        >>> mesh.maps
        array([[[0, 1, 2],
                [0, 1, 2]],
        <BLANKLINE>
               [[1, 1, 1],
                [2, 2, 2]]])

    """
    __slots__ = ['coordSys', 'fields', 'maps']
    __slotDtypes__ = [None, None, int]


if __name__ == '__main__':  # pragma: no cover
    import doctest
    doctest.testmod()
    # doctest.run_docstring_examples(TensorMaps, globals())

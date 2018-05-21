"""
This module contains types related to examples, such as RankedExample,
LabeledExample and Example itself.
"""
from collections import namedtuple
from scipy.sparse import spmatrix
import numpy as np
from future.utils import string_types
import numbers

"""
Example equality is determined by comparing an object's id and type. Otherwise, we would need to compare the
spmatrices by value, because new instances are created when deserialization is performed.
Spmatrix comparison is expensive, thus we use id and require clients to use unique ids for examples.
"""
example_equality = lambda x, y: (x.id == y.id and type(x) == type(y))
example_hash = lambda ex: hash((ex.id,))


class Example(namedtuple('Example', ['id', 'features'])):
    """Example is a single item from an unlabeled dataset.
    """

    def __new__(cls, id, features):
        assert isinstance(id, string_types)
        assert isinstance(features, spmatrix)
        return super(Example, cls).__new__(cls, id, features)

    def __eq__(self, other):
        return example_equality(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return example_hash(self)


class LabeledExample(namedtuple('LabeledExample', Example._fields + ('label', 'sampling_probability'))):
    def __new__(cls, id, features, label, sampling_probability):
        assert isinstance(id, string_types)
        assert isinstance(sampling_probability, numbers.Number)
        # labels should be strictly numpy arrays and not numpy matrices. This is because some operations
        # like multiplication * are redefined for matrices and give different results. Some other operations
        # also don't work for matrices, e.g. np.unique()
        assert isinstance(label, numbers.Number) or (isinstance(label, np.ndarray) and
                                                     not isinstance(label, np.matrixlib.defmatrix.matrix))
        if isinstance(label, np.ndarray):
            assert np.all((label == 0) | (label == 1)), "Multilabel labels should be an array of 0s or 1s"
        return super(LabeledExample, cls).__new__(cls, id, features, label, sampling_probability)

    def __eq__(self, other):
        return example_equality(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return example_hash(self)


class RankedExample(namedtuple('RankedExample', Example._fields + ('confidence',))):
    def __new__(cls, id, features, confidence):
        assert isinstance(id, string_types)
        assert isinstance(confidence, numbers.Number)
        return super(RankedExample, cls).__new__(cls, id, features, confidence)

    def __eq__(self, other):
        return example_equality(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return example_hash(self)

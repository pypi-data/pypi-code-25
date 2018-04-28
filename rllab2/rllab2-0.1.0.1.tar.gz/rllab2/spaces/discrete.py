from __future__ import absolute_import
from .base import Space
import numpy as np
from rllab2.misc import special
from rllab2.misc import ext


class Discrete(Space):
    u"""
    {0,1,...,n-1}
    """

    def __init__(self, n):
        self._n = n

    @property
    def n(self):
        return self._n

    def sample(self):
        return np.random.randint(self.n)

    def contains(self, x):
        x = np.asarray(x)
        return x.shape == () and x.dtype.kind == u'i' and x >= 0 and x < self.n

    def __repr__(self):
        return u"Discrete(%d)" % self.n

    def __eq__(self, other):
        return self.n == other.n

    def flatten(self, x):
        return special.to_onehot(x, self.n)

    def unflatten(self, x):
        return special.from_onehot(x)

    def flatten_n(self, x):
        return special.to_onehot_n(x, self.n)

    def unflatten_n(self, x):
        return special.from_onehot_n(x)

    @property
    def flat_dim(self):
        return self.n

    def weighted_sample(self, weights):
        return special.weighted_sample(weights, xrange(self.n))

    @property
    def default_value(self):
        return 0

    def new_tensor_variable(self, name, extra_dims):
        if self.n <= 2 ** 8:
            return ext.new_tensor(
                name=name,
                ndim=extra_dims+1,
                dtype=u'uint8'
            )
        elif self.n <= 2 ** 16:
            return ext.new_tensor(
                name=name,
                ndim=extra_dims+1,
                dtype=u'uint16'
            )
        else:
            return ext.new_tensor(
                name=name,
                ndim=extra_dims+1,
                dtype=u'uint32'
            )

    def __eq__(self, other):
        if not isinstance(other, Discrete):
            return False
        return self.n == other.n

    def __hash__(self):
        return hash(self.n)
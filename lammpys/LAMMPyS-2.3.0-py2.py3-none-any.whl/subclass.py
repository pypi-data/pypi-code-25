import numpy as np


class Atoms(np.ndarray):

    def __new__(cls, input_array, pi):
        obj = np.asarray(input_array).view(cls)
        obj.pi = pi
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.pi = getattr(obj, 'pi', None)

    def p(self, p):
        return self[self.pi[p]]


atoms = np.array([[1, 2], [3, 4]])
atoms = Atoms(atoms, pi={'x': 0, 'y': 1})




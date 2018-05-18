"""Simulating synapse objects more efficiently at higher orders."""

import numpy as np
from scipy.signal import cont2discrete

from nengo.synapses import LinearFilter

__all__ = ['SimulatorMixin']


class StateSpaceStep(LinearFilter.Step):

    def __init__(self, ss, output):
        self.output = output
        self._A, self._B, self._C, self._D = ss
        self._x = np.zeros(len(self._A))[:, None]

    def __call__(self, signal):
        u = signal[None, :]
        self._x = np.dot(self._A, self._x) + np.dot(self._B, u)
        self.output[...] = np.dot(self._C, self._x) + np.dot(self._D, u)


class SimulatorMixin(object):

    # assumes mixed in with an instance that has attributes: den, ss, analog

    def make_step(self, dt, output, method='zoh'):
        if len(self.den) <= 2:  # fall back to reference implementation
            # note: bug in nengo where subclasses don't pass method=method
            return super(SimulatorMixin, self).make_step(dt, output)
        A, B, C, D = self.ss
        if self.analog:
            A, B, C, D, _ = cont2discrete((A, B, C, D), dt, method=method)
        return StateSpaceStep((A, B, C, D), output)

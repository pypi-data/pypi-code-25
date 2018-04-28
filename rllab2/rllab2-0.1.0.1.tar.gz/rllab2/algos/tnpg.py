from __future__ import absolute_import
from rllab2.algos.npo import NPO
from rllab2.optimizers.conjugate_gradient_optimizer import ConjugateGradientOptimizer
from rllab2.misc import ext


class TNPG(NPO):
    u"""
    Truncated Natural Policy Gradient.
    """

    def __init__(
            self,
            optimizer=None,
            optimizer_args=None,
            **kwargs):
        if optimizer is None:
            default_args = dict(max_backtracks=1)
            if optimizer_args is None:
                optimizer_args = default_args
            else:
                optimizer_args = dict(default_args, **optimizer_args)
            optimizer = ConjugateGradientOptimizer(**optimizer_args)
        super(TNPG, self).__init__(optimizer=optimizer, **kwargs)

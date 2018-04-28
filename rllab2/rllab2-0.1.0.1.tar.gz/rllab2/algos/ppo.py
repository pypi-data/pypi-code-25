from __future__ import absolute_import
from rllab2.optimizers.penalty_lbfgs_optimizer import PenaltyLbfgsOptimizer
from rllab2.algos.npo import NPO
from rllab2.core.serializable import Serializable


class PPO(NPO, Serializable):
    u"""
    Penalized Policy Optimization.
    """

    def __init__(
            self,
            optimizer=None,
            optimizer_args=None,
            **kwargs):
        Serializable.quick_init(self, locals())
        if optimizer is None:
            if optimizer_args is None:
                optimizer_args = dict()
            optimizer = PenaltyLbfgsOptimizer(**optimizer_args)
        super(PPO, self).__init__(optimizer=optimizer, **kwargs)

from __future__ import division
from __future__ import absolute_import
import numpy as np

from rllab2.core.serializable import Serializable
from rllab2.envs.base import Step
from rllab2.envs.mujoco.mujoco_env import MujocoEnv
from rllab2.misc import autoargs
from rllab2.misc import logger
from rllab2.misc.overrides import overrides


# states: [
# 0: z-coord,
# 1: x-coord (forward distance),
# 2: forward pitch along y-axis,
# 6: z-vel (up = +),
# 7: xvel (forward = +)


class HopperEnv(MujocoEnv, Serializable):

    FILE = u'hopper.xml'

    @autoargs.arg(u'alive_coeff', type=float,
                  help=u'reward coefficient for being alive')
    @autoargs.arg(u'ctrl_cost_coeff', type=float,
                  help=u'cost coefficient for controls')
    def __init__(
            self,
            alive_coeff=1,
            ctrl_cost_coeff=0.01,
            *args, **kwargs):
        self.alive_coeff = alive_coeff
        self.ctrl_cost_coeff = ctrl_cost_coeff
        super(HopperEnv, self).__init__(*args, **kwargs)
        Serializable.quick_init(self, locals())

    @overrides
    def get_current_obs(self):
        return np.concatenate([
            self.model.data.qpos[0:1].flat,
            self.model.data.qpos[2:].flat,
            np.clip(self.model.data.qvel, -10, 10).flat,
            np.clip(self.model.data.qfrc_constraint, -10, 10).flat,
            self.get_body_com(u"torso").flat,
        ])

    @overrides
    def step(self, action):
        self.forward_dynamics(action)
        next_obs = self.get_current_obs()
        lb, ub = self.action_bounds
        scaling = (ub - lb) * 0.5
        vel = self.get_body_comvel(u"torso")[0]
        reward = vel + self.alive_coeff - \
            0.5 * self.ctrl_cost_coeff * np.sum(np.square(action / scaling))
        state = self._state
        notdone = np.isfinite(state).all() and \
            (np.abs(state[3:]) < 100).all() and (state[0] > .7) and \
            (abs(state[2]) < .2)
        done = not notdone
        return Step(next_obs, reward, done)

    @overrides
    def log_diagnostics(self, paths):
        progs = [
            path[u"observations"][-1][-3] - path[u"observations"][0][-3]
            for path in paths
        ]
        logger.record_tabular(u'AverageForwardProgress', np.mean(progs))
        logger.record_tabular(u'MaxForwardProgress', np.max(progs))
        logger.record_tabular(u'MinForwardProgress', np.min(progs))
        logger.record_tabular(u'StdForwardProgress', np.std(progs))

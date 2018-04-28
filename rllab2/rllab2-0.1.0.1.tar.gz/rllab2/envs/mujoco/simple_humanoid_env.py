from __future__ import division
from __future__ import absolute_import
from rllab2.envs.base import Step
from .mujoco_env import MujocoEnv
import numpy as np
from rllab2.core.serializable import Serializable
from rllab2.misc.overrides import overrides
from rllab2.misc import logger
from rllab2.misc import autoargs


class SimpleHumanoidEnv(MujocoEnv, Serializable):

    FILE = u'simple_humanoid.xml'

    @autoargs.arg(u'vel_deviation_cost_coeff', type=float,
                  help=u'cost coefficient for velocity deviation')
    @autoargs.arg(u'alive_bonus', type=float,
                  help=u'bonus reward for being alive')
    @autoargs.arg(u'ctrl_cost_coeff', type=float,
                  help=u'cost coefficient for control inputs')
    @autoargs.arg(u'impact_cost_coeff', type=float,
                  help=u'cost coefficient for impact')
    def __init__(
            self,
            vel_deviation_cost_coeff=1e-2,
            alive_bonus=0.2,
            ctrl_cost_coeff=1e-3,
            impact_cost_coeff=1e-5,
            *args, **kwargs):
        self.vel_deviation_cost_coeff = vel_deviation_cost_coeff
        self.alive_bonus = alive_bonus
        self.ctrl_cost_coeff = ctrl_cost_coeff
        self.impact_cost_coeff = impact_cost_coeff
        super(SimpleHumanoidEnv, self).__init__(*args, **kwargs)
        Serializable.quick_init(self, locals())

    def get_current_obs(self):
        data = self.model.data
        return np.concatenate([
            data.qpos.flat,
            data.qvel.flat,
            np.clip(data.cfrc_ext, -1, 1).flat,
            self.get_body_com(u"torso").flat,
        ])

    def _get_com(self):
        data = self.model.data
        mass = self.model.body_mass
        xpos = data.xipos
        return (np.sum(mass * xpos, 0) / np.sum(mass))[0]

    def step(self, action):
        self.forward_dynamics(action)
        next_obs = self.get_current_obs()

        alive_bonus = self.alive_bonus
        data = self.model.data

        comvel = self.get_body_comvel(u"torso")

        lin_vel_reward = comvel[0]
        lb, ub = self.action_bounds
        scaling = (ub - lb) * 0.5
        ctrl_cost = .5 * self.ctrl_cost_coeff * np.sum(
            np.square(action / scaling))
        impact_cost = .5 * self.impact_cost_coeff * np.sum(
            np.square(np.clip(data.cfrc_ext, -1, 1)))
        vel_deviation_cost = 0.5 * self.vel_deviation_cost_coeff * np.sum(
            np.square(comvel[1:]))
        reward = lin_vel_reward + alive_bonus - ctrl_cost - \
            impact_cost - vel_deviation_cost
        done = data.qpos[2] < 0.8 or data.qpos[2] > 2.0

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

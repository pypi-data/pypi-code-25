from __future__ import absolute_import
from rllab2.envs.mujoco.gather.gather_env import GatherEnv
from rllab2.envs.mujoco.point_env import PointEnv


class PointGatherEnv(GatherEnv):

    MODEL_CLASS = PointEnv
    ORI_IND = 2

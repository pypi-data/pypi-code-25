from __future__ import absolute_import
from rllab2.envs.mujoco.gather.gather_env import GatherEnv
from rllab2.envs.mujoco.ant_env import AntEnv


class AntGatherEnv(GatherEnv):

    MODEL_CLASS = AntEnv
    ORI_IND = 6

from __future__ import absolute_import
from rllab2.envs.mujoco.gather.gather_env import GatherEnv
from rllab2.envs.mujoco.swimmer_env import SwimmerEnv


class SwimmerGatherEnv(GatherEnv):

    MODEL_CLASS = SwimmerEnv
    ORI_IND = 2

from __future__ import absolute_import
import numpy as np

from rllab2.envs.mujoco.hill.hill_env import HillEnv
from rllab2.envs.mujoco.walker2d_env import Walker2DEnv
from rllab2.misc.overrides import overrides
import rllab2.envs.mujoco.hill.terrain as terrain
from rllab2.spaces import Box

class Walker2DHillEnv(HillEnv):

    MODEL_CLASS = Walker2DEnv
    
    @overrides
    def _mod_hfield(self, hfield):
        # clear a flat patch for the robot to start off from
        return terrain.clear_patch(hfield, Box(np.array([-2.0, -2.0]), np.array([-0.5, -0.5])))
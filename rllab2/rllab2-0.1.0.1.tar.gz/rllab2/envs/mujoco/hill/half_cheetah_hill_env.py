from __future__ import absolute_import
import numpy as np

from rllab2.envs.mujoco.hill.hill_env import HillEnv
from rllab2.envs.mujoco.half_cheetah_env import HalfCheetahEnv
from rllab2.misc.overrides import overrides
import rllab2.envs.mujoco.hill.terrain as terrain
from rllab2.spaces import Box

class HalfCheetahHillEnv(HillEnv):

    MODEL_CLASS = HalfCheetahEnv
    
    @overrides
    def _mod_hfield(self, hfield):
        # clear a flat patch for the robot to start off from
        return terrain.clear_patch(hfield, Box(np.array([-3.0, -1.5]), np.array([0.0, -0.5])))
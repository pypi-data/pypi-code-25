from __future__ import absolute_import
import numpy as np

from rllab2.envs.mujoco.hill.hill_env import HillEnv
from rllab2.envs.mujoco.swimmer3d_env import Swimmer3DEnv
from rllab2.misc.overrides import overrides
import rllab2.envs.mujoco.hill.terrain as terrain
from rllab2.spaces import Box

class Swimmer3DHillEnv(HillEnv):

    MODEL_CLASS = Swimmer3DEnv
    
    @overrides
    def _mod_hfield(self, hfield):
        # clear a flat patch for the robot to start off from
        return terrain.clear_patch(hfield, Box(np.array([-3.0, -1.5]), np.array([0.0, -0.5])))
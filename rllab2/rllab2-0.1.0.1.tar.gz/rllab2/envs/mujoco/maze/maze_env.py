from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
import os.path as osp
import tempfile
import xml.etree.ElementTree as ET
import math
import numpy as np

from rllab2 import spaces
from rllab2.envs.base import Step
from rllab2.envs.proxy_env import ProxyEnv
from rllab2.envs.mujoco.maze.maze_env_utils import construct_maze
from rllab2.envs.mujoco.mujoco_env import MODEL_DIR, BIG
from rllab2.envs.mujoco.maze.maze_env_utils import ray_segment_intersect, point_distance
from rllab2.core.serializable import Serializable
from rllab2.misc.overrides import overrides

from rllab2.misc import logger


class MazeEnv(ProxyEnv, Serializable):
    MODEL_CLASS = None
    ORI_IND = None

    MAZE_HEIGHT = None
    MAZE_SIZE_SCALING = None
    MAZE_MAKE_CONTACTS = False
    MAZE_STRUCTURE = [
        [1, 1, 1, 1, 1],
        [1, u'r', 0, 0, 1],
        [1, 1, 1, 0, 1],
        [1, u'g', 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]

    MANUAL_COLLISION = False

    def __init__(
            self,
            n_bins=20,
            sensor_range=10.,
            sensor_span=math.pi,
            maze_id=0,
            length=1,
            maze_height=0.5,
            maze_size_scaling=2,
            coef_inner_rew=0.,  # a coef of 0 gives no reward to the maze from the wrapped env.
            goal_rew=1.,  # reward obtained when reaching the goal
            *args,
            **kwargs):
        Serializable.quick_init(self, locals())

        Serializable.quick_init(self, locals())
        self._n_bins = n_bins
        self._sensor_range = sensor_range
        self._sensor_span = sensor_span
        self._maze_id = maze_id
        self.length = length
        self.coef_inner_rew = coef_inner_rew
        self.goal_rew = goal_rew

        model_cls = self.__class__.MODEL_CLASS
        if model_cls is None:
            raise u"MODEL_CLASS unspecified!"
        xml_path = osp.join(MODEL_DIR, model_cls.FILE)
        tree = ET.parse(xml_path)
        worldbody = tree.find(u".//worldbody")

        self.MAZE_HEIGHT = height = maze_height
        self.MAZE_SIZE_SCALING = size_scaling = maze_size_scaling
        self.MAZE_STRUCTURE = structure = construct_maze(maze_id=self._maze_id, length=self.length)

        torso_x, torso_y = self._find_robot()
        self._init_torso_x = torso_x
        self._init_torso_y = torso_y

        for i in xrange(len(structure)):
            for j in xrange(len(structure[0])):
                if unicode(structure[i][j]) == u'1':
                    # offset all coordinates so that robot starts at the origin
                    ET.SubElement(
                        worldbody, u"geom",
                        name=u"block_%d_%d" % (i, j),
                        pos=u"%f %f %f" % (j * size_scaling - torso_x,
                                          i * size_scaling - torso_y,
                                          height / 2 * size_scaling),
                        size=u"%f %f %f" % (0.5 * size_scaling,
                                           0.5 * size_scaling,
                                           height / 2 * size_scaling),
                        type=u"box",
                        material=u"",
                        contype=u"1",
                        conaffinity=u"1",
                        rgba=u"0.4 0.4 0.4 1"
                    )

        torso = tree.find(u".//body[@name='torso']")
        geoms = torso.findall(u".//geom")
        for geom in geoms:
            if u'name' not in geom.attrib:
                raise Exception(u"Every geom of the torso must have a name "
                                u"defined")

        if self.__class__.MAZE_MAKE_CONTACTS:
            contact = ET.SubElement(
                tree.find(u"."), u"contact"
            )
            for i in xrange(len(structure)):
                for j in xrange(len(structure[0])):
                    if unicode(structure[i][j]) == u'1':
                        for geom in geoms:
                            ET.SubElement(
                                contact, u"pair",
                                geom1=geom.attrib[u"name"],
                                geom2=u"block_%d_%d" % (i, j)
                            )

        _, file_path = tempfile.mkstemp(text=True)
        tree.write(file_path)  # here we write a temporal file with the robot specifications. Why not the original one??

        self._goal_range = self._find_goal_range()
        self._cached_segments = None

        inner_env = model_cls(*args, file_path=file_path, **kwargs)  # file to the robot specifications
        ProxyEnv.__init__(self, inner_env)  # here is where the robot env will be initialized

    def get_current_maze_obs(self):
        # The observation would include both information about the robot itself as well as the sensors around its
        # environment
        robot_x, robot_y = self.wrapped_env.get_body_com(u"torso")[:2]
        ori = self.get_ori()

        structure = self.MAZE_STRUCTURE
        size_scaling = self.MAZE_SIZE_SCALING

        segments = []
        # compute the distance of all segments

        # Get all line segments of the goal and the obstacles
        for i in xrange(len(structure)):
            for j in xrange(len(structure[0])):
                if structure[i][j] == 1 or structure[i][j] == u'g':
                    cx = j * size_scaling - self._init_torso_x
                    cy = i * size_scaling - self._init_torso_y
                    x1 = cx - 0.5 * size_scaling
                    x2 = cx + 0.5 * size_scaling
                    y1 = cy - 0.5 * size_scaling
                    y2 = cy + 0.5 * size_scaling
                    struct_segments = [
                        ((x1, y1), (x2, y1)),
                        ((x2, y1), (x2, y2)),
                        ((x2, y2), (x1, y2)),
                        ((x1, y2), (x1, y1)),
                    ]
                    for seg in struct_segments:
                        segments.append(dict(
                            segment=seg,
                            type=structure[i][j],
                        ))

        wall_readings = np.zeros(self._n_bins)
        goal_readings = np.zeros(self._n_bins)

        for ray_idx in xrange(self._n_bins):
            ray_ori = ori - self._sensor_span * 0.5 + 1.0 * (2 * ray_idx + 1) / (2 * self._n_bins) * self._sensor_span
            ray_segments = []
            for seg in segments:
                p = ray_segment_intersect(ray=((robot_x, robot_y), ray_ori), segment=seg[u"segment"])
                if p is not None:
                    ray_segments.append(dict(
                        segment=seg[u"segment"],
                        type=seg[u"type"],
                        ray_ori=ray_ori,
                        distance=point_distance(p, (robot_x, robot_y)),
                    ))
            if len(ray_segments) > 0:
                first_seg = sorted(ray_segments, key=lambda x: x[u"distance"])[0]
                # print first_seg
                if first_seg[u"type"] == 1:
                    # Wall -> add to wall readings
                    if first_seg[u"distance"] <= self._sensor_range:
                        wall_readings[ray_idx] = (self._sensor_range - first_seg[u"distance"]) / self._sensor_range
                elif first_seg[u"type"] == u'g':
                    # Goal -> add to goal readings
                    if first_seg[u"distance"] <= self._sensor_range:
                        goal_readings[ray_idx] = (self._sensor_range - first_seg[u"distance"]) / self._sensor_range
                else:
                    assert False

        obs = np.concatenate([
            wall_readings,
            goal_readings
        ])
        return obs

    def get_current_robot_obs(self):
        return self.wrapped_env.get_current_obs()

    def get_current_obs(self):
        return np.concatenate([self.wrapped_env.get_current_obs(),
                               self.get_current_maze_obs()
                               ])

    def get_ori(self):
        u"""
        First it tries to use a get_ori from the wrapped env. If not successfull, falls
        back to the default based on the ORI_IND specified in Maze (not accurate for quaternions)
        """
        obj = self.wrapped_env
        while not hasattr(obj, u'get_ori') and hasattr(obj, u'wrapped_env'):
            obj = obj.wrapped_env
        try:
            return obj.get_ori()
        except (NotImplementedError, AttributeError), e:
            pass
        return self.wrapped_env.model.data.qpos[self.__class__.ORI_IND]

    def reset(self):
        self.wrapped_env.reset()
        return self.get_current_obs()

    @property
    def viewer(self):
        return self.wrapped_env.viewer

    @property
    @overrides
    def observation_space(self):
        shp = self.get_current_obs().shape
        ub = BIG * np.ones(shp)
        return spaces.Box(ub * -1, ub)

    # space of only the robot observations (they go first in the get current obs) THIS COULD GO IN PROXYENV
    @property
    def robot_observation_space(self):
        shp = self.get_current_robot_obs().shape
        ub = BIG * np.ones(shp)
        return spaces.Box(ub * -1, ub)

    @property
    def maze_observation_space(self):
        shp = self.get_current_maze_obs().shape
        ub = BIG * np.ones(shp)
        return spaces.Box(ub * -1, ub)

    def _find_robot(self):
        structure = self.MAZE_STRUCTURE
        size_scaling = self.MAZE_SIZE_SCALING
        for i in xrange(len(structure)):
            for j in xrange(len(structure[0])):
                if structure[i][j] == u'r':
                    return j * size_scaling, i * size_scaling
        assert False

    def _find_goal_range(self):  # this only finds one goal!
        structure = self.MAZE_STRUCTURE
        size_scaling = self.MAZE_SIZE_SCALING
        for i in xrange(len(structure)):
            for j in xrange(len(structure[0])):
                if structure[i][j] == u'g':
                    minx = j * size_scaling - size_scaling * 0.5 - self._init_torso_x
                    maxx = j * size_scaling + size_scaling * 0.5 - self._init_torso_x
                    miny = i * size_scaling - size_scaling * 0.5 - self._init_torso_y
                    maxy = i * size_scaling + size_scaling * 0.5 - self._init_torso_y
                    return minx, maxx, miny, maxy

    def _is_in_collision(self, pos):
        x, y = pos
        structure = self.MAZE_STRUCTURE
        size_scaling = self.MAZE_SIZE_SCALING
        for i in xrange(len(structure)):
            for j in xrange(len(structure[0])):
                if structure[i][j] == 1:
                    minx = j * size_scaling - size_scaling * 0.5 - self._init_torso_x
                    maxx = j * size_scaling + size_scaling * 0.5 - self._init_torso_x
                    miny = i * size_scaling - size_scaling * 0.5 - self._init_torso_y
                    maxy = i * size_scaling + size_scaling * 0.5 - self._init_torso_y
                    if minx <= x <= maxx and miny <= y <= maxy:
                        return True
        return False

    def step(self, action):
        if self.MANUAL_COLLISION:
            old_pos = self.wrapped_env.get_xy()
            inner_next_obs, inner_rew, done, info = self.wrapped_env.step(action)
            new_pos = self.wrapped_env.get_xy()
            if self._is_in_collision(new_pos):
                self.wrapped_env.set_xy(old_pos)
                done = False
        else:
            inner_next_obs, inner_rew, done, info = self.wrapped_env.step(action)
        next_obs = self.get_current_obs()
        x, y = self.wrapped_env.get_body_com(u"torso")[:2]
        # ref_x = x + self._init_torso_x
        # ref_y = y + self._init_torso_y
        info[u'outer_rew'] = 0
        info[u'inner_rew'] = inner_rew
        reward = self.coef_inner_rew * inner_rew
        minx, maxx, miny, maxy = self._goal_range
        if minx <= x <= maxx and miny <= y <= maxy:
            done = True
            reward += self.goal_rew
            info[u'rew_rew'] = 1  # we keep here the original one, so that the AvgReturn is directly the freq of success
        return Step(next_obs, reward, done, **info)

    def action_from_key(self, key):
        return self.wrapped_env.action_from_key(key)

    @overrides
    def log_diagnostics(self, paths, *args, **kwargs):
        # we call here any logging related to the maze, strip the maze obs and call log_diag with the stripped paths
        # we need to log the purely gather reward!!
        with logger.tabular_prefix(u'Maze_'):
            gather_undiscounted_returns = [sum(path[u'env_infos'][u'outer_rew']) for path in paths]
            logger.record_tabular_misc_stat(u'Return', gather_undiscounted_returns, placement=u'front')
        stripped_paths = []
        for path in paths:
            stripped_path = {}
            for k, v in path.items():
                stripped_path[k] = v
            stripped_path[u'observations'] = \
                stripped_path[u'observations'][:, :self.wrapped_env.observation_space.flat_dim]
            #  this breaks if the obs of the robot are d>1 dimensional (not a vector)
            stripped_paths.append(stripped_path)
        with logger.tabular_prefix(u'wrapped_'):
            wrapped_undiscounted_return = np.mean([np.sum(path[u'env_infos'][u'inner_rew']) for path in paths])
            logger.record_tabular(u'AverageReturn', wrapped_undiscounted_return)
            self.wrapped_env.log_diagnostics(stripped_paths, *args, **kwargs)

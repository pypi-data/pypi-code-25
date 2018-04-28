from __future__ import absolute_import
import numpy as np
from .base import Env
from rllab2.spaces import Discrete
from rllab2.envs.base import Step
from rllab2.core.serializable import Serializable
from itertools import imap

MAPS = {
    u"chain": [
        u"GFFFFFFFFFFFFFSFFFFFFFFFFFFFG"
    ],
    u"4x4_safe": [
        u"SFFF",
        u"FWFW",
        u"FFFW",
        u"WFFG"
    ],
    u"4x4": [
        u"SFFF",
        u"FHFH",
        u"FFFH",
        u"HFFG"
    ],
    u"8x8": [
        u"SFFFFFFF",
        u"FFFFFFFF",
        u"FFFHFFFF",
        u"FFFFFHFF",
        u"FFFHFFFF",
        u"FHHFFFHF",
        u"FHFFHFHF",
        u"FFFHFFFG"
    ],
}


class GridWorldEnv(Env, Serializable):
    u"""
    'S' : starting point
    'F' or '.': free space
    'W' or 'x': wall
    'H' or 'o': hole (terminates episode)
    'G' : goal


    """

    def __init__(self, desc=u'4x4'):
        Serializable.quick_init(self, locals())
        if isinstance(desc, unicode):
            desc = MAPS[desc]
        desc = np.array(list(imap(list, desc)))
        desc[desc == u'.'] = u'F'
        desc[desc == u'o'] = u'H'
        desc[desc == u'x'] = u'W'
        self.desc = desc
        self.n_row, self.n_col = desc.shape
        (start_x,), (start_y,) = np.nonzero(desc == u'S')
        self.start_state = start_x * self.n_col + start_y
        self.state = None
        self.domain_fig = None

    def reset(self):
        self.state = self.start_state
        return self.state

    @staticmethod
    def action_from_direction(d):
        u"""
        Return the action corresponding to the given direction. This is a helper method for debugging and testing
        purposes.
        :return: the action index corresponding to the given direction
        """
        return dict(
            left=0,
            down=1,
            right=2,
            up=3
        )[d]

    def step(self, action):
        u"""
        action map:
        0: left
        1: down
        2: right
        3: up
        :param action: should be a one-hot vector encoding the action
        :return:
        """
        possible_next_states = self.get_possible_next_states(self.state, action)

        probs = [x[1] for x in possible_next_states]
        next_state_idx = np.random.choice(len(probs), p=probs)
        next_state = possible_next_states[next_state_idx][0]

        next_x = next_state // self.n_col
        next_y = next_state % self.n_col

        next_state_type = self.desc[next_x, next_y]
        if next_state_type == u'H':
            done = True
            reward = 0
        elif next_state_type in [u'F', u'S']:
            done = False
            reward = 0
        elif next_state_type == u'G':
            done = True
            reward = 1
        else:
            raise NotImplementedError
        self.state = next_state
        return Step(observation=self.state, reward=reward, done=done)

    def get_possible_next_states(self, state, action):
        u"""
        Given the state and action, return a list of possible next states and their probabilities. Only next states
        with nonzero probabilities will be returned
        :param state: start state
        :param action: action
        :return: a list of pairs (s', p(s'|s,a))
        """
        # assert self.observation_space.contains(state)
        # assert self.action_space.contains(action)

        x = state // self.n_col
        y = state % self.n_col
        coords = np.array([x, y])

        increments = np.array([[0, -1], [1, 0], [0, 1], [-1, 0]])
        next_coords = np.clip(
            coords + increments[action],
            [0, 0],
            [self.n_row - 1, self.n_col - 1]
        )
        next_state = next_coords[0] * self.n_col + next_coords[1]
        state_type = self.desc[x, y]
        next_state_type = self.desc[next_coords[0], next_coords[1]]
        if next_state_type == u'W' or state_type == u'H' or state_type == u'G':
            return [(state, 1.)]
        else:
            return [(next_state, 1.)]

    @property
    def action_space(self):
        return Discrete(4)

    @property
    def observation_space(self):
        return Discrete(self.n_row * self.n_col)


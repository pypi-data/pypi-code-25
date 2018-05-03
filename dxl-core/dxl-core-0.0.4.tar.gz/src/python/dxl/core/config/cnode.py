from typing import Dict
from enum import Enum


class QueryKey:
    def __init__(self, keys):
        """
        `key`: All possible value which is converatble to key.
        """
        if isinstance(keys, QueryKey):
            keys = keys._keys
        if isinstance(keys, str):
            keys = keys.split('/')
        if keys is None:
            keys = []
        if not isinstance(keys, (list, tuple)):
            raise TypeError(
                "Expected keys to be list or tuple, got {}.".format(keys))
        self._keys = tuple(keys)

    def head(self):
        if len(self._keys) == 0:
            return None
        else:
            return self._keys[0]

    def tail(self):
        return QueryKey(self._keys[1:])

    def last(self):
        return QueryKey(tuple(self._keys[-1]))

    def __len__(self):
        return len(self._keys)


class Keywords:
    EXPAND = '__expand__'


def need_expand(v):
    if not isinstance(v, dict):
        return False
    if Keywords.EXPAND in v:
        return v[Keywords.EXPAND]
    return True


class CNode:
    def __init__(self, config=None):
        """
        `config`: initial configs, which should be a dict of CNode/value.
        """
        if config is None:
            config = {}
        self.data = config

    def read(self, key: QueryKey):
        """
        Find value curresponding to key.
        if len(key) == 1, then find it in self._values,
        else find it in self._children recuresivly.
        """
        key = QueryKey(key)
        if len(key) == 0:
            return self
        if len(key) == 1:
            return self.data.get(key.head())
        if not key.head() in self.data or not isinstance(
                self.data[key.head()], CNode):
            return None
        return self.data.get(key.head()).read(key.tail())

    @property
    def children(self):
        return {k: v for k, v in self.data.items() if isinstance(v, CNode)}

    @property
    def values(self):
        return {k: v for k, v in self.data.items() if not isinstance(v, CNode)}

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key: str, value=None):
        return self.data.get(key, value)

    def __iter__(self):
        return iter(self.data)

    def items(self):
        return self.data.items()

    def keys(self):
        return self.data.keys()

    def create(self, key: QueryKey, node_or_value):
        """
        Create a new child node or value.
        """
        return self.update(key, node_or_value, allow_exist=False)

    def is_ancestor_of(self, n):
        for k, v in self.data.items():
            if not isinstance(v, CNode):
                continue
            if v is n or v.is_ancestor_of(n):
                return True
        return False

    def update(self,
               key: QueryKey,
               node_or_value,
               *,
               allow_exist=True,
               overwrite_node=False):
        """
        Updating config.
        If node_or_value is a value, update directly.
        If node_or_value is a CNode, check if this node exists.
            If not exists: direct assign.
            If exists: update each item of that node. 
        Note: the node_or_value argument is not assigned to the node tree.
        """
        key = QueryKey(key)
        if len(key) == 0:
            if not isinstance(node_or_value, (dict, CNode)):
                raise ValueError(
                    "Can not update node with none CNode object or dict, overrite_node might need to be True."
                )
            for k, v in node_or_value.items():
                if isinstance(self.data[k], CNode):
                    self.data[k].update(v)
                else:
                    self.data[k] = v
            return self
        if key.head() in self.data and not allow_exist:
            raise ValueError("Key {} alread existed.".format(key.head()))
        if len(key) > 1:
            if not isinstance(self.data.get(key.head()),
                              CNode) or overwrite_node:
                self.data[key.head()] = CNode().update(key.tail(),
                                                       node_or_value)
            else:
                self.data[key.head()].update(key.tail(), node_or_value)
            return self
        if len(key) == 1:
            if not isinstance(self.data.get(key.head()),
                              CNode) or overwrite_node:
                if need_expand(node_or_value):
                    self.data[key.head()] = from_dict(node_or_value)
                else:
                    self.data[key.head()] = node_or_value
            else:
                self.data[key.head()].update([], node_or_value)
            return self


def from_dict(config_dict):
    config_parsed = {}
    for k, v in config_dict.items():
        if need_expand(v):
            config_parsed[k] = from_dict(v)
        else:
            config_parsed[k] = v
    return CNode(config_parsed)


class DefaultConfig:
    _current = None

    def __init__(self, cnode):
        pass

    @property
    def node(self):
        return self._current

    def __enter__(self):
        pass
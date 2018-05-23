"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/22
-------------------------------------------------
   Description:
-------------------------------------------------
"""
from collections import defaultdict


class Way:
    def __init__(self, value, reverse=False):
        self.value = value
        self.reverse = reverse


class Region:
    """
    Region object
    """

    def __init__(self):
        self._name = ''
        self._node_dict = defaultdict(dict)
        self._way_dict = defaultdict(list)
        self._area_outer = []
        self._area_inner = []
        self._order_outer = []
        self._order_inner = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, values):
        self._name = values

    @property
    def nodes(self):
        return self._node_dict

    @nodes.setter
    def nodes(self, values):
        self._node_dict = values

    @property
    def ways(self):
        return self._way_dict

    @ways.setter
    def ways(self, values):
        self._way_dict = values

    @property
    def area_outer(self):
        return self._area_outer

    @area_outer.setter
    def area_outer(self, values):
        self._area_outer = values

    @property
    def area_inner(self):
        return self._area_inner

    @area_inner.setter
    def area_inner(self, values):
        self._area_inner = values

    @property
    def order_outer(self):
        return self._order_outer

    @order_outer.setter
    def order_outer(self, values):
        self._order_outer = values

    @property
    def order_inner(self):
        return self._order_inner

    @order_inner.setter
    def order_inner(self, values):
        self._order_inner = values

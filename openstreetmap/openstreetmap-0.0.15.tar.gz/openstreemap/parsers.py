"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
                Parser nodes, ways, areas
-------------------------------------------------
"""

from .errors import BoundaryError
from .region import Way


class Parser:
    def __init__(self):
        self.region = None

    def combine(self, tem_boundary, ways, area, area_start, area_end):
        """
        tem_boundary, next_area, area_start, area_end
        """
        if ways[0] == area:
            next_area = ways[-1]
        else:
            next_area = ways[0]
        _area = self.region.ways[area]
        _next_area = self.region.ways[next_area]
        if area_end == _next_area[0]:
            tem_boundary.append(Way(next_area))
            return tem_boundary, next_area, area_start, _next_area[-1], _next_area[-1]
        elif area_end == _next_area[-1]:
            tem_boundary.append(Way(next_area, True))
            return tem_boundary, next_area, area_start, _next_area[0], _next_area[0]
        elif area_start == _area[-1]:
            tem_boundary.insert(0, Way(next_area))
            return tem_boundary, next_area, _next_area[0], area_end, _next_area[0]
        elif area_start == _area[-1]:
            tem_boundary.insert(0, Way(next_area, True))
            return tem_boundary, next_area, _next_area[-1], area_end, _next_area[-1]
        else:
            raise BoundaryError('Combine error')

    @staticmethod
    def count_se(se_node, area, ele):
        if ele in se_node:
            se_node[ele]['count'] += 1
            se_node[ele]['ways'].append(area)
        else:
            se_node[ele] = {'count': 1, "ways": [area]}
        return se_node

    def order_areas(self, areas):
        if len(areas) < 0:
            return
        se_node = {}
        for area in areas:
            way = self.region.ways[area]
            se_node = self.count_se(se_node, area, way[0])
            se_node = self.count_se(se_node, area, way[-1])
        for k, v in se_node.items():
            if v['count'] != 2:
                raise BoundaryError("Path can't closed")
        data = ('', '', '', '', [], [])
        next_area, start, end, next_node, boundaries, tem_boundary = data
        areas_len = len(areas)
        while areas_len > 0:
            if len(tem_boundary) == 0:
                next_area = areas[0]
                tem_boundary.append(Way(next_area))
                start = self.region.ways[next_area][0]
                end = self.region.ways[next_area][-1]
                next_node = end
            areas.remove(next_area)
            areas_len = len(areas)
            if start == end:
                boundaries.append(tem_boundary)
                tem_boundary = []
                continue
            ways = se_node[next_node]['ways']
            tem_boundary, next_area, start, end, next_node = self.combine(tem_boundary, ways, next_area, start, end)
            if start == end:
                boundaries.append(tem_boundary)
                tem_boundary = []
        return boundaries

    def format_coordinate(self, region):
        self.region = region
        self.region.order_outer = self.order_areas(self.region.area_outer)
        self.region.order_inner = self.order_areas(self.region.area_inner)

        # def get_data(self):
        #     return self.region

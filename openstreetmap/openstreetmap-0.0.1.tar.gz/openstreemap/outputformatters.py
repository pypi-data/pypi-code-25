"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
-------------------------------------------------
"""
from .transformation import conversion


class DataOutput:
    def __init__(self):
        self.csys = None
        self.coo_order = None
        self.region = None
        self.boundary = None

    def format_node(self, node):
        # {'lon': str(lon), 'lat': str(lat)}
        lng = self.region.nodes[node]['lon']
        lat = self.region.nodes[node]['lat']
        coordinate = lng + "," + lat
        if self.csys != 'wgs84':
            lng, lat = conversion(self.csys, lng, lat)
        if self.coo_order:
            coordinate = lat + "," + lng
        return coordinate

    def reshape_area(self, areas):
        area_str = ''
        for area in areas:
            ways_str = ''
            for way in area:
                way_values = self.region.ways[way.value]
                if way.reverse:
                    way_values.reverse()
                way_str = ';'.join(list(map(self.format_node, way_values))) + ';'
                ways_str += way_str
            area_str += ways_str + '='
        return area_str.strip('=')

    def reshape_data(self, region, boundary, csys=False, coo_order=False):
        self.csys = csys
        self.coo_order = coo_order
        self.region = region
        self.boundary = boundary
        self.boundary.boundary_outer = self.reshape_area(self.region.order_outer)
        self.boundary.boundary_inner = self.reshape_area(self.region.order_inner)

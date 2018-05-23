"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
-------------------------------------------------
"""
from lxml import etree
from collections import defaultdict
from .region import Region


class Extractor:
    def __init__(self, html, relation_id):
        self.selector = etree.HTML(html)
        self.relation_id = relation_id
        self.region = Region()

    def get_nodes(self):
        node_dict = defaultdict(dict)
        node_list = self.selector.xpath('//node')
        for node in node_list:
            node_id = node.xpath('@id')[0]
            lon = node.xpath('@lon')[0]
            lat = node.xpath('@lat')[0]
            node_dict[str(node_id)] = {'lon': str(lon), 'lat': str(lat)}
        self.region.nodes = node_dict

    def get_ways(self):
        way_dict = defaultdict(list)
        way_list = self.selector.xpath('//way')
        for way in way_list:
            way_id = way.xpath('@id')[0]
            way_node_ele = way.xpath('nd/@ref')
            way_node = list(map(lambda x: str(x), way_node_ele))
            way_dict[str(way_id)] = way_node
        self.region.ways = way_dict

    def get_name(self):
        name = self.selector.xpath('//relation[@id="{0}"]/tag[@k="name:en"]/@v'.format(self.relation_id))
        if len(name) == 0:
            name = self.selector.xpath('//relation[@id="{0}"]/tag[@k="name"]/@v'.format(self.relation_id))
        self.region.name = str(name[0])

    def get_area(self):
        # role = inner outer
        _outer = self.selector.xpath(
            '//relation[@id="{0}"]/member[@role="outer"]/@ref'.format(self.relation_id))
        _inner = self.selector.xpath(
            '//relation[@id="{0}"]/member[@role="inner"]/@ref'.format(self.relation_id))
        self.region.area_outer = list(map(lambda x: str(x), _outer))
        self.region.area_inner = list(map(lambda x: str(x), _inner))

    def get_region(self):
        self.get_name()
        self.get_nodes()
        self.get_ways()
        self.get_area()
        return self.region


class NameExtractor:
    def __init__(self, html, name, level):
        self.selector = etree.HTML(html)
        self.name = name
        self.level = level

    def extractor_id(self):
        search_list = self.selector.xpath('//ul[@class="results-list"]/li')
        dist_dict = {
            'country': 'Country',
            'state': 'State',
            'city': 'Region Boundary',
            'county': 'County Boundary',
        }
        for search in search_list:
            data_type = search.xpath('p/a/@data-type')[0]
            if data_type != 'relation':
                continue
            prefix = search.xpath('p/a/@data-prefix')[0]
            if dist_dict[self.level] != prefix:
                continue
            name = search.xpath('p/a/@data-name')[0]
            data_id = search.xpath('p/a/@data-id')[0]
            return data_id, name
        return None, None

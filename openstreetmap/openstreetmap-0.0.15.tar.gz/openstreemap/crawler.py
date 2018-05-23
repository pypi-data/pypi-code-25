"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
   OpenStreetMap ：WGS84 coordinate system
   default coordinate order : lng,lat  coo_order = False
   boundary.info : all data
            name : boundary name
            relation_id :relation id
            boundary : including outer and inner
                    outer
                    inner
-------------------------------------------------
"""

from .boundary import Boundary
from .parsers import Parser
from .extractors import Extractor, NameExtractor
from .downloader import HtmlFetcher
from .errors import InvalidRelationId, PagesNotExist
from .outputformatters import DataOutput


class Crawler:
    def __init__(self):
        self.html_fetcher = HtmlFetcher()
        self.boundary = Boundary()
        self.parsers = Parser()
        self.outputer = DataOutput()

    def id_parse(self, relation_id, csys='wgs84', coo_order=False):
        """
        get Boundary,Conversion coordinate
        csys -> Coordinate System
        :param relation_id:
        :param csys: wgs84:wgs84; gcj02: Mars; bd09:Baidu
        :param coo_order: lng,lat  coo_order = False; lat,lng  coo_order = True;
        :return:
        """
        if not relation_id.isdigit():
            raise InvalidRelationId('Invalid id <{0}>'.format(str(relation_id)))
        url = 'https://www.openstreetmap.org/api/0.6/relation/{0}/full'.format(str(relation_id))
        html = self.html_fetcher.get_html(url)
        if len(html) == 0:
            raise PagesNotExist('Pages Not Found')
        extractor = Extractor(html, relation_id)
        region = extractor.get_region()
        self.boundary.name = region.name
        self.boundary.relation_id = relation_id
        self.parsers.format_coordinate(region)
        self.outputer.reshape_data(region, self.boundary, csys, coo_order)
        return self.boundary

    def name_parse(self, name, level, csys='wgs84', coo_order=False):
        """
        get boundary by name
        :param csys:
        :param coo_order:
        :param name: place name
        :param level: Administrative district level ,country state city county town
        :return:
        """
        url = 'https://www.openstreetmap.org/geocoder/search_osm_nominatim?query={0}'.format(str(name))
        html = self.html_fetcher.get_html(url, is_text=True)
        if len(html) == 0:
            raise PagesNotExist('Pages Not Found')
        extractor = NameExtractor(html, name, level)
        data_id, _ = extractor.extractor_id()
        if data_id is None:
            return self.boundary
        return self.id_parse(data_id, csys, coo_order)

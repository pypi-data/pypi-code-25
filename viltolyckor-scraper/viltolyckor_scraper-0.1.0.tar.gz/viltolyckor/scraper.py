# encoding: utf-8
import requests
from bs4 import BeautifulSoup
from statscraper import (BaseScraper, Collection, DimensionValue,
                         Dataset, Dimension, Result)
from viltolyckor.utils import parse_result_page

URL = "https://www.viltolycka.se/statistik/viltolyckor-for-respektive-viltslag/"


class ViltolyckorScraper(BaseScraper):

    def _fetch_itemslist(self, current_item):
        """This scraper has only one dataset."""
        yield ViltolyckorDataset("viltolyckor per viltslag")


    def _fetch_allowed_values(self, dimension):
        """Allowed values are only implemented for regions.
        Ie units would need to be fetched trough an json api.
        """
        dataset = dimension.dataset
        if dimension.id == "year":
            for option in dataset.soup.select("#ctl10_lstYearInterval option"):
                value = option.get("value")
                yield DimensionValue(value, dimension)

        elif dimension.id == "region":
            for option in dataset.soup.select("#ctl10_lstCounties option"):
                value = option.get("value")
                label = option.text.strip()
                yield DimensionValue(value, dimension, label)

        elif dimension.id == "viltslag":
            tds = dataset.soup.select_one(".statistics-report")\
                              .select("td.title")
            for td in tds:
                value = td.text.strip()
                yield DimensionValue(value, dimension)

    def _fetch_dimensions(self, dataset):
        yield Dimension("region")
        yield Dimension("year")
        yield Dimension("month")
        yield Dimension("viltslag")


    def _fetch_data(self, dataset, query):
        """Make the actual query.
        """
        if query is None:
            query = {}
        # default query
        _query = {
            "year": [dataset.latest_year],
            "region": "Hela landet"
        }
        _query.update(query)
        allowed_query_dims = ["year", "region"]

        # Validate query
        for dim in query.keys():
            if dim not in allowed_query_dims:
                msg = "Querying on {} is not implemented yet".format(dim)
                raise NotImplementedError(msg)

        for dim, value in _query.iteritems():
            if value == "*":
                _query[dim] = [x.value for x in dataset.dimensions[dim].allowed_values]
            elif not isinstance(value, list):
                _query[dim] = [value]
        input_elems = dataset.soup.select("input['value']")
        payload = dict([(x["name"], x["value"]) for x in input_elems])

        for region in _query["region"]:
            region_id = dataset._get_region_id(region)
            for year in _query["year"]:
                payload.update({
                    "ctl01$ctl10$lstCounties": region_id,
                    "ctl01$ctl10$lstYearInterval": year,
                })
                result_page = self._post_html(URL, payload)

                for datapoint in parse_result_page(result_page):
                    value = datapoint["value"]
                    del datapoint["value"]
                    yield Result(value, datapoint)


    ###
    # HELPER METHODS
    ###
    def _get_html(self, url):
        """ Get html from url
        """
        self.log.info(u"/GET {}".format(url))
        r = requests.get(url)
        if hasattr(r, 'from_cache'):
            if r.from_cache:
                self.log.info("(from cache)")

        r.raise_for_status()

        return r.content

    def _post_html(self, url, payload):
        self.log.info(u"/POST {} with {}".format(url, payload))
        r = requests.post(url, payload)
        r.raise_for_status()

        return r.content


    @property
    def log(self):
        if not hasattr(self, "_logger"):
            self._logger = PrintLogger()
        return self._logger



class ViltolyckorDataset(Dataset):

    @property
    def latest_year(self):
        """Get the latest available year."""
        return self.years[-1]

    @property
    def years(self):
        """Get all years."""
        return [x.value for x in self.dimensions["year"].allowed_values]

    def _get_region_id(self, region_label_or_id):
        """Get region id.

        :param region_label_or_id: an id or label of region.
        """
        regions = self.dimensions["region"].allowed_values
        if region_label_or_id in regions:
            return region_label_or_id
        else:
            return regions.get_by_label(region_label_or_id).value

    @property
    def html(self):
        if not hasattr(self, "_html"):
            self._html = self.scraper._get_html(URL)
        return self._html


    @property
    def soup(self):
        if not hasattr(self, "_soup"):
            self._soup = BeautifulSoup(self.html, 'html.parser')
        return self._soup




class PrintLogger():
    """ Empyt "fake" logger
    """

    def log(self, msg, *args, **kwargs):
        print msg

    def debug(self, msg, *args, **kwargs):
        print msg

    def info(self, msg, *args, **kwargs):
        print msg

    def warning(self, msg, *args, **kwargs):
        print msg

    def error(self, msg, *args, **kwargs):
        print msg

    def critical(self, msg, *args, **kwargs):
        print msg

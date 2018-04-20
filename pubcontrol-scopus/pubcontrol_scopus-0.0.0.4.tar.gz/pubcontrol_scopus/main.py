import pluggy

from pubcontrol_scopus.observe import AuthorObservatory, AuthorObservatoryABC
from pubcontrol_scopus.request import ScopusABC, Scopus

# Added 11.04.2018
# Need the DictQuery for implementation of the adapter, that translates the internal publication dict structure into
# the structure needed by pubcontrol to be inserted into the register
from jutil.processing import DictQuery

from pubcontrol_scopus.config import Config
import datetime

import logging

from pprint import pprint

from abc import ABC, abstractmethod
import json


hookimpl = pluggy.HookimplMarker('pubcontrol')


class PublicationDictAdapter(DictQuery):

    def __init__(self):
        DictQuery.__init__(self)
        self.keywords = []
        self.type = ''
        self.publication_dict = {}

    def set(self, arg):
        assert isinstance(arg[0], dict)
        self.set_query_dict(arg[0])
        self.keywords = arg[1]
        self.type = arg[2]
        self.publication_dict = {}

        return self

    def get(self):
        self.process()
        return self.publication_dict

    def process(self):
        self.publication_dict['doi'] = self.query('doi', '')
        self.publication_dict['title'] = self.query('title', '')
        self.publication_dict['description'] = self.query('description', '')
        self.publication_dict['published'] = self.query('date', datetime.datetime.now())
        self.publication_dict['authors'] = list(map(
            lambda x: {'first_name': x['first_name'], 'last_name': x['last_name']},
            self.query('authors', [])
        ))
        self.publication_dict['journal'] = {
            'name': self.query('journal', ''),
            'volume': self.query('volume', '')
        }
        self.publication_dict['tags'] = list(map(
            lambda x: {'content': x, 'description': ''},
            self.query('keywords', [])
        ))
        self.publication_dict['categories'] = list(map(
            lambda x: {'content': x, 'description': ''},
            self.keywords
        ))
        self.publication_dict['citations'] = list(map(
            lambda x: x['scopusID'],
            self.query('citedBy', [])
        ))
        self.publication_dict['origin'] = {
            'id': self.query('scopusID', 0),
            'name': Config().NAME,
            'type': self.type,
            'text': '',
            'raw': self.query('raw', '').encode('utf-8'),
            'fetched': datetime.datetime.now()
        }

    def query_exception(self, query, query_dict, default):
        return default


class BlacklistABC(ABC):

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def contains(self, item):
        pass

    def __contains__(self, item):
        return self.contains(item)

    @abstractmethod
    def remove(self, item):
        pass


class SimpleBlacklist(BlacklistABC):

    def __init__(self):
        self.config = Config()
        self.path = self.config.PATH / 'blacklist'

        self.list = json.load(self.path.open('r'))
        self.count = 0

    def add(self, item):
        self.list.append(item)
        self.count += 1
        if self.count == 5:
            self.count = 0
            json.dump(self.list, self.path.open('w+'))

    def contains(self, item):
        return item in self.list

    def remove(self, item):
        self.list.remove(item)


class Controller:
    
    def __init__(self,
                 scopus_class=Scopus,
                 observatory_class=AuthorObservatory,
                 publication_dict_adapter=PublicationDictAdapter,
                 blacklist_class=SimpleBlacklist
                 ):

        self.scopus = scopus_class()
        assert isinstance(self.scopus, ScopusABC)
        self.observatory = observatory_class()
        assert isinstance(self.observatory, AuthorObservatoryABC)
        self.blacklist = blacklist_class()
        assert isinstance(self.blacklist, BlacklistABC)
        self.adapter = publication_dict_adapter()

        self.config = Config()
        self.logger = logging.getLogger(self.config.NAME)
        self.logger.debug('[Scopus] Logger initialized')

    def run(self):
        """
        CHANGELOG

        Changed 11.04.2018:
        Added a try except around the fetching of the publications from the scopus object, as they raise a
        ConnectionError in case anything went wrong with the scopus database request. Skipping the publication in
        question in case a connection error occurs

        Changed 11.04.2018:
        Before yielding the publication dicts, adapting the scopus dict structure to the dict structure needed by
        pubcontrol

        Changed 12.04.2018:


        :return:
        """
        self.logger.info('[fetch] starting...')
        author_ids = self.observatory.author_ids
        self.logger.info('[fetch] publications for {} observed authors'.format(len(author_ids)))

        # Fetching all the authors from scopus
        authors = []
        for author_id in author_ids:
            # Changed 12.04.2018
            try:
                author = self.scopus.get_author(author_id)
                self.logger.info('[fetch] author {}'.format(author_id))
            except ConnectionError:
                self.logger.warning('[fetch] Connection error for author {}'.format(author_id))
                continue

            authors.append(author)

        self.logger.info('[fetch] Received {} author profiles from scopus'.format(len(authors)))
        self.logger.info('[fetch] Fetching {} publications...'.format(
            sum(map(lambda x: len(x['publications']), authors))
        ))

        # Fetching all the publications of those authors
        for author in authors:

            for publication_id in author['publications']:

                if self.blacklist.contains(publication_id):
                    self.logger.info('[fetch] skipping publication {}'.format(publication_id))
                    continue
                # Changed 11.04.2018
                # Added the try-except to detect ConnectionErrors, which tell us to skip the publication
                try:
                    publication_dict = self.scopus.get_publication(publication_id)
                    self.logger.info('[fetch] publication {}'.format(publication_id))
                except ConnectionError:
                    self.logger.warning('[fetch] connection error for publication {}'.format(publication_id))
                    self.blacklist.add(publication_id)
                    continue

                if self.observatory.check_publication(publication_dict):

                    self.logger.info('[fetch] yielding publication: {}'.format(publication_id))
                    # First yielding all the citation publications and then the actual one
                    for _publication_dict in publication_dict['citedBy']:
                        # Changed 11.04.2018
                        yield self.adapt_publication_dict(_publication_dict, 'CITATION')
                    # Changed 11.04.2018
                    yield self.adapt_publication_dict(publication_dict, 'PUBLICATION')

    def adapt_publication_dict(self, scopus_publication_dict, type_string):
        """
        CHANGELOG

        Added 11.04.2018
        A method, which will use the adapter to convert the scopus publication dict structure into the dict structure
        needed by pubcontrol create and insert the publication model into the database.

        :param scopus_publication_dict:
        :param type_string:
        :return:
        """
        keywords = self._keywords(scopus_publication_dict)
        arg = (scopus_publication_dict, keywords, type_string)
        return self.adapter.set(arg).get()

    def _keywords(self, scopus_publication_dict):
        keywords = self.observatory.author_keywords(scopus_publication_dict)
        return keywords


class Plugin:

    def __init__(self,
                 controller_class=Controller):
        self.controller_class = controller_class

    @hookimpl
    def fetch(self):
        controller = self.controller_class()
        controller.run()

    @hookimpl
    def install(self, project_path):
        print('[Scopus] Beginning to install scopus plugin')
        from pubcontrol_scopus.install import install_config, install_authors, install_folder
        install_folder(project_path)
        install_config(project_path)
        install_authors(project_path)

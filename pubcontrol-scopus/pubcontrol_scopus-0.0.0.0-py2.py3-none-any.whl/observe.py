from ScopusWp.config import PATH, PROJECT_PATH

from ScopusWp.scopus.data import ScopusAuthorObservation

import pubcontrol.config

from abc import abstractmethod

from jutil.processing import DictQuery

import os
import json
import configparser

# Added 12.04.2018
# Needed to log a few things in this module for debugging, for that the plugin name from config and obviously the
# logging module are needed
import logging
from pubcontrol_scopus.config import Config

from pprint import pprint


class AuthorObservationABC:

    @property
    @abstractmethod
    def ids(self):
        pass

    @abstractmethod
    def check(self, affiliation_list):
        pass


class AuthorObservation(AuthorObservationABC):

    def __init__(self, first_name, last_name, ids, whitelist, blacklist, keywords):
        self.first_name = first_name
        self.last_name = last_name
        self.id_list = ids
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.keywords = keywords

    @property
    def ids(self):
        return self.id_list

    def check(self, affiliation_list):

        # Added 11.04.2018
        # Checking the intersection of the given affiliation list with the whitelist and blacklist of affiliations
        # In case it intersects with the whitelist, its valid, for the blacklist it is invalid.
        # In case it somehow intersects with both the whitelist is favoured. That also means if it is not explicitly
        # in the whitelist it counts as invalid

        whitelist_intersect = list(set(affiliation_list) & set(self.whitelist))
        if len(whitelist_intersect) > 0:
            return True
        else:
            return False


class AuthorObservationBuilderABC:

    @abstractmethod
    def set(self, obj):
        pass

    @abstractmethod
    def get(self):
        pass


class DictAuthorObservationBuilder(AuthorObservationBuilderABC, DictQuery):

    def __init__(self):
        DictQuery.__init__(self)
        self.parameters = {}

    def set(self, obj):
        assert isinstance(obj, dict)
        self.dict = obj
        self.parameters = {}
        return self

    def get(self):
        self.process()
        author_observation = AuthorObservation(**self.parameters)
        return author_observation

    def process(self):
        self.parameters['first_name'] = self.query('first_name', '')
        self.parameters['last_name'] = self.query('last_name', '')
        self.parameters['ids'] = json.loads(self.query('ids', '[]'))
        self.parameters['keywords'] = json.loads(self.query('keywords', '[]'))
        self.parameters['blacklist'] = json.loads(self.query('scopus_blacklist', '[]'))
        self.parameters['whitelist'] = json.loads(self.query('scopus_whitelist', '[]'))

    def query_exception(self, query, query_dict, default):
        return default


class AuthorObservatoryABC:

    @abstractmethod
    def check_publication(self, obj):
        """
        CHANGELOG

        Added 11.04.2018
        A method, that checks a single publication for whether or not the whitelist blacklist condition checks out.
        Realized I needed this, when designing the main fetch method for scopus as a generator for RAM efficiency and
        a full list of publications is never generated, instead they are processed individually

        :param obj:
        :return:
        """
        pass

    @abstractmethod
    def author_keywords(self, obj):
        """
        CHANGELOG

        Added 11.04.2018
        Realized I still needed to somehow assign the author keywords to the publications.
        A method, that takes a publication dict and returns a list of keywords that was specified for each author in
        the author observation file.

        :param obj:
        :return:
        """
        pass

    @abstractmethod
    def filter_publications(self, publication_list):
        pass

    @property
    @abstractmethod
    def author_ids(self):
        pass


class PublicationAdapter(DictQuery):

    def __init__(self):
        DictQuery.__init__(self)
        self.author_dict = {}

    def set(self, obj):
        assert isinstance(obj, dict)
        self.set_query_dict(obj)
        self.author_dict = {}
        return self

    def get(self):
        self.process()
        return self.author_dict

    def process(self):
        author_list = self.query('authors', [])
        # Getting the author id and the list with affiliations from the scopus publication dict
        for author in author_list:
            self.set_query_dict(author)
            author_id = int(self.query('authorID', '0'))
            affiliation_list = int(self.query('affiliation', '0'))
            self.author_dict[author_id] = affiliation_list

    def query_exception(self, query, query_dict, default):
        return default


class AuthorObservatory(AuthorObservatoryABC):
    """
    CHANGELOG

    Changed 12.04.2018
    Added the config and the logger attributes to the class, to enable logging for debugging purposes
    """
    def __init__(self,
                 author_observation_builder_class=DictAuthorObservationBuilder,
                 publication_adapter_class=PublicationAdapter
                 ):
        # Changed 12.04.2018
        self.config = Config()
        self.logger = logging.getLogger(self.config.NAME)

        self.observation_builder = author_observation_builder_class()
        assert isinstance(self.observation_builder, AuthorObservationBuilderABC)
        self.adapter = publication_adapter_class()

        self.pubcontrol_config = pubcontrol.config.Config()
        self.path = self.pubcontrol_config.PROJECT_PATH / self.config.NAME / 'authors.ini'

        self.authors_config_parser = configparser.ConfigParser()
        self.authors_config_parser.read(str(self.path))

        self.dict = {}
        self._build_dict()

    def author_keywords(self, obj):
        """
        CHANGELOG

        Added 11.04.2018

        :param obj:
        :return:
        """
        keywords = []
        author_dict = self.adapter.set(obj).get()
        keys_observed = set(author_dict.keys()) & set(self.dict.keys())
        for author_id in keys_observed:
            keywords += self[author_id].keywords
        # Removing duplicates
        return list(set(keywords))

    def filter_publications(self, publication_list):
        """
        CHANGELOG

        Added 11.04.2018
        for each publication in the set, a author dict will be calculated, which contains the author ids of all
        the authors as keys and the affiliation lists as values. from this dict only those author ids are being
        used, that are being observed. For each of these observed ids the observation object is consulted if the
        affiliation list checks out with the white/blacklist

        Changed 11.04.2018
        After adding the 'check_publication' method, that checks single publications I moved the logic there and
        simply used the single check here for every single obj in the list.
        Slightly more inefficient, but way simpler.

        :param publication_list:
        :return:
        """
        filtered_publications = []
        for obj in publication_list:

            if self.check_publication(obj):
                filtered_publications.append(obj)

        return filtered_publications

    def check_publication(self, obj):
        author_dict = self.adapter.set(obj).get()

        keys_observed = list(set(author_dict.keys()).intersection(set(self.dict.keys())))
        for author_id in keys_observed:
            affiliation_id = author_dict[author_id]
            is_whitelist = affiliation_id in self[author_id].whitelist
            if is_whitelist:
                return True

        # Returning False in every case, where no whitelisting has caused a True return before
        return False

    @property
    def author_ids(self):
        return self.dict.keys()

    def _build_dict(self):
        """
        CHANGELOG

        Changed 12.04.2018
        previously the builder set received the raw value from the items iteration of the config parser, this however
        was a SECTION object from the configparser module not a dict object, which would have been needed for an
        unpacking operation in the builder though, so the SECTION object is being converted to a dict now before being
        passed to the builder
        :return:
        """
        for key, value in self.authors_config_parser.items():
            if key == 'DEFAULT':
                continue
            author_observation = self.observation_builder.set(dict(value)).get()
            for author_id in author_observation.ids:
                self.dict[author_id] = author_observation

    def __getitem__(self, item):
        return self.dict[item]

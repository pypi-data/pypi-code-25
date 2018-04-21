

from pprint import pprint

import logging
import urllib.parse as urlparse
import requests
import json

from jutil.processing import DictQuery

import os
import datetime

from abc import abstractmethod

from pubcontrol_scopus.config import Config

# Changed 13.04.2018
# Ran into a problem with the database encoding and chose to simply get rid of all the unicode in the raw input of the
# scopus database
from unidecode import unidecode


class ScopusABC:

    @abstractmethod
    def get_author(self, author_id):
        pass

    @abstractmethod
    def get_publication(self, publication_id):
        pass


# Changed 11.04.2018
# In case of an Exception during the request, a ConnectionError is invoked, so that the top level knows to skip the
# the publication

class ScopusFetcher(DictQuery):

    def __init__(self, api_key, url):
        super().__init__()

        self.key = api_key
        self.base_url = url

        # Setting the header for the request to tell the scopus website, we want the returned data structure in JSON
        # format.
        self.headers = {
            'Accept': 'application/json',
            'X-ELS-APIKey': self.key
        }
        self.config = Config()
        self.logger = logging.getLogger(self.config.NAME)
        self.url = ''

        self.id = None
        # Will contain the string of the whole response json structure, so unused fields can be analysed later on
        # eventually
        self.raw = None

    def request_retrieval(self, view, url_extension, initial_query, timeout_tuple):
        """
        CHANGELOG

        Changed 12.04.2018
        After executing the inital query, the method checks if that query has succeeded, because for every correct
        response this query has to be correct in case it is not a ConnectionError will be invoked to notify the higher
        level to skip the author in the current processing

        :param view:
        :param url_extension:
        :param initial_query:
        :param timeout_tuple:
        :return:
        """
        # This dict will be converted into the URL query for the API page. It specifies, that scopus is supposed to
        # send as much data as possible with the service level of the given api key
        query = {
            'view': view
        }

        # The url to the general abstract retrieval api page of scopus
        url_extension_split = url_extension.split('/')
        api_url = os.path.join(self.base_url, url_extension_split[0], url_extension_split[1], str(self.id))
        # Encoding the dict query into the url
        query_encoded = urlparse.urlencode(query)
        self.url = '{}?{}'.format(api_url, query_encoded)

        # Sending the request, but expecting a timeout error from the connection. In this case the error will be
        # mapped onto the more general Connection error, which will be catched at the top level.
        try:
            # Setting a relatively low timeout for both (connect, read), as the network is not supposed to slow the
            # the whole program down, better to skip a publication than to loose so much time
            response = requests.get(self.url, headers=self.headers, timeout=timeout_tuple)
            self.raw = response.text

            # Setting the main query dict to the json abstract retrieval
            abstract_retrieval_dict = json.loads(response.text)
            self.set_query_dict(abstract_retrieval_dict)
            # Setting the query dict to the sub level dict specified with the initial query offset

            # Changed 12.04.2018
            # In case the initial query fails, that is an indicator for the response containing an error
            initial = self.query(initial_query, None)
            if initial is None:
                raise ConnectionError
            else:
                self.set_query_dict(initial)
        except Exception as e:
            self.logger.error('[Web] Could not retrieve for {} exception: {}'.format(self.id, str(e)))

            # Changed 11.04.2018
            # The ConnectionError has been chosen by me to signal on the top level, that a request to scopus has gone
            # wrong in some way and that the publication for that request has to be skipped or otherwise handled
            raise ConnectionError

    def request_scopus_search(self, search_query, start, increment, initial_query, timeout_tuple):
        """
        CHANGELOG

        Changed 12.04.2018
        After executing the inital query, the method checks if that query has succeeded, because for every correct
        response this query has to be correct in case it is not a ConnectionError will be invoked to notify the higher
        level to skip the author in the current processing

        :param search_query:
        :param start:
        :param increment:
        :param initial_query:
        :param timeout_tuple:
        :return:
        """
        query = {
            'query': search_query,
            'count': str(increment),
            'start': str(start)
        }

        # The general url to the scopus search api
        api_url = os.path.join(self.base_url, 'search', 'scopus')
        # Encoding the query into the url
        query_encoded = urlparse.urlencode(query)
        self.url = '{}?{}'.format(api_url, query_encoded)

        # Sending the request, but expecting a timeout error from the connection. In this case the error will be
        # mapped onto the more general Connection error, which will be catched at the top level.
        try:
            # Setting a relatively low timeout for both (connect, read), as the network is not supposed to slow the
            # the whole program down, better to skip a publication than to loose so much time
            response = requests.get(self.url, headers=self.headers, timeout=timeout_tuple)

            search_retrieval_dict = json.loads(response.text)
            self.set_query_dict(search_retrieval_dict)

            # Changed 12.04.2018
            # In case the initial query fails, that is an indicator for the response containing an error
            initial = self.query(initial_query, None)
            if initial is None:
                raise ConnectionError
            else:
                self.set_query_dict(initial)
        except Exception as e:
            self.logger.error('[Web] Could not retrieve citation search for {} exception: {}'.format(self.id, str(e)))

            # Changed 11.04.2018
            # The ConnectionError has been chosen by me to signal on the top level, that a request to scopus has gone
            # wrong in some way and that the publication for that request has to be skipped or otherwise handled
            raise ConnectionError


# Changed 11.04.2018
# Added the field 'collaboration' to the keys of the publication dict. It will contain 'none' if the publication is not
# part of a collaboration and the name of the collaboration otherwise

# Changed 11.04.2018
# Added the method 'get_keywords', which will return the publication wide keywords, that come with the scopus raw data
# also implemented, that those keywords will be assigned to the field 'keywords' of the publication dict, which
# already existed, but was unused in the 'process' method

class ScopusPublicationBuilder(DictQuery):

    DEFAULT_AUTHOR_DICT = {
        'authorID': 0,
        'first_name': '',
        'last_name': '',
        'source': '',
        'affiliation': 0
    }

    DEFAULT_PUBLICATION_DICT = {
        'scopusID': 0,
        'eid': '',
        'doi': '',
        'title': '',
        'description': '',
        'date': datetime.datetime.now(),
        'fetched': datetime.datetime.now(),
        'creator': DEFAULT_AUTHOR_DICT,
        'authors': [],
        'citedBy': [],
        'keywords': [],
        'journal': '',
        'volume': '',
        'source': '',
        'raw': '',
        'collaboration': 'none'
    }

    DATETIME_FORMAT = '%Y-%m-%d'

    def __init__(self):
        DictQuery.__init__(self)
        self.publication_dict = {}
        self.id = 0
        self.config = Config()
        self.logger = logging.getLogger(self.config.NAME)

    def set(self, obj):
        assert isinstance(obj, dict)
        self.set_query_dict(obj)
        self.id = self.get_id()
        self.publication_dict = {}

        return self

    def get(self):
        self.process()
        return self.publication_dict

    def process(self):
        self.publication_dict['raw'] = json.dumps(self.dict)
        self.publication_dict.update(self.get_coredata_dict())

        # Changed 11.04.2018
        self.publication_dict['keywords'] = self.get_keywords()
        self.publication_dict['collaboration'] = self.get_collaboration()

        authors = self.get_authors()
        self.publication_dict['authors'] = authors
        if len(authors) != 0:
            self.publication_dict['creator'] = authors[0]
        else:
            self.publication_dict['creator'] = self.get_creator()

    def get_collaboration(self):
        """
        CHANGELOG

        Changed 12.04.2018
        Now the original query dict is being saved at the bigging and set as the query dict at the end, so that if a
        collaboration dict is found, it can be set as query dict, because the call to the dict may cause an error and
        in this case the error handling of the query method is desireable

        :return:
        """
        original_dict = self.dict

        author_group_list = self.query('item/bibrecord/head/author-group', [])
        collaboration = self.DEFAULT_PUBLICATION_DICT['collaboration']
        for item in author_group_list:
            if isinstance(item, dict) and 'collaboration' in item.keys():
                self.set_query_dict(item)
                collaboration = self.query('collaboration/ce:indexed-name', 'none')
                self.logger.info('[request] publication {} collab "{}"'.format(self.id, collaboration))
        # The default value in case no specific name has been returned
        self.set_query_dict(original_dict)
        return collaboration

    def get_id(self):
        """
        Gets the scopus id from the response dict structure.
        Is a separate function as the value needs additional string processing
        :return: the int id
        """
        return int(self.query('coredata/dc:identifier', 'SCOPUS_ID:0').replace('SCOPUS_ID:', ''))

    def get_coredata_dict(self):
        """
        Returns a partial publication dict, which contains all the the coredata, which can be acquired from the
        returned json data structure, without further processing.
        Can be used to update the publication dict with
        :return: dict
        """
        if 'error' in self.query('coredata', {}):
            raise ConnectionError
        return {
            'scopusID': self.get_id(),
            'source': self.query('coredata/prism:url', self.DEFAULT_PUBLICATION_DICT['source']),
            'title': unidecode(self.query('coredata/dc:title', self.DEFAULT_PUBLICATION_DICT['title'])).replace('"', "'"),
            'description': unidecode(self.query('coredata/dc:description', self.DEFAULT_PUBLICATION_DICT['description'])),
            'journal': self.query('coredata/prism:publicationName', self.DEFAULT_PUBLICATION_DICT['journal']),
            'volume': self.query('coredata/prism:volume', self.DEFAULT_PUBLICATION_DICT['volume']),
            'doi': self.query('coredata/prism:doi', self.DEFAULT_PUBLICATION_DICT['doi']),
            'eid': self.query('coredata/eid', self.DEFAULT_PUBLICATION_DICT['eid']),
            'date': datetime.datetime.strptime(self.query(
                'coredata/prism:coverDate',
                self.DEFAULT_PUBLICATION_DICT['date'].strftime(self.DATETIME_FORMAT)
            ), self.DATETIME_FORMAT)
        }

    def get_creator(self):
        """
        CHANGELOG

        Changed 13.04.2018
        Added a unidecode for the creator name, so that the program is not running into trouble with the database
        encoding later on

        :return:
        """
        creator_full = unidecode(self.query('coredata/dc:creator', ' '))
        creator_split = creator_full.split(' ')
        creator_dict = self.DEFAULT_AUTHOR_DICT
        creator_dict.update({'last_name': creator_split[0], 'first_name': creator_split[1]})
        return creator_dict

    def get_keywords(self):
        keywords = []
        original_dict = self.dict
        for item in self.query('idxterms/mainterm', []):
            self.set_query_dict(item)
            keyword = self.query('$')
            if keyword != '':
                keywords.append(keyword)
        self.set_query_dict(original_dict)
        return list(set(keywords))

    def get_authors(self):
        """
        The list of author dicts

        CHANGELOG

        Changed 13.04.2018
        Added a unidecode for the author first name and last name, so that the program is not running into trouble with
        the database encoding later on

        Changed 14.04.2018
        Added a set, that will gather all the full names of the authors and only authors whose name are not already
        added will be appended to the list of author dicts.
        This is for the duplicate key protection of the database.

        :return: [author dicts]
        """
        author_names = {' '}
        author_list = []
        original_dict = self.dict
        for item in self.query('authors/author', default=[]):
            self.set_query_dict(item)
            # Default values for the author dict
            author_dict = self.DEFAULT_AUTHOR_DICT.copy()
            author_dict['authorID'] = int(self.query('@auid', '0'))
            first_name = unidecode(self.query('preferred-name/ce:given-name', ' '))
            last_name = unidecode(self.query('preferred-name/ce:surname', ' '))
            full_name = '{} {}'.format(first_name, last_name)

            author_dict['first_name'] = first_name
            author_dict['last_name'] = last_name
            author_dict['affiliation'] = int(self.query('affiliation/@id', '0'))

            # Only adding non duplicate entries for the first and last name to the list
            if full_name not in author_names:
                author_names.add(full_name)
                author_list.append(author_dict)

        # Changed 11.04.2018
        # Resetting the internal query dict to be the original dict, it was before working with the authors
        self.set_query_dict(original_dict)

        return author_list

    def query(self, dict_query, default=None):
        """
        CHANGELOG

        Changed 14.04.2018
        Overwrote the super method to add behaviour, that in any case if None is actually the querried value from the
        dict, the default value will be returned instead, because a NoneType should really not get into a database
        insert.

        :param dict_query:
        :param default:
        :return:
        """
        query_result = super(ScopusPublicationBuilder, self).query(dict_query, default)
        if query_result is None:
            return default
        return query_result

    def query_exception(self, query, query_dict, default):
        """
        This method will be called if a dict query to the current query dict fails, it gets passed the query for which
        it failed the query dict and the default value chosen for the query.
        In case of failure, the error is simply being logged and the default is returned

        :param query: The query to the dict, that failed
        :param query_dict: The query dict which could not handle the query
        :param default: The default value given
        :return: the default value
        """
        self.logger.warning('[Web] Could not query {} for {}'.format(
            self.id,
            query
        ))
        return default


class ScopusPublicationFetcher(ScopusFetcher):

    def __init__(self, api_key, url, publication_builder_class=ScopusPublicationBuilder):
        super().__init__(api_key, url)

        self.publication_dict = {}
        self.builder = publication_builder_class()

    def set(self, scopus_id):
        """
        Sets the new scopus id fot the publication to be fetched from the scopus database
        :param scopus_id: the int id
        :return: void
        """
        self.id = scopus_id
        return self

    def get(self):
        """
        Returns the fetched scopus publication dict
        :return:
        """
        self.process()
        return self.publication_dict

    def process(self):
        """
        This function executes the whole process of getting the data from the scopus website and constructing the
        publication dict from currently set scopus id
        :return: void
        """
        self.request_abstract_retrieval()
        self.publication_dict = self.builder.set(self.dict).get()
        # Requesting the citation search and for each item in the response also calling the builder
        self.request_citations_search()
        self.publication_dict['citedBy'] = []
        for raw_dict in self.query('entry', []):
            publication_dict = self.builder.set({'coredata': raw_dict}).get()
            self.publication_dict['citedBy'].append(publication_dict)

    def request_citations_search(self, start=0, count=200):
        """
        Sends a request to retrieve all publications, that have cited the currently processed publication to scopus and
        sets the returned json dict structure as the current query dict
        :param start: The start of the list
        :param count: The amount of publications per page
        :return: void
        """
        self.request_scopus_search(
            'refeid({})'.format(self.publication_dict['eid']),
            start,
            count,
            'search-results',
            (15, 15)
        )

    def request_abstract_retrieval(self):
        """
        Sends a abstract retrieval request for the currently set scopus id to the api sites and sets the returned
        json dict structure as the current query dict
        :return: void
        """
        self.request_retrieval(
            'FULL',
            'abstract/scopus_id',
            'abstracts-retrieval-response',
            (15, 15)
        )

    def query_exception(self, query, query_dict, default):
        """
        This method will be called if a dict query to the current query dict fails, it gets passed the query for which
        it failed the query dict and the default value chosen for the query.
        In case of failure, the error is simply being logged and the default is returned
        :param query: The query to the dict, that failed
        :param query_dict: The query dict which coul not handle the query
        :param default: The default value given
        :return: the default value
        """
        self.logger.warning('[Web] Could not query {} for {}'.format(
            query,
            self.id
        ))
        return default


class ScopusAuthorFetcher(ScopusFetcher):

    DEFAULT_AUTHOR_DICT = {
        'authorID': 0,
        'created': datetime.datetime.now(),
        'fetched': datetime.datetime.now(),
        'first_name': '',
        'last_name': '',
        'activity_range': (0, 0),
        'citedBy_count': 0,
        'document_count': 0,
        'source': '',
        'raw': '',
        'h_index': 0,
        'publications': []
    }

    def __init__(self, api_key, url, publication_intervals=25):
        super().__init__(api_key, url)

        self.author_dict = {}
        self.publication_intervals = publication_intervals

    def set(self, author_id):
        self.id = author_id

        return self

    def get(self):
        self.process()
        return self.author_dict

    def process(self):
        # Setting the current query dict to the author retrieval dict
        self.request_author_retrieval()

        self.author_dict = self.DEFAULT_AUTHOR_DICT.copy()
        self.author_dict.update(self.get_coredata_dict())
        self.author_dict['raw'] = self.raw

        self.author_dict['publications'] = self.get_publications()

    def get_publications(self):
        scopus_id_list = []
        document_count = self.author_dict['document_count']
        for i in range(-(-document_count // self.publication_intervals)):
            # Setting the search result dict as current query dict
            self.request_publication_search(i * self.publication_intervals)

            for item in self.query('entry', []):
                self.set_query_dict(item)
                scopus_id = int(self.query('dc:identifier', 'SCOPUS_ID:0').replace('SCOPUS_ID:', ''))
                if scopus_id == 0:
                    continue
                scopus_id_list.append(scopus_id)
        return scopus_id_list

    def get_coredata_dict(self):
        return {
            'authorID': self.get_id(),
            'affiliation': int(self.query('affiliation-current/@id', '0')),
            'first_name': self.query('author-profile/preferred-name/given-name', self.DEFAULT_AUTHOR_DICT['first_name']),
            'last_name': self.query('author-profile/preferred-name/given-name', self.DEFAULT_AUTHOR_DICT['last_name']),
            'citedBy_count': int(self.query('coredata/cited-by-count', self.DEFAULT_AUTHOR_DICT['citedBy_count'])),
            'document_count': int(self.query('coredata/document-count', self.DEFAULT_AUTHOR_DICT['document_count'])),
            'source': self.query('coredata/prism:url', self.DEFAULT_AUTHOR_DICT['source']),
            'h_index': int(self.query('h-index', self.DEFAULT_AUTHOR_DICT['h_index']))
        }

    def get_id(self):
        return int(self.query('coredata/dc:identifier', 'AUTHOR_ID:0').replace('AUTHOR_ID:', ''))

    def request_author_retrieval(self):
        """
        Sends a abstract retrieval request for the currently set scopus id to the api sites and sets the returned
        json dict structure as the current query dict
        :return: void
        """
        self.request_retrieval(
            'ENHANCED',
            'author/author_id',
            'author-retrieval-response/0',
            (15, 15)
        )

    def request_publication_search(self, start):
        self.request_scopus_search(
            'AU-ID({})'.format(self.id),
            start,
            self.publication_intervals,
            'search-results',
            (30, 30)
        )

    def query_exception(self, query, query_dict, default):
        self.logger.warning((
            '[Web] The query {} for author {} failed'
        ).format(query, self.id))
        return default


class Scopus(ScopusABC):

    def __init__(self,
                 publication_fetcher_class=ScopusPublicationFetcher,
                 author_fetcher_class=ScopusAuthorFetcher
                 ):
        self.config = Config()

        self.key = self.config['SCOPUS']['key']
        self.url = self.config['SCOPUS']['url']

        self.publication_fetcher = publication_fetcher_class(self.key, self.url)
        self.author_fetcher = author_fetcher_class(self.key, self.url)

    def get_author(self, author_id):
        return self.author_fetcher.set(author_id).get()

    def get_publication(self, publication_id):
        return self.publication_fetcher.set(publication_id).get()


if __name__ == '__main__':
    publication_fetcher = ScopusPublicationFetcher('3396e90e0692ebaa0496efa66d481c5c', 'https://api.elsevier.com/content')
    pd = publication_fetcher.set(1242311986).get()
    pprint(pd)
from __future__ import absolute_import

import os
import xml.etree.cElementTree as eTree
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from statistics import mean
from typing import Callable, TypeVar

import requests
from appdirs import user_cache_dir

import anidb.compat as compat
from anidb import urls
from anidb.helper import download_file, AnidbHTTPAdapter
from anidb.models import Anime
from anidb.searchModels import ResultList, ResultEntry

__author__ = "Dean Gardiner"
__version__ = "1.0.0"
__version_code__ = 100

DEFAULT_CACHE_TTL = 86400  # 24 hours (cached responses are refreshed every 24 hours)
DEFAULT_LANGUAGE = 'en'
DEFAULT_RATE_LIMIT = 2     # 2 seconds (requests are rate limited to 1 every 2 seconds)
DEFAULT_USER_AGENT = "anidb.py (%s)" % __version__


class Anidb(object):
    client_name = "anidbpy"
    client_version = __version_code__

    def __init__(self, auto_download=True, language=DEFAULT_LANGUAGE, cache=True,
                 cache_expire_after=DEFAULT_CACHE_TTL, rate_limit=DEFAULT_RATE_LIMIT,
                 user_agent=DEFAULT_USER_AGENT, url_anime_list=urls.URL_ANIME_LIST,
                 url_http_api=urls.URL_HTTP_API, url_image_host=urls.URL_IMAGE_HOST):

        self.url_anime_list = url_anime_list
        self.url_http_api = url_http_api
        self.url_image_host = url_image_host

        self.auto_download = auto_download
        self.lang = language
        self.rate_limit = rate_limit

        self.session = None
        self._xml = None
        self._anime_titles = None

        # Initialize cache
        self._cache_path = self._build_session(cache, cache_expire_after, user_agent)
        self._anime_list_path = os.path.join(self._cache_path, "anime-titles.xml.gz")

    def custom_search(self, q, func: Callable, score_method: Callable=max, *args, **kwargs) -> ResultList[Anime]:
        if not self._anime_titles:
            if not self._xml:
                try:
                    self._xml = self._read_file(self._anime_list_path)
                except IOError:
                    if self.auto_download:
                        self.download_anime_list()
                        self._xml = self._read_file(self._anime_list_path)
                    else:
                        raise
        self._anime_titles = {}
        q = q.lower()
        results = ResultList()
        for anime in self._xml.findall("anime"):
            scores = [0]
            for title in anime.findall("title"):
                scores.append(func(q, title.text.lower(), *args, **kwargs))
            a = Anime(self, anime.attrib["aid"], False, anime, self.url_http_api, self.url_image_host)
            results.append(ResultEntry[Anime](a, score_method(scores)))
        return results

    def ratio_search(self, q, min_ratio=0.8, score_method=max) -> ResultList[Anime]:
        result = self.custom_search(q, lambda q, t: SequenceMatcher(None, q, t).ratio(), score_method=score_method)
        result.score_min = min_ratio
        return result

    def search(self, q) -> ResultList[Anime]:
        result = self.custom_search(q, lambda q, t: int(q in t))
        result.score_min = 0.5
        return result

    def anime(self, aid):
        return Anime(self, aid)

    def download_anime_list(self, force=False):
        if not force and os.path.exists(self._anime_list_path):
            modified_date = datetime.fromtimestamp(
                os.path.getmtime(self._anime_list_path))
            if modified_date + timedelta(1) > datetime.now():
                return False
        return download_file(self._anime_list_path, self.url_anime_list)

    def _build_session(self, cache, cache_expire_after, user_agent):
        # Retrieve cache directory
        if isinstance(cache, compat.string_types):
            cache_dir = cache
        else:
            cache_dir = user_cache_dir('anidbpy')

        # Ensure cache directory exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if cache:
            # Construct cached requests session
            import requests_cache

            self.session = requests_cache.CachedSession(
                expire_after=cache_expire_after,
                backend='sqlite',
                cache_name=os.path.join(cache_dir, 'anidbpy'),
            )
        else:
            # Construct simple requests session
            self.session = requests.Session()

        # Set user agent
        self.session.headers.update({
            'User-Agent': user_agent
        })

        # Setup request rate limit
        self.session.mount('http://', AnidbHTTPAdapter(self))
        self.session.mount('https://', AnidbHTTPAdapter(self))

        return cache_dir

    @staticmethod
    def _read_file(path):
        f = open(path, 'rb')
        return eTree.ElementTree(file=f)

    @property
    def cache_path(self):
        return self._cache_path

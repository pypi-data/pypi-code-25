from hurriyet.article import Article
from hurriyet.column import Column
from hurriyet.news_photo_gallery import NewsPhotoGallery
from hurriyet.news_video import NewsVideo
from hurriyet.page import Page
from hurriyet.path import Path
from hurriyet.search import Search
from hurriyet.writer import Writer


class Api(object):
    """Hurriyet API"""
    ROOT_URL = "https://api.hurriyet.com.tr"
    VERSION = "/v1"

    def __init__(self, api_key, **kwargs):
        """
        Hurriyet Api Instance Constructor

        :param api_key: Api Key
        :param kwargs:
        """
        self.root_url = self.ROOT_URL
        self.version = self.VERSION
        self.base_url = "%s%s" % (self.root_url, self.version)
        self.api_key = api_key

    @property
    def article(self):
        """
        Hurriyet Article Operations

        Available methods:

        all     : All articles.
        get     : Single article.
        """
        return Article(api=self)

    @property
    def column(self):
        """
        Hurriyet Column Operations

        Available methods:

        all     : All columns.
        get     : Single column.
        """
        return Column(api=self)

    @property
    def news_photo_gallery(self):
        """
        Hurriyet NewsPhotoGallery Operations

        Available methods:

        all     : All news photo galleries.
        get     : Single news photo gallery.
        """
        return NewsPhotoGallery(api=self)

    @property
    def news_video(self):
        """
        Hurriyet NewsVideo Operations

        Available methods:

        all     : All news videos.
        get     : Single news video.
        """
        return NewsVideo(api=self)

    @property
    def page(self):
        """
        Hurriyet Page Operations

        Available methods:

        all     : All pages.
        get     : Single page.
        """
        return Page(api=self)

    @property
    def path(self):
        """
        Hurriyet Page Operations

        Available methods:

        all     : All pages.
        get     : Single page.
        """
        return Path(api=self)

    @property
    def writer(self):
        """
        Hurriyet Writer Operations

        Available methods:

        all     : All writers.
        get     : Single writer.
        """
        return Writer(api=self)

    @property
    def search(self):
        """
        Hurriyet Writer Operations

        Available methods:

        article                 : Search article with keyword.
        column                  : Search column with keyword.
        folder                  : Search folder with keyword.
        news_photo_gallery      : Search news photo gallery with keyword.
        page                    : Search page with keyword.
        """
        return Search(api=self)

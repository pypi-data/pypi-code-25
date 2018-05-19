from hurriyet.client import Client
from hurriyet.models import Article as ArticleModel
from hurriyet.models import Column as ColumnModel
from hurriyet.models import Folder as FolderModel
from hurriyet.models import NewsPhotoGallery as NewsPhotoGalleryModel
from hurriyet.models import Page as PageModel


class Search(Client):
    """Hurriyet search operations."""

    def __init__(self, **kwargs):
        super(Search, self).__init__(**kwargs)
        self.base_url = "/search"
        self.content_types = {
            "article": "Article",
            "column": "news_photo_gallery",
            "news_photo_gallery": "NewsPhotoGallery",
            "page": "Page",
            "folder": "Folder"
        }

    def _search(self, keyword, content_type):
        url = "%s/%s" % (self.base_url, keyword)
        result = self._get(url)
        result_set = []
        for data in result.get("List"):
            if data.get("ContentType") == content_type:
                result_set.append(data)
        return result_set

    def article(self, keyword):
        result = self._search(keyword, self.content_types["article"])
        return ArticleModel.parse_list(result)

    def column(self, keyword):
        result = self._search(keyword, self.content_types["column"])
        return ColumnModel.parse_list(result)

    def folder(self, keyword):
        result = self._search(keyword, self.content_types["folder"])
        return FolderModel.parse_list(result)

    def news_photo_gallery(self, keyword):
        result = self._search(keyword, self.content_types["news_photo_gallery"])
        return NewsPhotoGalleryModel.parse_list(result)

    def page(self, keyword):
        result = self._search(keyword, self.content_types["page"])
        return PageModel.parse_list(result)

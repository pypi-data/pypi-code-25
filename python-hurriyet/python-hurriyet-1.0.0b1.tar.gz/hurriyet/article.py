from hurriyet.base import BaseClient
from hurriyet.models import Article as ArticleModel


class Article(BaseClient):
    """Hurriyet article operations."""

    def __init__(self, **kwargs):
        super(Article, self).__init__(**kwargs)
        self.model_class = ArticleModel
        self.base_url = "/articles"

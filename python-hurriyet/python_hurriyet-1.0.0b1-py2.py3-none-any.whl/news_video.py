from hurriyet.base import BaseClient
from hurriyet.models import NewsVideo as NewsVideoModel


class NewsVideo(BaseClient):
    """Hurriyet news video operations."""

    def __init__(self, **kwargs):
        super(NewsVideo, self).__init__(**kwargs)
        self.model_class = NewsVideoModel
        self.base_url = "/newsvideos"

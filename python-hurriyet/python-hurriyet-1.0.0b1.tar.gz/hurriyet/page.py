from hurriyet.base import BaseClient
from hurriyet.models import Page as PageModel


class Page(BaseClient):
    """Hurriyet page operations."""

    def __init__(self, **kwargs):
        super(Page, self).__init__(**kwargs)
        self.model_class = PageModel
        self.base_url = "/pages"

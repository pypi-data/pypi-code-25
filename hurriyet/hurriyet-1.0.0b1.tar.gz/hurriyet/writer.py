from hurriyet.base import BaseClient
from hurriyet.models import Writer as WriterModel


class Writer(BaseClient):
    """Hurriyet writer operations."""

    def __init__(self, **kwargs):
        super(Writer, self).__init__(**kwargs)
        self.model_class = WriterModel
        self.base_url = "/writers"

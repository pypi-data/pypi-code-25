from hurriyet.base import BaseClient
from hurriyet.models import Path as PathModel


class Path(BaseClient):
    """Hurriyet path operations."""

    def __init__(self, **kwargs):
        super(Path, self).__init__(**kwargs)
        self.model_class = PathModel
        self.base_url = "/paths"

from hurriyet.base import BaseClient
from hurriyet.models import NewsPhotoGallery as NewsPhotoGalleryModel


class NewsPhotoGallery(BaseClient):
    """Hurriyet news photo gallery operations."""

    def __init__(self, **kwargs):
        super(NewsPhotoGallery, self).__init__(**kwargs)
        self.model_class = NewsPhotoGalleryModel
        self.base_url = "/newsphotogalleries"

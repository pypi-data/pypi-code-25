from django.core.files.base import ContentFile
from reports.models import BaseReport


class ExampleReport(BaseReport):
    """
    Example report
    """

    id = u'example'
    name = u'Example report'

    def generate(self, **kwargs):
        return ContentFile(u'Some data')

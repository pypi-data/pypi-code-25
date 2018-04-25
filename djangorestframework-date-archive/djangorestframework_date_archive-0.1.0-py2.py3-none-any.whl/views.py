from django.core.exceptions import ImproperlyConfigured
from rest_framework.generics import ListAPIView

from .querysets import DateArchiveMixin


__all__ = ['DateArchiveView']


class DateArchiveView(ListAPIView):
    """
    Archived date view. makes use of DateArchiveMixin.
    """

    def get_queryset(self):
        queryset = super().get_queryset()

        if not isinstance(queryset, DateArchiveMixin):
            raise ImproperlyConfigured('model manager {0} must inherit from {1}.'
                                       ''.format(queryset.model.__name__,
                                                 DateArchiveMixin.__name__))

        elif 'year' in self.kwargs:
            return queryset.get_period(year=int(self.kwargs['year']),
                                       month=int(self.kwargs.get('month', 0)),
                                       day=int(self.kwargs.get('day', 0)))

        else:
            return queryset

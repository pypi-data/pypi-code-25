from rest_framework.routers import DefaultRouter, Route

from .querysets import Period


__all__ = ['DateArchiveRouter']


class DateArchiveRouter(DefaultRouter):
    """
    Router implementing date archive pattern from django
    https://docs.djangoproject.com/en/2.0/ref/class-based-views/generic-date-based/
    """

    year_regex = r'[12][0-9][0-9][0-9]'
    month_regex = r'[1-9]|1[0-2]'
    day_regex = r'[1-9]|[12][0-9]|3[01]'

    def get_routes(self, viewset):
        # add archive routes
        archive_portion = r''
        for period in Period.all:
            archive_portion += r'{slash}(?P<{name}>{pattern})' \
                               r''.format(name=period,
                                          pattern=getattr(self, '{}_regex'.format(period)),
                                          slash='/' if period != 'year' else '')
            self.routes.append(self.__make_archive_route(archive_portion, period))

        # call
        return super().get_routes(viewset)

    @classmethod
    def __make_archive_route(cls, archive_portion, period):
        return Route(url=r'^{{prefix}}/archive/{portion}{{trailing_slash}}$'
                         r''.format(portion=archive_portion),
                     mapping={'get': 'list'},
                     detail=False,
                     name=r'{{basename}}-archive-{period}'.format(period=period),
                     initkwargs={'suffix': 'List'})

from datetime import date, datetime, time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import DateTimeField
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views.generic.dates import timezone_today


__all__ = ['DateArchiveMixin']


PERIOD_LIST = ['year', 'month', 'day']


class DateArchiveMixin:  # pylint: disable=too-few-public-methods
    """
    Queryset mixin returning data for a given period
    """
    allow_future = False
    date_field = None
    date_archive_field = 'period'
    period_list = PERIOD_LIST

    def get_period(self, year, month=None, day=None):
        """
        :param year: the year to archive on
        :param month: the month to archive on. If none or 0, yearly archive
        :param day: the day to archive on. If non or 0, monthly archive
        :return: QuerySet containing the data for the period selected
        """
        # initial step
        date_args = [year, month, day]
        queryset = self

        # get period name
        if day and not month:
            raise ValueError("A month must be supplied if a day is "
                             "passed to 'get_period' method.")
        if not self.date_field:
            raise ImproperlyConfigured('class attribute {} must be supplied.'
                                       ''.format(self.date_field.__name__))

        period = self.period_list[len([arg for arg in date_args if arg]) - 1]

        # annotate by period
        queryset = queryset.annotate(**{self.date_archive_field: Trunc(self.date_field, period)})

        # remove future values
        if not self.allow_future:
            queryset = queryset.__filter_future_dates(self.date_field)  # pylint: disable=protected-access

        # get period value: consider date vs datetime?
        period_date = self.__make_date_value(self.date_field, date_args)

        # return filtered value
        return queryset.filter(**{self.date_archive_field: period_date})

    def __is_datetime_field(self, date_field):
        field = self.model._meta.get_field(date_field)  # pylint: disable=protected-access
        return isinstance(field, DateTimeField)

    def __make_date_value(self, date_field, date_args):
        date_ = date(**{period: val if val else 1
                        for period, val in zip(self.period_list, date_args)})

        if self.__is_datetime_field(date_field):
            date_ = datetime.combine(date_, time.min)
            if settings.USE_TZ:
                date_ = timezone.make_aware(date_, timezone.get_current_timezone())

        return date_

    def __filter_future_dates(self, date_field):
        now = timezone.now() if self.__is_datetime_field(date_field) else timezone_today()
        return self.filter(**{'%s__lte' % date_field: now})

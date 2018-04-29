from datetime import date, datetime, time

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import DateTimeField
from django.db.models.functions import Trunc
from django.utils import timezone
from django.views.generic.dates import timezone_today


__all__ = ['DateArchiveMixin', 'Period']


class Period(object):
    all = ['year', 'month', 'day']

    @classmethod
    def name(cls, *date_args):
        return cls.all[len(cls.__clean_args(date_args)) - 1]

    @classmethod
    def validate(cls, period):
        # check if period is correct
        if period not in cls.all:
            raise ValueError('Unknown period {}. Valid periods: {}'.format(period, cls.all))

    @classmethod
    def from_date(cls, period, date_):
        cls.validate(period)
        return [getattr(date_, cls.all[i]) for i in range(0, cls.all.index(period) + 1)]

    @classmethod
    def to_date(cls, *date_args):
        date_args = cls.__clean_args(date_args)
        date_args = list(date_args) + [1]*(len(cls.all) - len(date_args))
        return date(**{period: val if val else 1 for period, val in zip(cls.all, date_args)})

    @classmethod
    def __clean_args(cls, args):
        return [arg for arg in args if arg]


class DateArchiveMixin:  # pylint: disable=too-few-public-methods
    """
    Queryset mixin returning data for a given period
    """
    allow_future = False
    archive_field = None
    period_annotated_field = 'period'

    def get_period(self, year, month=0, day=0):
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
        if not self.archive_field:
            raise ImproperlyConfigured("class attribute 'archive_field' must be supplied.")

        period = Period.name(*date_args)

        # annotate by period
        queryset = queryset.__annotate_with_period(period)  # pylint: disable=protected-access

        # remove future values
        if not self.allow_future:
            queryset = queryset.__filter_future_dates()  # pylint: disable=protected-access

        # get period value: consider date vs datetime?
        date_ = Period.to_date(*(arg for arg in date_args if arg))
        period_date = self.__make_date_value(date_)

        # return filtered value
        return queryset.filter(**{self.period_annotated_field: period_date})

    def get_earliest_period(self, period):
        """
        :param period: the period over which to archive (year, month or day)
        :return: the earliest period as QuerySet
        """
        return self.__get_earliest_or_latest(period, True)

    def get_latest_period(self, period):
        """
        :param period: the period over which to archive (year, month or day)
        :return: the latest period as QuerySet
        """
        return self.__get_earliest_or_latest(period, False)

    def __annotate_with_period(self, period):
        return self.annotate(**{self.period_annotated_field: Trunc(self.archive_field, period)})

    def __get_earliest_or_latest(self, period, earliest):

        # validate data
        Period.validate(period)
        if not self.archive_field:
            raise ImproperlyConfigured("class attribute 'archive_field' must be supplied.")

        # get queryset annotated with period
        if self.allow_future:
            queryset = self
        else:
            queryset = self.__filter_future_dates()  # pylint: disable=protected-access

        # get queryset annotated with period
        queryset = queryset.__annotate_with_period(period)  # pylint: disable=protected-access

        # get earliest/latest period
        selector = getattr(queryset, 'earliest' if earliest else 'latest')
        selected_period = selector(self.period_annotated_field)
        period_date = getattr(selected_period, self.archive_field)

        # filter by said period
        return queryset.filter(**{self.period_annotated_field: period_date})

    def __is_datetime_field(self, date_field):
        field = self.model._meta.get_field(date_field)  # pylint: disable=protected-access
        return isinstance(field, DateTimeField)

    def __filter_future_dates(self):
        now = timezone.now() if self.__is_datetime_field(self.archive_field) else timezone_today()
        return self.filter(**{'%s__lte' % self.archive_field: now})

    def __make_date_value(self, date_):
        if self.__is_datetime_field(self.archive_field):
            date_ = datetime.combine(date_, time.min)
            if settings.USE_TZ:
                date_ = timezone.make_aware(date_, timezone.get_current_timezone())

        return date_

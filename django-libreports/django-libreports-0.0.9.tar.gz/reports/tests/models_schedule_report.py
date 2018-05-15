import json
from django_celery_beat.models import PeriodicTask
from mock import patch
from datetime import datetime
from django.test import TestCase

from reports.models import ReportSchedule
from reports.runtests.example.models import Organization


class ScheduleReportModelTestCase(TestCase):

    @patch('django.utils.timezone.now')
    def test_datetimes_by_period(self, mNow):

        mNow.return_value = datetime(2012, 12, 12, 12, 12, 12)
        org = Organization(name='Org')

        # Daily
        daily = ReportSchedule(organization=org)
        daily.period = ReportSchedule.PERIOD_DAILY
        start, end = daily.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 12, 11, 0, 0, 0))
        self.assertEquals(end, datetime(2012, 12, 11, 23, 59, 59))

        # Weekly
        weekly = ReportSchedule(organization=org)
        weekly.period = ReportSchedule.PERIOD_WEEKLY
        start, end = weekly.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 12, 3, 0, 0, 0))
        self.assertEquals(end, datetime(2012, 12, 9, 23, 59, 59))

        # Monthly
        monthly = ReportSchedule(organization=org)
        monthly.period = ReportSchedule.PERIOD_MONTHLY
        start, end = monthly.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 11, 1, 0, 0, 0))
        self.assertEquals(end, datetime(2012, 11, 30, 23, 59, 59))

        # Yearly
        yearly = ReportSchedule(organization=org)
        yearly.period = ReportSchedule.PERIOD_YEARLY
        start, end = yearly.datetimes_by_period()
        self.assertEquals(start, datetime(2011, 1, 1, 0, 0, 0))
        self.assertEquals(end, datetime(2011, 12, 31, 23, 59, 59))

    @patch('django.utils.timezone.now')
    def test_datetimes_by_period_choosen_date(self, mNow):

        org = Organization(name='Org')
        mNow.return_value = datetime(2012, 12, 12, 12, 12, 12)

        # Daily
        daily = ReportSchedule(organization=org)
        daily.period = ReportSchedule.PERIOD_DAILY
        daily.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        start, end = daily.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 12, 11, 10, 10, 11))
        self.assertEquals(end, datetime(2012, 12, 12, 10, 10, 10))

        # Weekly
        weekly = ReportSchedule(organization=org)
        weekly.period = ReportSchedule.PERIOD_WEEKLY
        weekly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        start, end = weekly.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 12, 5, 10, 10, 11))
        self.assertEquals(end, datetime(2012, 12, 12, 10, 10, 10))

        # Monthly
        monthly = ReportSchedule(organization=org)
        monthly.period = ReportSchedule.PERIOD_MONTHLY
        monthly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        start, end = monthly.datetimes_by_period()
        self.assertEquals(start, datetime(2012, 11, 12, 10, 10, 11))
        self.assertEquals(end, datetime(2012, 12, 12, 10, 10, 10))

        # Yearly
        yearly = ReportSchedule(organization=org)
        yearly.period = ReportSchedule.PERIOD_YEARLY
        yearly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        start, end = yearly.datetimes_by_period()
        self.assertEquals(start, datetime(2011, 12, 12, 10, 10, 11))
        self.assertEquals(end, datetime(2012, 12, 12, 10, 10, 10))

    def test_set_schedule(self):

        org = Organization.objects.create(name='Org')

        # Daily
        daily = ReportSchedule(organization=org)
        daily.period = ReportSchedule.PERIOD_DAILY
        daily.set_schedule()
        self.assertEquals(daily.schedule, {
            'day_of_month': '*',
            'day_of_week': '*',
            'hour': '6',
            'minute': '0',
            'month_of_year': '*'
        })

        # Weekly
        weekly = ReportSchedule(organization=org)
        weekly.period = ReportSchedule.PERIOD_WEEKLY
        weekly.set_schedule()
        self.assertEquals(weekly.schedule, {
            'day_of_month': '*',
            'day_of_week': '1',
            'hour': '6',
            'minute': '0',
            'month_of_year': '*'
        })

        # Monthly
        monthly = ReportSchedule(organization=org)
        monthly.period = ReportSchedule.PERIOD_MONTHLY
        monthly.set_schedule()
        self.assertEquals(monthly.schedule, {
            'day_of_month': '1',
            'day_of_week': '*',
            'hour': '6',
            'minute': '0',
            'month_of_year': '*'
        })

        # Yearly
        yearly = ReportSchedule(organization=org)
        yearly.period = ReportSchedule.PERIOD_YEARLY
        yearly.set_schedule()
        self.assertEquals(yearly.schedule, {
            'day_of_month': '1',
            'day_of_week': '*',
            'hour': '6',
            'minute': '0',
            'month_of_year': '1'
        })

    def test_set_schedule_choosen_date(self):

        org = Organization.objects.create(name='Org')

        # Daily
        daily = ReportSchedule(organization=org)
        daily.period = ReportSchedule.PERIOD_DAILY
        daily.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        daily.set_schedule()
        self.assertEquals(daily.schedule, {
            'day_of_month': '*',
            'day_of_week': '*',
            'hour': '10',
            'minute': '10',
            'month_of_year': '*'
        })

        # Weekly
        weekly = ReportSchedule(organization=org)
        weekly.period = ReportSchedule.PERIOD_WEEKLY
        weekly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        weekly.set_schedule()
        self.assertEquals(weekly.schedule, {
            'day_of_month': '*',
            'day_of_week': '6',
            'hour': '10',
            'minute': '10',
            'month_of_year': '*'
        })

        # Monthly
        monthly = ReportSchedule(organization=org)
        monthly.period = ReportSchedule.PERIOD_MONTHLY
        monthly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        monthly.set_schedule()
        self.assertEquals(monthly.schedule, {
            'day_of_month': '10',
            'day_of_week': '*',
            'hour': '10',
            'minute': '10',
            'month_of_year': '*'
        })

        # Yearly
        yearly = ReportSchedule(organization=org)
        yearly.period = ReportSchedule.PERIOD_YEARLY
        yearly.report_datetime = datetime(2010, 10, 10, 10, 10, 10)
        yearly.set_schedule()
        self.assertEquals(yearly.schedule, {
            'day_of_month': '10',
            'day_of_week': '*',
            'hour': '10',
            'minute': '10',
            'month_of_year': '10'
        })

    def test_periodic_task_kwargs(self):
        org = Organization.objects.create(name='Org')

        schedule = ReportSchedule(organization=org)
        schedule.period = ReportSchedule.PERIOD_DAILY
        schedule.set_schedule()
        schedule.set_periodic_task()

        task = schedule.periodic_task
        # Make sure django-celery-beat can properly load kwargs
        json.loads(task.kwargs)

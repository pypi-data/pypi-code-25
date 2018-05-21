import unittest
from datetime import datetime

from yangsutil import DateTimeUtil


class DateTimeUtilTestCase(unittest.TestCase):
    def test_1_gap_full_datetime(self):
        target_datetime = '2017-06-27 00:00:00'
        datetime_form = '%Y-%m-%d %H:%M:%S'

        # test
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=-5,
                datetime_type=DateTimeUtil.SECONDS,
                output_form=datetime_form
            ),
            '2017-06-26 23:59:55',
            msg='second test')

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=5,
                datetime_type=DateTimeUtil.MINUTES,
                output_form=datetime_form
            ),
            '2017-06-27 00:05:00',
            msg='minute test'
        )

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=-1,
                datetime_type=DateTimeUtil.HOURS,
                output_form=datetime_form
            ),
            '2017-06-26 23:00:00',
            msg='hour test'
        )

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=1,
                datetime_type=DateTimeUtil.DAYS,
                output_form=datetime_form
            ),
            '2017-06-28 00:00:00',
            msg='day test'
        )

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=-2,
                datetime_type=DateTimeUtil.WEEKS,
                output_form=datetime_form
            ),
            '2017-06-13 00:00:00',
            msg='week test'
        )

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=5,
                datetime_type=DateTimeUtil.MONTHS,
                output_form=datetime_form
            ),
            '2017-11-27 00:00:00',
            msg='month test'
        )

        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                gap=10,
                datetime_type=DateTimeUtil.YEARS,
                output_form=datetime_form
            ),
            '2027-06-27 00:00:00',
            msg='year test'
        )

    def test_2_gap_one_seconds(self):
        target_datetime = '2017-06-27 13:10'
        datetime_form = '%Y-%m-%d %H:%M'
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                output_form=datetime_form,
                gap=-1,
                datetime_type=DateTimeUtil.SECONDS
            ),
            '2017-06-27 13:09',
            msg='%Y-%m-%d %H:%M - 1sec'
        )

        target_datetime = '2017-06-27 13'
        datetime_form = '%Y-%m-%d %H'
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                output_form=datetime_form,
                gap=1,
                datetime_type=DateTimeUtil.SECONDS
            ),
            '2017-06-27 13',
            msg='%Y-%m-%d %H - 1sec'
        )

        target_datetime = '2017-06-27'
        datetime_form = '%Y-%m-%d'
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                output_form=datetime_form,
                gap=-1,
                datetime_type=DateTimeUtil.SECONDS
            ),
            '2017-06-26',
            msg='%Y-%m-%d - 1sec'
        )

        target_datetime = '2017-06'
        datetime_form = '%Y-%m'
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                output_form=datetime_form,
                gap=1,
                datetime_type=DateTimeUtil.SECONDS
            ),
            '2017-06',
            msg='%Y-%m - 1sec'
        )

        target_datetime = '2017'
        datetime_form = '%Y'
        self.assertEqual(
            DateTimeUtil.get_string(
                src_object=target_datetime,
                src_object_form=datetime_form,
                output_form=datetime_form,
                gap=-1,
                datetime_type=DateTimeUtil.SECONDS
            ),
            '2016',
            msg='%Y - 1sec'
        )

    def test_3_start_is_start_and_end_is_end(self):
        start_date = '20170626-102311'
        end_date = '20170626-102311'
        datetime_form = '%Y%m%d-%H%M%S'
        self.assertTrue(
            DateTimeUtil.is_avail_date_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form
            )
        )

        start_date = '20170626-1123'
        end_date = '20170625-1200'
        datetime_form = '%Y%m%d-%H%M'
        self.assertFalse(
            DateTimeUtil.is_avail_date_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form
            )
        )

        start_date = '20160626-11'
        end_date = '20170625-05'
        datetime_form = '%Y%m%d-%H'
        self.assertTrue(
            DateTimeUtil.is_avail_date_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form
            )
        )

        start_date = '20170626'
        end_date = '20170403'
        self.assertFalse(
            DateTimeUtil.is_avail_date_range(
                start_object=start_date,
                end_object=end_date
            )
        )

        start_date = '201606'
        end_date = '201701'
        datetime_form = '%Y%m'
        self.assertTrue(
            DateTimeUtil.is_avail_date_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form
            )
        )

    def test_4_date_range(self):
        start_date = '20170626-102311'
        end_date = '20160626-102311'
        datetime_form = '%Y%m%d-%H%M%S'
        self.assertListEqual(
            DateTimeUtil.get_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form,
                datetime_type=DateTimeUtil.SECONDS
            ),
            [
                datetime(year=2016, month=6, day=26, hour=10, minute=23, second=11)
            ]
        )

        start_date = '20170626-102311'
        end_date = '20170626-102315'
        datetime_form = '%Y%m%d-%H%M%S'
        self.assertListEqual(
            DateTimeUtil.get_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form,
                datetime_type=DateTimeUtil.SECONDS
            ),
            [
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=11),
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=12),
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=13),
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=14),
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=15),
            ]
        )

        start_date = '20170626-102311'
        end_date = '20170701-102311'
        datetime_form = '%Y%m%d-%H%M%S'
        self.assertListEqual(
            DateTimeUtil.get_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form,
                datetime_type=DateTimeUtil.DAYS
            ),
            [
                datetime(year=2017, month=6, day=26, hour=10, minute=23, second=11),
                datetime(year=2017, month=6, day=27, hour=10, minute=23, second=11),
                datetime(year=2017, month=6, day=28, hour=10, minute=23, second=11),
                datetime(year=2017, month=6, day=29, hour=10, minute=23, second=11),
                datetime(year=2017, month=6, day=30, hour=10, minute=23, second=11),
                datetime(year=2017, month=7, day=1, hour=10, minute=23, second=11),
            ]
        )

        start_date = '20170626-10'
        end_date = '20170626-15'
        datetime_form = '%Y%m%d-%H'
        self.assertListEqual(
            DateTimeUtil.get_range(
                start_object=start_date,
                end_object=end_date,
                start_object_form=datetime_form,
                end_object_form=datetime_form,
                datetime_type=DateTimeUtil.HOURS
            ),
            [
                datetime(year=2017, month=6, day=26, hour=10, minute=0, second=0),
                datetime(year=2017, month=6, day=26, hour=11, minute=0, second=0),
                datetime(year=2017, month=6, day=26, hour=12, minute=0, second=0),
                datetime(year=2017, month=6, day=26, hour=13, minute=0, second=0),
                datetime(year=2017, month=6, day=26, hour=14, minute=0, second=0),
                datetime(year=2017, month=6, day=26, hour=15, minute=0, second=0),
            ]
        )

    def test_5_get_weekday(self):
        target_date = '20170626-102311'
        datetime_form = '%Y%m%d-%H%M%S'

        self.assertEqual(
            DateTimeUtil.get_weekday(src_object=target_date, src_object_form=datetime_form),
            'Mon',
            msg='WeekDay Check "en"'
        )

        self.assertEqual(
            DateTimeUtil.get_weekday(src_object=target_date, src_object_form=datetime_form, lang='ko'),
            '월',
            msg='WeekDay Check "ko"'
        )

        self.assertEqual(
            DateTimeUtil.get_weekday(src_object=target_date, src_object_form=datetime_form, lang='aaaa'),
            0,
            msg='WeekDay Check "other"'
        )

    def test_6_get_datetime_diff(self):
        form = '%Y%m%d-%H%M%S'

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180327-103322',
                sec_object_form=form
            ),
            0,
            msg='equal seconds'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103323',
                fst_object_form=form,
                sec_object='20180327-103322',
                sec_object_form=form
            ),
            1,
            msg='plus one seconds'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180327-103323',
                sec_object_form=form
            ),
            -1,
            msg='minus one seconds'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180326-103322',
                sec_object_form=form
            ),
            86400,
            msg='one day'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180326-103321',
                sec_object_form=form
            ),
            86400 + 1,
            msg='one day plus one second'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180326-103323',
                sec_object_form=form
            ),
            86400 - 1,
            msg='one day minus one second'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180328-103322',
                sec_object_form=form
            ),
            -86400,
            msg='minus one day'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180328-103323',
                sec_object_form=form
            ),
            -86400 - 1,
            msg='minus one day minus one second'
        )

        self.assertEqual(
            DateTimeUtil.get_datetime_diff(
                fst_object='20180327-103322',
                fst_object_form=form,
                sec_object='20180328-103321',
                sec_object_form=form
            ),
            -86400 + 1,
            msg='minus one day plus one second'
        )

    @unittest.skip
    def test_7_get_date_diff(self):
        pass

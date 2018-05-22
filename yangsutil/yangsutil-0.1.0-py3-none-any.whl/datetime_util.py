from dateutils import relativedelta
from datetime import datetime, timedelta, date


class DateTimeUtil:
    SECONDS = 1
    MINUTES = 2
    HOURS = 3
    DAYS = 4
    WEEKS = 5
    MONTHS = 6
    YEARS = 7

    @staticmethod
    def get_object(src_object=None, src_object_form='%Y%m%d', gap=0, datetime_type=4):

        if src_object is not None:

            if type(src_object) == str:
                datetime_object = datetime.strptime(src_object, src_object_form)

            elif type(src_object) == datetime:
                datetime_object = src_object

            elif type(src_object) == date:
                datetime_object = datetime(year=src_object.year, month=src_object.month, day=src_object.day)

            else:
                datetime_object = datetime.now()

        else:
            datetime_object = datetime.now()

        if datetime_type == 1:
            datetime_object += timedelta(seconds=gap)
        elif datetime_type == 2:
            datetime_object += timedelta(minutes=gap)
        elif datetime_type == 3:
            datetime_object += timedelta(hours=gap)
        elif datetime_type == 4:
            datetime_object += timedelta(days=gap)
        elif datetime_type == 5:
            datetime_object += timedelta(weeks=gap)
        elif datetime_type == 6:
            datetime_object += relativedelta(months=gap)
        elif datetime_type == 7:
            datetime_object += relativedelta(years=gap)
        else:
            raise TypeError('before type ==> sec, min, hour, day, week, month, year')

        return datetime_object

    @staticmethod
    def get_string(src_object=None, src_object_form='%Y%m%d', gap=0, datetime_type=4, output_form='%Y%m%d'):
        return DateTimeUtil.get_object(
            src_object=src_object,
            src_object_form=src_object_form,
            gap=gap,
            datetime_type=datetime_type
        ).strftime(output_form)

    @staticmethod
    def is_avail_date_range(start_object=None, start_object_form='%Y%m%d', end_object=None, end_object_form='%Y%m%d',
                            datetime_type=4):

        start_datetime = DateTimeUtil.get_object(
            src_object=start_object,
            src_object_form=start_object_form
        )
        end_datetime = DateTimeUtil.get_object(
            src_object=end_object,
            src_object_form=end_object_form
        )

        if datetime_type in range(1, 4):
            return (end_datetime - start_datetime) >= timedelta(seconds=0)
        else:
            return (end_datetime - start_datetime) >= timedelta(days=0)

    @staticmethod
    def get_range(start_object=None, start_object_form='%Y%m%d', end_object=None, end_object_form='%Y%m%d',
                  datetime_type=4):

        if start_object is None:
            raise ValueError('start_object is none')

        start_datetime = DateTimeUtil.get_object(
            src_object=start_object,
            src_object_form=start_object_form
        )

        end_datetime = DateTimeUtil.get_object() if end_object is None else DateTimeUtil.get_object(
            src_object=end_object,
            src_object_form=end_object_form
        )

        if DateTimeUtil.is_avail_date_range(start_object=start_datetime, end_object=end_datetime) is False:
            return [end_datetime]

        date_list = list()

        while True:
            if start_datetime > end_datetime:
                break

            date_list.append(start_datetime)

            if datetime_type == 1:
                start_datetime += timedelta(seconds=1)
            elif datetime_type == 2:
                start_datetime += timedelta(minutes=1)
            elif datetime_type == 3:
                start_datetime += timedelta(hours=1)
            elif datetime_type == 4:
                start_datetime += timedelta(days=1)
            elif datetime_type == 5:
                start_datetime += timedelta(weeks=1)
            elif datetime_type == 6:
                start_datetime += relativedelta(months=1)
            elif datetime_type == 7:
                start_datetime += relativedelta(years=1)
            else:
                raise TypeError("should input datetime type ")

        return date_list

    @staticmethod
    def get_weekday(src_object=None, src_object_form='%Y%m%d', lang='en'):
        obj = DateTimeUtil.get_object(src_object=src_object, src_object_form=src_object_form)

        if lang == 'en':
            words = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        elif lang == 'ko':
            words = ['월', '화', '수', '목', '금', '토', '일']

        else:
            words = range(0, 7)

        return words[obj.weekday()]

    @staticmethod
    def get_datetime_diff(fst_object=None, fst_object_form='%Y%m%d', sec_object=None, sec_object_form='%Y%m%d'):

        first = DateTimeUtil.get_object(
            src_object=fst_object,
            src_object_form=fst_object_form
        )
        second = DateTimeUtil.get_object(
            src_object=sec_object,
            src_object_form=sec_object_form
        )

        days = (first - second).days
        seconds = (first - second).seconds
        total_seconds = (days * 60 * 60 * 24) + seconds

        return total_seconds

    @staticmethod
    def get_timestamp(src_object=None, src_object_form='%Y%m%d', gap=0, datetime_type=4):
        return int(DateTimeUtil.get_object(
            src_object=src_object,
            src_object_form=src_object_form,
            gap=gap,
            datetime_type=datetime_type
        ).timestamp())

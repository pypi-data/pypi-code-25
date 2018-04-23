import datetime
import pytz
import time
dt = datetime.datetime(2017, 3, 21, 15, 55, 44)
dt.replace(tzinfo=pytz.UTC)
print(time.mktime(dt.timetuple()))
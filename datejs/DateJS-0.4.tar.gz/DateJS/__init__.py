import datetime
import pytz
import JSPy as js

class DateJS():
    def __init__(self, JS_STRING, y=0, m=0, d=0, h=0, minute=0, s=0, ms=0, tzo=0):
        self.YEAR = y
        self.MONTH = m + 1
        self.DATE = d
        self.HOUR = h
        self.MINUTE = minute
        self.SECOND = s
        self.MILLISECONDS = ms
        self.OFFSET = int(tzo)
        self.TZ = None
        self.TZ_SIMPLE = None
        self.TZ_CUSTOM = None
        self.JS_TIME = JS_STRING
        self.PYTIME = datetime.datetime.now()
        self.PYTIME_SIMPLE = datetime.datetime.now()
        self.PYTIME_CUSTOM = datetime.datetime.now()
        self.CUSTOM_TIMEZONES = []
        self.jsFunction = None
        self.result = None
        if self.YEAR == 0:
            self.runJSFunction()
        self.setAllValues()

    def runJSFunction(self):
        self.jsFunction = """
                function run(x){
                    var date = new Date(x);
                    console.log(date.getFullYear());
                    console.log(date.getMonth());
                    console.log(date.getDate());
                    console.log(date.getHours());
                    console.log(date.getMinutes());
                    console.log(date.getSeconds());
                    console.log(date.getMilliseconds());
                    console.log(date.getTimezoneOffset());
                }
            """
        funcCall = "run('" + self.JS_TIME + "');"
        self.result = js.exec(self.jsFunction + funcCall).splitlines()
        self.result = [int(k) for k in self.result]
        return

    def setAllValues(self):
        if not self.result == None:
            self.setYear()
            self.setMonth()
            self.setDate()
            self.setHour()
            self.setMinute()
            self.setSecond()
            self.setMillisecond()
        self.setTZ()

    def getTime(self):
        self.PYTIME = self.PYTIME.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ))
        return self.PYTIME

    def getSimpleTime(self):
        self.PYTIME_SIMPLE = self.PYTIME_SIMPLE.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ_SIMPLE))
        return self.PYTIME_SIMPLE

    def getCustomTime(self):
        self.PYTIME_CUSTOM = self.PYTIME_CUSTOM.replace(year=self.YEAR, month=self.MONTH, day=self.DATE, hour=self.HOUR, minute=self.MINUTE, second=self.SECOND, microsecond=self.MILLISECONDS, tzinfo=pytz.timezone(self.TZ_CUSTOM))
        return self.PYTIME_CUSTOM

    def getYear(self):
        return self.YEAR

    def setYear(self):
        self.YEAR = self.result[0]
        return

    def getMonth(self):
        return self.MONTH

    def setMonth(self):
        self.MONTH = self.result[1] + 1 # This +1 moves month numbers from 0-11 to 1-12
        return

    def getDate(self):
        return self.DATE

    def setDate(self):
        self.DATE = self.result[2]
        return

    def getHours(self):
        return self.HOUR

    def setHour(self):
        self.HOUR = self.result[3]
        return

    def getMinutes(self):
        return self.MINUTE

    def setMinute(self):
        self.MINUTE = self.result[4]
        return

    def getSeconds(self):
        return self.SECOND

    def setSecond(self):
        self.SECOND = self.result[5]
        return

    def getMilliseconds(self):
        return self.MILLISECONDS

    def setMillisecond(self):
        self.MILLISECONDS = self.result[6]
        return

    def getTimezone(self):
        return self.TZ

    def getSimpleTimezone(self):
        return self.TZ_SIMPLE

    def getCustomTimezone(self):
        return self.TZ_CUSTOM

    def setTZ(self):
        if not self.result == None:
            self.OFFSET = self.result[7]
        self.OFFSET = self.offsetFormat()
        sorted_tzs = self.allTimezones()
        for zone in sorted_tzs:
            if self.OFFSET in zone[1]:
                self.TZ = zone[0]
                break
        simple_tzs = self.basicTimezones()
        for z in simple_tzs:
            if self.OFFSET in z[1]:
                self.TZ_SIMPLE = z[0]
                break
        custom_tzs = self.CUSTOM_TIMEZONES
        if custom_tzs == []:
            return
        for w in custom_tzs:
            if self.OFFSET in w[1]:
                self.TZ_CUSTOM = w[0]
                return
        raise Exception("No Timezone Found!")

    def offsetFormat(self):
        west = True
        if int(self.OFFSET) < 0:
            west = False
        hours_offset = int(self.OFFSET/60)
        if abs(hours_offset) < 10:
            hours_offset = "0" + str(hours_offset)
        minutes_offset = int(self.OFFSET%60)
        if minutes_offset < 10:
            minutes_offset = "0" + str(minutes_offset)
        if west:
            return "-" + str(hours_offset) + str(minutes_offset)
        return str(hours_offset) + str(minutes_offset)

    def allTimezones(self):
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        return sorted_tzs

    def basicTimezones(self):
        SHORT_LIST_TIMEZONES = ['Pacific/Midway', 'US/Hawaii', 'Pacific/Marquesas', 'Pacific/Gambier', 'US/Alaska', 'US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern', 'America/Argentina/Buenos_Aires',  'Canada/Newfoundland', 'America/Sao_Paulo', 'Atlantic/Cape_Verde', 'UTC', 'Europe/London', 'Europe/Paris', 'Europe/Moscow', 'Asia/Tehran', 'Asia/Dubai', 'Asia/Kabul', 'Asia/Karachi', 'Asia/Kolkata', 'Asia/Kathmandu', 'Asia/Dhaka', 'Indian/Cocos', 'Asia/Bangkok', 'Asia/Hong_Kong', 'Asia/Pyongyang', 'Australia/Eucla', 'Asia/Tokyo', 'Australia/Darwin', 'Australia/Brisbane', 'Australia/Adelaide', 'Australia/Sydney', 'Pacific/Fiji', 'Pacific/Auckland', 'Pacific/Chatham', 'Pacific/Kiritimati']
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones if item in SHORT_LIST_TIMEZONES]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        return sorted_tzs

    def setcustomTimezones(self, CUSTOM_LIST):
        tz = [(item, datetime.datetime.now(pytz.timezone(item)).strftime('%z') + " " + item) for item in pytz.common_timezones if item in CUSTOM_LIST]
        sorted_tzs = sorted(tz, key=lambda x: int(x[1].split()[0]))
        self.TZ_CUSTOM = sorted_tzs
        return

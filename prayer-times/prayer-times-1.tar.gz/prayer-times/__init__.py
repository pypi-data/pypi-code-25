import json
from datetime import datetime, timedelta
import requests
import os
import re
TIME_PATTERN = re.compile(r'\d{1,2}:\d{1,2}')


def get_prayers_times(latitude, longitude, tomorrow=False, method=2):
    date = datetime.now()
    if tomorrow is True:
        date = date + timedelta(days=1)

    res = requests.get(url="http://api.aladhan.com/"
                       "v1/calendar?latitude="+str(latitude)+"&longitude=" +
                       str(longitude)+"&method="+str(method) +
                       "&month="+str(date.month)
                       + "&year="+str(date.year))
    output = json.loads(res.content.decode('utf-8'))
    prayers = output['data'][int(date.day) - 1]['timings']

    return dict((k.lower(), TIME_PATTERN.findall(v)[0]) for k, v in prayers.items())

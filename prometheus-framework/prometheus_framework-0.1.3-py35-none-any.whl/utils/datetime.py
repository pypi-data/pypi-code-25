from django.utils.timezone import utc

import datetime


def utcnow():
    return datetime.datetime.utcnow().replace(tzinfo=utc)

import datetime

from ravenpackapi.utils.date_formats import as_datetime

SPLIT_YEARLY = 'yearly'
SPLIT_MONTHLY = 'monthly'


def parts_to_curl(method, endpoint, headers, data=None):
    ignored_headers = (
        'Accept', 'Accept-Encoding', 'Connection', 'Content-Type', 'Content-Length', 'User-Agent')
    headers = ["'{0}:{1}'".format(k, v) for k, v in headers.items() if
               k not in ignored_headers]
    headers = " -H ".join(sorted(headers))

    curl_parameters = ['curl']
    for prefix, values in (('-X', method.upper()),
                           ('-H', headers),
                           ('-d', "'%s'" % data if data else None),
                           ):
        if values:
            curl_parameters.append('%s %s' % (prefix, values))
    curl_parameters.append("'%s'" % endpoint)
    command = " ".join(curl_parameters)
    return command


def to_curl(request):
    if not request:
        return 'No request'
    return parts_to_curl(request.method,
                         request.url,
                         request.headers,
                         request.body if getattr(request, 'body') else None)


def time_intervals(date_start, date_end, split=SPLIT_MONTHLY):
    assert split in (SPLIT_MONTHLY, SPLIT_YEARLY)
    start = as_datetime(date_start)
    date_end = as_datetime(date_end)

    def get_end(get_next_end):
        result = get_next_end
        if split == SPLIT_MONTHLY:
            # up to beginning of next month
            result = result.replace(day=1) + datetime.timedelta(days=32)
            return result.replace(day=1,
                                  hour=0, minute=0, second=0, microsecond=0)
        elif split == SPLIT_YEARLY:
            # up to beginning of next year
            return result.replace(result.year + 1, month=1, day=1,
                                  hour=0, minute=0, second=0, microsecond=0)

    while True:
        # some datetime trick to get the beginning of next month
        end = min(date_end, get_end(start))
        if start >= date_end:
            break
        yield start, end
        start = end

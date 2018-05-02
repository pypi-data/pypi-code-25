import time
import datetime
from influxdb.exceptions import InfluxDBClientError
from influxdb import InfluxDBClient
import requests
import raven


def log(*args, **kwargs):
    print(*args, **kwargs)


class InfluxRequests(object):
    def __init__(self, influx_kwargs, points_count_max=30, points_waiting_time_max=10,
                 requests_timeout_max=3, sentry_dsn=None):
        """
        influx_kwargs: InfluxDBClient 参数，如:
            dict(
                 host='localhost',
                 port=8086,
                 username='root',
                 password='root',
                 database=None,
                 ssl=False,
                 verify_ssl=False,
                 timeout=None,
                 retries=3,
                 use_udp=False,
                 udp_port=4444,
                 proxies=None,
                 pool_size=10,
            )
        ######################################
        points_count_max: 最多 points_count_max 条发送
        points_waiting_time_max: 时间是检查上一次发送时间的时间差，大于 points_waiting_time_max 秒发送
            但是这个是再有发送任务的时候才检查
            所以并不是严格 points_waiting_time_max 秒，可能会多
        requests_timeout_max: requests 的 timeout max
        sentry_dsn: 发送 influx 这一步如果 trace, 且 sentry_dsn is not None, 则发送 sentry

        """
        self.points_count_max = points_count_max
        self.points_waiting_time_max = points_waiting_time_max
        self.requests_timeout_max = requests_timeout_max
        self.points_unsend = []
        self.last_send_time = int(time.time())

        self._influx_client = InfluxDBClient(**influx_kwargs)
        self._sentry_client = raven.Client(dsn=sentry_dsn) if sentry_dsn is not None else None

        # monkey patch
        requests.api.request = self.request_with_influx

    def unsend_waiting_time(self):
        return int(time.time()) - self.last_send_time

    def get_points_safe(self):
        count = len(self.points_unsend)
        r = []
        try:
            for i in range(count):
                r.append(self.points_unsend.pop(0))
        except IndexError:
            pass
        self.last_send_time = int(time.time())
        return r

    def write_batch_points(self):
        points = self.get_points_safe()
        if len(points) == 0:
            return None

        try:
            r = self._influx_client.write_points(points)
            # log('r', r)
        except InfluxDBClientError as e:
            code, content = e.code, e.content
            # log(code, content)
            # if code == 404 and 'database not found' in content:
            if code == 404:
                self._influx_client.create_database(self._influx_client._database)
                r = self._influx_client.write_points(points)
                # log('r-retry', r)
                return None
            else:
                raise e

    def collect_point(self, point):
        self.points_unsend.append(point)
        if len(self.points_unsend) >= self.points_count_max or self.unsend_waiting_time() >= self.points_waiting_time_max:
            self.write_batch_points()
        return None

    def http_point_handle(self, r, t1, t2):
        current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        # log('current', current_time)
        scheme, netloc, path, _params, query, _fragment = requests.utils.urlparse(r.url)
        request_body = r.request.body
        dt = t2 - t1
        point = {
            "time": current_time,
            "measurement": "service_succeed",
            "tags": {
                "scheme": scheme,
                'method': r.request.method,
                "netloc": netloc,
                'path': path,
                'dt': dt,
            },
            "fields": {
                "query": query,
                'body': request_body,
                'status_code': r.status_code,
            }
        }
        self.collect_point(point)

    def request_with_influx(self, method, url, **kwargs):
        # log('request_with_influx--start======url: \n', url)
        if kwargs.get('timeout', self.requests_timeout_max + 1) > self.requests_timeout_max:
            kwargs['timeout'] = self.requests_timeout_max

        try:
            t1 = self.timestamp_process_16()
            r = requests.request(method, url, **kwargs)
            t2 = self.timestamp_process_16()
        except Exception as e:
            raise e

        try:
            # log(type(t1), t1, type(t2 - t1), t2 - t1)
            self.http_point_handle(r, t1, t2)
        except Exception as e:
            if self._sentry_client is not None:
                self._sentry_client.captureException()
                # log('sentry-ok')
            pass

        return r

    @staticmethod
    def timestamp_process_16():
        return int(time.perf_counter() * 1000000)


if __name__ == '__main__':
    pass
    # config = {
    #     'host': '127.0.0.1',
    #     'port': 8086,
    #     'database': 'http_rest'
    # }
    # log(requests.api.get)
    # a = InfluxRequests(**config)
    # r = requests.get('https://mall.imeihao.shop/?a=67')
    # log(requests.api.get)
    # log(requests.get)

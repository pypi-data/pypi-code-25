import time
import datetime
from influxdb.exceptions import InfluxDBClientError
from influxdb import InfluxDBClient
import requests
import raven
from queue import Queue
from queue import Empty as EmptyError
from threading import Thread


def log(*args, **kwargs):
    print(*args, **kwargs)


class InfluxRequests(object):
    def __init__(self, influx_kwargs, points_waiting_time_max=5,
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
        points_waiting_time_max: 循环等待发送的时间间隔
        requests_timeout_max: requests 的 timeout max
        sentry_dsn: 发送 influx 这一步如果 trace, 且 sentry_dsn is not None, 则发送 sentry

        """
        self.points_waiting_time_max = points_waiting_time_max
        self.requests_timeout_max = requests_timeout_max
        self.points_unsend = Queue()
        self.last_send_time = int(time.time())

        self._influx_client = InfluxDBClient(**influx_kwargs)
        self._sentry_client = raven.Client(dsn=sentry_dsn) if sentry_dsn is not None else None

        # monkey patch
        requests.api.request = self.request_with_influx

        t1 = Thread(target=self.interval_write_from_queue, args=(), daemon=True)
        t1.start()

    def interval_write_from_queue(self):
        interval_time = self.points_waiting_time_max
        while True:
            try:
                time.sleep(interval_time)
                self.write_batch_points()
            except Exception:
                if self._sentry_client is not None:
                    self._sentry_client.captureException()
                    # log('sentry-ok')
                pass

    def unsend_waiting_time(self):
        return int(time.time()) - self.last_send_time

    def get_points_safe(self):
        count = self.points_unsend.qsize()
        r = []
        try:
            for i in range(count):
                r.append(self.points_unsend.get(block=False))
        except EmptyError:
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
        self.points_unsend.put(point)
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

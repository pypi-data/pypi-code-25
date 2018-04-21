import logging
import time

from django.conf import settings
from django.db import connection
from django.utils import timezone

class LoggingMiddleware(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request):
        try:
            if request.method in ['POST', 'PATCH'] and 'login' not in request.path:
                try:
                    remote_addr = request.META['HTTP_X_REAL_IP']
                except KeyError:
                    remote_addr = request.META.get('REMOTE_ADDR')

                self.logger.debug(
                    "{addr}: {method} {data}".format(
                        addr=remote_addr,
                        method=request.method,
                        data=request.body
                    )
                )
        except Exception as e:
            self.logger.error("LoggingMiddleware Error: %s" % e)

        self.start_time = time.time()

    def process_response(self, request, response):
        try:

            FORMATS = {
                'header': '\033[95m',
                'bold': '\033[1m',
                'underline': '\033[4m',
                'info': '\033[94m',
                'success': '\033[92m',
                'warning': '\033[93m',
                'danger': '\033[91m',
                'normal': '\033[0m',
            }

            timestamp = timezone.now().strftime("%d/%b/%Y %H:%M:%S %Z")
            try:
                remote_addr = request.META['HTTP_X_REAL_IP']
            except KeyError:
                remote_addr = request.META.get('REMOTE_ADDR')

            req_time = time.time() - self.start_time
            try:
                content_len = len(response.content)
            except AttributeError:
                content_len = response.streaming_content.__sizeof__()
            sql_log = ''
            if settings.DEBUG:
                sql_time = sum(float(q['time']) for q in connection.queries) * 1000
                sql_log = " ({0} SQL queries, {1} ms)".format(
                    len(connection.queries), round(sql_time,2)
                )
                print sql_log

            bad_request_note = ''
            status_string = str(response.status_code)
            if status_string[0] == '4':
                status_color = 'warning'
                try:
                    bad_request_note = '\n({0})'.format(response.data)
                except:
                    pass
            elif status_string[0] == '5':
                status_color = 'danger'
            else:
                status_color = 'normal'

            self.logger.info('{fmt_color}{fmt_header}[{timestamp}] {user} ({ip}){fmt_normal}\n\
{fmt_color}"{method} {path}" {status}; {len} Bytes, {time} seconds {sql}{bad_request}{fmt_normal}\n'.format(
                fmt_color=FORMATS[status_color],
                fmt_header=FORMATS['bold'],
                timestamp=timestamp,
                user=request.user,
                ip=remote_addr,
                method=request.method,
                path=request.get_full_path(),
                status=status_string,
                len=content_len,
                time=round(req_time, 2),
                sql=sql_log,
                bad_request=bad_request_note,
                fmt_normal=FORMATS['normal']
            ))

            try:
                self.logger.debug(response.content)
            except AttributeError:
                self.logger.debug(response.streaming_content)

        except Exception as e:
            self.logger.error("LoggingMiddleware Error: %s" % e)
        return response

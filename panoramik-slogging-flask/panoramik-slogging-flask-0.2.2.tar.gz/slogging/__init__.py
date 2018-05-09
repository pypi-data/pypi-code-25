import logging


class SLoggerHandler(logging.Handler):
    def __init__(self, backend_name, sender, out_handler_class=None):
        self.backend_name = backend_name

        if out_handler_class is None:
            from .out_handlers.threading_queue import ThreadingQueueOutHandler
            out_handler_class = ThreadingQueueOutHandler

        self._out_handler = out_handler_class(sender)

        super(SLoggerHandler, self).__init__()

    def __del__(self):
        self._out_handler.stop(block=True)

    def install(self):
        """
        Installs this slogger
        """
        logger = logging.getLogger()
        logger.addHandler(self)
        logger.setLevel(logging.DEBUG)
        self._out_handler.start()

    def emit(self, record):
        """
        :param record:
        :type record: logging.LogRecord
        :return:
        """
        self._logline(
            message=record.getMessage(),
            severity=record.levelname,
            severity_no=record.levelno,
            exc_info=record.exc_info,
            timestamp=record.created
        )

    def _logline(self, message, severity, severity_no=None, request_id=None, exc_info=None, timestamp=None):
        if exc_info is not None:
            from .utils.exception import exception_fmt_by_exc_info
            exc_fmt = exception_fmt_by_exc_info(exc_info)
        else:
            exc_fmt = None

        self._out_handler.queue_event(
            'logline',
            data={
                'request_id': request_id,
                'severity': severity,
                'message': message,
                'exception': exc_fmt
            },
            timestamp=timestamp
        )

    def _request_start(self, request_id, ip, url, method, host, timestamp=None):
        self._out_handler.queue_event(
            'start',
            data={
                'request_id': request_id,
                'backend_name': self.backend_name,
                'ip': ip,
                'url': url, 'method': method,
                'host': host
            },
            timestamp=timestamp
        )

    def _request_finish(self, request_id, status_code=None, log_severity=None, timestamp=None):
        self._out_handler.queue_event(
            'finish',
            data={
                'request_id': request_id,
                'status_code': status_code,
                'log_severity': log_severity
            },
            timestamp=timestamp
        )

    def set_request_custom(self, request_id, custom):
        self._out_handler.queue_event(
            'set_custom',
            data={
                'request_id': request_id,
                'custom': custom
            }
        )

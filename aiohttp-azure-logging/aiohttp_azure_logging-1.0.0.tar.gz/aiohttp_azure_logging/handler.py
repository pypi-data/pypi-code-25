import logging
import inspect
import asyncio
from aiohttp.web_request import Request, BaseRequest

class OMSHandler(logging.Handler):

    def __init__(self, oms_client=None, *args, **kwargs):
        self.oms_client = oms_client
        super().__init__(*args, **kwargs)

    def emit(self, record=None):
        frame = inspect.currentframe()
        if not frame:
            # small edge cases where inspect module 
            # will not provide a frame
            return
        request = None
        i = 0
        while i < 10:
            if ('request' in frame.f_locals.keys() 
                and type(frame.f_locals.get('request')) == Request 
                and type(frame.f_locals.get('request')) != BaseRequest
                ):
                request = frame.f_locals.get('request')
                break
            else:
                frame = frame.f_back
                i += 1

        if record.exc_info:
            # raised exception
            record_data = {
                'method': frame.f_code.co_name,
                'line': frame.f_lineno,
                'module': inspect.getmodule(frame).__name__,
                'path': frame.f_code.co_filename,
                'message': record.getMessage(),
                'status_code': getattr(record.exc_info[0],
                                       'status',
                                       500),
                'traceback': record.exc_text
            }

        else:
            # regular log
            record_data = {
                'method': record.funcName,
                'line': record.lineno,
                'module': record.module,
                'message': record.getMessage(),
                'path': record.pathname,
            }
        try:
            asyncio.ensure_future(self.oms_client.create_event(
                    log_type="serverLog",
                    name=record.levelname,
                    request=request,
                    event_data=record_data))
        except Exception as e:
            print("OMSHandler exc: {0}".format(str(e)))
 
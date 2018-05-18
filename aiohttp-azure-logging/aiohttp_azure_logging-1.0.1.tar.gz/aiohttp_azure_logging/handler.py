import logging
from datetime import datetime
import inspect
import asyncio
from aiohttp.web_request import Request, BaseRequest
import linecache
from traceback import walk_tb

class OMSHandler(logging.Handler):

    def __init__(self, oms_client=None, *args, **kwargs):
        self.oms_client = oms_client
        super().__init__(*args, **kwargs)

    def emit(self, record=None):
        self.format(record)
        request = None
        frames = inspect.stack()
        for frame in [frames[i].frame for i in range(len(frames)-1, 0, -1)]:
            if ('request' in frame.f_locals.keys() 
                and type(frame.f_locals.get('request')) == Request 
                and type(frame.f_locals.get('request')) != BaseRequest
                ):
                request = frame.f_locals.get('request')
                break

        if record.exc_info:
            # exception
            offending_frame, line_no = [(f,l) for f,l in walk_tb(record.exc_info[2])][-1]
            record_data = {
                'function': offending_frame.f_code.co_name,
                'lineno': line_no,
                'line': linecache.getline(offending_frame.f_code.co_filename, line_no).strip(),
                'module': inspect.getmodule(offending_frame).__name__,
                'file': offending_frame.f_code.co_filename,
                'message': record.getMessage(),
                'traceback': record.exc_text
            }
        else:
            # regular log
            record_data = {
                'function': record.funcName,
                'line': record.lineno,
                'module': record.module,
                'message': record.getMessage(),
                'file': record.pathname,
            }
        try:
            asyncio.ensure_future(self.oms_client.create_event(
                    log_type="serverLog",
                    name=record.levelname,
                    request=request,
                    event_data=record_data,
                    event_time=datetime.strptime(record.asctime, '%Y-%m-%d %H:%M:%S,%f')))
        except Exception as e:
            print("OMSHandler exc: {0}".format(str(e)))
 
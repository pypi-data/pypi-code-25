# coding=utf-8
import json
import structlog
import renderer.settings as stg
from renderer import StrRenderer
from renderer.slog import SemanticLogger, FileHandler as fH
import logging
from renderer.bridge_context import Context
from iohandler import IOFile

fileHandler = IOFile.IOFileHandler()
context = Context()


def open_json_file(file_name, file_path):
    with \
            fileHandler.open(file_name=file_name, file_path=file_path, create_file_if_none=False,
                             create_package=False, mode='r') as file_reader:
        raw_obj = fileHandler.read(reader=file_reader)
    x = json.loads(raw_obj)
    return x


def std_out_logging():
    # logging.basicConfig(
    #     format="%(message)s",
    #     stream=sys.stdout,
    #     level=logging.INFO,
    # )
    structlog.configure(
        processors=[
            structlog.processors.KeyValueRenderer(
                key_order=["event", "payload"],
            ),
        ],
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    handler = logging.StreamHandler()
    # handler.setFormatter(formatter)
    return handler


def _struct_logger():
    # Set up structured logging
    structlog.configure(
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            StrRenderer(target='file'),
        ],
        wrapper_class=SemanticLogger,
        cache_logger_on_first_use=True
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=False),
    )
    handler = fH(
        filename="{lp}{sep}file_.log".format(lp=stg.logs_path, sep=stg.sep),
        mode='ab+', encoding='utf-8')
    handler.setFormatter(formatter)
    return handler


def structlog_implementation(*args):
    x = open_json_file(args[0], args[1])
    import datetime
    ts = datetime.datetime(2018, 2, 19, 9, 58, 36, 529782)
    msg = x.get('message')
    locale = x.get('LOCALE')
    root_logger = logging.getLogger()
    root_logger.addHandler(args[2])
    root_logger.setLevel(logging.INFO)
    log = structlog.get_logger()

    for l in locale:
        sms_request_xml = """<?xml version="1.0" encoding="utf-8"?><sendsmsrequest><ucid>{ucid}
            </ucid><jumo_txt_id>{jumo_txt_id}</jumo_txt_id><txt>{message}</txt><locale>{locale}
            </locale></sendsmsrequest>""". \
            format(ucid='1234',
                   jumo_txt_id='jumo',
                   message=context.render(msg, target='stdout'),
                   locale=l
                   )
        log.info(event=l,
                 url="1",
                 payload=context.render(sms_request_xml, target='stdout'),
                 imestamps=ts,
                 session_id="r",
                 ucid="12345")


def main():
    import sys
    handler = std_out_logging()
    structlog_implementation(sys.argv[1], sys.argv[2], handler)
    # handler = _struct_logger()
    # structlog_implementation(sys.argv[1], sys.argv[2], handler)
    pass


if __name__ == "__main__":
    main()

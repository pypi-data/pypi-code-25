import logging
from .client import OMSLoggingClient
from .middleware import send_requests_to_oms
from .handler import OMSHandler

def log_to_azure(app, settings):
    app.middlewares.append(send_requests_to_oms)
    app['oms'] = OMSLoggingClient(settings)
    app_logger = logging.getLogger()
    oms_handler = OMSHandler(oms_client=app['oms'])
    app_logger.addHandler(oms_handler)
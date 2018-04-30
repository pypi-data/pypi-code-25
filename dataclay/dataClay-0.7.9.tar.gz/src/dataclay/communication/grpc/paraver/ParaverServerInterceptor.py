"""Interceptor for GRPC client calls."""

from grpc import ServerInterceptor
from logging import getLogger

from dataclay import PrvManager
from dataclay.paraver.prv_traces import TraceType

from . import HEADER_MESSAGEID


logger = getLogger(__name__)


class ParaverServerInterceptor(ServerInterceptor):
    def __init__(self, origin_hostname, origin_port):
        logger.debug("Initialize ParaverServerInterceptor")
        self.origin_hostname = origin_hostname
        self.origin_port = origin_port

    def intercept_service(self, continuation, handler_call_details):
        logger.debug("Intercept")

        logger.info("Handler call details %s ", handler_call_details)

        response = continuation(handler_call_details)
        
        return response

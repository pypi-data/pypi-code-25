#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import RPCBatchProtocol, RPCRequest, RPCResponse, RPCErrorResponse,\
               InvalidRequestError, MethodNotFoundError, ServerError,\
               InvalidReplyError, RPCError, RPCBatchRequest, RPCBatchResponse

import msgpack
import six


class FixedErrorMessageMixin(object):
    def __init__(self, *args, **kwargs):
        if not args:
            args = [self.message]
        super(FixedErrorMessageMixin, self).__init__(*args, **kwargs)

    def error_respond(self):
        response = MSGPACKRPCErrorResponse()

        response.error = self.message
        response.unique_id = None
        response._msgpackrpc_error_code = self.msgpackrpc_error_code
        return response



class MSGPACKRPCParseError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32700
    message = 'Parse error'


class MSGPACKRPCInvalidRequestError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32600
    message = 'Invalid Request'


class MSGPACKRPCMethodNotFoundError(FixedErrorMessageMixin, MethodNotFoundError):
    msgpackrpc_error_code = -32601
    message = 'Method not found'


class MSGPACKRPCInvalidParamsError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32602
    message = 'Invalid params'


class MSGPACKRPCInternalError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32603
    message = 'Internal error'


class MSGPACKRPCServerError(FixedErrorMessageMixin, InvalidRequestError):
    msgpackrpc_error_code = -32000
    message = ''


class MSGPACKRPCSuccessResponse(RPCResponse):
    def _to_dict(self):
        return {
            'msgpackrpc': MSGPACKRPCProtocol.MSGPACK_RPC_VERSION,
            'id': self.unique_id,
            'result': self.result,
        }

    def serialize(self):
        return msgpack.dumps(self._to_dict())


class MSGPACKRPCErrorResponse(RPCErrorResponse):
    def _to_dict(self):
        return {
            'msgpackrpc': MSGPACKRPCProtocol.MSGPACK_RPC_VERSION,
            'id': self.unique_id,
            'error': {
                'message': str(self.error),
                'code': self._msgpackrpc_error_code,
            }
        }

    def serialize(self):
        return msgpack.dumps(self._to_dict())


def _get_code_and_message(error):
    assert isinstance(error, (Exception, six.string_types))
    if isinstance(error, Exception):
        if hasattr(error, 'msgpackrpc_error_code'):
            code = error.msgpackrpc_error_code
            msg = str(error)
        elif isinstance(error, InvalidRequestError):
            code = MSGPACKRPCInvalidRequestError.msgpackrpc_error_code
            msg = MSGPACKRPCInvalidRequestError.message
        elif isinstance(error, MethodNotFoundError):
            code = MSGPACKRPCMethodNotFoundError.msgpackrpc_error_code
            msg = MSGPACKRPCMethodNotFoundError.message
        else:
            # allow exception message to propagate
            code = MSGPACKRPCServerError.msgpackrpc_error_code
            msg = str(error)
    else:
        code = -32000
        msg = error

    return code, msg


class MSGPACKRPCRequest(RPCRequest):
    def error_respond(self, error):
        if not self.unique_id:
            return None

        response = MSGPACKRPCErrorResponse()

        code, msg = _get_code_and_message(error)

        response.error = msg
        response.unique_id = self.unique_id
        response._msgpackrpc_error_code = code
        return response

    def respond(self, result):
        response = MSGPACKRPCSuccessResponse()

        if not self.unique_id:
            return None

        response.result = result
        response.unique_id = self.unique_id

        return response

    def _to_dict(self):
        jdata = {
            'msgpackrpc': MSGPACKRPCProtocol.MSGPACK_RPC_VERSION,
            'method': self.method,
        }
        if self.args:
            jdata['params'] = self.args
        if self.kwargs:
            jdata['params'] = self.kwargs
        if self.unique_id != None:
            jdata['id'] = self.unique_id
        return jdata

    def serialize(self):
        return msgpack.dumps(self._to_dict())


class MSGPACKRPCBatchRequest(RPCBatchRequest):
    def create_batch_response(self):
        if self._expects_response():
            return MSGPACKRPCBatchResponse()

    def _expects_response(self):
        for request in self:
            if isinstance(request, Exception):
                return True
            if request.unique_id != None:
                return True

        return False

    def serialize(self):
        return msgpack.dumps([req._to_dict() for req in self])


class MSGPACKRPCBatchResponse(RPCBatchResponse):
    def serialize(self):
        return msgpack.dumps([resp._to_dict() for resp in self if resp != None])


class MSGPACKRPCProtocol(RPCBatchProtocol):
    """MSGPACKRPC protocol implementation.

    Currently, only version 2.0 is supported."""

    MSGPACK_RPC_VERSION = "2.0"
    _ALLOWED_REPLY_KEYS = sorted(['id', 'msgpackrpc', 'error', 'result'])
    _ALLOWED_REQUEST_KEYS = sorted(['id', 'msgpackrpc', 'method', 'params'])

    def __init__(self, *args, **kwargs):
        super(MSGPACKRPCProtocol, self).__init__(*args, **kwargs)
        self._id_counter = 0

    def _get_unique_id(self):
        self._id_counter += 1
        return self._id_counter

    def create_batch_request(self, requests=None):
        return MSGPACKRPCBatchRequest(requests or [])

    def create_request(self, method, args=None, kwargs=None, one_way=False):
        if args and kwargs:
            raise InvalidRequestError('Does not support args and kwargs at '\
                                      'the same time')

        request = MSGPACKRPCRequest()

        if not one_way:
            request.unique_id = self._get_unique_id()

        request.method = method
        request.args = args
        request.kwargs = kwargs

        return request

    def parse_reply(self, data):
        if six.PY3 and isinstance(data, bytes):
            # zmq won't accept unicode strings, and this is the other
            # end; decoding non-unicode strings back into unicode
            data = data.decode()

        try:
            rep = msgpack.loads(data)
        except Exception as e:
            raise InvalidReplyError(e)

        for k in six.iterkeys(rep):
            if not k in self._ALLOWED_REPLY_KEYS:
                raise InvalidReplyError('Key not allowed: %s' % k)

        if not 'msgpackrpc' in rep:
            raise InvalidReplyError('Missing msgpackrpc (version) in response.')

        if rep['msgpackrpc'] != self.MSGPACK_RPC_VERSION:
            raise InvalidReplyError('Wrong MSGPACKRPC version')

        if not 'id' in rep:
            raise InvalidReplyError('Missing id in response')

        if ('error' in rep) == ('result' in rep):
            raise InvalidReplyError(
                'Reply must contain exactly one of result and error.'
            )

        if 'error' in rep:
            response = MSGPACKRPCErrorResponse()
            error = rep['error']
            response.error = error['message']
            response._msgpackrpc_error_code = error['code']
        else:
            response = MSGPACKRPCSuccessResponse()
            response.result = rep.get('result', None)

        response.unique_id = rep['id']

        return response

    def parse_request(self, data):
        if six.PY3 and isinstance(data, bytes):
            # zmq won't accept unicode strings, and this is the other
            # end; decoding non-unicode strings back into unicode
            data = data.decode()

        try:
            req = msgpack.loads(data)
        except Exception as e:
            raise MSGPACKRPCParseError()

        if isinstance(req, list):
            # batch request
            requests = MSGPACKRPCBatchRequest()
            for subreq in req:
                try:
                    requests.append(self._parse_subrequest(subreq))
                except RPCError as e:
                    requests.append(e)
                except Exception as e:
                    requests.append(MSGPACKRPCInvalidRequestError())

            if not requests:
                raise MSGPACKRPCInvalidRequestError()
            return requests
        else:
            return self._parse_subrequest(req)

    def _parse_subrequest(self, req):
        for k in six.iterkeys(req):
            if not k in self._ALLOWED_REQUEST_KEYS:
                raise MSGPACKRPCInvalidRequestError()

        if req.get('msgpackrpc', None) != self.MSGPACK_RPC_VERSION:
            raise MSGPACKRPCInvalidRequestError()

        if not isinstance(req['method'], six.string_types):
            raise MSGPACKRPCInvalidRequestError()

        request = MSGPACKRPCRequest()
        request.method = str(req['method'])
        request.unique_id = req.get('id', None)

        params = req.get('params', None)
        if params != None:
            if isinstance(params, list):
                request.args = req['params']
            elif isinstance(params, dict):
                request.kwargs = req['params']
            else:
                raise MSGPACKRPCInvalidParamsError()

        return request

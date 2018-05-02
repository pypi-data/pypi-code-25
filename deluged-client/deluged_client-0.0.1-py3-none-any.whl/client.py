
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details
# http://www.gnu.org/licenses/lgpl-3.0.txt

"""Deluge client
RPC Interface: http://deluge.readthedocs.io/en/develop/core/rpc.html """

import logging
log = logging.getLogger()

import asyncio
from blinker import Signal
import enum
import warnings

from .protocol import Protocol
from .errors import (ClientError, ConnectionError, AuthError)

class ResponseType(enum.IntEnum):
    response    = 1
    error       = 2
    event       = 3

class AbstractRPCResponse():

    def __init__(self, response_type):
        self.type = response_type

class RPCResponse(AbstractRPCResponse):

    def __init__(self, sequence, data):
        super().__init__(ResponseType.response)
        self.sequence = sequence
        self.data = data

class RPCError(ClientError, AbstractRPCResponse):
    prefix = 'Invalid RPC response: '

    def __init__(self, sequence, error):
        super().__init__('RPC Error')
        self.type = ResponseType.error
        self.sequence = sequence
        self.parse_remote_exception(error)

    def parse_remote_exception(self, data):
        data = list(data)
        self.cls = data.pop(0)
        self.msg = data.pop(0)
        self.callbacks = data

class RPCEvent(AbstractRPCResponse):

    def __init__(self, name, data):
        super().__init__(ResponseType.event)
        self.name = name
        self.data = data

# DottedObject and RemoteMethod are from Deluge's source: deluge/ui/client.py
class DottedObject(object):
    """
    This is used for dotted name calls to client
    """
    def __init__(self, client, method):
        self.client = client
        self.base = method
        self.__name__ = method
        self.__qualname__ = method

    def __call__(self, *args, **kwargs):
        raise AttributeError('You must make calls in the form of "component.method"')

    def __getattr__(self, name):
        return RemoteMethod(self.client, self.base + '.' + name)



class RemoteMethod(DottedObject):
    """
    This is used when something like 'client.core.get_something()' is attempted.
    """
    def __call__(self, *args, **kwargs):
        log.debug('Calling RPC method: %r', self.base)
        return self.client.call(self.base, *args, **kwargs)

def from_payload(payload):
    type = payload[0]
    # RPC response is a triple (type, sequence, data)

    if type == ResponseType.response:
        sequence = payload[1]
        return RPCResponse(sequence, payload[2])
    elif type == ResponseType.error:
        sequence = payload[1]
        return RPCError(sequence, payload[2])
    elif type == ResponseType.event:
        return RPCEvent(name=payload[1], data=payload[2])

class DelugeRPCProtocol(Protocol):

    def __init__(self, client, loop, timeout=10, on_error=Signal()):
        super().__init__()
        self._sequence = -1
        self._futures = {} 
        self._loop = loop
        self.timeout = timeout
        self._on_error = on_error 
        self._client = client
    
    def connection_made(self, transport):
        log.debug('Connection Made')
        self.transport = transport

    def connection_lost(self, e):
        e = ConnectionError('', e)

        for future in self._futures.values():
            future.set_exception(e)
        self._futures = {}
        # TODO: TEST this case
        self._client.disconnect(reason=e)


    def data_received(self, data):
        log.debug('Data received')
        self.append(data)

        payload = self.decode()
        log.debug('Payload %s', payload)

        if payload is None:
            return

        response = from_payload(payload)
        log.debug('Res %s', response)

        type = response.type
        log.debug('type: %s', type)
        if type == ResponseType.response or type == ResponseType.error:
            sequence = response.sequence
            log.debug('seq: %s', sequence)
            future = self.get_future(sequence)
            log.debug('f: %s', future)
            if future is not None:
                log.debug('f: %s, s: %s', future, sequence)
                self.pop_future(sequence)
                if type == ResponseType.error:
                    future.set_exception(response)
                else:
                    future.set_result(response)
        elif type == ResponseType.event:
            self._client._on_event.send(self, name=response.name, data=response.data)

    def get_future(self, sequence):
        return self._futures.get(sequence, None)

    def pop_future(self, sequence):
        del self._futures[sequence]

    def call(self, method, *args, **kwargs):
        self._sequence += 1
        log.debug('Calling %s with %s and %s', method, args, kwargs)
        # Deluge 2.0 requires a 5 byte header that contains the
        # size of the data prefixed with the byte encoding of 'D'
        self._send_data(((self._sequence, method, args, kwargs), ))

        future = self._loop.create_future()
        self._futures[self._sequence] = future

        def timeout_future(sequence):
            future = self.get_future(sequence)
            if future is not None and future.done() is False:
                e = ConnectionError('Timeout after %rs' % self.timeout)
                future.set_exception(e)
                self._on_error.send(self._client, err=e)
                self.pop_future(sequence)

        self._loop.call_later(self.timeout, timeout_future, self._sequence)

        return future


class Client():

    def __init__(self, host='localhost', port=58846, *, tls=True, user='',
                 password='', loop=None, enabled=True):
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self._host = host
        self._port = port
        self._tls = tls
        self._user = user
        self._password = password

        self._connecting_lock = asyncio.Lock(loop=loop)
        self._request_lock = asyncio.Lock(loop=loop)
        self._enabled_event = asyncio.Event(loop=loop)
        self._transport = None
        self._protocol = None
        self._authlevel = -1
        self._version = None
        self.enabled = enabled

        self._on_connecting = Signal()
        self._on_connected = Signal()
        self._on_disconnected = Signal()
        self._on_event = Signal()
        self._on_error = Signal()

        self._callbacks = list()

    def __getattr__(self, method):
        return DottedObject(self, method) 

    def __del__(self, _warnings=warnings):
        if self._transport is not None:
            _warnings.warn('disconnect() wasn\'t called', ResourceWarning)
            self._transport.close()
            
    def on(self, signal, callback, autoremove=True):
        """
        Register `callback` for `signal`

        signal: 'connecting', 'connected', 'disconnected', 'event', or 'error'
        callback: a callable that receives this instance as a positional
                  argument. The 'event' signal receive additional keyword arguments 
                  'name' and 'data' and, in case of the 'error' signal,
                  the exception as a keyword argument with the name 'error'.

        Callbacks are automatically unsubscribed when they are
        garbage-collected.
        """
        try:
            sig = getattr(self, '_on_' + signal)
        except AttributeError:
            raise ValueError('Unknown signal: {!r}'.format(signal))
        else:
            if not isinstance(sig, Signal):
                raise ValueError('Unknown signal: {!r}'.format(signal))
            else:
                log.debug('Registering %r for %r event', callback, signal)
                sig.connect(callback, weak=autoremove)

    @property
    def authlevel(self):
        """Authorization Level for Deluge RPC, -1 if not connected"""
        return self._authlevel

    @property
    def host(self):
        """
        Hostname or IP of the Deluge RPC interface

        Setting this property calls disconnect().
        """
        return self._host

    @host.setter
    def host(self, host):
        self._host = str(host)
        self.disconnect('Changing host: %r' % self._host)

    @property
    def port(self):
        """
        Port of the Deluge RPC interface

        Setting this property calls disconnect().
        """
        return self._port

    @port.setter
    def port(self, port):
        self._port = int(port)
        self.disconnect('Changing port: %r' % self._port)

    @property
    def user(self):
        """
        Username for authenticating to the Deluge RPC interface or None

        Setting this property calls disconnect().
        """
        return self._user

    @user.setter
    def user(self, user):
        self._user = str(user)
        self.disconnect('Changing user: %r' % self._user)

    @property
    def password(self):
        """
        Password for authenticating to the Deluge RPC interface or None

        Setting this property calls disconnect().
        """
        return self._password

    @password.setter
    def password(self, password):
        self._password = str(password)
        self.disconnect('Changing password: %r' % self._password)

    @property
    def tls(self):
        """
        Whether to use TLS for connecting to the Deluge RPC interface

        Setting this property calls disconnect().
        """
        return self._tls

    @tls.setter
    def tls(self, tls):
        self._tls = bool(tls)
        self.disconnect('Changing tls: %r' % self._tls)

    @property
    def url(self):
        """Schema, host, and port combined as a string"""
        return '%s://%s:%d' % (
            'tls' if self.tls else 'tcp', self.host, self.port)

    @property
    def enabled(self):
        """
        Whether requests should connect

        If this is set to False, requests will wait for it to be set to True.
        This allows you to block any connection attempts until the connection
        parameters (host, user, password, etc) are specified to prevent any
        unwarranted error messages.
        """
        return self._enabled_event.is_set()

    @enabled.setter
    def enabled(self, enabled):
        if enabled:
            log.debug('Enabling %r', self)
            self._enabled_event.set()
        else:
            log.debug('Disabling %r', self)
            self._enabled_event.clear()
            if self.connected:
                self.disconnect()

    @property
    def connected(self):
        """Return True if connected, False otherwise"""
        return self._transport is not None

    @property
    def version(self):
        """Return the version of the RPC daemon if connected, None otherwise"""
        return self._version

    async def connect(self):
        if self._connecting_lock.locked():
            log.debug('Connection is already being established')
            while True:
                log.debug('Waiting for connection to come up ...')
                await asyncio.sleep(0.1, loop=self.loop)
                if self.connected:
                    log.debug('Connection is up: %r', self.url)
                    return
            
        async with self._connecting_lock:
            log.debug('Acquired connect() lock')

            if self.connected:
                self.disconnect('Reconnecting')

            await self._enabled_event.wait()

            log.debug('Connecting to %s', self.url)
            self._on_connecting.send(self)

            # Deluge requires TLS but the mock daemon omits it
            context = False
            if self.tls:
                import ssl
                context = ssl.SSLContext()

            try:
                log.debug('Creating connection %s %s', self.user, self.password)
                self._transport, self._protocol = await self.loop.create_connection( 
                    lambda: DelugeRPCProtocol(self, self.loop, on_error=self._on_error),
                    host=self.host, port=self.port, ssl=context
                )
                # Attempt to authenticate
                try:
                    # NOTE: A deadlock can occur if we call rpc methods on self. Make
                    # calls directly on the protocol
                    # Deluge 2.0 requires a client_version karg
                    res = await self._protocol.call('daemon.login', self.user,
                            self.password, client_version='2.0')
                    self._authlevel = res.data
                except RPCError:
                    self._reset()
                    e = AuthError(self.url)
                    log.debug('Authentication failed: %s: user=%r, password=%r' % (
                        self.url, self.user, self.password))
                    self._on_error.send(self, error=e)
                    raise e
                # Obtain version number
                version = await self._protocol.call('daemon.info')
                self._version = version.data
                log.debug('Created connection version:%s', self.version)
                self._on_connected.send(self)
            except OSError:
                self._on_error.send(self)
                raise ConnectionError('Server not found')

    def disconnect(self, reason=None):
        """
        Disconnect if connected

        reason: Why are we disconnecting? Only used in a debugging message.
        """
        if self.connected:
            self._reset()
            log.debug('Disconnecting from %s (%s)', self.url,
                      reason if reason is not None else 'for no reason')
            log.debug('Calling "disconnected" callbacks for %s', self.url)
            self._on_disconnected.send(self)

    async def call(self, method, *args, **kwargs):
        async with self._request_lock:
            if not self.connected:
                log.debug('Autoconnecting for %r', method)
                await self.connect()

            try:
                return await self._protocol.call(method, *args, **kwargs)
            except ClientError as e:
                log.debug('Caught ClientError in %r request: %r', method, e)

                # RPCError does not mean host is unreachable, there was just a
                # misunderstanding, so we're still connected.
                if not isinstance(e, RPCError) and self.connected:
                    self.disconnect(str(e))

                self._on_error.send(self, error=e)
                raise

    def _reset(self):
        if self._transport is not None:
            self._transport.close()
        self._transport = None
        self._protocol = None
        self._authlevel = -1
        self._version = None

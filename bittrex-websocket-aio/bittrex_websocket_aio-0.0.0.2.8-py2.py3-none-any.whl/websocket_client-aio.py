#!/usr/bin/python
# -*- coding: utf-8 -*-

# bittrex_websocket/websocket_client22.py
# Stanislav Lazarov

import uvloop
import asyncio
import logging
from ._logger import add_stream_logger, remove_stream_logger
from threading import Thread
from ._queue_events import *
from ._constants import EventTypes, BittrexParameters, BittrexMethods, ErrorMessages
from ._auxiliary import process_message, BittrexConnection
from ._abc import WebSocket
from time import sleep as sync_sleep

logger = logging.getLogger(__name__)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

## TO BE REMOVED BEFORE PUBLISHING ##
import sys

sys.path.insert(0, '/Users/slazarov/Documents/Python-Projects/python-signalr-client')
from signalr_aio import Connection


class BittrexSocket(WebSocket):

    def __init__(self):
        self.socket_loop = None
        self.control_queue = None
        self.invokes = []
        self.tickers = None
        self.connection = None
        self.futures = []
        self._start_main_thread()

    def _start_main_thread(self):
        def start():
            # self.futures.append(asyncio.ensure_future(self.control_queue_handler(), loop=self.socket_loop))
            # self.socket_loop.run_forever()
            self.socket_loop.run_until_complete(self.control_queue_handler())

        self.socket_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.socket_loop)
        self.control_queue = asyncio.Queue(loop=self.socket_loop)
        asyncio.Task(self.control_queue.put(ConnectEvent()), loop=self.socket_loop)
        thread = Thread(target=start, daemon=True, name='ControlQueue')
        thread.start()

    async def control_queue_handler(self):
        while True:
            event = await self.control_queue.get()
            if event is not None:
                if event.type == EventTypes.CONNECT:
                    await self._handle_connect()
                elif event.type == EventTypes.SUBSCRIBE:
                    await self._handle_subscribe(event.tickers, event.invoke)
                elif event.type == EventTypes.CLOSE:
                    break
                self.control_queue.task_done()

    async def _handle_connect(self):
        connection = Connection(BittrexParameters.URL)
        hub = connection.register_hub(BittrexParameters.HUB)
        connection.received += self._on_debug
        connection.error += self.on_error
        hub.client.on(BittrexParameters.MARKET_DELTA, self._on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA, self._on_public)
        hub.client.on(BittrexParameters.SUMMARY_DELTA_LITE, self._on_public)
        # Future implementations
        # hub.client.on(BittrexParameters.BALANCE_DELTA, self._on_private)
        # hub.client.on(BittrexParameters.ORDER_DELTA, self._on_private)
        self.connection = BittrexConnection(connection, hub)
        self.futures.append(asyncio.ensure_future(self._connection_handler(), loop=self.socket_loop))

    async def _connection_handler(self):
        try:
            self.connection.conn.start()
            logger.info('Establishing connection to Bittrex.')
        except Exception as e:
            print(e)

    async def _handle_subscribe(self, tickers, invoke):
        if tickers is None:
            self.invokes.append({'invoke': invoke, 'ticker': None})
            self.connection.corehub.server.invoke(invoke)
        else:
            for ticker in tickers:
                self.invokes.append({'invoke': invoke, 'ticker': ticker})
                self.connection.corehub.server.invoke(invoke, ticker)

    # ==============
    # Public Methods
    # ==============

    def subscribe_to_exchange_deltas(self, tickers):
        if type(tickers) is list:
            invoke = BittrexMethods.SUBSCRIBE_TO_EXCHANGE_DELTAS
            event = SubscribeEvent(payload=tickers, invoke=invoke)
            asyncio.Task(self.control_queue.put(event), loop=self.socket_loop)
        else:
            raise TypeError(ErrorMessages.INVALID_TICKER_INPUT)

    def subscribe_to_summary_deltas(self):
        invoke = BittrexMethods.SUBSCRIBE_TO_SUMMARY_DELTAS
        event = SubscribeEvent(payload=None, invoke=invoke)
        asyncio.Task(self.control_queue.put(event), loop=self.socket_loop)

    def subscribe_to_summary_lite_deltas(self):
        invoke = BittrexMethods.SUBSCRIBE_TO_SUMMARY_LITE_DELTAS
        event = SubscribeEvent(payload=None, invoke=invoke)
        asyncio.Task(self.control_queue.put(event), loop=self.socket_loop)

    def query_summary_state(self):
        invoke = BittrexMethods.QUERY_SUMMARY_STATE
        event = SubscribeEvent(payload=None, invoke=invoke)
        asyncio.Task(self.control_queue.put(event), loop=self.socket_loop)

    def query_exchange_state(self, ticker):
        invoke = BittrexMethods.QUERY_EXCHANGE_STATE
        event = SubscribeEvent(ticker, invoke=invoke)
        asyncio.Task(self.control_queue.put(event), loop=self.socket_loop)

    def disconnect(self):
        # asyncio.Task(self.control_queue.put(CloseEvent()), loop=self.socket_loop)
        self.connection.conn.close()
        # asyncio.Task(self.control_queue.put(CloseEvent()), loop=self.socket_loop)
        while self.connection.conn.started is True:
            sync_sleep(0.5)
        else:
            #     self.socket_loop.close()
            asyncio.Task(self.control_queue.put(CloseEvent()), loop=self.socket_loop)
        while True:
            for future in self.futures + self.connection.conn._Connection__transport.futures:
                future.cancel()
                while not future.done():
                    sync_sleep(1)
            break
        while self.socket_loop.is_running():
            sync_sleep(1)
        print(1)
        # # self.socket_loop.close()
        # while self.socket_loop.is_running():
        #     sync_sleep(5)
        #     # self.connection.conn.close()
        #     # self.socket_loop.stop()
        #     print('sleeping is running')
        # else:
        #     self.socket_loop.close()
        #     while not self.socket_loop.is_closed():
        #         print('sleeping is closed')
        #         sync_sleep(10)
        #     else:
        #         logger.info('Socket exit')

    # =======================
    # Private Channel Methods
    # =======================

    async def _on_public(self, args):
        await self.on_public(await process_message(args[0]))

    async def _on_private(self, args):
        ### TO BE IMPLEMENTED ###
        pass

    async def _on_debug(self, **kwargs):
        # `QueryExchangeState` and `QuerySummaryState` are received in the debug channel.
        await self._is_query_invoke(kwargs)

    async def _is_query_invoke(self, kwargs):
        if 'R' in kwargs and type(kwargs['R']) is not bool:
            msg = await process_message(kwargs['R'])
            if msg is None:
                return
            elif 'M' in msg:
                msg['invoke_type'] = BittrexMethods.QUERY_EXCHANGE_STATE

                # Missing ticker name workaround.
                # Fixed in https://github.com/Bittrex/beta/issues/6.
                # Leaving just in case.
                # msg['M'] = self.invokes[int(kwargs['I'])]['ticker']

            else:
                msg['invoke_type'] = BittrexMethods.QUERY_SUMMARY_STATE
            await self.on_public(msg)

    # ======================
    # Public Channel Methods
    # ======================

    async def on_public(self, msg):
        pass

    async def on_private(self, args):
        pass

    async def on_error(self, args):
        pass

    # =============
    # Other Methods
    # =============

    @staticmethod
    def enable_log(file_name=None):
        """
        Enables logging.
        :param file_name: The name of the log file, located in the same directory as the executing script.
        :type file_name: str
        """
        add_stream_logger(file_name=file_name)

    @staticmethod
    def disable_log():
        """
        Disables logging.
        """
        remove_stream_logger()

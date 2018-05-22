from __future__ import print_function

import logging

from concurrent.futures import ThreadPoolExecutor

from google.protobuf.text_format import MessageToString

import grpc

from tornado import gen
from tornado.ioloop import IOLoop
from tornado import queues

from bonsai.proto.instructor_api_pb2_grpc import InstructorStub

from bonsai.drivers import DriverState

log = logging.getLogger(__name__)

# Timeouts for the websocket connection.
_INITIAL_CONNECT_TIMEOUT_SECS = 60


class ManualClosedException(Exception):
    pass


class _Runner(object):

    def __init__(self, access_key, brain_api_url, driver, recording_file):
        self.access_key = access_key
        self.brain_api_url = brain_api_url
        self.driver = driver
        self.recording_file = recording_file
        if self.recording_file:
            self.recording_queue = queues.Queue()
        self._sim_executor = ThreadPoolExecutor(max_workers=1)

    @gen.coroutine
    def record_to_file(self):
        if not self.recording_file:
            return

        with open(self.recording_file, 'w') as out:
            while True:
                line = yield self.recording_queue.get()
                if not line:
                    break
                print(line, file=out)

    @gen.coroutine
    def _record(self, send_or_recv, message):
        yield self.recording_queue.put(send_or_recv)
        if message:
            yield self.recording_queue.put(
                MessageToString(message, as_one_line=True))
        else:
            yield self.recording_queue.put('None')

    @gen.coroutine
    def run(self):

        log.info("About to connect to %s", self.brain_api_url)

        channel = grpc.insecure_channel(self.brain_api_url)

        ready = grpc.channel_ready_future(channel)

        # Block until ready
        ready.result()

        scholar = InstructorStub(channel)

        input_message = None

        try:
            # The driver starts out in an unregistered... the first "next" will
            # perform the registration and all subsequent "next"s will continue
            # the operation.
            while self.driver.state != DriverState.FINISHED:
                if self.recording_file:
                    yield self._record('RECV', input_message)

                output_message = yield self._sim_executor.submit(
                    self.driver.next, input_message)

                if self.recording_file:
                    yield self._record('SEND', output_message)

                # If the driver is FINSIHED, don't bother sending and
                # receiving again before exiting the loop.
                if self.driver.state != DriverState.FINISHED:
                    if not output_message:
                        raise RuntimeError(
                            "Driver did not return a message to send.")

                    input_message = scholar.advance(output_message)

        except grpc.RpcError as e:
            code = e.code()
            reason = e.details()
            log.error("Connection to '%s' is closed, code='%s', reason='%s'",
                      self.brain_api_url, code, reason)
        finally:
            if self.recording_file:
                yield self.recording_queue.put(None)


def run(access_key, brain_api_url, driver, recording_file):

    run_sim, record = create_tasks(access_key,
                                   brain_api_url,
                                   driver,
                                   recording_file)
    IOLoop.current().add_callback(record)
    IOLoop.current().run_sync(run_sim)


def create_tasks(access_key, brain_api_url, driver, recording_file):
    server = _Runner(access_key, brain_api_url, driver, recording_file)
    return server.run, server.record_to_file

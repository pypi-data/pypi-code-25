import zmq
import msgpack
import threading

from collections import namedtuple


Gaze = namedtuple('Gaze', ('pt3d', 't'))


class PupilClient(object):
    def __init__(self, ip, port):
        # Connect to Pupil Remote
        ctx = zmq.Context()
        self.req = ctx.socket(zmq.REQ)
        self.req.connect('tcp://{}:{}'.format(ip, port))

        # Request the SUB port
        self.req.send_string('SUB_PORT')
        sub_port = self.req.recv_string()

        # Connect to the SUB client
        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect('tcp://{}:{}'.format(ip, sub_port))
        # We only want the gaze topic
        self.sub.set(zmq.SUBSCRIBE, b'gaze')

        # Start polling gaze information in background
        self._poll_t = threading.Thread(target=self._run)
        self._poll_t.daemon = True
        self._poll_t.start()

    @property
    def ready(self):
        return hasattr(self, '_gaze')

    @property
    def gaze(self):
        if not self.ready:
            raise IOError('No gaze information received yet from Pupil server.')
        return self._gaze

    def _run(self):
        while True:
            topic, payload = self.sub.recv_multipart()
            message = msgpack.loads(payload)
            if topic == b'gaze':
                self._gaze = Gaze(message[b'gaze_point_3d'], message[b'timestamp'])

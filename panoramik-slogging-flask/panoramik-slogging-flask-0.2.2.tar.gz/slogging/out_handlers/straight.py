class StraightOutHandler:
    def __init__(self, sender):
        self._sender = sender

    def start(self):
        pass

    def stop(self, block=False):
        pass

    def queue_event(self, event, data, timestamp=None):
        self._sender.send(event, data, timestamp)

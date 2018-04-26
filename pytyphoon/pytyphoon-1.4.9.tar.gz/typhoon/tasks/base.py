import time
import json


class BaseTask:
    def __init__(self, config, task, queue_name=None):

        self.config = config
        self.task = task
        self.queue_name = queue_name
        self.added_at = time.time()
        self.created_at = time.time()

    def serialize(self):
        return json.dumps(self.task)

    def set_timestamp(self):
        self.added_at = time.time()

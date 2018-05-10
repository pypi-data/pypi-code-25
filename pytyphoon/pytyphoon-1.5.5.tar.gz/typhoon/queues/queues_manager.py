from typhoon.base_manager import BaseManager
from .priority_queue_collection import PriorityQueueCollection
from .simple import SimpleQueue
import aiohttp
import requests
import json

class QueuesManager(BaseManager):

    def __init__(self, config, callback):

        super().__init__(callback, config, "queues")

        self.status = False
        self.queues = {}
        self.init_queues()

    def init_queues(self):
        for q in self.config["queues"]:
            if q.endswith("priority"):
                self.queues[q] = PriorityQueueCollection(self.config)
                self.queues[q].set_callback(self.on_message)
            self.queues[q] = SimpleQueue(self.config, name=q)

        # self.queues["priority"] = PriorityQueueCollection(self.config)
        # self.queues["priority"].set_callback(self.on_message)

    def get_nsqd_ips(self):
        address = []
        data = requests.get("http://nsqlookupd:4161/nodes").content
        nodes = json.loads(data.decode())
        for producer in nodes.get("producers"):
            ip = producer["remote_address"].split(':')[0]
            address.append("{}:{}".format(ip, 4151))

        return address

    def get_topic_queues(self):
        queues = []
        for q in self.queues:
            if q.endswith("priority"):
                for p in self.queues[q].priorities:
                    queue = self.queues[q].priorities[p]
                    queues.append(queue.topic)
                continue
            queues.append(self.queues[q].topic)

        for p in self.queues["priority"].priorities:
            q = self.queues["priority"].priorities[p]
            queues.append(q.topic)

        return queues

    async def empty_channel(self, nsqdaddr, topic):
        async with aiohttp.ClientSession() as session:
            async with session.post("http://{}/channel/empty".format(nsqdaddr), params={
                "topic": topic,
                "channel": "tasks"
            }) as response:
                return response, await response.read()

    async def empty_topic(self, nsqdaddr, topic):
        async with aiohttp.ClientSession() as session:
            async with session.post("http://{}/topic/empty".format(nsqdaddr), params={
                "topic": topic
            }) as response:
                return response, await response.read()

    def init(self):
        for q in self.queues:
            if q.endswith("priority"): continue

            if self.queues[q].config_queue.get("readable"):
                self.queues[q].set_callback(self.on_message)
                self.queues[q].init_reader()

    def on_message(self, qname, task):
        self.loop.create_task(self.callback(qname, task))

    def start(self):
        self.init()
        self.status = True
        for q in self.queues:
            if self.queues[q].config_queue.get("readable"):
                self.queues[q].start()
        print("Start Manager Queues")

    def stop(self):
        self.status = False
        for q in self.queues:
            if self.queues[q].config_queue.get("readable"):
                self.queues[q].pause()
        print("Stop Manager Queues")
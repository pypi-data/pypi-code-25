from kazoo.client import KazooClient
import threading
import time
import random
import json
import logging


class RangerClient(threading.Thread):
    def __init__(self, zk_hosts, namespace, service_name, endpoint, protocol='http', refresh_interval=2):
        threading.Thread.__init__(self)
        self.namespace = namespace
        self.service_name = service_name
        self.nodes = []
        self.active = True
        self.endpoint = endpoint
        self.protocol = protocol
        self.refresh_interval = refresh_interval
        self.logger = logging.getLogger("RangerClient")
        self.zk = KazooClient(hosts=zk_hosts, read_only=True)
        self.zk.start()

    def run(self):
        self.logger.info("Starting ranger client for namespace: " + self.namespace + " | Service " + self.service_name)
        while self.active:
            children = self.zk.get_children("/" + self.namespace + "/" + self.service_name)
            avl_nodes = []
            for n in children:
                node, stat = self.zk.get("/" + self.namespace + "/" + self.service_name + "/" + n)
                node_data = json.loads(node)
                if node_data['healthcheckStatus'] == 'healthy':
                    avl_nodes.append(node_data['host'] + ":" + str(node_data['port']))
            self.nodes = avl_nodes
            time.sleep(self.refresh_interval)

    def get_node(self):
        return "%s://%s/%s" % (self.protocol, self.nodes[random.randint(0, len(self.nodes)-1)], self.endpoint)

    def stop(self):
        self.active = False



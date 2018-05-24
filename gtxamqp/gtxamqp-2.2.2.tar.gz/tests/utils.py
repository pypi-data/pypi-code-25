import os
import random
import sys


def generate_message():
    return "test-message-%d" % random.randint(0, sys.maxint)


def generate_factory_config():
    factory_conf = {
        "host": os.getenv("RABBITMQ_HOST", "localhost")
    }
    return factory_conf


def generate_rabbitmq_config():
    factory_conf = generate_factory_config()
    client_conf = generate_client_config()
    factory_conf.update(client_conf)
    return factory_conf


def generate_client_config():
    random_name = "test-txamqpr-client-%s" % random.randint(0, sys.maxint)
    rabbitmq_conf = {
        "exchange": {
            "exchange": random_name,
            "type": "fanout",
            "durable": False,
            "auto_delete": True},
        "queue": {
            "queue": random_name,
            "durable": False,
            "exclusive": False,
            "arguments": {"x-expires": 180000}},
        "binding": {
            "exchange": random_name,
            "queue": random_name,
            "routing_key": random_name}}
    return rabbitmq_conf

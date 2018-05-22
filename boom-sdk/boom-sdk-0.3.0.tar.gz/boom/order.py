import os

from boom.api import API


class OrderService(API):

    def __init__(self):
        self.url = os.getenv("BOOM_ORDER_URL", "https://order.boom.app")


class OrderResponse(object):

    def __init__(self):
        self.order = None

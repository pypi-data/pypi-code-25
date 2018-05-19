from datetime import datetime
from typing import Optional

import requests


class Client:
    ISO_8601_DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, host: str):
        self.host = host

    def get(self):
        return requests.get(f"{self.host}").json()

    # trades
    def get_trade_by_id(self, trade_id: str):
        return requests.get(f"{self.host}/v1/trades/{trade_id}").json()

    def find_trades(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/trades", {'limit': limit, 'skip': skip}).json()

    def find_trades_by_status(self, status: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/trades/status/{status}", {'limit': limit, 'skip': skip}).json()

    def find_trades_by_symbol(self, symbol_a: str, symbol_b: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/trades/symbol/{symbol_a}/{symbol_b}", {'limit': limit, 'skip': skip}).json()

    def find_trades_by_unallocated(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/trades/unallocated", {'limit': limit, 'skip': skip}).json()

    def update_trade_allocated(self, trade_id: str, allocated: Optional[datetime] = None):
        allocated = None if allocated is None else allocated.strftime(Client.ISO_8601_DATE_FORMAT)
        return requests.put(f"{self.host}/v1/trades/{trade_id}/allocate", json={'allocated': allocated})

    # orders
    def get_order_by_id(self, order_id: str):
        return requests.get(f"{self.host}/v1/orders/{order_id}").json()

    def find_orders(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/orders", {'limit': limit, 'skip': skip}).json()

    def find_orders_by_trade_id(self, trade_id: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/orders/trade/{trade_id}", {'limit': limit, 'skip': skip}).json()

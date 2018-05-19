from datetime import datetime
from decimal import Decimal
from typing import Optional

import requests


class Client:

    def __init__(self, host: str):
        self.host = host

    def get(self):
        return requests.get(f"{self.host}").json()

    # leads
    def get_lead_by_id(self, lead_id: str):
        return requests.get(f"{self.host}/v1/leads/{lead_id}").json()

    def find_leads(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/leads", {'limit': limit, 'skip': skip}).json()

    # accounts
    def get_account_by_id(self, account_id: str):
        return requests.get(f"{self.host}/v1/accounts/{account_id}").json()

    def find_accounts(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/accounts", {'limit': limit, 'skip': skip}).json()

    # deposits
    def create_deposits(self, account_id: str, amount: Decimal, currency: str, crypto_transaction_reference: str, created: Optional[datetime] = None):
        amount = str(amount)
        created = None if created is None else created.isoformat()
        return requests.post(f"{self.host}/v1/deposits", json={'accountId': account_id, 'amount': amount, 'currency': currency, 'cryptoTransactionReference': crypto_transaction_reference, 'created': created})

    def get_deposit_by_id(self, deposit_id: str):
        return requests.get(f"{self.host}/v1/deposits/{deposit_id}").json()

    def find_deposits_by_range(self, begin: datetime, end: datetime, limit: int = 100, skip: int = 0):
        begin = begin.isoformat()
        end = end.isoformat()
        return requests.get(f"{self.host}/v1/deposits/range", {'begin': begin, 'end': end, 'limit': limit, 'skip': skip}).json()

    def find_deposits_by_account_id(self, account_id: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/deposits/account/{account_id}", {'limit': limit, 'skip': skip}).json()

    def find_deposits_by_account_id_and_currency(self, account_id: str, currency: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/deposits/account/{account_id}/currency/{currency}", {'limit': limit, 'skip': skip}).json()

    # withdraws
    def create_withdraws(self, account_id: str, amount: Decimal, currency: str, address: str, created: Optional[datetime] = None):
        amount = str(amount)
        created = None if created is None else created.isoformat()
        return requests.post(f"{self.host}/v1/withdraws", json={'accountId': account_id, 'amount': amount, 'currency': currency, 'address': address, 'created': created})

    def get_withdraw_by_id(self, withdraw_id: str):
        return requests.get(f"{self.host}/v1/withdraws/{withdraw_id}").json()

    def find_withdraws_by_range(self, begin: datetime, end: datetime, limit: int = 100, skip: int = 0):
        begin = begin.isoformat()
        end = end.isoformat()
        return requests.get(f"{self.host}/v1/withdraws/range", {'begin': begin, 'end': end, 'limit': limit, 'skip': skip}).json()

    def find_withdraws_by_account_id(self, account_id: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/withdraws/account/{account_id}", {'limit': limit, 'skip': skip}).json()

    def find_withdraws_by_account_id_and_currency(self, account_id: str, currency: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/withdraws/account/{account_id}/currency/{currency}", {'limit': limit, 'skip': skip}).json()

    # interests
    def create_interests(self, account_id: str, amount: Decimal, currency: str, trading_trade_reference: str, created: Optional[datetime] = None):
        amount = str(amount)
        created = None if created is None else created.isoformat()
        return requests.post(f"{self.host}/v1/interests", json={'accountId': account_id, 'amount': amount, 'currency': currency, 'tradingTradeReference': trading_trade_reference, 'created': created})

    def find_interests_by_range(self, begin: datetime, end: datetime, limit: int = 100, skip: int = 0):
        begin = begin.isoformat()
        end = end.isoformat()
        return requests.get(f"{self.host}/v1/interests/range", {'begin': begin, 'end': end, 'limit': limit, 'skip': skip}).json()

    def get_interest_by_id(self, interest_id: str):
        return requests.get(f"{self.host}/v1/interests/{interest_id}").json()

    def find_interests_by_account_id(self, account_id: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/interests/account/{account_id}", {'limit': limit, 'skip': skip}).json()

    def find_interests_by_account_id_and_currency(self, account_id: str, currency: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/interests/account/{account_id}/currency/{currency}", {'limit': limit, 'skip': skip}).json()

    # wallets
    def get_wallet_by_id(self, wallet_id: str):
        return requests.get(f"{self.host}/v1/wallets/{wallet_id}").json()

    def get_wallet_by_account_id_and_currency(self, account_id: str, currency: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/wallets/account/{account_id}/currency/{currency}", {'limit': limit, 'skip': skip}).json()

    def find_wallets(self, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/wallets", {'limit': limit, 'skip': skip}).json()

    def find_wallets_by_account_id(self, account_id: str, limit: int = 100, skip: int = 0):
        return requests.get(f"{self.host}/v1/wallets/account/{account_id}", {'limit': limit, 'skip': skip}).json()

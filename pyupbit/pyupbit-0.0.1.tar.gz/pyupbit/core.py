import requests


class publicApi:
    @staticmethod
    def ticker(currency):
        pass

    @staticmethod
    def recent_transactions(currency):
        coin = "CRIX.UPBIT.KRW-" + currency
        uri = "/candles/ticks/1"
        return UpbitHttp().get(uri, code=coin, count = 1)

    @staticmethod
    def orderbook(currency):
        pass


class HttpMethod:
    def __init__(self):
        self.session = requests.session()

    @property
    def base_url(self):
        return ""

    def _handle_response(self, response):
        print(response)
        return response.json()

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def post(self, path, timeout=3, **kwargs):
        uri = self.base_url + path
        response = self.session.post(url=uri, data=kwargs, timeout=timeout)
        return self._handle_response(response)

    def get(self, path, timeout=3, **kwargs):
        uri = self.base_url + path
        response = self.session.get(url=uri, headers=headers, params=kwargs, timeout=timeout)
        return self._handle_response(response)


class UpbitHttp(HttpMethod):
    def __init__(self):
        super(UpbitHttp, self).__init__()

    def get(self, path, timeout=3, **kwargs):
        headers = {"User-Agent": "HACK"}
        uri = self.base_url + path
        response = self.session.get(url=uri, headers=headers, params=kwargs, timeout=timeout)
        return self._handle_response(response)

    @property
    def base_url(self):
        return "https://crix-api-endpoint.upbit.com/v1/crix"

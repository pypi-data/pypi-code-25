import re
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from http_request_randomizer.requests.errors.ProxyListException import ProxyListException
from .func_utils import ensure_params_under_instance_context


VARIABLE_CHECK = re.compile('{([A-Z0-9a-z])+}')
API_URL = 'https://api.iextrading.com'

class API(object):

    def __init__(self, api_name, *args):
        """
        route path is the route for the desired API endpoint
        for variables in path, simply wrap that string with '{}'

        Examples:
        ['1.0', 'stock', 'aapl', 'company'] =>
        https://api.iextrading.com/1.0/stock/aapl/company
        ['1.0', 'stock', '<symbol>', 'company'] =>
        https://api.iextrading.com/1.0/stock/{symbol}/company

        The variables will be required parameters for the call function.
        """
        self._base_path = [API_URL] + list(args)
        self._api_name = api_name
        self.req_proxy = RequestProxy()

    def _call(self, path, *args, **kwargs):
        """
        path: a list path for subroute, variable format is the same as the base_path
        args, kwargs: arguments to fill in the variables in path
        """

        full_path = self._base_path + path
        variables = [segment[1:-1] for segment in full_path if VARIABLE_CHECK.match(segment)]
        params_dict = {variables[i]: arg for (i, arg) in enumerate(args)}
        remaining_args = variables[len(args):]
        for arg in remaining_args:
            if arg not in kwargs:
                raise ValueError('Missing argument {} for API {}'.format(arg, self._api_name))
            params_dict[arg] = kwargs[arg]

        url = "/".join(full_path)
        url = url.format(**params_dict)
        while True:
            try:
                response = self.req_proxy.generate_proxied_request(url)
                break
            except ProxyListException:
                self.req_proxy = RequestProxy()

        if response.status_code != 200:
            message = [response.text, 'API Call Error for url:', url]
            raise ValueError("\n".join(message))
        return response.json()

if __name__ == '__main__':
    stock_api = API('Stock', '1.0', 'stock', '{symbol}')
    result = stock_api._call(['company'], symbol='aapl')
    print(result)
    result = stock_api._call(['company'], symbol='aaapl')
    print(result)

import json
import requests
from bs4 import BeautifulSoup


class WebUtil:
    @staticmethod
    def get(url, ret_type='text'):
        res = requests.get(url=url, verify=False)
        res.close()

        if res.status_code == 200:

            data = None
            if ret_type == 'json':
                data = res.json()
            elif ret_type == 'text':
                data = res.text

            return {
                'status': True,
                'data': data
            }
        else:

            return {
                'status': False,
                'data': res.status_code
            }

    @staticmethod
    def post(url, data_dict, ret_type='text'):
        res = requests.post(url=url, json=data_dict, verify=False)
        res.close()

        if res.status_code == 200:

            data = None
            if ret_type == 'json':
                try:
                    data = res.json()
                except json.decoder.JSONDecodeError:
                    data = None

            elif ret_type == 'text':
                data = res.text

            return {
                'status': True,
                'data': data
            }

        else:
            return {
                'status': False,
                'data': res.status_code
            }

    @staticmethod
    def crawl(url, output_type='html'):

        try:
            res = WebUtil.get(url)
        except requests.exceptions.ConnectionError:
            return None

        if res['status'] is False:
            return None

        if output_type == 'html':
            return BeautifulSoup(res['data'], 'html.parser')
        elif output_type == 'text':
            return res['data']
        else:
            return None

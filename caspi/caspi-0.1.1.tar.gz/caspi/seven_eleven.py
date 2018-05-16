from bs4 import BeautifulSoup as Soup
from caspi.util import escape_unit_suffix

import requests

SITE_URL = 'http://www.7-eleven.co.kr'
PRODUCT_ENDPOINT = SITE_URL + '/product'
UTIL_ENDPOINT = SITE_URL + '/util'

PRODUCT_TYPES = {
    'one_plus_one': 1,
    'two_plus_one': 2,
    '7_select': 5,
}


def get_products(kind=None):
    if isinstance(kind, str):
        kind = PRODUCT_TYPES[kind]

    products = []
    page = 1

    url = PRODUCT_ENDPOINT + '/listMoreAjax.asp'
    data = {'pTab': kind}

    prev_resp = None

    while True:
        data['intPageSize'] = page * 10
        cur_resp = requests.post(url=url, data=data)

        if prev_resp and prev_resp.text == cur_resp.text:
            break

        prev_resp = cur_resp
        page += 1

    soup = Soup(prev_resp.text, 'html.parser')

    for box in soup.select('div.pic_product'):
        product = {
            'name': box.select('div.name')[0].get_text().strip(),
            'price': escape_unit_suffix(box.select('div.price')[0].get_text().strip()),
            'image': SITE_URL + box.select('img')[0].attrs['src'].strip(),
        }

        if kind in {1, 2}:
            flag_list = box.find_previous("ul")

            if flag_list:
                product['flag'] = flag_list.select('li')[0].get_text().strip()

        products.append(product)

    return products


def get_stores(city):
    stores = []

    url = UTIL_ENDPOINT + '/storeLayerPop.asp'

    data = {
        'storeLaySido': city,
        'hiddenText': 'none'
    }

    resp = requests.post(url=url, data=data)
    soup = Soup(resp.text, 'html.parser')

    for item in soup.select('div.list_stroe.type02 li'):
        spans = item.select('span')

        store = {
            'name': spans[0].get_text().strip(),
            'address': spans[1].get_text().strip().replace("\n", "") or None,
            'tel': spans[2].get_text().strip() or None if len(spans) > 2 else None
        }

        stores.append(store)

    return stores

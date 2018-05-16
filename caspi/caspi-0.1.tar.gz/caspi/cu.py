from bs4 import BeautifulSoup as Soup
from .util import escape_unit_suffix
import re
import requests

SITE_URL = 'http://cu.bgfretail.com'
PRODUCT_ENDPOINT = SITE_URL + '/product'
STORE_ENDPOINT = SITE_URL + '/store'
EVENT_ENDPOINT = SITE_URL + '/event'


def get_products(kind=None):
    url = '/' + kind + 'Ajax.do'
    data = {}

    if kind == 'pb':
        url = PRODUCT_ENDPOINT + url
        data['searchgubun'] = 'PBG'

    elif kind == 'plus':
        url = EVENT_ENDPOINT + url
        data['listType'] = 0

    prods = []
    page = 1

    while True:
        data['pageIndex'] = page

        resp = requests.post(url=url, data=data)
        soup = Soup(resp.text, 'html.parser')

        def is_prod_list_item(item):
            return bool(re.findall(r'\d+,*\d+원', item.get_text()))

        items = [item for item in soup.select('li') if is_prod_list_item(item)]

        if len(items) == 0:
            break

        for item in items:
            prod = {
                'name': item.select('.prodName')[0].get_text().strip(),
                'price': escape_unit_suffix(item.select('.prodPrice')[0].get_text().strip()),
                'image': item.select('img')[0].attrs['src'].strip(),
            }

            if kind == 'plus':
                flag_items = item.select('li')

                if flag_items and flag_items[0].get_text():
                    prod['flag'] = flag_items[0].get_text().strip()

            prods.append(prod)

        page += 1

    return prods


def get_stores(city):
    stores = []
    page = 1

    url = STORE_ENDPOINT + '/list_Ajax.do'

    data = {
        'jumpoSido': city,
        'jumpoLotto': '',
        'jumpoToto': '',
        'jumpoCash': '',
        'jumpoHour': '',
        'jumpoCafe': '',
        'jumpoDelivery': '',
        'jumpoBakery': '',
        'jumpoFry': '',
    }

    while True:
        data['pageIndex'] = page
        resp = requests.post(url=url, data=data)

        soup = Soup(resp.text, 'html.parser')
        rows = soup.select('div.detail_store tbody tr')

        if len(rows) == 0:
            break

        for row in rows:
            store = {
                'name': row.select('span.name')[0].get_text() or None,
                'tel': row.select('span.tel')[0].get_text() or None,
                'address': row.select('address')[0].get_text() or None,
            }

            stores.append(store)

        page += 1

    return stores

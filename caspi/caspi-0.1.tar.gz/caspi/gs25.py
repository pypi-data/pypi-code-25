from bs4 import BeautifulSoup as Soup
from .util import snake_str_to_pascal_str

import json
import requests

SITE_URL = 'http://gs25.gsretail.com/gscvs/ko'
PRODUCT_ENDPOINT = SITE_URL + '/products'
STORE_ENDPOINT = SITE_URL + '/store-services'

EVENT_TYPES = {
    'one_plus_one': 'ONE_TO_ONE',
    'two_plus_one': 'TWO_TO_ONE'
}


def get_csrf_session():
    # Load MainPage to Get CSRF Token and Cookies
    resp = requests.get(url=SITE_URL + '/main')
    soup = Soup(resp.text, 'html.parser')

    # Get CSRF Token and Cookies from HTML and Set-Coookie Headers
    csrf_token = soup.select('input[name="CSRFToken"]')[0].attrs['value'].strip()
    csrf_cookie = resp.headers['Set-Cookie']

    # Request for Register CSRF Session with CSRF Token and Cookies
    requests.post(url=SITE_URL + '/main',
                  data={'CSRFToken': csrf_token},
                  headers={'Cookie': csrf_cookie})

    # Return CSRF Token and Cookies
    return csrf_token, csrf_cookie


def get_products(kind=None):
    # Initialize Product List and Page Number
    prods = []
    page = 1

    # Get CSRF Token and Cookies
    csrf_token, csrf_cookie = get_csrf_session()
    url = PRODUCT_ENDPOINT

    # Set Default Search Data
    data = {
        'pageSize': 16,
        'searchSort': 'searchALLSort',
        'searchProduct': 'productALL',
    }

    # If We'll Find Youus Products (Fresh Food, Different Service),
    # Set URL and Search Data to Search Youus Products
    if kind in {'fresh_food', 'different_service'}:
        url = url + '/youus-freshfoodDetail-search'
        data['searchSrvFoodCK'] = snake_str_to_pascal_str(kind) + 'Key'

    # If We'll Find Event Products (One Plus One, Two Plus One),
    # Set URL and Search Data to Search Plus Event Products
    elif kind in EVENT_TYPES.keys():
        url = url + '/event-goods-search'
        data['parameterList'] = EVENT_TYPES[kind]

    # Set CSRF Token and Cookies
    params = {'CSRFToken': csrf_token}
    headers = {'Cookie': csrf_cookie}

    while True:
        # Set page number and send product search request
        data['pageNum'] = page
        resp = requests.post(url, data=data, params=params, headers=headers)

        # Get unicode escaped JSON objects from response
        resp_text = resp.text.replace('\\"', '"').replace('\\\\', '\\')

        # We'll remove double quote around response
        resp_json = json.loads(resp_text[1:-1])

        # Get Products from Response JSON
        items = resp_json.get('SubPageListData') or resp_json.get('results')

        # We'll Stop the Loop if We Cannot Get Products
        if not items:
            break

        items = [i for i in items if i['goodsStatNm'] == '정상']

        for item in items:
            # Initialize product dict from JSON object
            prod = {
                'name': item['goodsNm'],
                'price': int(item['price']),
                'image': item['attFileNm'],
                'flag': item.get('eventTypeNm')
            }

            # Append product to products list
            prods.append(prod)

        # Increase page number
        page += 1

    # Finally, we'll return products list
    return prods


def get_stores(city):
    # Initialize stores list and page number
    stores = []
    page = 1

    # Get CSRF token and cookies and
    # Set URL to search store list
    csrf_token, csrf_cookie = get_csrf_session()
    url = STORE_ENDPOINT + '/locationList'

    # Set CSRF token and cookies
    params = {'CSRFToken': csrf_token}
    headers = {'Cookie': csrf_cookie}

    # Set default search data
    data = {
        'pageSize': 5,
        'searchSido': city, 'searchShopName': '',
        'searchType': '', 'searchTypeService': 0,
        'searchTypeLotto': 0, 'searchTypeToto': 0,
        'searchTypeCoffee': 0, 'searchTypeBakery': 0,
        'searchTypeInstant': 0, 'searchTypeDrug': 0,
        'searchTypeSelf25': 0, 'searchTypePost': 0,
        'searchTypeATM': 0, 'searchTypeWithdrawal': 0,
        'searchTypeTaxrefund': 0, 'searchTypeGelasoft': 0,
    }

    while True:
        # Set page number and send store search request
        data['pageNum'] = page
        resp = requests.post(url=url, data=data, params=params, headers=headers)

        # Get escaped JSON objects from response
        resp_text = resp.text.replace('\\', '')
        resp_json = json.loads(resp_text[1:-1])

        # Get stores from response JSON
        items = resp_json['results']

        # We'll Stop loop if we cannot get products
        if not items:
            break

        for item in items:
            # Initialize store dict from JSON object
            store = {
                'name': item['shopName'],
                'address': item['address'] or None,
            }

            # Append store to stores list
            stores.append(store)

        # Increase page number
        page += 1

    # Finally, we'll return stores list
    return stores










from bs4 import BeautifulSoup as Soup
from caspi.util import HeadlessChrome

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pprint import pprint
import time


"""
    module for cu convenience store api
    
    Attribute:
        SITE_URL (str): base url in Seven Eleven website
        EVENT_PRODUCT_LIST (str): url to visit event product list page
        
        SEVEN_SELECT (str): url path args for call seven eleven dosirak
        SEVEN_ELEVEN_DOSIRAK (str): url path args for call seven eleven dosirak 
        
        ONE_PLUS_ONE (int): args for call 1 + 1 event products from event product list page
        TWO_PLUS_ONE (int): args for call 2 + 1 event products from event product list page
"""

SITE_URL = 'http://www.7-eleven.co.kr'

SEVEN_SELECT = '7select'
SEVEN_ELEVEN_DOSIRAK = 'bestdosirak'

EVENT_PRODUCT_LIST = '{0}/product/presentList.asp'.format(SITE_URL)
ONE_PLUS_ONE = 1
TWO_PLUS_ONE = 2


def get_pb_products(kind=""):
    """
        Get PB products from seven eleven

        Args:
            kind(str): Kind about seven eleven PB Product (7 select, dosirak)

        Return:
            list: PB Product dict list
    """

    if not kind:
        return get_pb_products(SEVEN_SELECT) + get_pb_products(SEVEN_ELEVEN_DOSIRAK)

    products = []

    with HeadlessChrome() as chrome:
        chrome.get('{0}/product/{1}List.asp'.format(SITE_URL, kind))
        time.sleep(0.5)

        while True:
            try:
                more_prod_btn = chrome.find_element_by_css_selector('li.btn_more')
                more_prod_btn.click()

                wait = WebDriverWait(chrome, 10)
                wait.until(EC.staleness_of(more_prod_btn))

            except NoSuchElementException:
                break

        time.sleep(0.5)
        soup = Soup(chrome.page_source, 'html.parser')

        for box in soup.select('li > div.pic_product'):
            product = {
                'name': box.select('div.name')[0].get_text().strip(),
                'price': box.select('div.price')[0].get_text().strip(),
                'image': box.select('img')[0].attrs['src'].strip()
            }

            products.append(product)

    return products


def get_plus_event_products(kind=0):
    if not kind:
        return get_plus_event_products(ONE_PLUS_ONE) + get_plus_event_products(TWO_PLUS_ONE)

    products = []

    with HeadlessChrome() as chrome:
        chrome.get(EVENT_PRODUCT_LIST)
        chrome.execute_script('fncTab({0})'.format(kind))
        time.sleep(0.5)

        while True:
            try:
                more_prod_btn = chrome.find_element_by_css_selector('li.btn_more')
                more_prod_btn.click()

                wait = WebDriverWait(chrome, 10)
                wait.until(EC.staleness_of(more_prod_btn))

            except NoSuchElementException | TimeoutException:
                break

        time.sleep(0.5)
        soup = Soup(chrome.page_source, 'html.parser')

        for box in soup.select('li > div.pic_product'):
            product = {
                'name': box.select('div.name')[0].get_text().strip(),
                'price': box.select('div.price')[0].get_text().strip(),
                'flag': box.find_previous("ul").select("li")[0].get_text().strip(),
                'image': SITE_URL + box.select('img')[0].attrs['src'].strip()
            }

            products.append(product)

    return products


def get_products():
    return get_pb_products()


def get_stores():
    stores = []

    with HeadlessChrome() as chrome:
        chrome.get(SITE_URL)
        time.sleep(0.5)

        wait = WebDriverWait(chrome, 10)
        open_store_list_btn = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'store_open')))
        open_store_list_btn.click()
        time.sleep(5)

        city_name_selections = chrome.find_elements_by_css_selector('select#storeLaySido > option')
        city_names = [o.get_attribute('value') for o in city_name_selections][1:]

        for city_name in city_names:
            city_name_selection = Select(chrome.find_element_by_id('storeLaySido'))
            city_name_selection.select_by_value(city_name)

            time.sleep(1)
            chrome.execute_script('$.Fn_store_search(1)')

            time.sleep(5)
            soup = Soup(chrome.page_source, 'html.parser')

            for item in soup.select('div.list_stroe > ul > li'):
                spans = item.select('span')

                store = {
                    'name': spans[0].get_text().strip(),
                    'address': spans[1].get_text().strip() or None,
                    'tel': spans[2].get_text().strip() or None if len(spans) > 2 else None
                }

                stores.append(store)

    return stores

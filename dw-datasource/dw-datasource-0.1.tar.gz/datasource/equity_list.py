import urllib2
from bs4 import BeautifulSoup
from .util import retry, ascii

WIKI_SP500_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
WIKI_NASDAQ100_URL = 'https://en.wikipedia.org/wiki/NASDAQ-100'


def __get_sp500_list():

    def extract_row(tr):
        tds = tr.findAll('td')
        symbol = ascii(tds[0].text.strip())
        name = ascii(tds[1].text.strip())
        sector = ascii(tds[3].text.strip())
        sub_sector = ascii(tds[4].text.strip())
        date_added = ascii(tds[6].text.strip())

        return {'symbol': symbol,
                'name': name,
                'sector': sector,
                'sub_sector': sub_sector,
                'date_added': date_added}

    wiki_page = urllib2.urlopen(WIKI_SP500_URL)
    soup = BeautifulSoup(wiki_page, 'html.parser')

    table = soup.find('table').findAll('tr')
    table = table[1:]   # remove table header

    return map(extract_row, table)


def get_sp500_list():
    return retry(__get_sp500_list)()


def __get_nasdaq100_list():

    def parse_row(r):
        a = r.findAll('a')[0]
        name = a.text.strip()
        symbol = ascii(r.find(text=True, recursive=False).strip())
        symbol = symbol[symbol.find('(')+1: symbol.find(')')]

        return {'name': name, 'symbol': symbol}

    wiki_page = urllib2.urlopen(WIKI_NASDAQ100_URL)
    soup = BeautifulSoup(wiki_page, 'html.parser')

    ulist = soup.find('ol').findAll('li')
    return map(parse_row, ulist)


def get_nasdaq100_list():
    return retry(__get_nasdaq100_list)()

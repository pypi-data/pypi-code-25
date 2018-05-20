import requests
import urllib.parse

class Trump(object):

    def __init__(self):
        self.quote = None
        self.quote_id = None
        self.quote_date = None
        self.quote_tag = None

class TronaldDump(object):

    def __init__(self):
        self.base_url = 'https://api.tronalddump.io/'

    def randomquote(self):
        url = self.base_url + 'random/quote'
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                trump = Trump()
                trump.quote = data["value"]
                trump.quote_id = data["quote_id"]
                trump.quote_date = data["created_at"]
                trump.quote_tag = data["tags"]
                return trump
            elif response.status_code == 429:
                return ("Too many requests!")
            else:
                return ("There was an issue")
        except ValueError:
            return ("Error")

    def tags(self):
        url = self.base_url + 'tag'
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                tag_list = data["_embedded"]
                return tag_list
            elif response.status_code == 429:
                return ("Too many requests!")
            else:
                return ("There was an issue")
        except ValueError:
            return ("Error")

    def search(self, search_term):
        url = self.base_url + 'search/quote?query='
        try:
            response = requests.get(url + search_term)

            if response.status_code == 200:
                data = response.json()
                if data["count"] == 0:
                    return ("Couldn't find anything")
                else:
                    data = data["_embedded"]["quotes"]
                    quotes_returned = []
                    for quote in data:
                        trump = Trump()
                        trump.quote = quote["value"]
                        trump.quote_id = quote["quote_id"]
                        trump.quote_date = quote["created_at"]
                        trump.quote_tag = quote["tags"]
                        quotes_returned.append(trump)
                    return quotes_returned
            elif response.status_code == 429:
                return ("Too many requests!")
            else:
                return ("There was an issue")
        except ValueError:
            return ("Error")

    def searchtag(self, search_tag):
        url = self.base_url = 'https://api.tronalddump.io/tag/'
        search_tag = urllib.parse.quote(search_tag)
        try:
            response = requests.get(url + search_tag)

            if response.status_code == 200:
                data = response.json()
                if data["count"] == 0:
                    return ("Couldn't find anything")
                else:
                    data = data["_embedded"]["tags"]
                    tag_quotes = []
                    for quote in data:
                        trump = Trump()
                        trump.quote = quote["value"]
                        trump.quote_id = quote["quote_id"]
                        trump.quote_date = quote["created_at"]
                        trump.quote_tag = quote["tags"]
                        tag_quotes.append(trump)
                    return tag_quotes
            elif response.status_code == 429:
                return ("Too many requests!")
            else:
                return ("There was an issue")
        except ValueError:
            return ("Error")

    def getquote(self, quoteid):
        url = self.base_url = 'https://api.tronalddump.io/quote/'
        quoteid = str(quoteid)
        try:
            response = requests.get(url + quoteid)

            if response.status_code == 200:
                data = response.json()
                trump = Trump()
                trump.quote = data["value"]
                trump.quote_id = data["quote_id"]
                trump.quote_date = data["created_at"]
                trump.quote_tag = data["tags"]
                return trump
            elif response.status_code == 429:
                return ("Too many requests!")
            else:
                return ("There was an issue")
        except ValueError:
            return ("Error")
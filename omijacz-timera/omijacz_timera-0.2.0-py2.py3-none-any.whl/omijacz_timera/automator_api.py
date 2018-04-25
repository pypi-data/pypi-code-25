import os.path
from urllib.parse import urlparse

import requests


class Prawojazdy_API:
    def __init__(self, cookie, current_url):
        self.cookie = cookie
        self.cookie_str = "PHPSESSID=" + cookie
        self.current_url = current_url
    origin = "https://ekurs.prawojazdy.com.pl"
    requested_with = "XMLHttpRequest"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    content_type = "application/x-www-form-urlencoded"
    DNT = "1"
    # referer_template = "https://ekurs.prawojazdy.com.pl/prawojazdy/lekcja/{contentId}/{scenarioId}"
    accept = "application/json, text/javascript, */*; q=0.01"
    accept_encoding = "gzip, deflate, br"
    accept_language = "pl,en-US;q=0.9,en;q=0.8,de;q=0.7"
    URL_post = "https://ekurs.prawojazdy.com.pl/prawojazdy/slidepass"

    def parse_url(self):
        path = urlparse(self.current_url).path
        sections = []
        temp = ""
        while path != "/":
            temp = os.path.split(path)
            path = temp[0]
            sections.append(temp[1])
        return sections

    def get_content_from_url(self):
        sections = self.parse_url()
        try:
            int(sections[0])
            int(sections[1])
        except TypeError:
            raise Exception("Nie można znaleść danych w URL")
        content = {
            "contentId": sections[1],
            "scenarioId": sections[0]
        }
        return content

    def get_content(self, slide_id):
        """
        Zwraca gotową zawartość zapytania
        :param slide_id: Numer slajdu
        :return: Zawartość zapytania (params)
        """
        # content = "content=&contentId={contentId}&currentSlide={currentSlide}&scenarioId={scenarioId}&slideType={slideType}"
        content_parsed = self.get_content_from_url()
        content_dict = {
            "content": "",
            "slideType": "1",
            "currentSlide": slide_id,
        }
        content_dict.update(content_parsed) # Dodaje wpisy z content_parsed do content
        # content = content.format(**content_dict)
        # return content
        return content_dict

    def get_header(self):
        """
        Zwraca słownik z nagłówkami (header) dla zapytania
        :return: Header (słownik) do zapytania
        """
        header = {
            "Accept": self.accept,
            "Origin": self.origin,
            "X-Requested-With": self.requested_with,
            "User-Agent": self.user_agent,
            # "Content-Type": self.content_type,
            "DNT": self.DNT,
            "Referer": self.current_url,
            "Accept-Encoding": self.accept_encoding,
            "Accept-Language": self.accept_language,
            "Cookie": self.cookie_str
        }
        return header

    def send_request(self, content, header):
        try:
            r = requests.post(self.URL_post, data=content, headers=header)
        except requests.exceptions.ConnectionError:
            return False
        try:
            r.raise_for_status()
        except:
            return False
        response = r.json()
        if response['success'] == False:
            return False
        else:
            return True


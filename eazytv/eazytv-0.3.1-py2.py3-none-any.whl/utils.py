import random
import difflib


import os
import io

import requests

from .eztv.parser import process_showlist


HERE = os.path.abspath(os.path.dirname(__file__))

EZTV_URL = "https://eztv.ag/"
SHOWLIST_URL = EZTV_URL + "showlist/"


def read_version():
    # Load the package's __version__.py module as a dictionary.
    about = {}
    with io.open(os.path.join(HERE, '__version__.py')) as f:
        exec(f.read(), about)

    return about['version']


def fuzzy_matches(shows, name):
    matches = difflib.get_close_matches(name, shows, 5)
    return matches


def whatdoyoumean(shows, name):
    matches = difflib.get_close_matches(name, shows, 3)
    error_msg = '\nDid you mean one of these?\n    %s' % '\n    '.join(matches)
    print(error_msg)


def get_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    ]

    uint = random.randint(0, 2)
    ua = USER_AGENTS[uint]

    return ua


def do_request(url):
    ua = get_user_agent()

    headers = requests.utils.default_headers()

    headers.update({'User-Agent': ua})

    r = requests.get(url, headers=headers)

    return r


def get_shows():

    r = do_request(SHOWLIST_URL)
    r.raise_for_status()

    for show, link, status, rating in process_showlist(r.content):
        yield (show, link, status, rating)

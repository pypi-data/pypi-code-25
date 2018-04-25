from bs4 import BeautifulSoup as Soup
from muse.util import HeadlessChrome
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import time

"""
    Module for genie music chart API

    Attribute:
        SITE_URL: Path for genie web site
        REAL_TIME_CHART: Path for genie real time chart page
"""

SITE_URL = "https://www.genie.co.kr"
REAL_TIME_CHART = "{0}/chart/top200".format(SITE_URL)


def get_real_time_chart_songs(pages=2):
    """
        Get top 50 x n songs
        from genie real time chart

        Args:
            pages(int): page counts how many read songs (50 x n songs)

        Return:
            list: Top 50 x n songs from genie real time chart
    """

    songs = []

    with HeadlessChrome() as chrome:
        # get current time
        now = datetime.now()

        for page in range(pages):
            # Move into genie real time chart page
            # we need query string ymd=(year)(month)(date), hh=(hour), pg=(page)
            chrome.get('{0}?ditc=D&ymd={1}{2:02d}{3:02d}&hh={4:02d}&rtm=Y&pg={5}'.format(
                REAL_TIME_CHART,
                now.year,
                now.month,
                now.day,
                now.hour,
                page + 1
            ))

            wait = WebDriverWait(chrome, 10)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'tr.list')))

            time.sleep(0.5)
            soup = Soup(chrome.page_source, 'html.parser')

            for row in soup.select('tr.list'):
                # remove suffix from rank text
                rank_text = row.select('td.number')[0]
                rank_text.select('span.rank')[0].extract()

                song = {
                    'rank': rank_text.get_text().strip(),
                    'title': row.select('a.title')[0].get_text().strip(),
                    'artist': row.select('a.artist')[0].get_text().strip(),
                    'album': row.select('a.albumtitle')[0].get_text().strip()
                }

                songs.append(song)

    return songs

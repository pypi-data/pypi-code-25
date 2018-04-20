#!/usr/bin/env python
# coding: utf-8

import requests
from bs4 import BeautifulSoup


class PyData:
    @classmethod
    def scraping(self):
        target_url = 'https://www.meetup.com/ja-JP/pro/pydata/#meetups'
        r = requests.get(target_url)

        soup = BeautifulSoup(r.text, 'lxml')

        group = soup.find_all('div', class_='chunk', )
        group_title = group[12].find_all('a')

        count = 1
        title = []

        for t in group_title:
            if count % 2 != 0:
                title.append(t.string)
                if count % 3 == 0:
                    join_title = "  ".join(title)
                    print(join_title)
                    title = []
                    # print("name:", name)

            count += 1

        return True

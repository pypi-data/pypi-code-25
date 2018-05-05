import json
import requests
from urllib import urlencode

BASE_URL = 'https://api.phish.net/v3/'

class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class Phish(object):

    def __init__(self, api):
        self.api = api

    def artists(self):
        url = 'artists/all'
        phish_artists = self._request(url)

        members = {}

        # NOTE @remstone7
        # currently, need to slice the link, waiting for 'name' key to be fixed
        for member in phish_artists['response']['data'].items():
            # members[member['name']] = member['link']
            name = member[1]['link']
            name_index = name.rfind('/')
            member_name = name[name_index+1:]
            members[member_name] = name

        return members

    # need to add POST functionality
    # action defaults to get unless sepcificied otherwise
    # https://phishnet.api-docs.io/v3/attendance/get-attendance
    def attendance(self, showid, action=None, showdate=None, authkey=None, uid=None):
        allowed_actions = [
            'get',
            # 'add',
            # 'remove'
        ]

        if action not in allowed_actions and action is not None:
            raise InvalidArgument('{} is not a valid method, use get, add, or remove'.format(action))


        url = 'attendance/'
        full_url = url + (action if action else 'get')

        method = 'POST' if action != 'get' else None

        params = {
            'showid': showid
        }

        content = self._request(full_url, method, params)

        return content

    # https://phishnet.api-docs.io/v3/authority/authority-get
    def authority(self):
        pass

    # https://phishnet.api-docs.io/v3/blog/blog-get
    def blog(self, month=None, day=None, username=None, author=None, monthname=None, year=None):
        url = 'blog/get'

        params = {
            'month': month,
            'day': day,
            'username': username,
            'author': author,
            'monthname': monthname,
            'year': year
        }

        if all(params.values()) is False:
            return self._request(url)

        

        content = self._request(url, params)

        return content

    # https://phishnet.api-docs.io/v3/collections/collection-query
    # need to pass query or get
    def collections(self, action):
        allowed_actions = [
            'query',
            'get'
        ]
        if action not in allowed_actions:
            raise InvalidArgument('{} is not a valid action, use query or get'.format(action))



    # https://phishnet.api-docs.io/v3/jamcharts/jamcharts-all
    # if post, action and song are required
    def jam_charts(self, action=None, songid=None):
        pass

    # https://phishnet.api-docs.io/v3/people/people-get
    def people(self):
        pass

    # https://phishnet.api-docs.io/v3/relationships/get-friends-and-fans
    def relationships(self):
        pass

    # https://phishnet.api-docs.io/v3/reviews/get-a-review
    def reviews(self):
        pass

    # https://phishnet.api-docs.io/v3/setlists/get-the-most-recent-setlist
    def setlists(self):
        pass

    # https://phishnet.api-docs.io/v3/shows/get-show-links
    def shows(self):
        pass

    # https://phishnet.api-docs.io/v3/user/get-user-details
    def users(self):
        pass

    # https://phishnet.api-docs.io/v3/venues/get-all-venues
    def venues(self):
        pass

    def _request(self, path, method=None, params=None):

        if not method:
            method = 'get'

        url = self.build_url(path, params)

        try:
            if method.lower() == 'post':
                pass
            response = requests.request(method, url)
        except:
            pass

        content = response.json()

        return content

    # build the url for request
    def build_url(self, path, params=None):
        header = {'apikey': self.api}

        if params:
            header.update(params)

        url_params = urlencode(header)
        url = BASE_URL + path + '?' + url_params

        return url

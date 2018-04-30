# -*- coding: utf-8 -*-
from mastodon import Mastodon
from typing import Optional
import feedparser
import shelve
import getpass
import argparse

class Rss2Toot:
    def __init__(self, feedurl, mastodonurl, appname='rss2toot', verbose=False, fmt='title:enclosure:link'):
        self.feedurl = feedurl
        self.mastodonurl = mastodonurl
        self.cache = Rss2TootCache(filename=appname)

        allentries = feedparser.parse(feedurl).get('entries', None)
        if verbose:
            print("Found {} items in total for feed {}".format(len(allentries), self.feedurl))
        if not allentries:
            return
        allentries.reverse()

        (self.client_id, self.client_secret) = self.cache.get_client() if self.cache.get_client() else self.register_app(appname)
        access_token = self.cache.get_access_token() if self.cache.get_access_token() else self.get_access_token()

        self.mastodon = Mastodon(
            client_id=self.client_id,
            client_secret=self.client_secret, 
            access_token=access_token,
            api_base_url=mastodonurl, 
            debug_requests=False, 
        )

        newentries = [ Rss2TootItem(item) for item in allentries if not self.cache.exists(item) ]
        if verbose:
            print("Found {} new items for feed {}".format(len(newentries), self.feedurl))
        for i in newentries:
            self.cache.put(i.itemid)
            self.status_post(i)
            
    def register_app(self, appname):
        client = Mastodon.create_app(appname, api_base_url=self.mastodonurl)
        self.cache.set_client(client)
        return client
    
    def get_access_token(self):
        print("First run of this tool, we need to generate access token.")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        mastodon = Mastodon(
            client_id=self.client_id,
            client_secret=self.client_secret,
            api_base_url=self.mastodonurl,
        )
        access_token = mastodon.log_in(username, password)
        self.cache.set_access_token(access_token)
        return access_token
    
    def media_post(self, item):
        if not item.enclosure:
            return None
        return self.mastodon.media_post(item.enclosure['content'], item.enclosure['type'])
    
    def status_post(self, item):
        media_ids = []
        media_ids.append(self.media_post(item))
        text = u'{}\n{}'.format(item.title, item.link)
        self.mastodon.status_post(text, media_ids=media_ids)
        
class Rss2TootItem:
    def __init__(self, item):
        self.__dict__ = item
        self.itemid = item.get('guid', item.get('id', item.get('link')))
    
    @property
    def enclosure(self):
        import requests
        if not self.links:
            return None
        l = [e for e in self.links if
                e.get('rel') == 'enclosure' and
                'image/' in e.get('type')
                ]
        if not len(l):
            return None
        link = l[0]
        if link['url'].startswith('//'):
            link['url'] = 'https:' + link['url']
        link['content'] = requests.get(link['url']).content
        return link
    
class Rss2TootCache:
    def __init__(self, filename='cache.db'):
        self.cache = shelve.open(filename)
        
    def __del__(self):
        self.cache.close()
    
    def exists(self, item):
        itemid = item.get('guid', item.get('id', item.get('link')))
        return str(itemid) in self.cache
    
    def put(self, itemid):
        self.cache[str(itemid)] = itemid
    
    def set_client(self, client):
        self.cache['client'] = client;
    
    def get_client(self):
        return self.cache.get('client', None)
    
    def set_access_token(self, access_token):
        self.cache['access_token'] = access_token
        
    def get_access_token(self):
        return self.cache.get('access_token', None)

def toot(feedurl:str, mastodonurl:str, **kwargs) -> None:
    r"""Parse RSS feed and send it's items as a mastodon toots to Mastodon instance.

    :param feedurl: RSS URL to read from.
    :param mastodonurl: Mastodon URL to send toots to.
    :param \*\*kwargs: Optional arguments that ``toot`` takes.
    """
    kwargs.setdefault('appname', 'rss2toot')
    kwargs.setdefault('verbose', False)
    Rss2Toot(feedurl, mastodonurl, **kwargs)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--application-name', default='rss2toot')
    parser.add_argument('-m', '--mastodon-url', required=True)
    parser.add_argument('-r', '--rss-url', required=True, action='append', help='can be specified multiple times')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()
    
    for r in args.rss_url:
        toot(r, args.mastodon_url, appname=args.application_name, verbose=args.verbose)

if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import sys
from ezflix.request import Request
from tmdbv3api import TMDb


tmdb = TMDb()
tmdb.api_key = 'YOUR_API_KEY'
movie = Movie()
search = movie.search(q)
if not search:
    return
first = search[0]
id = first.imdb_id
req = reqests.get('https://eztv.ag/api/get-torrents?imdb_id=%s' % id)

if not req.ok:
    return
    
results = []
count = 1
search_results = req.json()
for result in search_results['torrents']:
    obj = {'id': count,
           'title': result['title'],
           'magnet': result['magnet_url'],
           'seeds': result['seeds'],
           'peers': result['peers'],
           'release_date': result['1505989981']
           }
          
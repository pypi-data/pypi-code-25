from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.test.client import RequestFactory

import requests,bs4

class Command(BaseCommand):
  def add_arguments(self, parser):
    # Positional arguments
    parser.add_argument('origin', type=str)
  def handle(self,*args,**kwargs):
    r = requests.get(kwargs['origin']+"/sitemap.xml")
    s = bs4.BeautifulSoup(r.text,"lxml")
    sitemap_urls = [l.get_text() for l in s.find_all("loc")]
    settings_urls = [kwargs['origin']+u for u in getattr(settings,'TEST_URLS',[])]
    for url in sitemap_urls + settings_urls:
      r = requests.get(url)
      if r.status_code != 200:
        print r.status_code,"\t",url

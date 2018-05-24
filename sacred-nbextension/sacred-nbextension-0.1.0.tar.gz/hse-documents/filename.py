# coding=utf-8
import logging
import re

import scrapy

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from w3lib.html import remove_tags

import coloredlogs

coloredlogs.install(level='DEBUG')

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'scrapy': {
            'level': 'DEBUG',
        },
    }
}

logging.config.dictConfig(DEFAULT_LOGGING)



# %%
class Spider(CrawlSpider):
    name = "site"

    allowed_domains = ['www.site.com']
    
    rules = (
#         Rule(LinkExtractor(allow=(r'links/.*$'), deny=('')), callback='parse_item'),
        Rule(LinkExtractor(allow=(r'ba/[a-z]+'))),
        Rule(LinkExtractor(allow=(r'ba/[a-z]+/documents')), callback='parse_item')
    )
    custom_settings = {
        'LOGSTATS_INTERVAL': 15,
        'EXTENSIONS': {
            'scrapy.extensions.logstats.LogStats': 300
        },
        'ITEM_PIPELINES': {'scrapy.pipelines.files.FilesPipeline': 1},
        'FILES_STORE': 'documents',
        'FILES_URLS_FIELD': 'file'
    }
    
    start_urls = ['https://ba.hse.ru/']

    def parse_item(self, response):
        item = {}
        item['url'] = response.url
        # logging.debug('yo!')
        item['file'] = item['url'] + response.css('.file')[0].xpath('./a/@href').extract_first()

        
#         attrs = ['age', 'sex', 'country', 'profile-hits', 'videos-views', 'signedup']
#         for attr in attrs:
#             xpath = '//*[@id="pinfo-{}"]/span/text()'.format(attr)
#             item[attr] = response.xpath(xpath).extract_first()

        # xpath = '//*[@id="pinfo-{}"]/*'.format(attr)
        # lst = response.xpath(xpath).extract()
        # item['list'] = list(filter(None, (map(remove_tags, lst))))
        
        # elems = response.xpath('//*').extract()
        # item['text'] = ' '.join((map(remove_tags, elems))

        yield item

#     def parse_start_url(self, response):
#         for link in LinkExtractor(allow=(r'/[a-z]$')).extract_links(response):
#             logging.debug(link.url)
#             yield scrapy.Request(link.url)

from dcoutside.crawler import DCInsideCrawler
from pprint import pprint

crawler = DCInsideCrawler(include_comments=True)
pprint(crawler.get_post('cat', 0))
# pprint(crawler.get_all_comments('cat', 0, 30))

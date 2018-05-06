"""Google api class.
"""

import json

from datahunters.shared.selenium_scraper import SeleniumScraper
from datahunters.search.common import ImgSearchObject


class BingImageAPI(SeleniumScraper):
  """Class for google image search api.
  """
  base_url = "https://www.bing.com/images/search"

  def __init__(self, use_headless=False):
    super().__init__(use_headless)
    print("Bing image api initialized")

  def scrape(self, keywords):
    try:
      print("start scraping {} using Bing".format(keywords))
      formatted_keywords = keywords.strip().replace(" ", "+")
      req_url = "{}?q={}&qs=n&form=QBILPG&sp=-1&sc=8-3&sk=&cvid=1B063871C36E42438CC99549B92CD76D".format(
          self.base_url, formatted_keywords)
      elems = self.scrape_inf_scroll(
          req_url, "a.iusc", "a.iusc", load_btn_selector="a.btn_seemore")
      print("total fetched items: {}".format(len(elems)))
      for elem in elems:
        try:
          # create result object.
          cur_res = ImgSearchObject()
          raw_data = self.get_attribute_values([elem], "m")[0]
          # parse link.
          parsed_data = json.loads(raw_data)
          cur_res.img_url = parsed_data["murl"]
          yield cur_res
        except Exception as ex:
          print("error in processing item: {}".format(ex))
          continue
      self.browser.close()
      print("Bing image scraping finished.")
      yield None
    except Exception as ex:
      print("error in Bing image scraper: {}".format(ex))
      self.browser.close()
      yield None


if __name__ == "__main__":
  api = BingImageAPI()
  img_gen = api.scrape("car crash")
  res = next(img_gen)
  cnt = 0
  while True:
    res = next(img_gen)
    if res is None:
      break
    cnt += 1
    if cnt % 10 == 0:
      print("scraped {} images".format(cnt))
  print("scrape finished.")

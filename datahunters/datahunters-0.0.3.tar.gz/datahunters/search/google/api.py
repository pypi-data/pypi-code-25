"""Google api class.
"""

import urllib

from datahunters.shared.selenium_scraper import SeleniumScraper
from datahunters.search.common import ImgSearchObject


class GoogleImageAPI(SeleniumScraper):
  """Class for google image search api.
  """
  base_url = "https://www.google.com/search"

  def __init__(self, use_headless=True):
    super().__init__(use_headless)
    print("Google image api initialized")

  def scrape(self, keywords):
    try:
      print("start scraping '{}' using Google".format(keywords))
      formatted_keywords = keywords.strip().replace(" ", "+")
      req_url = "{}?q={}&source=lnms&tbm=isch&sa=X&ei=0eZEVbj3IJG5uATalICQAQ&ved=0CAcQ_AUoAQ&biw=939&bih=591".format(
          self.base_url, formatted_keywords)
      elems = self.scrape_inf_scroll(
          req_url, "a.rg_l", "a.rg_l", load_btn_selector="input#smb")
      print("total fetched items: {}".format(len(elems)))
      for elem in elems:
        try:
          # create result object.
          cur_res = ImgSearchObject()
          link = self.get_attribute_values([elem], "href")[0]
          link = urllib.parse.unquote(link)
          cur_res.img_url = link[link.find("imgurl=") + 7:link.find(
              "&imgrefurl")].rstrip(".")
          yield cur_res
        except Exception as ex:
          print("error in processing item: {}".format(ex))
          continue
      self.browser.close()
      print("Google image scraping finished.")
      yield None
    except Exception as ex:
      print("error in Google image scraper: {}".format(ex))
      self.browser.close()
      yield None


if __name__ == "__main__":
  api = GoogleImageAPI()
  img_gen = api.scrape("car crash")
  cnt = 0
  while True:
    res = next(img_gen)
    if res is None:
      break
    cnt += 1
    if cnt % 10 == 0:
      print("scraped {} images".format(cnt))
  print("scrape finished.")

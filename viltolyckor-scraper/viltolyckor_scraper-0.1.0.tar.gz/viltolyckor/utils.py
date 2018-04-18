# encoding:utf-8
from bs4 import BeautifulSoup
import re

def parse_int(val):
    """Parse int from str."""
    return int(float(val))


def parse_result_page(html):
    """
    """
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.select_one(".statistics-report")
    months = [u'Jan', u'Feb', u'Mar', u'Apr', u'Maj', u'Jun', u'Jul',
              u'Aug', u'Sep', u'Okt', u'Nov', u'Dec', u'Total']
    viltslag = [x.text for x in table.select("td.title")]

    year_cell = table.select_one("th").text
    year = re.search("(\d\d\d\d)", year_cell).group(0)

    region_select_elem = soup.select_one("#ctl10_lstCounties")
    selected_region = region_select_elem.find('option', selected=True)
    # if no option is selected the data refers to the first region in list ("Hela landet")
    if selected_region is None:
        selected_region = region_select_elem.select_one("option")
    region = selected_region.text

    value_rows = table.select("tr")[2:]
    assert len(value_rows) == len(viltslag)
    for row_i, tr in enumerate(table.select("tr")[2:]):
        value_cols = tr.select("td")[1:]
        assert len(value_cols) == len(months)
        for col_i, td in enumerate(value_cols):
            datapoint = {
                "viltslag": viltslag[row_i],
                "region": region,
                "month": months[col_i],
                "year": parse_int(year),
                "value": parse_int(td.text),
            }
            yield datapoint

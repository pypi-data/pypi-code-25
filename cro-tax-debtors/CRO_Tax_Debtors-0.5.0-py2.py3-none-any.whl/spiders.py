import six
import requests
import lxml.html as lxml_html

from .debtors import Item, CategoryDone


if six.PY2:
    import unidecode
    from StringIO import StringIO

    def prepare_content(response):
        return response.content

    def to_str(_text):
        return unidecode.unidecode(_text)
else:
    from io import StringIO

    def prepare_content(response):
        return str(response.content.decode('utf-8'))

    def to_str(_text):
        return _text


class Spider(object):

    def __init__(self, url):
        self._url = url


class CroTaxDepartment(Spider):

    def parse(self):
        try:
            response = requests.get(self._url)
        except:
            yield None

        html_parsed = lxml_html.parse(StringIO(prepare_content(response)))

        is_done = True
        for table in html_parsed.iter('table'):
            fields = []
            if table.attrib.has_key('class') and table.attrib['class'] == 'dataTable':
                for tr in table.iter('tr'):
                    if tr.attrib.has_key('class') and tr.attrib['class'] == 'tableHeader':
                        for td in tr.iter('td'):
                            field_name = to_str(td.text_content()).strip(' \t\n\r').lower()
                            fields.append(field_name)
                    else:
                        item = Item()
                        for i, td in enumerate(tr.iter('td')):
                            if not td.attrib.has_key('class') or td.attrib['class'] != 'navBar':
                                item[fields[i]] = td.text_content().strip(' \t\n\r')
                        if item == True:
                            is_done = False
                            yield item

        if is_done:
            raise CategoryDone()


from lxml import html


def process_showlist(content):
    root = html.fromstring(content)

    table = root.cssselect('table.forum_header_border')
    table = table[1]
    for tr in table.cssselect('tr[name=hover]'):
        _a = tr.cssselect('td a')
        title = _a[0].text_content()
        link = _a[0].attrib['href']
        _font = tr.cssselect('td font')
        status = _font[0].text_content()
        _b = tr.cssselect('td b')
        rating = _b[0].text_content()

        yield title, link, status, rating

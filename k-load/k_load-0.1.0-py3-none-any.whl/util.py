from .extractor import WeSing, midishow
import getopt
import sys
import re

SITES = {
    'midishow': 'midishow',
    'WeSing': 'kg.qq',
}

fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  # noqa
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',  # noqa
}


def main():
    _DEBUG = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], ":ho:v:", ['--debug', "output="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    web_url = 'https://node.kg.qq.com/play?s=jWwYyijWB6CFhWPw&shareuid=66999b8c2125348236&topsource='

    if len(args) > 0:
        web_url = args[0]

    site = None
    for tar_site in SITES:
        if re.search(SITES[tar_site], web_url):
            site = tar_site

    if not site:
        raise NotImplementedError('This site is not implemented yet...')

    if site == 'midishow':
        obj = midishow.MidiShow(web_url)
    elif site == 'WeSing':
        obj = WeSing.WeSing(web_url)
    else:
        obj = None

    obj.site = site
    obj.exec()



if __name__ == "__main__":
    main()

import argparse
import re

from util import SITES
from extractor import WeSing, midishow

def main():
    parser = argparse.ArgumentParser()

    # Data and vocabulary file
    parser.add_argument('url', type=str,
                        default=None,
                        help='url to download from')

    parser.add_argument('--debug', type=bool,
                        default=False,
                        help='show debug information')

    parser.set_defaults()
    args = parser.parse_args()


    if args.debug:
        print('Arguments: ', args)
    if not args.url:
        raise NotImplementedError
    web_url = args.url

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
				
    if args.debug:
        print('File url: ', obj.file_url)
				
				
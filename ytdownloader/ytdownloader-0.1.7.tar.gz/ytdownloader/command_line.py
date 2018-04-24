import argparse
import ytdownloader
from ytdownloader import YoutubeDownloader


def main():
    ''' main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='?', default=None,
                        help='''configuration file for ytdownloader''')
    parser.add_argument('--version', action="store_true",
                        help='current version of ytdownloader')
    parser.add_argument('--about', action="store_true",
                        help='YoutubeDownloader is an automated service to download videos from youtube')

    args = parser.parse_args()

    if args.version:
        return ytdownloader.__VERSION__

    yt = YoutubeDownloader()
    yt.read_config(args.configuration)
    yt.start_download()

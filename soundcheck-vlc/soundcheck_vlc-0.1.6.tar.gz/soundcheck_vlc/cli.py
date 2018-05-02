import argparse
import logging
import logging.config


from soundcheck_vlc.main import main
from soundcheck_vlc.utils import parseinput
from soundcheck_vlc.utils.config import get_config_or_create, save_config, get_logger_config

logging.config.fileConfig(str(get_logger_config()))
# logging.config.fileConfig('/home/alex/.local/share/SoundCheckVLC/logging.conf')
logger = logging.getLogger()


class ParseException(Exception):
    pass


def run():
    """

    :return:
    """
    config = get_config_or_create()

    parser = argparse.ArgumentParser(description="""listen to Mastodon for a predefined hashtag (e.g. #SoundCheck)
    and will append any video link to your vlc playlist.""")
    parser.add_argument('-t', '--hashtag', action='store', nargs=1,
                        default='soundcheck', help='Hashtag to listen to, without the # symbol.')
    parser.add_argument('-s', '--save', action='store_true', help='Permanently store configuration changes.')
    parser.add_argument('-p', '--prefetch', action='store', type=int, help='Specify how many status to\ '
                                                                           'preload from the existing timeline.')

    args = parser.parse_args()

    if args.hashtag:
        status, hashtag = parseinput.parse_hashtag(args.hashtag)
        if status == parseinput.ParseStatus.FAIL:
            err_msg = '{} is not a valid hashtag format'.format(args.hashtag)
            logger.error(err_msg)
            raise ParseException(err_msg)
        else:
            if status == parseinput.ParseStatus.PARTIAL_PASS:
                logger.warning('{0} is not valid, {1} has been used'.format(args.hashtag, hashtag))

            config['mastodon']['tag'] = hashtag  # we override the config file

    if args.save:
        save_config(config)

    main(config=config, preload=args.prefetch)


if __name__ == '__main__':
    run()

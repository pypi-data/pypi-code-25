import time
import re
import subprocess
import logging

from mastodon import StreamListener
from soundcheck_vlc.utils.config import get_config_or_create
from soundcheck_vlc.register import init_instance
from soundcheck_vlc.utils.video_parse import parse_url
from soundcheck_vlc.utils.vlchttp import VlcStatus, check_status, enqueue

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

url_re = re.compile(r"https?://\S+")


def process_status(status):
    """

    :param status:
    :return:
    """
    match = url_re.search(status['content'])
    if match:
        result = parse_url(match.string[match.start():match.end()])
        if result[0]:
            logger.info('Video enqueued.')
            enqueue(result[2])


class SoundCheckListener(StreamListener):
    def on_update(self, status):
        """

        :param status:
        :return:
        """
        process_status(status)


def startup_vlc():
    if check_status() == VlcStatus.HTTP_ERROR:
        is_vlc_running = int(subprocess.getoutput('ps -a | grep -w vlc | wc -l'))
        if is_vlc_running > 0:
            # todo: add a better exception
            raise Exception('Error starting vlc. Http status: {0}, ps output: {1}'.format(check_status(),
                                                                                          is_vlc_running))
        else:
            p = subprocess.Popen('vlc')
            time.sleep(1)
            startup_vlc()


def main(*args, **kwargs):
    if kwargs['config']:
        config = kwargs['config']
    else:
        config = get_config_or_create()

    mastard = init_instance(config)
    my_soundcheck = SoundCheckListener()
    startup_vlc()

    hashtag = config['mastodon']['tag']

    if 'preload' in kwargs:
        if kwargs['preload'] > 0:
            statuses = mastard.timeline_hashtag(hashtag, limit=kwargs['preload'])
            for status in statuses:
                process_status(status)

    while True:
        try:
            mastard.stream_hashtag(hashtag, my_soundcheck, async=False)
        except Exception as error:
            logger.warning('General exception caught: ' + str(error))
            time.sleep(0.5)


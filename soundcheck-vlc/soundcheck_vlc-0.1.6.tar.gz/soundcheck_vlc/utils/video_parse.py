import re
import requests
import operator
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def parse_url(url):
    """
    Parse the url and compare against predefined sources:
        - Youtube
        - Dailymotion
        - Peertube instances
        - Vimeo

    :param url: string
    :return: tuple (Boolean, source, url)
    """
    url_prefix = r"https?://(www\.)?"
    sources = {
        'youtube': r"youtu\.?be\S+$",
        'dailymotion': r"dai(lymotion\.com)|(\.ly)\S+$",
        'peertube': r".+/video/watch/[0-9a-fA-F]{8}(\-[0-9a-fA-F]{4}){3}\-[0-9a-fA-F]{12}$",
        # video guid format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        'vimeo': r"vimeo\.com\S+$",
    }

    for k, v in sources.items():
        pattern = url_prefix + v
        if re.match(pattern, url):
            if k == 'peertube':
                try:
                    video_url = get_peertube_source_url(url)
                except requests.exceptions.ConnectionError as e:
                    logger.warning('Connection error: ' + str(e))
                    video_url = ''
            else:
                video_url = url

            if video_url:
                return True, k, video_url
            else:
                return False, None, None
    return False, None, None


def get_peertube_source_url(url):
    """
    This function fetch the video metadata, json formatted, from the API supplied by peertube.
    It then parses its content and returns the direct video link.
    When multiple sources are available, it takes the video with the highest resolution.
    :param url: source url from a peertube instance
    :type url: str
    :return: original video url
    :rtype: str
    """
    api_url = url.replace('videos/watch', 'api/v1/videos')
    try:
        r = requests.get(api_url)
    except requests.exceptions.ConnectionError as e:
        raise e

    if r.status_code == requests.codes.ok:
        video_details = r.json()
        res_dict = {k: int(v['resolution']['id']) for k, v in enumerate(video_details['files'])}
        max_res_file = max(res_dict.items(), key=operator.itemgetter(1))[0]
        return video_details['files'][max_res_file]['fileUrl']
    else:
        return None

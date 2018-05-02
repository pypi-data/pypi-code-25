# Python standard modules
import logging
from enum import Enum
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus, urlencode

# Project dependencies
import requests

# Project modules
from soundcheck_vlc.utils.config import get_config_or_create

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

config = get_config_or_create()
BASE_URL = 'http://localhost:' + str(config['vlc']['port'])
STATUS_XML_URL = BASE_URL + '/requests/status.xml'
AUTH = ('', config['vlc']['password'])


class VlcStatus(Enum):
    HTTP_ERROR = 0
    IDLE = 1
    PLAYING = 2
    ENQUEUED  = 3


def check_status():
    try:
        r = requests.get(STATUS_XML_URL, auth=AUTH)
    except requests.exceptions.ConnectionError:
        return VlcStatus.HTTP_ERROR

    if r.status_code == requests.codes.ok:
        player_status = ET.fromstring(r.text).find(".//state").text
        if player_status == 'playing':
            return VlcStatus.PLAYING
        else:
            return VlcStatus.IDLE
    else:
        logger.warning('HTTP Error: {}'.format(str(r.status_code)))
        return VlcStatus.HTTP_ERROR


def play():
    query = urlencode({'command':'pl_pause'})
    r = requests.get(STATUS_XML_URL + '?' + query, auth=AUTH)
    if r.status_code == requests.codes.ok:
        return VlcStatus.PLAYING
    else:
        logger.warning('HTTP Error: {}'.format(str(r.status_code)))
        return VlcStatus.HTTP_ERROR


def enqueue(url):
    query = urlencode({'command':'in_enqueue', 'input': url})
    r = requests.get(STATUS_XML_URL + '?' + query, auth=AUTH)
    if r.status_code == requests.codes.ok:
        if check_status() == VlcStatus.IDLE:
            play()
        return VlcStatus.ENQUEUED
    else:
        logger.warning('HTTP Error: {}'.format(str(r.status_code)))
        return VlcStatus.HTTP_ERROR

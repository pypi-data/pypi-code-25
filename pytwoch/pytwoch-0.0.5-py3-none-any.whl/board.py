import logging
from typing import List, Dict

import requests

from pytwoch.api_urls import APIUrls
from pytwoch.thread import Thread

logger = logging.getLogger(__file__)


class Board(object):
    def __init__(self, board_id: str):
        self.board_id: str = board_id
        self.BoardName: str = None
        self.BoardInfo: str = None
        self.BoardInfoOuter: str = None
        self.banner_image: str = None
        self.banner_link: str = None
        self.bump_limit: int = None
        self.default_name: str = None
        self.enable_dices: bool = None
        self.enable_flags: bool = None
        self.enable_icons: bool = None
        self.enable_images: bool = None
        self.enable_names: bool = None
        self.enable_oekaki: bool = None
        self.enable_posting: bool = None
        self.enable_sage: bool = None
        self.enable_shield: bool = None
        self.enable_subject: bool = None
        self.enable_thread_tags: bool = None
        self.enable_trips: bool = None
        self.enable_video: bool = None
        self.filter: str = None
        self.max_comment: int = None
        self.max_files_size: int = None
        self.threads: List[Thread] = []
        self.raw_threads: List[Dict] = []

    def prepare_threads(self, thread_limit):
        self.raw_threads = self.threads[:thread_limit]
        self.threads = [Thread(self.board_id, raw_thread.get('num', None)) for raw_thread in self.raw_threads]

    def load_threads(self):
        logger.debug('Loading threads for board {}'.format(self.board_id))
        for thread in self.threads:
            thread.load()

    def load(self, auto_load_threads=False, thread_limit=10):
        logger.debug('Loading board {}'.format(self.board_id))
        response = requests.get(APIUrls.get_board(self.board_id)).json()
        for field in response.keys():
            if hasattr(self, field):
                setattr(self, field, response.get(field))
        self.prepare_threads(thread_limit)
        if auto_load_threads:
            self.load_threads()

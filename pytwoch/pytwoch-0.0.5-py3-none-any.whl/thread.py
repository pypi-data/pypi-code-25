import logging
from typing import Dict, List

import requests

from pytwoch.api_urls import APIUrls
from pytwoch.post import Post

logger = logging.getLogger(__file__)


class Thread(object):
    def __init__(self, board_id, thread_id: str):
        self.thread_id: str = thread_id
        self.board_id: str = board_id
        self.title: str = None
        self.files_count: int = None
        self.posts_count: int = None
        self.is_board: bool = None
        self.is_closed: bool = None
        self.is_index: bool = None
        self.raw_posts: List[Dict] = []
        self.posts: List[Post] = []

    def prepare_posts(self):
        self.posts = [Post(**raw_post) for raw_post in self.raw_posts]

    def load(self):
        response = requests.get(APIUrls.get_thread(self.board_id, self.thread_id)).json()
        for field in response.keys():
            if hasattr(self, field):
                setattr(self, field, response.get(field, None))
        try:
            self.raw_posts = response.get('threads')[0].get('posts')
        except (AttributeError, KeyError):
            self.raw_posts = []

        self.prepare_posts()

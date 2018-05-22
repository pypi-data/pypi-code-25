import logging
from typing import List, Dict

logger = logging.getLogger(__file__)


class Post(object):
    def __init__(self, **kwargs):
        self.banned: bool = kwargs.get('banned', False)
        self.closed: bool = kwargs.get('closed', False)
        self.comment: str = kwargs.get('comment', '')
        self.date: str = kwargs.get('date', '')
        self.endless: bool = kwargs.get('endless', False)
        self.email: str = kwargs.get('email', '')
        self.lasthit: str = kwargs.get('lasthit', '')
        self.name: str = kwargs.get('name', '')
        self.num: str = kwargs.get('num', '')
        self.number: int = kwargs.get('number', 0)
        self.op: bool = kwargs.get('op', False)
        self.parent: str = kwargs.get('parent', '')
        self.sticky: bool = kwargs.get('sticky', False)
        self.subject: str = kwargs.get('subject', '')
        self.tags: str = kwargs.get('tags', '')
        self.timestamp: str = kwargs.get('timestamp', '')
        self.trip: str = kwargs.get('trip', '')
        self.raw_files: List[Dict] = kwargs.get('files', [])
        self.files: List[PostFile]

        self.load_files()

    def load_files(self):
        self.files = [PostFile(**raw_file) for raw_file in self.raw_files]


class PostFile(object):
    def __init__(self, **kwargs):
        self.displayname: str = kwargs.get('displayname', '')
        self.fullname: str = kwargs.get('fullname', '')
        self.name: str = kwargs.get('name', '')
        self.path: str = kwargs.get('path', '')
        self.thumbnail: str = kwargs.get('thumbnail', '')
        self.md5: str = kwargs.get('md5', '')
        self.height: int = kwargs.get('height', 0)
        self.width: int = kwargs.get('width', 0)
        self.size: int = kwargs.get('size', 0)
        self.type: int = kwargs.get('type', 0)
        self.tn_width: int = kwargs.get('tn_width', 0)
        self.tn_height: int = kwargs.get('tn_height', 0)
        self.nsfw: bool = kwargs.get('nsfw', False)

import pickle
import zlib
from pathlib import Path
import os

from . import guesser

_current_repo_version = "0.0.1"
_repo_dir = str(Path.home().joinpath(".config/scilicet"))
_repo_path = os.path.join(_repo_dir, "repo")


def _check_and_create_repo_dir():
    if not os.path.exists(_repo_dir):
        os.makedirs(_repo_dir)


# Not tested
def _convert(old_repo):
    if old_repo.version == _current_repo_version:
        return old_repo
    else:
        raise NotImplementedError


# Not tested
def _dump(obj, location):
    with open(location, "wb") as out_file:
        out_file.write(obj)


def _load(location):
    with open(location, "rb") as in_file:
        return in_file.read()


def load():
    if not os.path.exists(_repo_path):
        return ScilicetRepository()
    try:
        return _convert(pickle.loads(zlib.decompress(_load(_repo_path))))
    except NotImplementedError:
        return ScilicetRepository()


def dump(repo):
    _check_and_create_repo_dir()
    dumped = pickle.dumps(repo)
    compressed = zlib.compress(dumped)
    _dump(compressed, _repo_path)


class ScilicetRepository:

    def __init__(self):
        self.version = _current_repo_version
        self.templates = dict()
        self.guesser = guesser.ScilicetGuesser()

    def process(self, image):
        bytes_image = pickle.dumps(image)
        identifier = hash(bytes_image)

        if identifier in self.templates.keys():
            return self.templates[identifier]["character"]

        return self.guesser.guess(image)

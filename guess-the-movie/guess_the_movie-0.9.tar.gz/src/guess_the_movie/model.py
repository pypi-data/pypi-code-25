import json
import urllib.request
import random
import os
import collections
import enum
from . import utils
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtGui import QImage, QPixmap


class Difficult(enum.IntEnum):
    EASY = 0
    NORMAL = 1
    HARD = 2


def compute_difficult(votes_count):
    left, right = 20000, 100000
    if votes_count < left:
        return Difficult.HARD
    elif left <= votes_count < right:
        return Difficult.NORMAL
    else:  # right < votes_count
        return Difficult.EASY


class MovieData(QObject):
    # Signals
    screenshot_downloaded = pyqtSignal("QPixmap")

    def __init__(self, title, screenshots_links, votes_count, id, parent=None):
        super().__init__(parent)

        self.title = title
        self.screenshot_link = random.choice(screenshots_links)
        self.votes_count = votes_count
        self.id = id

        self._screenshot = None
        self.__is_screenshot_downloaded = False
        self._network_manager = QNetworkAccessManager()
        self._network_manager.finished.connect(self._downloaded)

    def get_title(self):
        return self.title

    def get_difficult(self):
        return compute_difficult(self.votes_count)

    def get_id(self):
        return self.id

    def download_screenshot(self):
        if not self.__is_screenshot_downloaded:
            # print("download started " + self.screenshot_link)
            request = QNetworkRequest(QUrl(self.screenshot_link))
            request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
            self._network_manager.get(request)
        else:
            self.screenshot_downloaded.emit(self._screenshot)

    @pyqtSlot("QNetworkReply*")
    def _downloaded(self, reply):
        self._screenshot = QPixmap()
        self._screenshot.loadFromData(reply.readAll())
        if self._screenshot.isNull():
            print("download failed")
            return
        self.__is_screenshot_downloaded = True
        self.screenshot_downloaded.emit(self._screenshot)


class Movies:
    """
        {'votes_count': '100',
        'title': 'Давай! Давай!',
        'screenshots_links':
            ['http://kinopoisk.ru/images/kadr/633729.jpg',
            'http://kinopoisk.ru/images/kadr/633728.jpg',
            'http://kinopoisk.ru/images/kadr/633727.jpg',
            'http://kinopoisk.ru/images/kadr/633726.jpg',
            'http://kinopoisk.ru/images/kadr/633725.jpg'],
        'id': 718},
    """

    def __init__(self):
        this_dir, this_filename = os.path.split(__file__)
        movies_json_path = os.path.join(this_dir, "data", "movies.json")

        with open(movies_json_path, "r") as f:
            movies = json.load(f)

        self.movies = []
        for m in movies:
            self.movies.append(MovieData(m["title"], m["screenshots_links"], int(m["votes_count"]), m["id"]))
            # todo change votes_count type in json document str -> int

    def get_movies(self, count=1, difficult=None, except_movies_with_ids=None):
        movies = self.movies
        if difficult is not None:
            movies = filter(lambda m: m.get_difficult() == difficult, movies)
        if except_movies_with_ids is not None:
            movies = filter(lambda m: m.get_id() not in except_movies_with_ids, movies)
        return random.sample(list(movies), count)


class PickedMovies:
    def __init__(self, answer, answer_options):
        # answer_options is a list of MovieData objects. It includes answer
        self.answer = answer
        self.answer_options = random.sample(answer_options, k=len(answer_options))

    def get_answer(self):
        return self.answer

    def get_answer_options(self):
        return self.answer_options


class MoviesPicker:
    __OPTIONS_COUNT = 4

    def __init__(self, options_count=__OPTIONS_COUNT):
        self.movies = Movies()
        self.options_count = options_count
        self.picked_movies_history = []
        self.picked_movies_cash = collections.deque([None, None], maxlen=2)

    def __pick_movies(self, difficult):
        answer_options = self.movies.get_movies(count=1,
                                                difficult=difficult,
                                                except_movies_with_ids=self.picked_movies_history)
        self.picked_movies_history.append(answer_options[0].get_id())
        answer_options += self.movies.get_movies(count=self.options_count - 1,
                                                 difficult=difficult,
                                                 except_movies_with_ids=[self.picked_movies_history[-1]])

        return PickedMovies(answer_options[0], answer_options)

    def pick_movies(self, difficult):
        # todo download asynchronously
        result = self.picked_movies_cash[-1]
        if result is None or result.get_answer().get_difficult() != difficult:
            self.picked_movies_cash.append(self.__pick_movies(difficult))
            result = self.picked_movies_cash[-1]

        next_pick = self.__pick_movies(difficult)
        next_pick.answer.download_screenshot()
        self.picked_movies_cash.append(next_pick)

        return result

    def clear_picked_movies_history(self):
        self.picked_movies_history = []


class Score:
    def __init__(self):
        self.__score = 0

    def get_score(self):
        return self.__score

    def add_points(self, points):
        self.__score += points

    def clear_score(self):
        self.__score = 0


class Records(metaclass=utils.Singleton):
    class __SignalsAndSlots(QObject):
        # Signals
        records_updated = pyqtSignal()
        """
        def __init__(self, parent=None):
            QObject.__init__(self, parent)
        """
    RECORDS_COUNT_LIMIT = 10

    def __init__(self):
        this_dir, this_filename = os.path.split(__file__)
        self._path_to_records_data = os.path.join(this_dir, "data", "records.json")
        self.signals = self.__SignalsAndSlots()
        self.__records = self.__load_from_disk()

    def __save_to_disk(self) -> None:
        with open(self._path_to_records_data, 'w') as f:
            json.dump(self.__records, f)

    def __load_from_disk(self) -> list:
        if os.path.exists(self._path_to_records_data):
            with open(self._path_to_records_data, 'r') as f:
                return json.load(f)
        else:
            return [[{"name": "", "score": 0} for _ in range(self.RECORDS_COUNT_LIMIT)] for _ in range(3)]

    def is_score_record(self, difficult: Difficult, score: Score) -> bool:
        return self.__records[difficult][0]["score"] < score.get_score()

    def update_records(self, difficult: Difficult, score: Score, name: str="") -> None:
        if self.is_score_record(difficult, score):
            self.__records[difficult][0]["score"] = score.get_score()
            self.__records[difficult][0]["name"] = name
            self.__records[difficult].sort(key=lambda r: r["score"])

            self.__save_to_disk()
            self.signals.records_updated.emit()

    def get_records(self, difficult: Difficult):
        yield from self.__records[difficult]










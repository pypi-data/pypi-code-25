from typing import List, TypeVar, Generic, Iterable

T = TypeVar('T')


class ResultEntry(Generic[T]):
    def __init__(self, element: T, score: float) -> None:
        self.element: T = element
        self.score: float = score

    def get(self) -> T:
        return self.element

    def set(self, element: T):
        self.element = element


class ResultList(Generic[T]):
    def __init__(self):
        self._results: List[ResultEntry[T]] = []

        self.score_min: float = 0

        self._results_cache: List[ResultEntry[T]] = None
        self._cache_score_min: float = self.score_min

    @property
    def result(self) -> List[ResultEntry[T]]:
        if not (self._cache_score_min == self.score_min and self._results_cache):
            self._results_cache = [e for e in self._results if e.score >= self.score_min]
            self._cache_score_min = self.score_min
        return self._results_cache

    def append(self, entry: ResultEntry[T]):
        self._results.append(entry)
        self._results_cache = None

    def __len__(self):
        return len(self.result)

    def __iter__(self):
        return self.result.__iter__()

    def __getitem__(self, item) -> ResultEntry[T]:
        return self.result.__getitem__(item)

    def get(self, item, default=None):
        try:
            self.__getitem__(item)
        except IndexError:
            return default

    def __contains__(self, item):
        return self.result.__contains__(item)

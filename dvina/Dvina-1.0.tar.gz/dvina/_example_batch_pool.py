import itertools
import threading
from ._utils.iter import ibatch
from ._example import Example
from future.utils import implements_iterator


@implements_iterator
class ExampleBatchPool(object):
    """
    Thread-safe infinite iterator over the provided examples Iterable.
    Batches examples in order to decrease number of lock operations.

    """
    BATCH_SIZE = 10

    def __init__(self, examples, batch_size=BATCH_SIZE):
        """

        Parameters
        ----------
        examples: Iterable

        batch_size: int

        """
        self._lock = threading.Lock()
        self._cycle_batch_iter = ibatch(self._cycle_examples(examples), batch_size)

    def __iter__(self):
        return self

    def __next__(self):
        with self._lock:
            return next(self._cycle_batch_iter)

    @staticmethod
    def _cycle_examples(examples):
        for epoch, examples in enumerate(itertools.repeat(examples)):
            for index, example in enumerate(examples):
                yield {
                    'epoch': epoch,
                    'index': index,
                    'example': Example(example['id'], example['features'])
                }

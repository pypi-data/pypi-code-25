import threading
from heapq import heappush, heappop
import logging

from ._utils.serialization import DvinaSerialization
from ._ranked_example_pool import RankedExamplePool


@DvinaSerialization.serializes(["_already_sampled", "_counter", "_n_examples", "_heap_of_examples",
                               "_latest_example_versions"])
class RankedPoolStandard(RankedExamplePool):

    """This class has the Ranked Pool of examples which are ordered according to their confidences.
    sample() provides the least confident examples"""
    def __init__(self):
        self._already_sampled = {}
        self._counter = 0  # unique count in case two examples have the same confidences
        self._n_examples = 0 # the number of unique examples which have been added to the ranked pool but not sampled
        self._heap_of_examples = []
        """
        Map each example id to a version which represents the number of times the example has been added.
        It is set to 1 after it is initially added. We increment the version each time the example is added again.
        We check versions when sampling so we only sample the latest version of each example.
        """
        self._latest_example_versions = {}
        self.deserialized_init()

    def pre_serialize(self):
        self._lock.acquire()

    def post_serialize(self):
        self._lock.release()

    def deserialized_init(self):
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)

    def sample(self, n_batch=1):
        with self._lock:
            self._logger.debug("sample(n_batch={})".format(n_batch))
            if n_batch > self._n_examples:
                self._logger.warning("Asking for {0} examples but have only {1}, will return {1}"
                                     .format(n_batch, self._n_examples))
                # if not enough examples, return all that there is
                n_batch = self._n_examples

            ids = [self._sample_one() for _ in range(n_batch)]
            for cur_id in ids:
                self._already_sampled[cur_id] = 1
            probs = [1.0 for _ in range(n_batch)]
            return ids, probs

    def add_batch(self, ranked_examples):
        with self._lock:
            for example in ranked_examples:
                example_id, _, priority = example
                if example_id not in self._already_sampled:
                    self._add_example(example_id, priority)

    def _add_example(self, example_id, priority):
        previous_version = self._latest_example_versions.get(example_id, 0)
        new_version = previous_version + 1
        if new_version == 1:
            # this is the first time we've added the example,
            # increment the count of unique added and non-sampled examples
            self._n_examples += 1
        self._latest_example_versions[example_id] = new_version
        self._counter += 1
        entry = [priority, self._counter, new_version, example_id]
        heappush(self._heap_of_examples, entry)

    def _sample_one(self):
        while self._heap_of_examples:
            priority, count, version, example_id = heappop(self._heap_of_examples)
            # only sample an example if it is the latest version
            if version == self._latest_example_versions.get(example_id):
                self._n_examples -= 1
                return example_id
        raise StopIteration('Sample from an empty pool')

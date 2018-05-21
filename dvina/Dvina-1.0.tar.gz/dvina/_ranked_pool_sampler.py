import threading
import numpy as np
from future.utils import listvalues

from ._utils.serialization import DvinaSerialization
from ._ranked_example_pool import RankedExamplePool
from . import _utils as utils


@DvinaSerialization.serializes(["_random", "_already_sampled", "_confidences"])
class RankedPoolSampler(RankedExamplePool):
    """This class has the Ranked Pool of examples which are ordered according to whether they are sampled.
    The sampling distribution comes from normalizing confidences across all examples in the pool"""

    def __init__(self, seed=42):
        self._already_sampled = {}
        self._confidences = {}
        self.deserialized_init()
        self._random = np.random.RandomState(seed)

    def deserialized_init(self):
        self._lock = threading.Lock()

    def sample(self, n_batch=1):
        with self._lock:
            if len(self._confidences) == 0:
                return [], []

            example_ids = np.array(list(self._confidences))
            confidences = np.array(listvalues(self._confidences))
            confidences = confidences.max() - confidences
            sampling_probabilities = utils.normalize_scores(confidences, norm='l1')
            if n_batch > len(self._confidences):
                # if not enough examples, return all that there is
                indices = range(len(self._confidences))
            else:
                indices = self._random.choice(len(self._confidences), size=n_batch, replace=False,
                                              p=sampling_probabilities)

            ids = []
            probabilities = []
            for i in indices:
                cur_id = example_ids[i]
                ids.append(cur_id)
                probabilities.append(sampling_probabilities[i])
                self._already_sampled[cur_id] = 1
                del self._confidences[cur_id]
            return ids, probabilities

    def add_batch(self, ranked_examples):
        with self._lock:
            for example in ranked_examples:
                if example.id not in self._already_sampled:
                    self._confidences[example.id] = example.confidence

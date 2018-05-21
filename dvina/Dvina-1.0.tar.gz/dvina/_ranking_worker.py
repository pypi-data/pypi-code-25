import threading
from builtins import map
import logging

from ._meta_model import MetaModel
from ._ranked_example_pool import RankedExamplePool
from ._example_batch_pool import ExampleBatchPool


class RankingWorker(object):
    def start(self, meta_model, example_batch_pool, ranked_example_pool):
        assert isinstance(meta_model, MetaModel)
        assert isinstance(example_batch_pool, ExampleBatchPool)
        assert isinstance(ranked_example_pool, RankedExamplePool)
        self._rev_start_epoch = None
        self._rev_start_index = None
        self._model_rev = None
        self._meta_model = meta_model
        self._example_batch_pool = example_batch_pool
        self._ranked_example_pool = ranked_example_pool
        self._logger = logging.getLogger(__name__)

        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        return self

    def run(self):
        for batch in self._example_batch_pool:
            assert batch, "Batch can not be empty"

            if self._is_already_ranked(batch):
                self._logger.info('Already ranked, waiting for revision change')
                self._meta_model.wait_revision_change()

            examples = list(map(lambda item: item['example'], batch))
            # When calling synchronized objects, we should use batched versions of methods
            # to minimize number of locks.
            self._ranked_example_pool.add_batch(self._meta_model.rank_batch(examples))

    def _is_already_ranked(self, batch):
        """Pessimistically checks whether a batch was already ranked
        by the current meta model's revision by looking at the first element."""
        batch_epoch = batch[0]['epoch']
        batch_index = batch[0]['index']
        if self._model_rev != self._meta_model.revision:
            self._model_rev = self._meta_model.revision
            self._rev_start_epoch = batch_epoch
            self._rev_start_index = batch_index

        # We assume that number of examples in epoch does not change,
        # so once we reach the same example index using the same revision of meta model
        # we consider all subsequent examples to be processed.
        return (batch_epoch > (self._rev_start_epoch + 1)) or \
               (batch_epoch == (self._rev_start_epoch + 1) and batch_index > self._rev_start_index)

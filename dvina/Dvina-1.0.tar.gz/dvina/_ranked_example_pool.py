import abc
from future.utils import with_metaclass


class RankedExamplePool(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def sample(self, n_batch=1):
        """
        Returns which examples need to be labeled
        Parameters
        ----------
        n_batch
            Number of examples to return
        Returns
        -------
            Tuple: ids of examples and probabilities with which the example has been sampled
        """
        pass

    @abc.abstractmethod
    def add_batch(self, ranked_examples):
        """
        Add batch of RankedExamples to the pool, to enable further sampling
        Parameters
        ----------
        ranked_examples: `list` oif `RankedExample`
        """
        pass

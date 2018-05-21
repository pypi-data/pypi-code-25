import abc
from future.utils import with_metaclass


class DataProcessor(with_metaclass(abc.ABCMeta, object)):
    """An abstract class which can be used as a parent for data processors: classes for processing example attributes
    into features. It is an iterable over processed examples containing `features` field with feature arrays."""

    @abc.abstractmethod
    def fit(self, examples):
        """
           Given an iterator over unprocessed examples, computes statistics required to perform data processing.

       Parameters
       ----------
       examples : list
           List of examples
       """

    @abc.abstractmethod
    def __iter__(self):
        """Makes an iterator

        Returns
        -------
            An iterator over processed examples (with 'features' field).
        """

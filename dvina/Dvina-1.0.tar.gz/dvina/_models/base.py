import abc
from future.utils import with_metaclass


class BatchModel(with_metaclass(abc.ABCMeta, object)):
    """Base class for Active Learning Models. Not Thread-safe."""
    @abc.abstractmethod
    def train(self, labeled_examples):
        """Re-trains the model with passed labeled examples.

        Parameters
        ----------
        labeled_examples: :obj:`list` of :obj:`LabeledExample`

        """

    @abc.abstractmethod
    def is_trained(self):
        """Says whether the model is trained. Once the model entered the trained state,
        it should remain trained.

        Returns
        -------
        bool
            True if trained, False otherwise.


        """


class SequentialModel(with_metaclass(abc.ABCMeta, object)):
    """Base class for Active Learning Models. Not Thread-safe."""
    @abc.abstractmethod
    def partial_train(self, example, label):
        """Incremental train of the model

        Parameters
        ----------
        example: Example

        label: Label

        """

    @classmethod
    def __subclasshook__(cls, subclass):
        return callable(getattr(subclass, 'partial_train', None))


class EvaluationModel(BatchModel):
    @abc.abstractmethod
    def evaluate(self, labeled_examples=None):
        """"Evaluates performance on the dataset of examples. If dataset is not passed,
        evaluates on already labeled examples provided the right evaluator type

        Parameters
        ----------
        labeled_examples: :obj:`list` of :obj:`LabeledExample`

        Returns
        -------
        float

        """


class ActiveLearningModel(BatchModel):
    @abc.abstractmethod
    def get_confidence(self, examples):
        """Returns non-normalized confidence for the passed examples.

        Parameters
        ----------
        examples: List of examples

        Returns
        -------
        list
            List of floats indicating how confident the model is about the examples.
        """

    @abc.abstractmethod
    def needs_serialized(self):
        """Returns a boolean indicating whether this type of al model has state that needs persisted.

        Returns
        -------
        bool
            true if the model has state that needs persisted by serializing the model. otherwise, false
        """

class LabelingModel(BatchModel):
    @abc.abstractmethod
    def label(self, examples):
        """Labels example.

        Parameters
        ----------
        examples: List of Examples

        Returns
        -------
        labels: list of labels
        confidences: list of confidences

        """

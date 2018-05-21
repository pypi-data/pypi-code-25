import logging
import numpy as np
from sklearn.metrics import accuracy_score

from .base import EvaluationModel, LabelingModel
from .. import _utils as utils


class StandardEvaluator(EvaluationModel):
    def __init__(self, labeling_model, min_examples_for_eval=30, compute_performance_func=accuracy_score):
        if not isinstance(labeling_model, LabelingModel):
            raise ValueError(
                "labeling_model should be an instance of LabelingModel, "
                "received {0} instead".format(type(labeling_model)))
        self._labeling_model = labeling_model
        self._min_examples_for_eval = min_examples_for_eval
        if not callable(compute_performance_func):
            raise TypeError("compute_performance_func should be callable")
        self._compute_performance_func = compute_performance_func
        self._logger = logging.getLogger(__name__)

    def evaluate(self, labeled_examples):
        if labeled_examples is None:
            raise ValueError("StandardEvaluator requires examples for evaluation, but None provided")

        self._logger.info('Evaluating with provided examples')
        if (len(labeled_examples) < self._min_examples_for_eval) or (
                not self._labeling_model.is_trained()):
            # return nan performance as there is not enough instances to properly evaluate
            return np.nan

        labels = utils.get_fields_as_arrays(labeled_examples, ['label'])['label']

        predictions, confidence = self._labeling_model.label(labeled_examples)
        performance = self._compute_performance_func(labels, predictions)

        return performance

    def train(self, labeled_examples):
        pass

    def is_trained(self):
        return True

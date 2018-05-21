import numpy as np
import logging
from copy import deepcopy
from sklearn.metrics import accuracy_score
from sklearn.model_selection import KFold

from .base import EvaluationModel, LabelingModel
from .. import _utils as utils


class OfflineEvaluator(EvaluationModel):
    def __init__(self, labeling_model, labeled_examples=None,
                 min_examples_for_eval=30, compute_performance_func=accuracy_score,
                 n_splits=3,
                 seed=42):
        if not isinstance(labeling_model, LabelingModel):
            raise ValueError(
                "labeling_model should be an instance of LabelingModel, "
                "received {0} instead".format(type(labeling_model)))

        self._labeling_model = labeling_model
        self._min_examples_for_eval = min_examples_for_eval
        if not callable(compute_performance_func):
            raise TypeError("compute_performance_func should be callable")
        self._compute_performance_func = compute_performance_func
        self._n_splits = n_splits
        self._random = np.random.RandomState(seed)
        if labeled_examples is None:
            self._labeled_examples = []
        else:
            self._labeled_examples = labeled_examples

        self._logger = logging.getLogger(__name__)

    def evaluate(self, labeled_examples=None):
        # if examples are provided, just evaluate on them the currently trained model
        if labeled_examples is not None:
            self._logger.info('Evaluating with provided examples')
            valid_examples = self._filter_valid_examples(labeled_examples)
            return self._calculate_model_performance_on_set(self._labeling_model, valid_examples)

        self._logger.info('Evaluating with with cross-validation')
        # otherwise, run cross-validation-style evaluation
        valid_examples = self._filter_valid_examples(self._labeled_examples)

        performances = np.array([np.nan] * self._n_splits)
        kf = KFold(n_splits=self._n_splits, random_state=self._random.seed())

        if len(valid_examples) < self._n_splits:
            self._logger.info('Will not split for evaluation as there is only {0} examples but required {1} splits '
                              ''.format(len(valid_examples), self._n_splits))
            return np.nan

        split_ind = kf.split(valid_examples)
        for si, (train_indices, test_indices) in enumerate(split_ind):
            train_examples = [valid_examples[i] for i in train_indices]
            test_examples = [valid_examples[i] for i in test_indices]
            cur_model = deepcopy(self._labeling_model)
            cur_model.train(train_examples)

            performances[si] = self._calculate_model_performance_on_set(cur_model, test_examples)

        return np.mean(performances)

    def train(self, labeled_examples):
        pass

    def is_trained(self):
        return True

    def _calculate_model_performance_on_set(self, model, examples):
        if (len(examples) < self._min_examples_for_eval) or (
                not self._labeling_model.is_trained()):
            self._logger.info('Skipping evaluation as there is only {0} examples but required {1}, or model '
                              'is not trained'.format(len(examples), self._min_examples_for_eval))
            # return nan performance as there is not enough instances to properly evaluate
            return np.nan

        predictions, _ = model.label(examples)
        fields = utils.get_fields_as_arrays(examples, ['label', 'sampling_probability'])
        labels = fields['label']

        sampling_probabilities = fields['sampling_probability']
        return self._compute_performance_func(labels, predictions, sample_weight=1.0 / sampling_probabilities)

    def _filter_valid_examples(self, examples):
        valid_examples = []
        for example in examples:
            if 0 < getattr(example, 'sampling_probability') < 1:
                valid_examples.append(example)
            else:
                self._logger.debug("Skipping example {0} as it doesn't have valid sampling_probability".
                                   format(example))

        return valid_examples

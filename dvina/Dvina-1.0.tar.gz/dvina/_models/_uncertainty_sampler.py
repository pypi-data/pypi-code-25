import numpy as np
from copy import deepcopy
from .. import _utils as utils
from .base import ActiveLearningModel


class UncertaintySampler(ActiveLearningModel):
    def __init__(self, labeling_model, seed=42, uncertainty_measure='Margin', eps=1e-5):
        self._labeling_model = labeling_model
        self._random = np.random.RandomState(seed)
        self._eps = eps

        self._uncertainty_measure = uncertainty_measure
        self._init_certainty_measure(self._uncertainty_measure)

    def get_confidence(self, examples):
        if len(examples) == 0:
            return []
        _, probabilities = self._labeling_model.label(examples)

        confidence = self.get_certainty(probabilities)

        return confidence

    def train(self, labeled_examples):
        pass

    def is_trained(self):
        return self._labeling_model.is_trained()

    def _prob_to_exam_class_matrix(self, prob_):
        if prob_.ndim > 2:
            # if multilabel, take probability of the positive
            return prob_[:, 1, :]

        return prob_

    def _get_certainty_from_prediction(self, prob_):
        prob = self._prob_to_exam_class_matrix(prob_)
        return np.amax(prob, axis=1)  # take probability of most confident class

    def _get_certainty_from_margin(self, prob_):
        prob = self._prob_to_exam_class_matrix(prob_)
        # in every row, sort predicted probabilities (we don't care about which specific class is predicted)
        prob_sorted = np.sort(prob, axis=1)
        # the larger the difference between the most confident prediction, and the next one,
        # the more certain the classifier is
        certainty = prob_sorted[:, -1] - prob_sorted[:, -2]
        return certainty

    def _get_certainty_from_entropy(self, prob_):
        prob = self._prob_to_exam_class_matrix(prob_)
        # smooth probabilities (no 0 or 1 probabilities)
        prob = utils.smooth_probabilities(prob, self._eps)
        entropy = -np.sum(prob * np.log(prob), axis=1)
        return -entropy

    # this measure works for multi-label classifiers (Li and Guo, 2013)
    def _get_certainty_from_ml_margin(self, prob):
        # dimensions (2 in case binary or multiclass), more for multilabel,
        # need to take all except the one across examples
        dimensions = tuple(np.arange(1, prob.ndim))

        prob_pos = deepcopy(prob)
        prob_pos[prob_pos < 0.5] = np.inf

        min_pos = np.min(prob_pos, axis=dimensions)
        min_pos[min_pos == np.inf] = 0

        prob_neg = deepcopy(prob)
        prob_neg[prob_neg > 0.5] = -np.inf
        max_neg = np.max(prob_neg, axis=dimensions)
        max_neg[max_neg == -np.inf] = 0

        # add 0.5 to make certainty positive
        certainty = min_pos - max_neg + 0.5
        return certainty

    def _init_certainty_measure(self, uncertainty_measure):
        if uncertainty_measure == 'LeastConfident':
            self.get_certainty = self._get_certainty_from_prediction
        elif uncertainty_measure == 'Margin':
            self.get_certainty = self._get_certainty_from_margin
        elif uncertainty_measure == 'Entropy':
            self.get_certainty = self._get_certainty_from_entropy
        elif uncertainty_measure == 'MLMargin':
            self.get_certainty = self._get_certainty_from_ml_margin
        else:
            raise ValueError('Undefined uncertainty measure {0}'.format(uncertainty_measure))

    def needs_serialized(self):
        return False

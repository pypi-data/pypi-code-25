import logging
import numpy as np
from copy import deepcopy, copy

from sklearn.linear_model import SGDClassifier

from .. import _utils as utils
from .._utils.serialization import DvinaSerialization
from .base import ActiveLearningModel


@DvinaSerialization.serializes(["_clf_base", "_random", "_eps", "_num_classes", "_committee_size",
                               "_vote_type", "_predictors", "_is_trained"])
class QBCSampler(ActiveLearningModel):
    def __init__(self, clf_base=None, seed=42, num_classes=2, committee_size=7, vote_type='soft', eps=1e-5):
        if clf_base is None:
            # non-mutable default value
            self._clf_base = SGDClassifier(loss='log', penalty='l2',
                                           alpha=1e-4, max_iter=100, random_state=42, n_jobs=-1)
        else:
            self._clf_base = copy(clf_base)

        self._random = np.random.RandomState(seed)
        self._eps = eps
        self._num_classes = num_classes
        self._committee_size = committee_size
        self._vote_type = vote_type

        # this is the committee of the classifiers
        self._predictors = []
        self._is_trained = False
        self.deserialized_init()

    def deserialized_init(self):
        self._init_vote_type(self._vote_type)
        self._logger = logging.getLogger(__name__)

    def is_trained(self):
        return self._is_trained

    def train(self, labeled_examples):
        """
        This function trains committee predictors on the dataset
        and updates internal predictors array with the newly trained predictors
        If training is not possible, issue a warning and return. is_trained will be false
        Parameters
        ----------
        labeled_examples: :obj:`list` of :obj:`LabeledExample`
        """
        self._logger.info('Training ')
        fields = utils.get_fields_as_arrays(labeled_examples, ['features', 'label'])
        X = fields['features']
        labels = fields['label']

        if labels.ndim > 2:
            raise NotImplementedError("Multilabel classification is not supported by QBCSampler")

        if len(np.unique(labels)) > self._num_classes:
            # not testing for less, as this training set might only be part of the dataset
            raise ValueError("Passed dataset with more classes than declared, unique labels are: {0}".
                             format(np.unique(labels)))

        # train the committee on a sample of the training set
        n_examples = X.shape[0]
        self._predictors = []
        for _ in np.arange(self._committee_size):
            pred = deepcopy(self._clf_base)
            idx = [self._random.randint(0, n_examples) for _ in range(n_examples)]
            if not self._is_training_possible(labels[idx]):
                self._logger.warning('Training is skipped because labels are not suitable')
                return
            X_tr = X[idx, :]
            y_tr = labels[idx]

            pred.fit(X_tr, y_tr)
            self._predictors.append(pred)
        self._is_trained = True

    def get_confidence(self, examples):
        if len(examples) == 0:
            return []
        X = utils.get_fields_as_arrays(examples, ['features'])['features']
        # in QBC, high scores and probabilities indicate which examples should be sampled,
        # thus reversing to be consistent across other models
        return -self._get_committee_scores(X=X)

    def _get_committee_scores(self, **kwargs):
        """
        Get committee scores on the unlabeled examples
        :param kwargs: should have X: the matrix of unlabeled examples
        :return: scores
        """
        X = kwargs['X']

        n = X.shape[0]
        # if committee wasn't fit yet, get random ordering
        if not self.is_trained():
            # get random scores
            return self._random.rand(n)

        # as sometimes not all classes will be in training set, we need to realign predictions
        prob = np.zeros([n, self._num_classes, self._committee_size])
        for m in range(self._committee_size):
            pred = self._predictors[m]
            classes_ind = pred.classes_.astype(int)
            prob[:, classes_ind, m] = pred.predict_proba(X)

        # get scores
        scores = self._point_scorer(prob)

        return scores

    def _hard_vote_scorer(self, prob):
        """
        we expect a 3-dimensional matrix of prob with size[num_examples, num_classes, num_predictors]
        for the hard vote we select with the argmax on the prob in vote entropy calculation
        :param prob: probabilities
        :return: consensus scores
        """
        hv = np.zeros([prob.shape[0], prob.shape[1]])
        predicted_classes = np.argmax(prob, axis=1)
        for cl in np.arange(prob.shape[1]):
            hv[:, cl] = np.mean(predicted_classes == cl, axis=1)

        consensus_prob = utils.smooth_probabilities(hv, self._eps)
        vote_entropy = -np.sum(consensus_prob * np.log(consensus_prob), axis=1)
        return vote_entropy

    def _soft_vote_scorer(self, prob):
        """
        we expect a 3-dimensional matrix of prob with size[num_examples, num_classes, num_predictors]
        for the soft vote we calculate entropy of the votes considering members' confidence
        :param prob: probabilities
        :return: consensus scores
        """
        prob = utils.smooth_probabilities(prob, self._eps)
        consensus_prob = np.mean(prob, axis=2)
        vote_entropy = -np.sum(consensus_prob * np.log(consensus_prob), axis=1)
        return vote_entropy

    def _kl_scorer(self, prob):
        """
        we expect a 3-dimensional matrix of prob with size[num_examples, num_classes, num_predictors]
        for the kl vote we look at the kl divergence between the members' probabilities and the consensus
        :param prob: probabilities
        :return: consensus scores
        """
        prob = utils.smooth_probabilities(prob, self._eps)
        consensus_prob = np.mean(prob, axis=2)
        cons_broadcast = np.repeat(np.expand_dims(consensus_prob, axis=2), self._committee_size, axis=2)
        return np.mean(np.sum(prob * np.log(prob / cons_broadcast), axis=1), axis=1)

    def _init_vote_type(self, vote_type):
        # decide which kind of voting schema to use in the committee - more can be added
        if vote_type == 'soft':
            self._point_scorer = self._soft_vote_scorer
        elif vote_type == 'hard':
            self._point_scorer = self._hard_vote_scorer
        elif vote_type == 'kl':
            self._point_scorer = self._kl_scorer
        else:
            raise ValueError('Undefined scoring schema', vote_type)

    @staticmethod
    def _is_training_possible(labels):
        if labels.size < 1:
            return False

        if len(np.unique(labels)) < 2:
            return False

        return True

    def needs_serialized(self):
        return True

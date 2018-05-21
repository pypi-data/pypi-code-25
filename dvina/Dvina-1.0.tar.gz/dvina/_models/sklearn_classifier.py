import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.utils import validation
from sklearn.multioutput import MultiOutputClassifier
from copy import deepcopy

from .._utils.serialization import DvinaSerialization
from .base import LabelingModel
import dvina._utils as utils


@DvinaSerialization.serializes(["_classifier", "_is_trained", "_present_classes"])
class SklearnClassifier(LabelingModel):
    def __init__(self, classifier=None, is_trained=False):
        """
        Initializes SklearnClassifier

        Parameters
        ----------
        classifier: object
            A classifier from scikit-learn family
        is_trained: bool
            Whether the passed classifier has been trained previously
        """
        if classifier is None:
            self._classifier = SGDClassifier(loss='log', penalty='l2',
                                             alpha=1e-4, max_iter=100, random_state=42, n_jobs=-1)
            self._is_trained = False
        else:
            self._classifier = deepcopy(classifier)
            self._is_trained = is_trained

        # this variable contains a binary numpy array indicating which of the classes were present during training
        # of the method, for multilabel classification
        self._present_classes = None

    def train(self, labeled_examples):
        """Re-trains the model with passed labeled examples.

        Parameters
        ----------
        labeled_examples: :obj:`list` of :obj:`LabeledExample`
        
        Returns
        -------
        bool
            True if trained or False otherwise
        """
        fields = utils.get_fields_as_arrays(labeled_examples, ['features', 'label'])
        X = fields['features']
        labels = fields['label']
        is_many_classes = labels.ndim > 1 and labels.shape[1] > 1
        if is_many_classes:
            labels, self._present_classes = utils.clean_multilabels(labels)

        if self._is_training_possible(labels):
            self._classifier.fit(X, labels)
            self._is_trained = True
            return True

        return False

    def label(self, examples):
        X = utils.get_fields_as_arrays(examples, ['features'])['features']
        labels = self._classifier.predict(X)
        if isinstance(self._classifier, MultiOutputClassifier):
            # MultiOutputClassifier has a bug where it doesn't check for the right thing (starting with Scikit 0.19)
            # https://github.com/scikit-learn/scikit-learn/issues/10113
            # so we need to do this workaround
            validation.check_is_fitted(self._classifier, 'estimators_')
            confidences = np.dstack([estimator.predict_proba(X) for estimator in self._classifier.estimators_])
        else:
            confidences = self._classifier.predict_proba(X)

        if self._present_classes is not None:
            # if multilabel, and not all classes were present during fitting, need to reshape labels and confidences
            # to match the original shapes
            labels_ = np.zeros([labels.shape[0], self._present_classes.size])
            confidences_ = np.zeros([confidences.shape[0], 2, self._present_classes.size])

            if np.any(self._present_classes):
                labels_[:, self._present_classes] = labels
                confidences_[:, :, self._present_classes] = confidences

            return labels_, confidences_

        return labels, confidences

    def classifier(self):
        return self._classifier

    def is_trained(self):
        """
        Checks if the model has been fitted
        Returns
        -------
        bool
            True if trained or False otherwise
        """
        return self._is_trained

    @property
    def classifier(self):
        return self._classifier

    @staticmethod
    def _is_training_possible(labels):
        if labels.size < 1:
            return False

        if len(np.unique(labels)) < 2:
            return False

        return True

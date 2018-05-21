import unicodedata as ucd
from builtins import str

import logging
import numpy as np
import scipy
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer, StandardScaler, OneHotEncoder
from ._utils.serialization import DvinaSerialization

from . import _utils as utils
from .data_processor import DataProcessor


@DvinaSerialization.serializes(["_raw_examples", "_attributes", "numerical_transformer", "categorical_transformer",
                               "text_transformer"])
class BasicDataProcessor(DataProcessor):
    """Provides basic functionality for data processing. Results in an iterable over :term:`processed example`-s,
    with the `features` field."""
    def __init__(self, raw_examples, attributes={}, transformers={}):
        """
        Parameters
        ----------
        raw_examples : Iterable object over :term:`unprocessed example`-s
            Iterable over the dataset of examples which needs to be processed
        attributes : dict
            Dictionary with three keys: `numerical_attributes`, `categorical_attributes`, and `text_attributes`.
            The values are lists of strings: names of the attributes in the `raw_examples` dictionary
        transfomers : dict
            Dictionary with three keys: `numerical_transformer`: `StandardScaler()` from Scikit-learn by default.
            `categorical_transformer`: `OneHotEncoder()` from Scikit-learn by default.  `text_transformer`:
            `Pipeline([('vect', HashingVectorizer(n_features=2 ** 16)), 'normalized', Normalizer())])`
            from Scikit-learn by default
        """
        self._raw_examples = raw_examples
        self._attributes = attributes
        self._init_transformers(**transformers)
        self.deserialized_init()

    def deserialized_init(self):
        self._init_attributes(**self._attributes)
        self._logger = logging.getLogger(__name__)

    def fit(self, examples):
        """
        Fits a data processing pipeline.
        It stores all the provided dataset in memory, as it needs to fit the pipeline to the whole data

        Parameters
        ----------
        examples : iterable
            An iterable object which contains :term:`unprocessed example`-s
        """
        self._logger.info('Starting fitting')
        # right now, we only support one text attribute
        fields = utils.get_fields_as_arrays(examples,
                                            self.numerical_attributes +
                                            self.categorical_attributes +
                                            self.text_attributes)

        if len(self.categorical_attributes) > 0:
            examples_with_att = np.array([fields[attribute] for attribute in self.categorical_attributes])
            examples_with_att.shape = (-1, len(self.categorical_attributes))
            self.categorical_transformer.fit(examples_with_att)
        if len(self.numerical_attributes) > 0:
            examples_with_att = np.array([fields[attribute] for attribute in self.numerical_attributes])
            examples_with_att.shape = (-1, len(self.numerical_attributes))
            self.numerical_transformer.fit(examples_with_att)
        if len(self.text_attributes) > 0:
            text_attribute = self._clean_text_features(
                [fields[attribute] for attribute in self.text_attributes])
            self.text_transformer.fit(text_attribute)

    def __iter__(self):
        for example in self._raw_examples:
            X = np.array([])
            X = self._transform_attributes_of_one_example(
                np.array([example[attribute] for attribute in self.categorical_attributes]).reshape(1, -1),
                self.categorical_transformer,
                X)
            X = self._transform_attributes_of_one_example(
                np.array([example[attribute] for attribute in self.numerical_attributes]).reshape(1, -1),
                self.numerical_transformer,
                X)
            if len(self.text_attributes) > 0:
                text_attribute = self._clean_text_features(
                    [example[attribute] for attribute in self.text_attributes])
                X = self._transform_attributes_of_one_example(
                    np.array([text_attribute]),
                    self.text_transformer,
                    X)
            example['features'] = X
            yield example

    def _init_transformers(self, numerical_transformer=None, categorical_transformer=None, text_transformer=None):
        self.numerical_transformer = StandardScaler() if numerical_transformer is None else numerical_transformer
        self.categorical_transformer = OneHotEncoder() if categorical_transformer is None else categorical_transformer
        self.text_transformer = Pipeline([('vect', HashingVectorizer(n_features=2 ** 16)),
                                          ('normalized', Normalizer())]) \
            if text_transformer is None else text_transformer

    def _init_attributes(self,
                         numerical_attributes=[],
                         categorical_attributes=[],
                         text_attributes=[]):

        self.numerical_attributes = numerical_attributes
        self.categorical_attributes = categorical_attributes
        self.text_attributes = text_attributes

    @staticmethod
    def _transform_attributes_of_one_example(array_of_attributes, transformer, X):
        if array_of_attributes.size > 0:
            X_current = transformer.transform(array_of_attributes)
            # if other features were present, need to concatenate
            if X.shape[0] > 0:
                # need to reshape to a row two-dimensional vector
                # to correctly concatenate as numpy considers it a one-dimensional vector
                if isinstance(X_current, np.ndarray):
                    X_current.reshape((X.shape[0], -1))
                if isinstance(X, scipy.sparse.csr_matrix) or isinstance(X_current, scipy.sparse.csr_matrix):
                    # if any of the matrices are sparse, use scipy concatenation
                    X = scipy.sparse.hstack([X, X_current])
                    # because scipy has many sparse formats, need to convert to csr
                    X = scipy.sparse.csr_matrix(X)
                else:
                    X = np.hstack((X, X_current))
            else:
                X = X_current

        return X

    @staticmethod
    def _clean_text_features(fields):
        """
        Takes a list of string fields, cleans every string, and concatenates them with a space
        :param fields: list of numpy arrays of strings
        :return: numpy array of concatenated cleaned strings
        """
        if len(fields) == 0:
            raise ValueError("Nothing to clean: {0}".format(fields))
        norm_func = np.vectorize(lambda x: ucd.normalize('NFKD', str(x)))
        cleaned_text = norm_func(fields[0])

        # if there is more than one field, concatenate
        for i in range(1, len(fields)):
            cleaned_text = np.core.defchararray.add(cleaned_text, " ")
            cur_text = norm_func(fields[i])
            cleaned_text = np.core.defchararray.add(cleaned_text, cur_text)

        return cleaned_text

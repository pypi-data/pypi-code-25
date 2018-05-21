import logging
from ._example_batch_pool import ExampleBatchPool
from ._ranked_pool_sampler import RankedPoolSampler
from ._ranked_pool_standard import RankedPoolStandard
from ._meta_model import MetaModel
from ._ranking_worker import RankingWorker
from ._example import Example, LabeledExample
from ._utils.serialization import DvinaSerialization
import jsonpickle


@DvinaSerialization.serializes(["_examples", "_batch_pool", "_meta_model", "_synchronous", "_ranked_example_pool"])
class ActiveLabeler(object):
    """This is the main class of the package. It is responsible for creating models, processing examples into
    internal representation, as well as provides the main public APIs.
    """
    def __init__(self, examples, ranker={}, models={}, batch_pool={}, synchronous=False):
        """
        Parameters
        ----------
        examples : iterable over :term:`example`-s.
            The collection of examples makes the dataset which needs to be annotated.
        ranker : dict, optional
            Configuration parameters for the ranker
        models : dict, optional
            Configuration parameters for the models
        batch_pool : dict, optional
            Configuration parameters for the ``ExampleBatchPool``
        synchronous : bool, optional
            Whether to run :func:`next_examples` and :func:`add_labeled` synchronously. If True, :func:`next_examples`
            will wait until training finished and all the examples have been ranked
        Raises
        ------
        KeyError
            If one of the examples in the dataset does not contain ``id`` or ``features`` field
        AssertionError
            If ``features`` field of one of the examples is not of ``scipy.sparse.spmatrix`` type
        """
        self._examples = examples
        self._batch_pool = batch_pool
        self._meta_model = MetaModel(**models)
        self._synchronous = synchronous
        self._ranked_example_pool = self._create_ranked_pool(**ranker)
        self.deserialized_init()

    def deserialized_init(self):
        self._logger = logging.getLogger(__name__)
        self._example_batch_pool = ExampleBatchPool(self._examples, **self._batch_pool)

    def start(self):
        """
        Called on a constructed or deserialized instance to perform runtime initialization (setting a logger)
        and starting threads.
        Returns
        -------
        ActiveLabeler
            the active labeler instance
        """
        self._logger.info('Created all models and starting worker')
        self._worker = RankingWorker().start(self._meta_model, self._example_batch_pool, self._ranked_example_pool)
        return self

    def __enter__(self):
        """
        __enter__ and exit are convenience methods and are called if the user creates an active labeler in a with
        context.
        Example: 'with ActiveLabeler() as labeler:'
        :return: a started active labeler instance
        """
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def next_examples(self, n_batch=1):
        """
        Provides ids and sampling probabilities for the next examples which need to be manually annotated.
        Sampling probabilities need to be added as fields to the :term:`labeled example`-s
        used into :func:`add_labeled`.

        Parameters
        ----------
        n_batch : int, optional
            Size of the batch of how many examples need to be provided

        Returns
        -------
        tuple of two lists
            Tuple of lists, the first element is a list of example ids which need to be manually annotated.
            The second element is a list of sampling probabilities with which these ids were selected.

        Raises
        ------
        StopIteration
            If there is more examples requested than there are in the pool.
            This can happen either because not enough examples have yet been added,
            or because most of the examples have been provided with the previous calls to this function.
        """
        self._logger.info('Getting next examples')
        if self._synchronous:
            self._meta_model.wait_done_previous_revision()
        return self._ranked_example_pool.sample(n_batch)

    def add_labeled(self, labeled_examples):
        """
        Adds labeled examples to the models. Trains all the models on these and previously labeled examples.
        Keeps all previously labeled examples in memory. For multiclass classification, 
        number of unique values of the labels in all the examples fed so far determines the number of classes. 
        
        Note that only Random and Uncertainty Samplers support multilabel classification, 
        QBCSampler does not support it. 
        Moreover, for multilabel, 
        it is important to use MLMargin uncertainty_measure in UncertaintySampler, 
        otherwise performance can be much worse than random sampling 

        Parameters
        ----------
        labeled_examples : list of :term:`labeled example`-s
            List of labeled examples to add to the model. Label in every :term:`labeled example` 
            should be a whole number float or a numpy array of 0s and 1s for multilabel classification. 
        """
        self._logger.info('Adding labeled examples')
        converted_examples = list(self._iter_validated_and_converted_examples(labeled_examples, labeled=True))
        self._meta_model.train(converted_examples)

    def label(self, examples):
        """
        Automatically labels the dataset of :term:`example`-s. Loops through examples only once.
        This method calls the pre-built model to predict labels on the provided examples.
         
        Parameters
        ----------
        examples : iterable over examples

        Returns
        -------
        tuple of two lists
            Tuple of lists, the first element is a list of labels.
            The second element is a list of confidences. Every confidence is a row of probabilities,
            with every element in the row corresponds to the predicted probability of one of the classes. 
            For the multiclass case, the order of the classes corresponds to the sorted order of the classes fed into
            :func:`add_labeled`. For example, if there are three labeled examples with labels 0.0, 1.0, -3.0, the first
            element in the confidence row is the confidence of the class -3.0, the second one is the confidence of the 
            class 0.0, and the third one is the confidence of the class 1.0
        """
        self._logger.info('Labeling examples')
        converted_examples = self._iter_validated_and_converted_examples(examples, labeled=False)
        labels, confidences = self._meta_model.label(converted_examples)
        return labels, confidences

    def evaluate(self, examples=None):
        """
        Evaluates the labeling model.

        - If examples are provided and ``'Standard'`` evaluator is selected, performance metric is calculated on the
          provided examples.
        - If ``'Offline'`` evaluator is selected, offline evaluation procedure is performed. If
          examples are given, they are filtered to those which have applicable values of sampling_probability (stritly 
          between 0 and 1), and the performance metric is evaluated by weighing the examples with inverted 
          probabilities. 
        - If examples are not given with ``'Offline'`` evaluator, all labeled examples provided so far for training,
          are used in n-fold cross-validation with examples weighted with inverted probabilities. Note that if in any
          of the testing folds, there is not enough examples for evaluation, evaluate() will return np.nan.
          
        Note that Offline evaluation provides an estimate of the model's performance, by performing train/test 
        cross-validation on the train set, and with sampling bias correction during testing. Thus, it should provide
        reliable estimates after enough training data was passed to the model.

        Parameters
        ----------
        examples : list of :term:`labeled example`-s, optional
            List of labeled examples on which the model will be evaluated

        Returns
        -------
        float
            performance metric, or np.nan if evaluation is not possible

        Raises
        ------
        ValueError
            If 'Standard' evaluator is selected, but examples are not provided
        """
        self._logger.info('Evaluating')
        converted_examples = None
        if examples is not None:
            converted_examples = list(self._iter_validated_and_converted_examples(examples, labeled=True))
        return self._meta_model.evaluate(converted_examples)

    def get_labeling_model(self):
        """
        Gets labeling model
        Returns
        -------
        LabelingModel
            The model object
        """
        return self._meta_model.labeling_model

    def serialize(self):
        """
        :return: the active labeler's current state serialized as a json string
        """
        return jsonpickle.encode(self)

    @classmethod
    def deserialize(cls, json):
        """
        :param json: a json string previously returned from serialize()
        :return: an ActiveLabeler instance that has been initialized, but not started
        """
        return jsonpickle.decode(json)

    @staticmethod
    def _create_ranked_pool(ranker_name='Sampler', ranker_params={}):
        # choose evaluator
        if ranker_name == 'Sampler':
            ranker = RankedPoolSampler(**ranker_params)
        elif ranker_name == 'Standard':
            ranker = RankedPoolStandard(**ranker_params)
        else:
            raise ValueError("Unknown ranker '{0}'".format(ranker_name))

        return ranker

    def _iter_validated_and_converted_examples(self, examples, labeled=False):
        for example in examples:
            if 'id' not in example:
                raise ValueError("Field 'id' is not in example {0}".format(example))
            if 'features' not in example:
                raise ValueError("Field 'features' is not in example {0}".format(example))
            if labeled:
                if 'label' not in example:
                    raise ValueError("Field 'label' is not in labeled example {0}".format(example))
                if 'sampling_probability' not in example:
                    self._logger.debug("Field 'sampling_probability' is not in labeled example {0}, using 1.0"
                                       .format(example))
            if not labeled:
                converted_example = Example(example['id'], example['features'])
            else:
                converted_example = LabeledExample(example['id'],
                                                   example['features'],
                                                   example['label'],
                                                   example.get('sampling_probability', 1.0))
            yield converted_example

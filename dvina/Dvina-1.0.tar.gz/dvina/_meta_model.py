import threading
import logging

from ._utils.serialization import DvinaSerialization
from ._models._standard_evaluator import StandardEvaluator
from ._models._offline_evaluator import OfflineEvaluator
from ._models._random_sampler import RandomSampler
from ._models._uncertainty_sampler import UncertaintySampler
from ._models._qbc_sampler import QBCSampler
from ._models import SklearnClassifier
from ._example import RankedExample
from ._models import SequentialModel, BatchModel


@DvinaSerialization.serializes(["_model", "_labeling_model", "_evaluation", "_fallback", "_revision",
                               "_labeled_examples", "_persisted_primary_al_model", "_persisted_fallback_al_model"])
class MetaModel(object):

    def __init__(self, model={}, labeler={}, evaluation={}, fallback={'model_name': 'Random'}):
        """Thread-safe abstraction above active learning model, labeler and evaluator.
        Parameters
        ----------
        model
            Active learning model params.
        labeler
            Labeling model params.
        evaluation
            Evaluation model params.
        fallback
            Params for an active learning model that is being used when main model is not yet trained.
        """
        self._model = model
        self._labeling_model = self._create_labeling_model(**labeler)
        self._evaluation = evaluation
        self._fallback = fallback
        self._revision = 0
        # Holds labeled examples
        self._labeled_examples = set()
        """
        The primary and fallback al models are one of three classes: RandomSampler, UncertaintySampler, or QBCSampler. 
        Only QBCSampler has state that changes after construction and needs (de)serialized.
        We can't always set the primary and fallback al model fields with deserialization.
        This is because the UncertaintySampler class uses a reference of the labeling_model instance (which is also 
        deserialized).
        """
        self._persisted_primary_al_model = None
        self._persisted_fallback_al_model = None
        self.deserialized_init()

    def deserialized_init(self):
        # TODO Change re-entrant lock to read write lock, once its in Brazil.
        # There is no need to add lock per model for higher granularity,
        # once we switch to ReadWriteLock. Because all models are trained together.
        self._lock = threading.RLock()
        # Used to implement waiting for the revision change.
        self._revision_cond = threading.Condition(self._lock)
        # Used to implement waiting for all revision changes to be done, not just training
        self._done_previous_revision_cond = threading.Condition(self._lock)
        # we do not create logger at the module level,
        # otherwise it can be created before configuration by the user is added.
        # Revision increases on every model update.
        self._waiting_previous_revision_done = True

        self._logger = logging.getLogger(__name__)

        # set the primary & fallback models to the deserialized instead or create a new instance
        self._primary_al_model = self._get_persisted_or_new_al_model(self._persisted_primary_al_model, self._model)
        self._fallback_al_model = self._get_persisted_or_new_al_model(self._persisted_fallback_al_model, self._fallback)
        # we'll persist the primary & fallback models if they have state
        self._persisted_primary_al_model = self._get_al_model_to_persist(self._primary_al_model)
        self._persisted_fallback_al_model = self._get_al_model_to_persist(self._fallback_al_model)

        self._evaluation_model = self._create_evaluation_model(**self._evaluation)

    def _get_persisted_or_new_al_model(self, persisted_model, model_config):
        """Method which helps with setting the primary and fallback al model instance variables.

        :param persisted_model: a primary or fallback al model which was restored from serialized data
        :param model_config: the primary or fallback al model config
        :return: the persisted model if it is present. otherwise we create and return a new model using the config
        """
        return persisted_model if persisted_model else self._create_al_model(**model_config)

    def _get_al_model_to_persist(self, model):
        """Method which helps with setting the persisted primary and fallback al model instance variables.

        :param model: the primary or fallback al model
        :return: the model if it has state that needs serialized. otherwise, None
        """
        return model if model.needs_serialized() else None

    def label(self, examples):
        """
        Labels all the provided examples with the current model
        Parameters
        ----------
        examples: :obj:`list` of :obj:`Example`

        Returns
        -------
            List of labels, and list of confidences
        """
        with self._lock:
            return self._labeling_model.label(examples)

    def train(self, examples):
        """
        Trains all the models with the examples provided. If some examples have been provided previously, those are
        filtered out
        Parameters
        ----------
        examples: :obj:`list` of :obj:`LabeledExample`
        """
        unseen_labeled_examples = []

        def train(model):
            if isinstance(model, SequentialModel):
                return model.partial_train(unseen_labeled_examples)
            elif isinstance(model, BatchModel):
                return model.train(self._labeled_examples)

        with self._lock:
            self._waiting_previous_revision_done = True
            self._labeled_examples.update(examples)

            if not train(self._labeling_model):
                self._logger.warning('Skipped model training because all labels are the same')

            list(map(train, [self._primary_al_model, self._fallback_al_model, self._evaluation_model]))

            self._revision += 1
            self._revision_cond.notifyAll()

    def rank_batch(self, examples):
        with self._lock:
            confidences = self._al_model.get_confidence(examples)
            ranked_examples = []
            for example, confidence in zip(examples, confidences):
                ranked_examples.append(RankedExample(example[0], example[1], confidence))

            return ranked_examples

    def evaluate(self, examples=None):
        self._logger.info('Starting model evaluation')
        with self._lock:
            return self._evaluation_model.evaluate(examples)

    @property
    def labeling_model(self):
        return self._labeling_model

    @property
    def revision(self):
        with self._lock:
            return self._revision

    @property
    def waiting_previous_revision_done(self):
        with self._lock:
            return self._waiting_previous_revision_done

    def wait_revision_change(self):
        # notify threads that they don't need to wait for previous revision anymore as it is done ranking
        with self._lock:
            self._waiting_previous_revision_done = False
            self._done_previous_revision_cond.notifyAll()

        with self._revision_cond:
            self._revision_cond.wait()

    def wait_done_previous_revision(self):
        with self._done_previous_revision_cond:
            self._logger.info('Choose to wait for revision change')
            # allow sampling only when MetaModel is done with the new revision and waiting for new revision change
            if self._waiting_previous_revision_done:
                self._done_previous_revision_cond.wait()

    @property
    def _al_model(self):
        """Points to a currently active active learning model.
        Initially it's a fallback model, but once the primary model was trained
        we switch to it.

        Returns
        -------
        ActiveLearningModel

        """
        if self._primary_al_model.is_trained():
            return self._primary_al_model
        else:
            self._logger.info('Active Learning Models is not fully trained yet. Using a fallback.')
            return self._fallback_al_model

    def _create_al_model(self, model_name='Uncertainty', model_params={}):
        """
        In this function, we initialize the Active Learning model
        We chose to implement selection by name to make sure we have better control over adding additional samplers
        to the library
        Parameters
        ----------
        model_name
            Name of the model
        model_params
            parameters of the model
        Returns
        -------
            ActiveLearningModel
        """
        # choose sampler
        if model_name == 'Random':
            sampler = RandomSampler(**model_params)
        elif model_name == 'Uncertainty':
            sampler = UncertaintySampler(self._labeling_model, **model_params)
        elif model_name == 'QBC':
            sampler = QBCSampler(**model_params)
        else:
            raise ValueError("Unknown sampler '{0}'".format(model_name))

        return sampler

    def _create_labeling_model(self, model=None):
        if model is None:
            return SklearnClassifier()
        return model

    def _create_evaluation_model(self, evaluator_type='Offline', evaluator_params={}):
        # choose evaluator
        if evaluator_type == 'Offline':
            evaluator = OfflineEvaluator(self._labeling_model, labeled_examples=self._labeled_examples,
                                         **evaluator_params)
        elif evaluator_type == 'Standard':
            evaluator = StandardEvaluator(self._labeling_model, **evaluator_params)
        else:
            raise ValueError("Unknown evaluator '{0}'".format(evaluator_type))

        return evaluator

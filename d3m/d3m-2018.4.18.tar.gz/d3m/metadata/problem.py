import json
import math
import typing

import numpy  # type: ignore
from sklearn import metrics, preprocessing  # type: ignore

from . import base
from d3m import exceptions, utils

__all__ = ('TaskType', 'TaskSubtype', 'PerformanceMetric', 'parse_problem_description')

# Comma because we unpack the list of validators returned from "load_schema_validators".
PROBLEM_SCHEMA_VALIDATOR, = utils.load_schema_validators(base.SCHEMAS_PATH, base.DEFINITIONS_JSON, ('problem.json',))

PROBLEM_SCHEMA_VERSION = 'https://metadata.datadrivendiscovery.org/schemas/v0/problem.json'

D3M_CURRENT_VERSION = '3.0'


class TaskTypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'classification': cls.CLASSIFICATION,  # type: ignore
            'regression': cls.REGRESSION,  # type: ignore
            'clustering': cls.CLUSTERING,  # type: ignore
            'linkPrediction': cls.LINK_PREDICTION,  # type: ignore
            'vertexNomination': cls.VERTEX_NOMINATION,  # type: ignore
            'communityDetection': cls.COMMUNITY_DETECTION,  # type: ignore
            'graphClustering': cls.GRAPH_CLUSTERING,  # type: ignore
            'graphMatching': cls.GRAPH_MATCHING,  # type: ignore
            'timeSeriesForecasting': cls.TIME_SERIES_FORECASTING,  # type: ignore
            'collaborativeFiltering': cls.COLLABORATIVE_FILTERING,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskTypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskType
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskType = utils.create_enum_from_json_schema_enum(
    'TaskType', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_type.oneOf[*].enum[*]',
    module=__name__, base_class=TaskTypeBase,
)


class TaskSubtypeBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            None: cls.NONE,  # type: ignore
            'binary': cls.BINARY,  # type: ignore
            'multiClass': cls.MULTICLASS,  # type: ignore
            'multiLabel': cls.MULTILABEL,  # type: ignore
            'univariate': cls.UNIVARIATE,  # type: ignore
            'multivariate': cls.MULTIVARIATE,  # type: ignore
            'overlapping': cls.OVERLAPPING,  # type: ignore
            'nonOverlapping': cls.NONOVERLAPPING,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'TaskSubtypeBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        TaskSubtype
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))


TaskSubtype = utils.create_enum_from_json_schema_enum(
    'TaskSubtype', base.DEFINITIONS_JSON,
    'definitions.problem.properties.task_subtype.oneOf[*].enum[*]',
    module=__name__, base_class=TaskSubtypeBase,
)

Truth = typing.TypeVar('Truth', bound=typing.Sequence)
Predictions = typing.TypeVar('Predictions', bound=typing.Sequence)


class PerformanceMetricBase:
    @classmethod
    def get_map(cls) -> dict:
        """
        Returns the map between JSON string and enum values.

        Returns
        -------
        dict
            The map.
        """

        return {
            'accuracy': cls.ACCURACY,  # type: ignore
            'f1': cls.F1,  # type: ignore
            'f1Micro': cls.F1_MICRO,  # type: ignore
            'f1Macro': cls.F1_MACRO,  # type: ignore
            'rocAuc': cls.ROC_AUC,  # type: ignore
            'rocAucMicro': cls.ROC_AUC_MICRO,  # type: ignore
            'rocAucMacro': cls.ROC_AUC_MACRO,  # type: ignore
            'meanSquaredError': cls.MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredError': cls.ROOT_MEAN_SQUARED_ERROR,  # type: ignore
            'rootMeanSquaredErrorAvg': cls.ROOT_MEAN_SQUARED_ERROR_AVG,  # type: ignore
            'meanAbsoluteError': cls.MEAN_ABSOLUTE_ERROR,  # type: ignore
            'rSquared': cls.R_SQUARED,  # type: ignore
            'normalizedMutualInformation': cls.NORMALIZED_MUTUAL_INFORMATION,  # type: ignore
            'jaccardSimilarityScore': cls.JACCARD_SIMILARITY_SCORE,  # type: ignore
            'precisionAtTopK': cls.PRECISION_AT_TOP_K,  # type: ignore
        }

    @classmethod
    def parse(cls, name: str) -> 'PerformanceMetricBase':
        """
        Converts JSON string into enum value.

        Parameters
        ----------
        name : str
            JSON string.

        Returns
        -------
        PerformanceMetric
            Enum value.
        """

        return cls.get_map()[name]

    def unparse(self) -> str:
        """
        Converts enum value to JSON string.

        Returns
        -------
        str
            JSON string.
        """

        for key, value in self.get_map().items():
            if self == value:
                return key

        raise exceptions.InvalidStateError("Cannot convert {self}.".format(self=self))

    def get_function(self) -> typing.Callable[..., float]:
        """
        Returns a function suitable for computing this metric.

        Some functions get extra parameters which should be provided as keyword arguments.

        Returns
        -------
        function
            A function with (y_true, y_pred, **kwargs) signature, returning float.
        """

        def binarize(y_true: Truth, y_score: Predictions, pos_label: str = None) -> typing.Tuple[Truth, Predictions]:
            label_binarizer = preprocessing.LabelBinarizer()

            y_true = label_binarizer.fit_transform(y_true)
            y_score = label_binarizer.transform(y_score)

            if pos_label is not None and label_binarizer.classes_[0] == pos_label:
                return 1 - y_true, 1 - y_score  # type: ignore
            else:
                return y_true, y_score

        def f1(y_true: Truth, y_pred: Predictions, *, pos_label: str = None) -> float:
            if pos_label is not None:
                return metrics.f1_score(y_true, y_pred, pos_label=pos_label)
            return metrics.f1_score(y_true, y_pred)

        def roc_auc(y_true: Truth, y_pred: Predictions, *, pos_label: str = None) -> float:
            if pos_label is not None:
                y_true, y_pred = binarize(y_true, y_pred, pos_label)
            return metrics.roc_auc_score(y_true, y_pred)

        def roc_auc_micro(y_true: Truth, y_pred: Predictions) -> float:
            y_true, y_pred = binarize(y_true, y_pred)
            return metrics.roc_auc_score(y_true, y_pred, average='micro')

        def roc_auc_macro(y_true: Truth, y_pred: Predictions) -> float:
            y_true, y_pred = binarize(y_true, y_pred)
            return metrics.roc_auc_score(y_true, y_pred, average='macro')

        def root_mean_squared_error_avg(y_true: Truth, y_pred: Predictions) -> float:
            error_sum = 0.0
            count = 0

            for y_t, y_p in zip(y_true, y_pred):  # type: ignore
                error_sum += math.sqrt(metrics.mean_squared_error([y_t], [y_p]))
                count += 1

            return error_sum / count

        def precision_at_top_k(y_true: Truth, y_pred: Predictions, *, k: int = 20) -> float:
            y_true = numpy.argsort(y_true)[::-1]
            y_pred = numpy.argsort(y_pred)[::-1]

            y_true = typing.cast(Truth, y_true[0:k])
            y_pred = typing.cast(Predictions, y_pred[0:k])

            return numpy.float(len(numpy.intersect1d(y_true, y_pred))) / k

        functions_map = {
            self.ACCURACY: lambda y_true, y_pred: metrics.accuracy_score(y_true, y_pred),  # type: ignore
            self.F1: f1,  # type: ignore
            self.F1_MICRO: lambda y_true, y_pred: metrics.f1_score(y_true, y_pred, average='micro'),  # type: ignore
            self.F1_MACRO: lambda y_true, y_pred: metrics.f1_score(y_true, y_pred, average='macro'),  # type: ignore
            self.ROC_AUC: roc_auc,  # type: ignore
            self.ROC_AUC_MICRO: roc_auc_micro,  # type: ignore
            self.ROC_AUC_MACRO: roc_auc_macro,  # type: ignore
            self.MEAN_SQUARED_ERROR: lambda y_true, y_pred: metrics.mean_squared_error(y_true, y_pred),  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR: lambda y_true, y_pred: math.sqrt(metrics.mean_squared_error(y_true, y_pred)),  # type: ignore
            self.ROOT_MEAN_SQUARED_ERROR_AVG: root_mean_squared_error_avg,  # type: ignore
            self.MEAN_ABSOLUTE_ERROR: lambda y_true, y_pred: metrics.mean_absolute_error(y_true, y_pred),  # type: ignore
            self.R_SQUARED: lambda y_true, y_pred: metrics.r2_score(y_true, y_pred),  # type: ignore
            self.NORMALIZED_MUTUAL_INFORMATION: lambda labels_true, labels_pred: metrics.normalized_mutual_info_score(labels_true, labels_pred),  # type: ignore
            self.JACCARD_SIMILARITY_SCORE: lambda y_true, y_pred: metrics.jaccard_similarity_score(y_true, y_pred),  # type: ignore
            self.PRECISION_AT_TOP_K: precision_at_top_k,  # type: ignore
        }

        if self not in functions_map:
            raise exceptions.NotSupportedError("Computing metric {metric} is not supported.".format(metric=self))

        return functions_map[self]  # type: ignore


PerformanceMetric = utils.create_enum_from_json_schema_enum(
    'PerformanceMetric', base.DEFINITIONS_JSON,
    'definitions.problem.properties.performance_metrics.items.oneOf[*].properties.metric.enum[*]',
    module=__name__, base_class=PerformanceMetricBase,
)


def parse_problem_description(problem_doc_path: str) -> dict:
    """
    Parses problem description according to ``problem.json`` metadata schema.

    It parses constants to enums when suitable.

    Parameters
    ----------
    problem_doc_path : str
        File path to the problem description (``problemDoc.json``).

    Returns
    -------
    dict
        A parsed problem description.
    """

    with open(problem_doc_path, 'r') as problem_doc_file:
        problem_doc = json.load(problem_doc_file)

    if problem_doc.get('about', {}).get('problemSchemaVersion', None) != D3M_CURRENT_VERSION:
        raise exceptions.NotSupportedVersionError("Only supporting problem descriptions whose schema version is {version}.".format(version=D3M_CURRENT_VERSION))

    # To be compatible with problem descriptions which do not adhere to the schema and have only one entry for data.
    if not isinstance(problem_doc['inputs']['data'], list):
        problem_doc['inputs']['data'] = [problem_doc['inputs']['data']]

    performance_metrics = []
    for performance_metric in problem_doc['inputs']['performanceMetrics']:
        params = {}

        # A special case, setting a default value.
        # See: https://gitlab.datadrivendiscovery.org/nist/nist_eval_output_validation_scoring/commit/6e3e6e2efe99c8210e5de5e17847a2f6e89b0c82
        if performance_metric['metric'] == 'f1':
            params['pos_label'] = performance_metric.get('pos_label', '1')

        # Future compatibility.
        # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/70
        if 'pos_label' in performance_metric:
            params['pos_label'] = performance_metric['pos_label']

        if 'K' in performance_metric:
            params['k'] = performance_metric['K']

        performance_metrics.append({
            'metric': PerformanceMetric.parse(performance_metric['metric']),
            'params': params,
        })

    inputs = []
    for data in problem_doc['inputs']['data']:
        targets = []
        for target in data['targets']:
            targets.append({
                'target_index': target['targetIndex'],
                'resource_id': target['resID'],
                'column_index': target['colIndex'],
                'column_name': target['colName'],
                # TODO: What exactly are those two fields? Commented out for now.
                #       See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/64
                # 'classes': target.get('classes', None),
                # 'clusters_number': target.get('numClusters', None)
            })

        problem_input = {
            'dataset_id': data['datasetID'],
        }

        if targets:
            problem_input['targets'] = targets

        inputs.append(problem_input)

    # "dataSplits" are not exposed because it is unclear for what it would be used.
    # It is mostly interesting to know how train/test split was made for evaluation.
    # See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/37
    #      https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/42
    description = {
        'schema': PROBLEM_SCHEMA_VERSION,
        'problem': {
            'id': problem_doc['about']['problemID'],
            # "problemVersion" is required by the schema, but we want to be compatible with problem
            # descriptions which do not adhere to the schema.
            'version': problem_doc['about'].get('problemVersion', '1.0'),
            'name': problem_doc['about']['problemName'],
            'task_type': TaskType.parse(problem_doc['about']['taskType']),
            'task_subtype': TaskSubtype.parse(problem_doc['about'].get('taskSubType', None)),
        },
        'outputs': {
            'predictions_file': problem_doc['expectedOutputs']['predictionsFile'],
        }
    }

    if performance_metrics:
        description['problem']['performance_metrics'] = performance_metrics  # type: ignore

    if problem_doc['about'].get('problemDescription', None):
        description['problem']['description'] = problem_doc['about']['problemDescription']  # type: ignore

    if inputs:
        description['inputs'] = inputs  # type: ignore

    if problem_doc['expectedOutputs'].get('scoresFile', None):
        description['outputs']['scores_file'] = problem_doc['expectedOutputs']['scoresFile']  # type: ignore

    PROBLEM_SCHEMA_VALIDATOR.validate(description)

    return description


if __name__ == '__main__':
    import pprint
    import sys

    for problem_doc_path in sys.argv[1:]:
        try:
            pprint.pprint(parse_problem_description(problem_doc_path))
        except Exception as error:
            raise Exception("Unable to parse problem description: {problem_doc_path}".format(problem_doc_path=problem_doc_path)) from error

# -*- encoding: utf-8 -*-
import pyspark

from .constants import CLASSIFICATION, REGRESSION, CORRELATION
from .constants import RANDOM_FOREST_CLASSIFIER, RANDOM_FOREST_REGRESSOR
from .exceptions import MismatchColumnNumberError, InvalidConfigError, MissingConfigError, MismatchTypeError

from sparkmlpipe.pipeline.classification import ClassificationPipelineBuilder
from sparkmlpipe.pipeline.regression import RegressionPipelineBuilder
from sparkmlpipe.stat.correlation import CorrelationBuilder


# general config file check
def verify_config(config):
    assert isinstance(config, dict)

    if 'data' not in config.keys():
        raise MissingConfigError('data')
    else:
        for key in ['location', 'header', 'types']:
            if key not in config['data'].keys():
                raise MissingConfigError('data.' + key)
        # check if header and types has the same size
        num_header_cols = len(config['data']['header'])
        num_types_cols = len(config['data']['types'])
        if num_header_cols != num_types_cols:
            raise MismatchColumnNumberError(num_header_cols, num_types_cols)

    if 'pipe' not in config.keys():
        raise MissingConfigError('pipe')
    else:
        for key in ['type', 'data_prep', 'feat_prep', 'model']:
            if key not in config['pipe'].keys():
                raise MissingConfigError('pipe.' + key)


def verify_input_dataset(config, data):
    num_conf_cols = len(config['data']['types'])
    num_data_cols = len(data.columns)

    if num_conf_cols > num_data_cols:
        raise MismatchColumnNumberError(num_conf_cols, num_data_cols)


def get_pipeline_builder(pipe_type):
    if pipe_type == CLASSIFICATION:
        return ClassificationPipelineBuilder
    elif pipe_type == REGRESSION:
        return RegressionPipelineBuilder
    elif pipe_type == CORRELATION:
        return CorrelationBuilder
    else:
        raise InvalidConfigError('pipe.type', pipe_type)


def fit_pipeline(pipeline, config, data, label_col):
    if isinstance(pipeline, pyspark.ml.Pipeline):
        pipe_type = config['pipe']['type']
        model_type = config['pipe']['model']['type']

        model_pipe = pipeline.fit(data)
        predictions = model_pipe.transform(data)

        y_true = None
        y_pred = None
        feature_importance = None

        # NOTE: toPandas() should only be used if the resulting Pandas's DataFrame is expected to be small,
        # as all the data is loaded into the driver's memory.
        if pipe_type == CLASSIFICATION:
            predictions_df = predictions.select(label_col, 'probability').toPandas()
            y_true = predictions_df[label_col]
            y_pred = [prob[1] for prob in predictions_df['probability']]

            if model_type == RANDOM_FOREST_CLASSIFIER:
                feature_importance = model_pipe.stages[-1].featureImportances
        elif pipe_type == REGRESSION:
            predictions_df = predictions.select(label_col, 'prediction').toPandas()
            y_true = predictions_df[label_col]
            y_pred = predictions_df['prediction']

            if model_type == RANDOM_FOREST_REGRESSOR:
                feature_importance = model_pipe.stages[-1].featureImportances
        else:
            raise InvalidConfigError('pipe.type', pipe_type)
    else:
        raise MismatchTypeError(type(pipeline), pyspark.ml.Pipeline)

    return model_pipe, y_true, y_pred, feature_importance

# -*- encoding: utf-8 -*-
from pyspark.ml.evaluation import RegressionEvaluator, MulticlassClassificationEvaluator

from .constants import CLASSIFICATION, REGRESSION, CORRELATION
from .constants import RANDOM_FOREST_CLASSIFIER, RANDOM_FOREST_REGRESSOR
from .exceptions import MismatchColumnNumberError, InvalidConfigError, MissingConfigError

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
        for key in ['type', 'data_prep', 'model']:
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
    pipe_type = config['pipe']['type']
    model_type = config['pipe']['model']['type']

    model_pipe = pipeline.fit(data)
    transformed_data = model_pipe.transform(data)
    metrics = {}
    feature_importances = None

    if pipe_type == CLASSIFICATION:
        evaluator = MulticlassClassificationEvaluator(predictionCol='prediction', labelCol=label_col)
        metrics['f1'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'f1'})
        metrics['weightedPrecision'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'weightedPrecision'})
        metrics['weightedRecall'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'weightedRecall'})
        metrics['accuracy'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'accuracy'})

        if model_type == RANDOM_FOREST_CLASSIFIER:
            feature_importances = model_pipe.stages[-1].featureImportances

    elif pipe_type == REGRESSION:
        evaluator = RegressionEvaluator(predictionCol="prediction", labelCol=label_col)
        metrics['rmse'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'rmse'})
        metrics['r2'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'r2'})
        metrics['mae'] = evaluator.evaluate(transformed_data, {evaluator.metricName: 'mae'})

        if model_type == RANDOM_FOREST_REGRESSOR:
            feature_importances = model_pipe.stages[-1].featureImportances
    else:
        raise InvalidConfigError('pipe.type', pipe_type)

    return model_pipe, metrics, feature_importances

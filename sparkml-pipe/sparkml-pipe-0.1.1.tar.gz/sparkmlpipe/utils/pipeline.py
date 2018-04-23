# -*- encoding: utf-8 -*-
from .constants import CLASSIFICATION, REGRESSION, CORRELATION
from .exceptions import MismatchColumnNumberError, InvalidConfigError, MissingConfigError

from sparkmlpipe.pipeline.classification import ClassificationPipelineBuilder
from sparkmlpipe.pipeline.regression import RegressionPipelineBuilder
from sparkmlpipe.stat.correlation import CorrelationBuilder


# TODO
def verify_config(config):
    assert isinstance(config, dict)

    if 'data' not in config.keys():
        raise MissingConfigError('data')
    else:
        for key in ['location', 'header', 'types']:
            if key not in config['data'].keys():
                raise MissingConfigError('data.' + key)


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

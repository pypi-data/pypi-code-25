# -*- encoding: utf-8 -*-
from .constants import CLASSIFICATION, REGRESSION
from .exceptions import MismatchColumnNumberError, InvalidConfigError

from sparkmlpipe.pipeline.classification import ClassificationPipelineBuilder
from sparkmlpipe.pipeline.regression import RegressionPipelineBuilder


# TODO
def verify_pipeline_config(config):
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

    if num_conf_cols != num_data_cols:
        raise MismatchColumnNumberError(num_conf_cols, num_data_cols)


def get_pipeline_builder(pipe_type):
    if pipe_type == CLASSIFICATION:
        return ClassificationPipelineBuilder
    elif pipe_type == REGRESSION:
        return RegressionPipelineBuilder
    else:
        raise InvalidConfigError('pipe.type', pipe_type)


class MissingConfigError(Exception):
    error_message = 'mandatory config key \'{name}\' not found'

    def __init__(self, conf_name):
        self.conf_name = conf_name
        super(MissingConfigError, self).__init__(
            self.error_message.format(name=conf_name))

# -*- encoding: utf-8 -*-
from pyspark.ml import Pipeline

from sparkmlpipe.utils.pipeline import fit_pipeline, get_pipeline_builder, verify_config, verify_input_dataset


class SparkMLPipeline(Pipeline):
    def __init__(self, config):
        super(SparkMLPipeline, self).__init__()

        verify_config(config)

        self.config = config

        pipe_builder = get_pipeline_builder(config['pipe']['type'])
        self._pipeline, self.label_col = pipe_builder(config).build_pipeline()

    def fit(self, training_data):
        verify_input_dataset(self.config, training_data)
        model = self._pipeline.fit(training_data)

        return model

    def fit_with_outputs(self, training_data):
        verify_input_dataset(self.config, training_data)
        model, metrics, feature_importances = \
            fit_pipeline(self._pipeline, self.config, training_data, self.label_col)

        return model, metrics, feature_importances


class SparkStatPipeline:
    def __init__(self, config, data):
        verify_config(config)
        verify_input_dataset(config, data)

        self.config = config

        pipe_builder = get_pipeline_builder(config['pipe']['type'])
        self._pipeline = pipe_builder(config, data)

    def get_stat(self):
        stat = self._pipeline.compute_stat()

        return stat

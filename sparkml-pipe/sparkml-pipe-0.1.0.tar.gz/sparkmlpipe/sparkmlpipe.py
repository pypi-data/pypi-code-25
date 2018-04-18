# -*- encoding: utf-8 -*-
from pyspark.ml import Pipeline

from sparkmlpipe.utils.pipeline import get_pipeline_builder, verify_pipeline_config, verify_input_dataset


class SparkMLPipeline(Pipeline):
    def __init__(self, config, data):
        super(SparkMLPipeline, self).__init__()

        verify_pipeline_config(config)
        verify_input_dataset(config, data)

        self.config = config

        pipe_builder = get_pipeline_builder(config['pipe']['type'])
        self._pipeline = pipe_builder(config).build_pipeline()

    def fit(self, training_data, params=None):
        verify_input_dataset(self.config, training_data)
        model = self._pipeline.fit(training_data, params)

        return model

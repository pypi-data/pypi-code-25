# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

from pyspark.sql import SparkSession

from sparkmlpipe.sparkmlpipe import SparkMLPipeline
from sparkmlpipe.utils.common import load_config
from sparkmlpipe.utils.constants import ROOT_PATH, APP_PATH, CONFIG_CLASSIFY_LOG_FILE, CONFIG_CLASSIFY_RF_FILE,\
    CONFIG_REGRESSOR_LINEAR_FILE, CONFIG_REGRESSOR_RF_FILE


class TestPipe(TestCase):

    spark = SparkSession.builder \
        .master("local") \
        .appName("Test") \
        .getOrCreate()

    def test_classify_log_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CLASSIFY_LOG_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model = sparkml_pipe.fit(data)

        self.assertTrue(len(model.stages) == 9)

    def test_classify_rf_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CLASSIFY_RF_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model = sparkml_pipe.fit(data)

        self.assertTrue(len(model.stages) == 9)

    def test_regressor_linear_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_REGRESSOR_LINEAR_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model = sparkml_pipe.fit(data)

        self.assertTrue(len(model.stages) == 9)

    def test_regressor_rf_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_REGRESSOR_RF_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config)

        model = sparkml_pipe.fit(data)

        self.assertTrue(len(model.stages) == 9)

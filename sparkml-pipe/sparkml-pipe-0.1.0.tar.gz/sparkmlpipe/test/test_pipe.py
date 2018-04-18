# -*- encoding: utf-8 -*-
import os
from unittest import TestCase

from pyspark.sql import SparkSession

from sparkmlpipe.sparkmlpipe import SparkMLPipeline
from sparkmlpipe.utils.common import load_config
from sparkmlpipe.utils.constants import APP_PATH, CONFIG_CLASSIFY_FILE, CONFIG_REGRESSOR_FILE
from sparkmlpipe.utils.constants import ROOT_PATH


class TestPipe(TestCase):

    spark = SparkSession.builder \
        .master("local") \
        .appName("Test") \
        .getOrCreate()

    def test_classify_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_CLASSIFY_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config, data)

        model = sparkml_pipe.fit(data)

        self.assertTrue(len(model.stages) == 9)

    def test_regressor_pipe(self):
        conf_path = os.path.join(APP_PATH, CONFIG_REGRESSOR_FILE)
        config = load_config(conf_path)

        data_path = config['data']['location']

        data = self.spark.read.option('header', 'true')\
            .option("inferSchema", "true") \
            .csv(os.path.join(ROOT_PATH, data_path))

        sparkml_pipe = SparkMLPipeline(config, data)

        model = sparkml_pipe.fit(data)
        print(len(model.stages))
        self.assertTrue(len(model.stages) == 9)

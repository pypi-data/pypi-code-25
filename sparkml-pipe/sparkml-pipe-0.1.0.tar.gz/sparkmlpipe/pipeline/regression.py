# -*- encoding: utf-8 -*-
from pyspark.ml.regression import LinearRegression, RandomForestRegressor

from .base import BasePipelineBuilder
from sparkmlpipe.utils.constants import LINEAR_REGRESSION_REGRESSOR, RANDOM_FOREST_REGRESSOR
from sparkmlpipe.utils.exceptions import MissingConfigTypeError


class RegressionPipelineBuilder(BasePipelineBuilder):

    def _get_model_stages(self):
        model_stages = []
        model_conf = self.config['pipe']['model']
        if model_conf['type'] == LINEAR_REGRESSION_REGRESSOR:
            model = LinearRegression(featuresCol=self.feat_col, labelCol=self.label_col,
                                     maxIter=10, regParam=0.3, elasticNetParam=0.8)
        elif model_conf['type'] == RANDOM_FOREST_REGRESSOR:
            model = RandomForestRegressor(featuresCol=self.feat_col, labelCol=self.label_col, seed=model_conf['seed'],
                                          numTrees=10)
        else:
            raise MissingConfigTypeError('pipe.model.type', model_conf['type'])

        model_stages.append(model)
        return model_stages

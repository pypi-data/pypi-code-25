# -*- encoding: utf-8 -*-
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier

from .base import BasePipelineBuilder
from sparkmlpipe.utils.constants import LOGISTIC_REGRESSION_CLASSIFIER, RANDOM_FOREST_CLASSIFIER
from sparkmlpipe.utils.exceptions import InvalidConfigError


class ClassificationPipelineBuilder(BasePipelineBuilder):

    def _get_model_stages(self):
        model_stages = []
        model_conf = self.config['pipe']['model']
        params = model_conf['params'] if 'params' in model_conf else {}
        if model_conf['type'] == LOGISTIC_REGRESSION_CLASSIFIER:
            model = LogisticRegression(featuresCol=self.feat_col, labelCol=self.label_col)
            if 'maxIter' in params:
                model.setMaxIter(params['maxIter'])
            if 'regParam' in params:
                model.setRegParam(params['regParam'])
            if 'elasticNetParam' in params:
                model.setElasticNetParam(params['elasticNetParam'])
        elif model_conf['type'] == RANDOM_FOREST_CLASSIFIER:
            model = RandomForestClassifier(featuresCol=self.feat_col, labelCol=self.label_col)
            if 'seed' in params:
                model.setSeed(params['seed'])
            if 'numTrees' in params:
                model.setNumTrees(params['numTrees'])
            if 'maxDepth' in params:
                model.setMaxDepth(params['maxDepth'])
            if 'subsamplingRate' in params:
                model.setSubsamplingRate(params['subsamplingRate'])
        else:
            raise InvalidConfigError('pipe.model.type', model_conf['type'])

        model_stages.append(model)
        return model_stages

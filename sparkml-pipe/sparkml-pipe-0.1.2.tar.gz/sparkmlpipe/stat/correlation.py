# -*- encoding: utf-8 -*-
from pyspark.ml.stat import Correlation

from .base import BaseStatsBuilder
from sparkmlpipe.utils.exceptions import InvalidConfigError
from sparkmlpipe.utils.constants import PEARSON_CORR, SPEARMAN_CORR


class CorrelationBuilder(BaseStatsBuilder):

    def _get_stat(self, data):
        model_conf = self.config['pipe']['model']
        params = model_conf['params'] if 'params' in model_conf else {}

        if 'method' in params:
            if params['method'] in [PEARSON_CORR, SPEARMAN_CORR]:
                corr = Correlation.corr(data, self.feat_col, params['method']).collect()[0][0]
            else:
                raise InvalidConfigError('pipe.model.params.method', params['method'])
        else:
            corr = Correlation.corr(data, self.feat_col, PEARSON_CORR).collect()[0][0]

        return corr

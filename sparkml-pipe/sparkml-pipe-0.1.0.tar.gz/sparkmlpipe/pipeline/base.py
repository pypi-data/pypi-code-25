# -*- encoding: utf-8 -*-
from abc import ABCMeta

from pyspark.ml import Pipeline
from pyspark.ml.feature import MinMaxScaler, StandardScaler, MaxAbsScaler, Imputer, VectorAssembler

from pyspark.ml.feature import StringIndexer, OneHotEncoderEstimator

from pyspark.ml.feature import PCA, ChiSqSelector

from sparkmlpipe.utils.exceptions import MissingConfigTypeError
from sparkmlpipe.utils.constants import STRING_TYPE, NUM_TYPE, \
    MIN_MAX_SCALER_TYPE, STANDARD_SCALER_TYPE, MAXABS_SCALER_TYPE, \
    MEAN_IMPUTER_TYPE, MEDIAN_IMPUTER_TYPE, CHISQ_FEAT_TYPE, PCA_FEAT_TYPE


class BasePipelineBuilder:
    __metaclass__ = ABCMeta

    def __init__(self, config):
        self.config = config

        self.num_out_cols = []
        self.str_out_cols = []
        self.feat_col = None
        self.label_col = None

    def build_pipeline(self):
        data_prep_stages = self._get_data_prep_stages()
        feat_prep_stages = self._get_feat_prep_stages()
        model_stages = self._get_model_stages()

        pipeline = Pipeline(stages=data_prep_stages + feat_prep_stages + model_stages)
        return pipeline

    def _get_data_prep_stages(self):
        header = self.config['data']['header']
        types = self.config['data']['types']

        # preprocess label
        label_stages = []
        label_index = self.config['pipe']['label']
        label_input_col_name = header[label_index]
        label_type = types[label_index]

        if label_type == STRING_TYPE:
            self.label_col = 'indexed_' + label_input_col_name
            label_string_indexer = StringIndexer(inputCol=label_input_col_name,
                                                 outputCol=self.label_col)
            label_stages.append(label_string_indexer)
        elif label_type == NUM_TYPE:
            self.label_col = label_input_col_name
        else:
            raise MissingConfigTypeError('pipe.label', label_type)

        # preprocess numeric cols
        num_stages = []
        num_cols = [header[i] for i, typ in enumerate(types) if typ == NUM_TYPE and i != label_index]
        self.num_out_cols = num_cols

        imputer_conf = self.config['pipe']['data_prep']['numeric']['imputer']
        if len(num_cols) != 0 and imputer_conf != 0:
            imputer_cols = ['imputed_' + col for col in num_cols]
            if imputer_conf == MEAN_IMPUTER_TYPE:
                num_imputer = Imputer(inputCols=num_cols,
                                       outputCols=imputer_cols).setStrategy('mean')
            elif imputer_conf == MEDIAN_IMPUTER_TYPE:
                num_imputer = Imputer(inputCols=num_cols,
                                       outputCols=imputer_cols).setStrategy('median')
            else:
                raise MissingConfigTypeError('pipe.data_prep.numeric.imputer', imputer_conf)
            num_stages.append(num_imputer)
            self.num_out_cols = imputer_cols

        scaler_conf = self.config['pipe']['data_prep']['numeric']['scaler']
        if len(num_cols) != 0 and scaler_conf != 0:
            assembled_num_col_name = 'assembled_num_features'
            scaled_features_col_name = 'scaled_features'
            scaler_assembler = VectorAssembler(inputCols=self.num_out_cols, outputCol=assembled_num_col_name)
            if scaler_conf == MIN_MAX_SCALER_TYPE:
                num_scaler = MinMaxScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            elif scaler_conf == STANDARD_SCALER_TYPE:
                num_scaler = StandardScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            elif scaler_conf == MAXABS_SCALER_TYPE:
                num_scaler = MaxAbsScaler(inputCol=assembled_num_col_name, outputCol=scaled_features_col_name)
            else:
                raise MissingConfigTypeError('pipe.data_prep.numeric.scaler', scaler_conf)

            num_stages.append(scaler_assembler)
            num_stages.append(num_scaler)
            # overwrite the num out cols
            self.num_out_cols = [scaled_features_col_name]

        # preprocess string cols
        # TODO
        # <= 30 different values: OneHotEncoderEstimator (Integer type, since spark 2.3.0)
        # 30 diff values: FeatureHasher
        str_stages = []
        str_cols = [header[i] for i, typ in enumerate(types) if typ == STRING_TYPE and i != label_index]
        str_indexed_cols = [str_col + '_indexed' for str_col in str_cols]
        onehot_conf = self.config['pipe']['data_prep']['string']['onehot']
        if len(str_cols) != 0:
            if onehot_conf == 0:
                # str_indexer
                str_indexers = [
                    StringIndexer(inputCol=str_col,
                                  outputCol=str_out_col)
                    for str_col, str_out_col in zip(str_cols, str_indexed_cols)
                ]

                str_stages.extend(str_indexers)
                self.str_out_cols = str_indexed_cols

            elif onehot_conf == 1:
                # str_indexer
                str_indexers = [
                    StringIndexer(inputCol=str_col,
                                  outputCol=str_out_col)
                    for str_col, str_out_col in zip(str_cols, str_indexed_cols)
                ]

                # onehot_encoder
                str_vec_cols = [str_indexed_col + '_vec' for str_indexed_col in str_indexed_cols]
                str_encoder = OneHotEncoderEstimator(inputCols=str_indexed_cols,
                                                 outputCols=str_vec_cols)

                str_stages.extend(str_indexers)
                str_stages.append(str_encoder)
                self.str_out_cols = str_vec_cols
            else:
                raise MissingConfigTypeError('pipe.data_prep.string.onehot', onehot_conf)

        return label_stages + num_stages + str_stages

    def _get_feat_prep_stages(self):
        feat_stages = []

        feat_assembler = VectorAssembler(inputCols=self.num_out_cols + self.str_out_cols, outputCol='features')

        feat_stages.append(feat_assembler)

        if 'feat_prep' in self.config['pipe']:
            feat_type = self.config['pipe']['feat_prep']['type']
            feat_k = self.config['pipe']['feat_prep']['k']

            if feat_type == CHISQ_FEAT_TYPE:
                selector = ChiSqSelector(numTopFeatures=feat_k, featuresCol="features",
                                         outputCol="selectedFeatures", labelCol=self.label_col)

                feat_stages.append(selector)
                self.feat_col = 'selectedFeatures'
            elif feat_type == PCA_FEAT_TYPE:
                pca = PCA(k=feat_k, inputCol="features", outputCol="pcaFeatures")

                feat_stages.append(pca)
                self.feat_col = 'pcaFeatures'
            else:
                raise MissingConfigTypeError('pipe.feat_prep.type', feat_type)
        else:
            self.feat_col = 'features'

        return feat_stages

    def _get_model_stages(self):
        raise NotImplementedError()

# -*- encoding: utf-8 -*-
from os.path import dirname

LOGGING_CONF = 'conf/logging.yaml'
CONFIG_REGRESSOR_FILE = 'conf/conf_regressor.yaml'
CONFIG_CLASSIFY_FILE = 'conf/conf_classify.yaml'

ROOT_PATH = dirname(dirname(dirname(__file__)))
APP_PATH = dirname(dirname(__file__))

STRING_TYPE = 'string'
NUM_TYPE = 'numeric'

# scale types
MIN_MAX_SCALER_TYPE = 1
STANDARD_SCALER_TYPE = 2
MAXABS_SCALER_TYPE = 3

# impute types
MEAN_IMPUTER_TYPE = 1
MEDIAN_IMPUTER_TYPE = 2

# feature prep types
CHISQ_FEAT_TYPE = 1
PCA_FEAT_TYPE = 2

# model tasks
CLASSIFICATION = 1
REGRESSION = 2

# classifier types
LOGISTIC_REGRESSION_CLASSIFIER = 1
RANDOM_FOREST_CLASSIFIER = 2

# regressor types
LINEAR_REGRESSION_REGRESSOR = 1
RANDOM_FOREST_REGRESSOR = 2

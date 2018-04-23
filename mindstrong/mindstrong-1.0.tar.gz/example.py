'''
    Mindstrong biomarker model fitting software, example model fit script.
    Copyright (C) 2018  Mindstrong Health, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy as np
import pandas as pd
import os
from mindstrong import mindstrong_modelfit as mindstrong

target_file = mindstrong.get_example_data('example_targets.csv')
feature_file = mindstrong.get_example_data('example_features.csv')
target_colname = 'target1'

# Load target data
target_df = pd.read_csv(target_file)
target_df.set_index('device_id', inplace=True)

# Load Feature Data
feature_df = pd.read_csv(feature_file).set_index(['device_id', 'targetDOY'])

# Cross Validated supervised kernel PCA model-fitting
cvdf, best_model = mindstrong.calculateCrossValidatedCorrelation(target_df, feature_df, target_colname,
                                                                 fold_type='n', n_folds=5,
                                                                 kernel_training='linear',
                                                                 kernel_training_param=1,
                                                                 kernel_target='linear',
                                                                 kernel_target_param=1,
                                                                 regularization=0.1)

# Print the final results
print(best_model)



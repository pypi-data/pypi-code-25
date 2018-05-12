"""
Module for testing the evaluate function.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import tempfile
import shutil

import pytest

from idly import NormalPredictor
from idly import Dataset
from idly import Reader
from idly import evaluate


def test_performances():
    """Test the returned dict. Also do dumping."""

    current_dir = os.path.dirname(os.path.realpath(__file__))
    folds_files = [(current_dir + '/custom_train',
                    current_dir + '/custom_test')]

    reader = Reader(line_format='user item rating', sep=' ', skip_lines=3,
                    rating_scale=(1, 5))
    data = Dataset.load_from_folds(folds_files=folds_files, reader=reader)

    algo = NormalPredictor()
    tmp_dir = tempfile.mkdtemp()  # create tmp dir
    with pytest.warns(UserWarning):
        performances = evaluate(algo, data, measures=['RmSe', 'Mae'],
                                with_dump=True, dump_dir=tmp_dir, verbose=2)
    shutil.rmtree(tmp_dir)  # remove tmp dir

    assert performances['RMSE'] is performances['rmse']
    assert performances['MaE'] is performances['mae']

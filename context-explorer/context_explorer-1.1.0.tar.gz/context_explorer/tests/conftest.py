from unittest.mock import Mock

import pandas as pd
import pytest

from context_explorer import data_processing


sample_objects = {
    'one': pd.DataFrame({
        'Well': ['A1', 'B3', 'H12'],
        'Field': [1, 4, 2],
        'Left': [10, 14, 22],
        'Top': [11, 12, 25]
    }),
    'two': pd.DataFrame({
        'Well': ['A3', 'B4', 'H11'],
        'Field': [10, 14, 22],
        'Left': [100, 214, 322],
        'Top': [112, 122, 252]
    }),
    'three': pd.DataFrame({
        'Well': ['A11', 'B11', 'G12'],
        'Field': [11, 14, 12],
        'Left': [110, 114, 212],
        'Top': [111, 112, 125]
    }),
}


@pytest.fixture(params=['one', 'two', 'three'])
def sample_object(request):
    sample_object = Mock()
    sample_object.data = sample_objects[request.param]
    sample_object.spinBox_resolution = Mock()
    sample_object.spinBox_resolution.value = Mock(return_value=0)
    sample_object.spinBox_resolution.setValue = Mock(return_value=None)
    sample_object.tp = Mock(return_value=None)
    data_processing.load_defaults(sample_object)
    return sample_object, request.param

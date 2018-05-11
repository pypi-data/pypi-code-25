from context_explorer import data_processing


# @pytest.mark.parametrize('size', [1, 2, 4])
def test_preprocessing(sample_object):
    sample_object, param_name = sample_object

    data_processing.preprocessing(sample_object)

    sample_object.spinBox_resolution.value.assert_called_once()
    assert sample_object.data.shape == (3, 7)
    if param_name == 'one':
        assert sample_object.pixsize == 256
    elif param_name == 'two':
        assert sample_object.pixsize == 512
    elif param_name == 'three':
        assert sample_object.pixsize == 256


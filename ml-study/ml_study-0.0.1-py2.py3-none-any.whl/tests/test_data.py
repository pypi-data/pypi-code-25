from src.data import read_raw_data, preprocess_data, get_features, get_label


def test_raw_shape():
    dframe = read_raw_data()
    assert dframe.shape == (150, 5)


def test_get_features_shape():
    dframe = read_raw_data()
    processed = preprocess_data(dframe)
    features = get_features(processed)
    label = get_label(processed)

    assert label.shape == (150,)
    assert features.shape == (150, 4)

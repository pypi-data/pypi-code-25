from collections import OrderedDict
import opedia_dataset_validator as odv
import pandas as pd

def test_validate_column_generic_required():
    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, {}, 'foo')
    assert len(errors) == 0
    assert sfilt.tolist() == ['a']

    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True }, 'foo')
    assert len(errors) == 1
    assert sfilt.tolist() == ['a']
    assert errors[0]['row'] == 3

    s = pd.Series(['a', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True, 'na': '' }, 'foo')
    assert len(errors) == 0
    assert sfilt.tolist() == ['a']

    s = pd.Series(['a', 'na', ''], dtype=str)
    errors, sfilt = odv.validator.validate_column_generic(s, { 'required': True, 'na': 'na' }, 'foo')
    assert len(errors) == 1
    assert sfilt.tolist() == ['a']
    assert errors[0]['row'] == 4


def test_validate_column_strings():
    s = pd.Series(['a', 'bb', 'ccc'], dtype=str)
    errors = odv.validator.validate_column_strings(s, { 'max': 2 }, 'foo')
    assert len(errors) == 1
    assert errors[0]['row'] == 4


def test_validate_column_floats():
    s = pd.Series(['a', 98.6, 99, 100], dtype=str)
    errors = odv.validator.validate_column_floats(s, { 'max': 99 }, 'foo')
    assert len(errors) == 2
    assert errors[0]['row'] == 2
    assert errors[1]['row'] == 5



def test_validate_column_datetime():
    s = pd.Series(['a', '2018-05-22', '2018-02-29', '2018-05-2'], dtype=str)
    errors = odv.validator.validate_column_datetimes(s, { 'format': 'YYYY-MM-DD' }, 'foo')
    assert len(errors) == 3
    assert errors[0]['row'] == 2
    assert errors[1]['row'] == 4
    assert errors[2]['row'] == 5


def test_validate_filename():
    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-22_v1.0.xlsx')
    assert len(errors) == 0

    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-22_1.0.xlsx')
    assert len(errors) == 1

    errors = odv.validator.validate_filename('foo/bar/dataset_2018-05-2_v1.0.xlsx')
    assert len(errors) == 1

    errors = odv.validator.validate_filename('foo/bar/2018-05-22_v1.0.xlsx')
    assert len(errors) == 1


def test_validate_all_sheets_present():
    wb = OrderedDict([(k, True) for k in ['data', 'dataset_meta_data', 'vars_meta_data']])
    errors = odv.validator.validate_all_sheets_present(wb)
    assert len(errors) == 0

    wb = OrderedDict([(k, True) for k in ['data', 'dataset_meta_data', 'vars_meta_data', 'extra']])
    errors = odv.validator.validate_all_sheets_present(wb)
    assert len(errors) == 0

    wb = OrderedDict([(k, True) for k in ['dataset_meta_data', 'data', 'vars_meta_data']])
    errors = odv.validator.validate_all_sheets_present(wb)
    assert len(errors) == 1

    wb = OrderedDict([(k, True) for k in ['dataset_meta_data', 'vars_meta_data']])
    errors = odv.validator.validate_all_sheets_present(wb)
    assert len(errors) == 1


def test_validate_sheet_generic():
    spec = {
        'sheets': { 'vars': 'vars_meta_data' },
        'columns': { 'vars': OrderedDict([('a', { 'type': 'float' }), ('b', { 'type': 'float' })]) }
    }

    df = pd.DataFrame({ 'a': [], 'b': [] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars', spec=spec)
    assert len(errors) == 0

    df = pd.DataFrame({ 'a': [] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars', spec=spec)
    assert len(errors) == 1

    df = pd.DataFrame({ 'a': ['a'], 'b': [200] }, dtype=str)
    errors = odv.validator.validate_sheet_generic(df, 'vars', spec=spec)
    assert len(errors) == 1

# TODO: test for data sheet custom column correspondence to vars_meta_data and
# basic presence test for custom columns in data.

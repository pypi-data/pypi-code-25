from __future__ import unicode_literals
from io import open
import arrow
import os
import oyaml as yaml
import pandas as pd
import re
import sys


def validate(input_path):
    wb = pd.read_excel(input_path, sheet_name=None, na_values=[],
                       keep_default_na=False)
    errors = []
    errors.extend(validate_filename(input_path))
    errors.extend(validate_all_sheets_present(wb))
    errors.extend(validate_sheet_metadata(wb))
    errors.extend(validate_sheet_vars(wb))
    errors.extend(validate_sheet_data(wb))
    return errors


def validate_column_datetimes(series, colspec, sheet):
    errors = []

    # Convert to strings, might be a datetime.datetime object
    if (sys.version_info > (3, 0)):
        converted = series.astype(str)
    else:
        converted = series.astype(unicode)

    if colspec.get('required', False):
        # Find empty rows first
        empty_errors = converted[converted.str.len() == 0]
        for idx, val in empty_errors.iteritems():
            errors.append({
                'message': 'missing required field',
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })

    # Now look for format errors in non-empty rows
    present = converted[converted.str.len() > 0]
    for idx, val in present.iteritems():
        try:
            dt = arrow.get(val, colspec['format'])
        except ValueError as e:
            errors.append({
                'message': 'error in datetime string: %s' % e,
                'value': val,
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })
        except arrow.parser.ParserError as e:
            errors.append({
                'message': 'invalid datetime string - should match %s' % colspec['format'],
                'value': val,
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })

    return errors


def validate_column_floats(series, colspec, sheet):
    errors = []

    if colspec.get('required', False):
        empty_errors = converted[converted.str.len() == 0]
        for idx, val in empty_errors.iteritems():
            errors.append({
                'message': 'missing required field',
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })

    if colspec.get('na', False):
        # Remove NA values
        series = series[_series != colspec['na']]

    # Convert to floats
    converted = pd.to_numeric(series, errors='coerce')

    # Non-numeric strings are now NaN
    # Flag NaN as errors
    nonnumeric_errors = series[pd.isna(converted)]
    for idx, val in nonnumeric_errors.iteritems():
        errors.append({
            'message': 'invalid value',
            'value': val,
            'row': idx + 1,
            'column': series.name,
            'sheet': sheet
        })
    # Check range
    min_errors = None
    max_errors = None
    if colspec.get('min', False):
        min_errors = series[converted < colspec['min']]
        for idx, val in min_errors.iteritems():
            errors.append({
                'message': 'value less than minimum of {}'.format(colspec['min']),
                'value': val,
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })
    if colspec.get('max', False):
        max_errors = series[converted > colspec['max']]
        for idx, val in max_errors.iteritems():
            errors.append({
                'message': 'value greater than maximum of {}'.format(colspec['max']),
                'value': val,
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })

    return errors


def validate_column_strings(series, colspec, sheet):
    errors = []

    # Convert to strings
    if (sys.version_info > (3, 0)):
        converted = series.astype(str)
    else:
        converted = series.astype(unicode)

    if colspec.get('required', False):
        empty_errors = converted[converted.str.len() == 0]
        for idx, val in empty_errors.iteritems():
            errors.append({
                'message': 'missing required field',
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })
    if colspec.get('max', False):
        maxlen_errors = converted[converted.str.len() >= colspec['max']]
        for idx, val in maxlen_errors.iteritems():
            errors.append({
                'message': 'string length > %d' % colspec['max'],
                'value': val,
                'row': idx + 1,
                'column': series.name,
                'sheet': sheet
            })

    return errors


def validate_filename(input_path):
    fn = os.path.basename(input_path)
    errors = []
    filename_re = re.compile(r'^(?P<shortname>.+)_(?P<date>[^_]+)_(?P<version>[^_]+)\.xlsx$')
    m = filename_re.match(fn)
    if not m:
        errors.append({
            'message': 'filename does not match format <dataset_short_name>_<dataset_release_date>_v<dataset_version>.xlxs',
            'value': fn
        })
    else:
        try:
            dt = arrow.get(m.group('date'), spec['file_date'])
        except ValueError as e:
            errors.append({
                'message': 'error in filename datatime string: %s' % e,
                'value': m.group('date')
            })
        except arrow.parser.ParserError as e:
            errors.append({
                'message': 'date in filename must be in %s format' % spec['file_date'],
                'value': m.group('date')
            })
        if not re.match(r'^v.+$', m.group('version')):
            errors.append({
                'message': 'version string in filename must start with "v"',
                'value': fn
            })
    return errors


def validate_sheet_data(wb):
    errors = []
    if not (spec['sheets']['data'] in wb and spec['sheets']['vars'] in wb):
        return errors

    df = wb[spec['sheets']['data']]

    # Check that required columns are in order
    required_columns = list(spec['columns']['data'].keys())
    if len(df.columns.tolist()) < len(required_columns) or \
       df.columns.tolist()[0:len(required_columns)] != required_columns:
        errors.append({
            'message': 'the first %d columns of "%s" worksheet should be %s' % (len(required_columns), spec['sheets']['data'], required_columns)
        })
        return errors

    # Collect variable short names from vars_meta_data sheet
    vars_defined = wb[spec['sheets']['vars']]['var_short_name'].tolist()
    vars_found = df.columns.tolist()[len(required_columns):]
    extra_defined = set(vars_defined).difference(set(vars_found))
    extra_found = set(vars_found).difference(set(vars_defined))
    if extra_defined:
        errors.append({
            'message': 'some data variables were defined in the "%s" worksheet but were not found in the "%s" worksheet:' % (spec['sheets']['vars'], spec['sheets']['data']),
            'value': list(extra_defined)
        })
    if extra_found:
        errors.append({
            'message': 'some data variables were found in the "%s" worksheet but were not defined in the "%s" worksheet' % (spec['sheets']['data'], spec['sheets']['vars']),
            'value': list(extra_found)
        })

    # Validate cells
    for colname, colspec in spec['columns']['data'].items():
        validator = validator_lookup[colspec["type"]]
        errors.extend(validator(df[colname], colspec, spec['sheets']['data']))

    return errors


def validate_sheet_metadata(wb):
    errors = []
    if not spec['sheets']['metadata'] in wb:
        return errors

    required_columns = list(spec['columns']['metadata'].keys())
    df = wb[spec['sheets']['metadata']]
    if df.columns.tolist() != required_columns:
        errors.append({
            'message': 'incorrect set or order of columns in the "%s" worksheet, expected %s' % (spec['sheets']['metadata'], required_columns),
            'value': str(df.columns.tolist())
        })
        return errors

    # Validate cells
    for colname, colspec in spec['columns']['metadata'].items():
        validator = validator_lookup[colspec["type"]]
        errors.extend(validator(df[colname], colspec, spec['sheets']['metadata']))

    return errors


def validate_sheet_vars(wb):
    errors = []
    if not spec['sheets']['vars'] in wb:
        return errors

    required_columns = list(spec['columns']['vars'].keys())
    df = wb[spec['sheets']['vars']]
    if df.columns.tolist() != required_columns:
        errors.append({
            'message': 'incorrect set or order of columns in "%s" worksheet, expected %s' % (spec['sheets']['vars'], required_columns),
            'value': str(df.columns.tolist())
        })
        return errors

    # Validate cells
    for colname, colspec in spec['columns']['vars'].items():
        validator = validator_lookup[colspec["type"]]
        errors.extend(validator(df[colname], colspec, spec['sheets']['vars']))

    return errors


def validate_all_sheets_present(wb):
    errors = []
    sheets = [spec['sheets']['data'], spec['sheets']['metadata'], spec['sheets']['vars']]
    if list(wb.keys()) != sheets:
        errors.append({
            'message': 'spreadsheet should contain 3 worksheets: %s' % sheets,
            'value': str(list(wb.keys()))
        })
    return errors


# Load dataset file specifications
spec_file_name = 'dataset_file_def.yaml'
spec_file_path = os.path.join(os.path.dirname(__file__), spec_file_name)
with open(spec_file_path, encoding='utf-8') as fh:
    spec = yaml.load(fh)


# Register data type validators in lookup
validator_lookup = {
    'float': validate_column_floats,
    'string': validate_column_strings,
    'datetime': validate_column_datetimes
}

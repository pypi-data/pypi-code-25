import sys
import pandas as pd
import numpy as np


left_rule = {'<': ':', '^': ':', '>': '-'}
right_rule = {'<': '-', '^': ':', '>': ':'}


def _trim_record(record, digits):
    """ If the record is a float, trim it to given digits

    Args:
        record (iterable): Rows will be generated from this.
        digits: The number of digits that will be kept after dot.

    Returns:
        any: Trimmed str if record is a float, otherwise return the original
            record.
    """
    if type(record) is float or type(record) is np.float64 and digits != None:
        return ('{:.' + str(digits) + 'f}').format(record)
    else:
        return record


def _evalute_field(record, field_spec, digits):
    """ Evaluate a field of a record using the type of the field_spec as a
    guide.

    Args:
        record (iterable): Rows will be generated from this.
        field_spec (any): Either int, str or float

    Returns:
        str: The guide for the field_spec
    """
    if type(field_spec) is int:
        return str(_trim_record(record[field_spec], digits))
    elif type(field_spec) is str:
        return str(_trim_record(getattr(record, field_spec), digits))
    else:
        return str(_trim_record(field_spec(record), digits))


def _table(file, records, fields, headings, alignment, digits=None, index=True):
    """ Generate a Doxygen-flavor Markdown table from records.

    Args:
        file (obj): Any object with a 'write' method that takes a single string
            parameter.

        records (iterable): Rows will be generated from this

        fields (list):
            List of fields for each row.  Each entry may be an
            integer, string or a function.  If the entry is an integer, it is
            assumed to be an index of each record.  If the entry is a string,
            it is assumed to be a field of each record.  If the entry is a
            function, it is called with the record and its return value is
            taken as the value of the field.

        headings (list of str): List of column headings.

        alignment (list of char):
            List of pairs alignment characters.  The first of the pair specifies
            the alignment of the header, (Doxygen won't respect this, but it
            might look good, the second specifies the alignment of the cells in
            the column.

            Possible alignment characters are:
            '<' = Left align (default for cells)
            '>' = Right align
            '^' = Center (default for column headings)

        index (bool): Whether to keep the index column in the output table.

    Returns:
        None
    """

    num_columns = len(fields)
    assert len(headings) == num_columns

    # Compute the table cell data
    columns = [[] for i in range(num_columns)]
    for record in records:
        for i, field in enumerate(fields):
            columns[i].append(_evalute_field(record, field, digits))

    extended_align = alignment

    heading_align, cell_align = [x for x in zip(*extended_align)]

    field_widths = [len(max(column, key=len)) if len(column) > 0 else 0
                    for column in columns]
    heading_widths = [max(len(head), 2) for head in headings]
    column_widths = [max(x) for x in zip(field_widths, heading_widths)]

    _ = ' | '.join(['{:' + a + str(w) + '}'
                    for a, w in zip(heading_align, column_widths)])
    heading_template = '| ' + _ + ' |'
    _ = ' | '.join(['{:' + a + str(w) + '}'
                    for a, w in zip(cell_align, column_widths)])
    row_template = '| ' + _ + ' |'

    _ = ' | '.join([left_rule[a] + '-'*(w-2) + right_rule[a]
                    for a, w in zip(cell_align, column_widths)])
    ruling = '| ' + _ + ' |'

    # Bold the first column if the first column is index
    if index == True:
        header_line = heading_template.format(*headings).rstrip().split('|')
        ruling_line = ruling.rstrip().split('|')
        header_line[1] += '    '
        ruling_line[1] = ' :--' + ruling_line[1][2:-2] + '--: '
        file.write('|'.join(header_line) + '\n')
        file.write('|'.join(ruling_line) + '\n')
    else:
        file.write(heading_template.format(*headings).rstrip() + '\n')
        file.write(ruling.rstrip() + '\n')

    for row in zip(*columns):
        if index == True:
            row_line = row_template.format(*row).rstrip().split('|')
            extra = ''
            # Additional space for item that cannot be directly bold
            if len(row_line[1][1:-1].strip()) != len(row_line[1][1:-1]):
                for i in range(len(
                        row_line[1][1:-1]) - len(row_line[1][1:-1].strip())):
                    extra += ' '
            row_line[1] = ' **' + row_line[1][1:-1].strip() + '** ' + extra
            file.write('|'.join(row_line) + '\n')
        else:
            file.write(row_template.format(*row).rstrip() + '\n')


def pd_to_md(df, digits=None, index=True, file=sys.stdout, alignments=None):
    """ Transform a pandas DataFrame to a markdown format table

    Args:
        df (pandas.DataFarme): A normal data frame.

        digits (int): The number digits that will kept after dot.

        index (bool): Whether to keep the index column in the output table.

        file (obj): A writable obj, default sys.stdout.

        alignments (list): List of pairs alignment characters.  The first
            of the pair specifies the alignment of the header, (Doxygen won't
            respect this, but it might look good, the second specifies the
            alignment of the cells in the column.

            Possible alignment characters are:
            '<' = Left align (default for cells)
            '>' = Right align
            '^' = Center (default for column headings)

            If nothing input, default to everything as center

    Returns:
        None
    """
    headings = df.columns.values.tolist()
    if index == True:
        records = df.to_records()
        headings = [''] + headings
    else:
        records = df.values

    if alignments == None:
        alignments = list(map(lambda x: ['^', '^'], range(len(headings))))

    fields = list(range(len(headings)))

    _table(file, records, fields, headings, alignments, digits, index)
import click
import sys

def print_tsv_errors(errors, fh, print_all=True, header=True, print_value=False):
    fill_error_fields(errors)
    fix_row_number(errors)
    errors_output = []
    errors_seen = set()
    for e in errors:
        key = (e['sheet'], e['column'], e['message'])
        if key in errors_seen and not print_all:
            continue
        errors_seen.add(key)
        errors_output.append(e)
    if print_value:
        outkeys = ['sheet', 'column', 'row', 'value', 'message']
    else:
        outkeys = ['sheet', 'column', 'row', 'message']
        for e in errors_output:
            _ = e.pop('value', None)

    outlines = []
    if header:
        outlines.append('#%s' % '\t'.join(outkeys))

    for e in errors_output:
        # Convert all values to unicode strings and concatenate before output
        if (sys.version_info > (3, 0)):
            outlines.append('\t'.join([str(e[k]) for k in outkeys]))
        else:
            outlines.append('\t'.join([unicode(e[k]) for k in outkeys]))
    fh.write('\n'.join(outlines) + '\n')


def fill_error_fields(errors):
    for e in errors:
        for k in ['column', 'message', 'row', 'sheet', 'value']:
            e.setdefault(k, None)


def fix_row_number(errors):
    for e in errors:
        if e.get('row', None) is not None:
            e['row'] += 2  # add two for header row and 1-based counting

import sys

def print_tsv_errors(errors, fh, print_all=True, header=True, print_value=False):
    fill_error_fields(errors)
    errors_output = []
    errors_seen = set()
    for e in errors:
        key = (e['sheet'], e['column'], e['message'])
        if not print_all and key in errors_seen:
            continue
        errors_seen.add(key)
        errors_output.append(e)
    if print_value:
        outkeys = ['sheet', 'column', 'row', 'value', 'message']
    else:
        outkeys = ['sheet', 'column', 'row', 'message']
        for e in errors:
            _ = e.pop('value', None)

    if header:
        print('#%s' % '\t'.join(outkeys))
    for e in errors:
        if (sys.version_info > (3, 0)):
            print('%s' % '\t'.join([str(e[k]) for k in outkeys]))
        else:
            print('%s' % '\t'.join([unicode(e[k]) for k in outkeys]))


def fill_error_fields(errors):
    for e in errors:
        for k in ['column', 'message', 'row', 'sheet', 'value']:
            e.setdefault(k, None)

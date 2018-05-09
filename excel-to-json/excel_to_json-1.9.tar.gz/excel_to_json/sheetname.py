import re


def shortname(sheetname):
    shortname_ends = list(map(lambda i: i.span()[0], re.finditer('[\.!]', sheetname)))
    if len(shortname_ends) != 0:
        return sheetname[:min(shortname_ends)]
    return sheetname


def is_outfile(sheetname):
    return is_json(sheetname)


def is_json(sheetname):
    return sheetname.find('.json') != -1


def is_array(sheetname):
    return sheetname.find('!') == -1

def out_file_name(sheetname):
    return sheetname.rstrip('@')
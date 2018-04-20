def shortname(sheetname):
    index = sheetname.find('.')
    return sheetname if index == -1 else sheetname[:index]

def is_outfile(sheetname):
    return is_json(sheetname)

def is_json(sheetname):
    return sheetname.find('.json') != -1


def is_array(sheetname):
    return sheetname.find('@') != -1

def out_file_name(sheetname):
    return sheetname.rstrip('@')
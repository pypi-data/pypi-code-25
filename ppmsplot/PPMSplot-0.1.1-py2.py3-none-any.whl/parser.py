import codecs
from math import inf

def parse_data_element(element):
    try:
        if '.' in element:
            return float(element)
        elif element:
            return int(element)
        elif element == u'':
            return None
    except Exception:
        return None

def parse_file(file_config):
    filename = file_config['filename']
    if file_config['rowEnd'] == 0:
        file_config['rowEnd'] = inf
    
    # Setup series data
    series = []
    for s in file_config['series']:
        series.append({'x':[], 'y':[], 'style':s['style'], 'label':s['label']})

    with codecs.open(filename, "r", encoding='utf-8', errors='replace') as data_file:
        for i, line in enumerate(data_file.readlines()):
            # Only read data in specified line range
            if i < file_config['rowStart'] or i > file_config['rowEnd']:
                continue

            # Strip the newline from each line
            line = line.strip('\n').strip('\r')

            # Split into an array of strings at each comma
            line = line.split(',')

            # Get data for each series
            for i, s in enumerate(file_config['series']):
                x_value = parse_data_element(line[s['xColumnIndex']])
                # Trim based on min and max values and remove null data
                if x_value is None or not s['xMin'] <= x_value <= s['xMax']:
                    continue 
                series[i]['x'].append( x_value )
                series[i]['y'].append(
                    parse_data_element(
                        line[s['yColumnIndex']]
                    )
                )
        
    return series

def extract_columns(headings, data, *indices):
    '''
    Extracts selected columns from data
    '''
    new_headings = [headings[x] for x in indices]

    columns = [ [] for i in indices]
    for row in data:
        new_row = []
        for index, element in enumerate(indices):
            columns[index].append(row[element])
    return new_headings, columns


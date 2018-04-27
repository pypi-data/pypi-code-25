import os


def read(filename, field_separator=',', null_as="", newline="\n", quote=None):
    size = os.path.getsize(filename)
    with open(filename, 'rb') as f:
        data = memoryview(f.read())
    return parse(data, size, field_separator=field_separator, null_as=null_as, newline=newline, quote=quote)


def parse(data, size, field_separator=',', null_as="", newline="\n", quote=None):
    parsed_data = []
    row_data = []
    field_data = bytearray()
    i = 0
    in_quotes = False
    escaped = False
    while i < size:
        byte = data[i]
        if byte == "\\":
            if escaped:
                escaped = False
                field_data.append(byte)
            else:
                escaped = True
        elif quote and byte == quote:
            if escaped:
                field_data.append(byte)
                escaped = False
            elif in_quotes:
                in_quotes = False
            else:
                in_quotes = True
        elif byte == field_separator:
            if escaped:
                field_data.append(byte)
                escaped = False
            elif in_quotes:
                field_data.append(byte)
            else:
                row_data.append(field_data)
                field_data = clear_field_data()
        elif byte == newline:
            if escaped:
                field_data.append(byte)
                escaped = False
            elif in_quotes:
                field_data.append(byte)
            else:
                field_data, row_data, parsed_data = finish_row(field_data, row_data, parsed_data)
        else:
            field_data.append(byte)
        i = i + 1
    if not byte == newline:
        # Dont record trailing newline
        row_data.append(field_data)
        parsed_data.append(tuple(row_data))
    return parsed_data


def clear_field_data():
    return bytearray()


def finish_row(field_data, row_data, parsed_data):
    row_data.append(field_data)
    parsed_data.append(tuple(row_data))
    field_data = clear_field_data()
    row_data = []
    return field_data, row_data, parsed_data

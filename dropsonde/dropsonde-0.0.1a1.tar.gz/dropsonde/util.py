def get_uuid_string(**x):
    """This method parses a UUID protobuf message type from its component
    'high' and 'low' longs into a standard formatted UUID string

    Args:
        x (dict): containing keys, 'low' and 'high' corresponding to the UUID
            protobuf message type

    Returns:
        str: UUID formatted string
    """
    if 'low' not in x or 'high' not in x:
        return None

    # convert components to hex strings and strip off '0x'
    low = int(x['low'])
    high = int(x['high'])

    l = hex(low)[2:-1]
    h = hex(high)[2:-1]

    # ensure we have leading 0 bytes set
    l = ''.join(['0' * (16 - len(l)), l])
    h = ''.join(['0' * (16 - len(h)), h])

    # split/reverse/join little endian bytes
    x = ''.join([
        ''.join([l[i:i+2] for i in range(0, len(l), 2)][::-1]),
        ''.join([h[i:i+2] for i in range(0, len(h), 2)][::-1]),
    ])

    # create uuid formatted string
    return '-'.join([x[:8], x[8:12], x[12:16], x[16:20], x[20:]])

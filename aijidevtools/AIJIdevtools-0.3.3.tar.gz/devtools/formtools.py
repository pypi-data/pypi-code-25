import re


def tostr(sth):
    if isinstance(sth, str):
        return sth
    elif isinstance(sth, bytes):
        return sth.decode()
    else:
        return str(sth)


def tobytes(sth):
    if isinstance(sth, bytes):
        return sth
    elif isinstance(sth, str):
        return sth.encode()
    else:
        return bytes(sth)


def toaddr(strs):
    host = 'localhost'
    port = 0
    if isinstance(strs, list):
        if len(strs) == 1:
            return toaddr(strs[0])
        elif len(strs) == 2:
            host = strs[0]
            port = int(strs[1])
        else:
            raise ValueError
        return (host, port)
    elif isinstance(strs, str):
        strs = strs.split(':')
        if len(strs) == 1:
            host = strs[0]
            return (host, port)
        elif len(strs) == 2:
            return toaddr(strs)
        else:
            raise ValueError
    else:
        raise ValueError


def strtodict(text, mode, *args):
    '''
    # parse text to dict
    # mode: '[rc][v]'
    #     site 0: keys' orientation, (r)ow or (c)olumn
    #     site 1: multi (v)lues, return a list of dict 
    # mode c: len(args) == 1
    #     k1: v1
    #     k2: v2
    # mode cs: len(args) == 2
    #     k1: d1v1, d2v1
    #     k2: d1v2, d2v2, d3v2,
    # mode r(s): len(args) == 1
    #     k1   k2    k3 
    #     v1   v2    v3 
    #     d2v1 d2v2  d3v3

    '''
    if mode == 'c':
        rows = filter(lambda x: x.strip(), re.split('\n', text))
        dic = {}
        sep = args[0]
        for r in rows:
            try:
                k, v = re.split(sep, r, 1)
            except Exception as why:
                continue
            else:
                k, v = k.strip(), v.strip()
                dic[k] = v
        return dic

    elif mode == 'cs':
        dics = []
        dic = strtodict(text, 'c', args[0])
        for (k, v) in dic.items():
            values = [i.strip() for i in re.split(args[1], v) if i.strip()]
            while len(values) > len(dics):
                dics.append({})
            for n, value in enumerate(values):
                dics[n][k] = value
        return dics

    elif mode == 'rs':
        dics = []
        items = list(filter(lambda x: x.strip(), re.split('\n', text)))
        sep = args[0]
        keys = re.split(sep, items[0])
        for values in items[1:]:
            dics.append(dict(zip(keys, re.split(sep, values))))
        return dics
    elif mode == 'r':
        return strtodict(text, 'rs', *args)[0]

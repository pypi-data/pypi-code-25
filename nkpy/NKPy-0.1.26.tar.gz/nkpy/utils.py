def find_min_idx(a):
    n = len(a)
    min_idx = 0
    b = []
    for j in a.keys():
        b.append(j)
    for i in range(1, n):
        if len(b[i]) > len(b[min_idx]):
            min_idx = i

    return min_idx


def sel_sort(a):
    result = dict()

    while a:
        b = []
        for j in a.keys():
            b.append(j)

        min_idx = find_min_idx(a)
        value = b[min_idx]
        result[value] = a[value]
        del a[b[min_idx]]

    return result

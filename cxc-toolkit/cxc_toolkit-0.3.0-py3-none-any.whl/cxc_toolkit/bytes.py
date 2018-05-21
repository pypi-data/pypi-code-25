def xor(bytes_1, bytes_2, longest=False):
    """
    Xor bytes_1 and bytes_2, return the result as a bytes

    :param bytes_1:
    :param bytes_2:
    :type ytes_1: bytes
    :type bytes_2: bytes
    :return:
    :rtype: bytes
    """
    # init variables
    bytearray_1 = bytearray(bytes_1)
    bytearray_2 = bytearray(bytes_2)
    xor_bytearray = bytearray()

    # make bytearray_1 be the longest bytearray
    if len(bytearray_1) < len(bytearray_2):
        bytearray_1, bytearray_2 = bytearray_2, bytearray_1

    for i in range(len(bytearray_1)):
        if i < len(bytearray_2):
            xor_bytearray.append(bytearray_1[i] ^ bytearray_2[i])
        else:
            if longest:
                xor_bytearray += bytearray_1[i:]
            break
    return bytes(xor_bytearray)

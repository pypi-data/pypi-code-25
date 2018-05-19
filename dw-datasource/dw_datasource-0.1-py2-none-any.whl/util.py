
def retry(f, n_attempts=3):
    """
    Wrapper function to retry an operation
    :param f:
    :param n_attempts:
    :return:
    """
    def wrapper(*args, **kwargs):
        for i in range(n_attempts):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if i == n_attempts - 1:
                    raise e
    return wrapper


def ascii(utf_str):
    if utf_str is None:
        return utf_str

    return utf_str.encode('ascii')

import os


def read(*rnames):
    '''
    return content from file informed in '*rnames'
    :param rnames:
    :return:
    >>> read(os.path.dirname(__file__), 'version.txt')
    0.2
    '''
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def namespace(s):
    '''
    return the namespace from to s='incolumepy.package.module'
    :param s:
    :return:

    >>> namespace('incolumepy.package.module')
    ['incolumepy','package']
    '''

    return s.split('.')[:-1]


if __name__ == "__main__":
    pass

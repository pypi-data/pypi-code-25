""" Helper to check if a given version is in a version range """

import re

version_re = re.compile(r'20\d\dv\d\.\d\Z')
strict=True

def validate_version(version):
    if not version_re.match(version):
        raise ValueError("Illegal version string '%s'" % version)
    return True

def check_version(version_start, version_end, version_test):

    if strict:
        [validate_version(i) for i in [version_start, version_end, version_test]]


if __name__ == '__main__':
    check_version('2013v3.0', '2014v2.3', '2014v1.0')

    
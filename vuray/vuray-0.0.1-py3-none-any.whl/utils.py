import platform

from vuray import __version__


def build_user_agent():
    return 'VuRay/1.0 ({}; {}) vuray-client/{}'.format(
        platform.system(), platform.machine(), __version__
    )


def parse_requirements(fp):
    raise NotImplementedError


def parse_setup(fp):
    raise NotImplementedError

import os

from conans.client.conan_api import Conan
from cpt.runner import TestPackageRunner


def run():
    _, client_cache, _ = Conan.factory()
    if os.path.exists(client_cache.default_profile_path):
        os.remove(client_cache.default_profile_path)
    runner = TestPackageRunner()
    runner.run()

if __name__ == '__main__':
    run()

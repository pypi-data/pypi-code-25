import os
from py_gardener.InternalTestBase import InternalTestBase


class TestDocker(InternalTestBase):

    def test_docker(self):
        """ Test that tests are run inside a Docker container """
        if len(self.DOCKER) > 0:
            assert os.path.exists(os.path.join("/.dockerenv")), (
                'Please run in Docker using ". manage.sh"')

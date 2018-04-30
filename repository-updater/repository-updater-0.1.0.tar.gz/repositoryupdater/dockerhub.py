"""
DockerHub module

Handles communication with Docker Hub
"""

import urllib.request


class DockerHub:
    """This class represents Docker Hub"""

    @staticmethod
    def image_exists_on_dockerhub(name, version):
        """Check if give image and version exists on Docker Hub"""
        location = "https://registry.hub.docker.com/v2/repositories/" \
            f"{name}/tags/{version}/"
        request = urllib.request.Request(location)
        request.get_method = lambda: 'HEAD'

        try:
            urllib.request.urlopen(request)
            return True
        except urllib.request.HTTPError:
            return False

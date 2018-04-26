class PolicyVersion:
    """A policy version"""

    def __init__(self, version):
        self.version = version
        self.builds = []

    def __str__(self):
        return self.version


class Policy:
    """A policy"""

    def __init__(self, name):
        self.name = name
        self.versions = {}

    def __str__(self):
        return self.name

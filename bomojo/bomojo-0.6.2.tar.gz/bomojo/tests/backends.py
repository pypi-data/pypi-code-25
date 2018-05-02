"""
bomojo test backends

This module exists to provide example custom backends, to test the library's
support for customizing certain behavior.
"""

from bomojo.backends import AbstractUserBackend


class FeatureBobBackend(AbstractUserBackend):
    def is_featured_contributor(self, user):
        return user.username == 'bob'

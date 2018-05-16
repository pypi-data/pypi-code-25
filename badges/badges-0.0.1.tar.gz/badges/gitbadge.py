#!/usr/bin/env python
from badges.badge import Badge


class GitBadge(Badge):
    def __init__(self, fullname, branch="master", **kwargs):
        self.update(fullname=fullname, branch=branch, **kwargs)

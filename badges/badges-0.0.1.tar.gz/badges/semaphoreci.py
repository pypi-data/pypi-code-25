#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://semaphoreci.com/api/v1/owner/repo/branches/master/badge.svg
# https://semaphoreci.com/api/v1/owner/repo/branches/master/shields_badge.svg


class Semaphoreci(GitBadge):
    title = "Semaphore CI"

    def __init__(self, fullname, branch="master", shields=True, **kwargs):
        self.update(fullname=fullname, branch=branch, shields=shields, **kwargs)

    @property
    def image(self):
        fullname = self.fullname.replace(".", "-")
        if not self.shields:
            return "https://semaphoreci.com/api/v1/%s/branches/{branch}/badge.svg" % fullname
        return "https://semaphoreci.com/api/v1/%s/branches/{branch}/shields_badge.svg" % fullname

    @property
    def link(self):
        fullname = self.fullname.replace(".", "-")
        return "https://semaphoreci.com/%s" % fullname

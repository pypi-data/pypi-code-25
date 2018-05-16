#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://scrutinizer-ci.com/g/owner/repo/
# https://scrutinizer-ci.com/g/owner/repo/badges/quality-score.png?b=master
# https://scrutinizer-ci.com/g/owner/repo/badges/build.png?b=master


class Scrutinizer(GitBadge):
    title = "Scrutinizer"
    link = "https://scrutinizer-ci.com/g/{fullname}/"

    def __init__(self, fullname, branch="master", build=False, **kwargs):
        self.update(fullname=fullname, branch=branch, build=build, **kwargs)

    @property
    def image(self):
        if self.build:
            return "https://scrutinizer-ci.com/g/{fullname}/badges/build.png?b={branch}"
        return "https://scrutinizer-ci.com/g/{fullname}/badges/quality-score.png?b={branch}"

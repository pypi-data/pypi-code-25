#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://travis-ci.org/owner/repo
# https://api.travis-ci.org/owner/repo.svg?branch=master


class Travis(GitBadge):
    title = "Travis"
    image = "https://api.travis-ci.org/{fullname}.svg?branch={branch}"
    link = "https://travis-ci.org/{fullname}/"

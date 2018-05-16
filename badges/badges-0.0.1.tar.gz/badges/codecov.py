#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://codecov.io/gh/owner/repo
# https://codecov.io/gh/owner/repo/branch/master/graph/badge.svg


class Codecov(GitBadge):
    title = "Codecov"
    image = "https://codecov.io/gh/{fullname}/branch/{branch}/graph/badge.svg"
    link = "https://codecov.io/gh/{fullname}"

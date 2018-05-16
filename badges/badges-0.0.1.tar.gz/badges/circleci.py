#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://circleci.com/gh/owner/repo/tree/master
# https://circleci.com/gh/owner/repo/tree/master.svg?style=svg


class Circleci(GitBadge):
    title = "CircleCI"
    image = "https://circleci.com/gh/{fullname}/tree/{branch}.svg?style=svg"
    link = "https://circleci.com/gh/{fullname}/tree/{branch}"

#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://www.codefactor.io/repository/github/owner/repo
# https://www.codefactor.io/repository/github/owner/repo/badge


class Codefactor(GitBadge):
    title = "CodeFactor"
    image = "https://www.codefactor.io/repository/github/{fullname}/badge"
    link = "https://www.codefactor.io/repository/github/{fullname}"

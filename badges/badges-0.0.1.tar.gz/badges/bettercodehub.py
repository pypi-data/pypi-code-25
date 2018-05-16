#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://bettercodehub.com/results/owner/repo
# https://bettercodehub.com/edge/badge/owner/repo?branch=master


class Bettercodehub(GitBadge):
    title = "BetterCodeHub"
    image = "https://bettercodehub.com/edge/badge/{fullname}?branch={branch}"
    link = "https://bettercodehub.com/results/{fullname}"

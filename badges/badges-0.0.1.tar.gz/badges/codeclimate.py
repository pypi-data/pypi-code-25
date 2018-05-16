#!/usr/bin/env python
from badges.gitbadge import GitBadge

# https://github.com/owner/repo
# https://codeclimate.com/github/owner/repo
# https://codeclimate.com/github/owner/repo/badges/gpa.svg


class Codeclimate(GitBadge):
    title = "CodeClimate"
    image = "https://codeclimate.com/github/{fullname}/badges/gpa.svg"
    link = "https://codeclimate.com/github/{fullname}"

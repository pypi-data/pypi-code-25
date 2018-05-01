# This is the main file.

import re

class formatter(object):
    def __init__(self, msg):
        self.msg = msg

    # Sender's Nickname
    def nick(self):
        return re.match(r'^:(.+?)!', self.msg).group(1)

    # Username
    def username(self):
        return re.match(r'.+?~(.+?)@', self.msg).group(1)

    # IP
    def ip(self):
        return re.match(r'.+?@(.+?)\s', self.msg).group(1)

    # Username & IP
    def userwithip(self):
        return re.match(r'.+?~(.+?@.+?)\s', self.msg).group(1)

    # Msg Status
    def status(self):
        return re.match(r'.+?\s([A-Z]+?)\s', self.msg).group(1)

    # Channel
    def channel(self):
        return re.match(r'.+?\s(#.+?)\s', self.msg).group(1)

    # PRIVMSG Msg Detail
    def msgdetail(self):
        return re.match(r'.+?\s:(.+)$', self.msg).group(1) 

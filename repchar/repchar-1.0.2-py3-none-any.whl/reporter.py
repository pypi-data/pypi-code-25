# -*- coding: UTF-8 -*-

"""
Reporter for character usage
"""

import logging
import unicodedata

class CharReporter(object):

    chars = None
    combining = False
    combdir = None

    def __init__(self, combining=False):
        self.chars = {}
        self.combining = combining
        if self.combining:
            self.combdir = {}

    def report(self):
        logging.info("{} unique character codes.".format(len(self.chars)))
        ret = [u"chr\thex\tcount\tunicode"]
        clist = [(c, count) for (c, count) in self.chars.items()]
        clist.sort(key=lambda x: ord(x[0]))
        for (c, count) in clist:
            if c == u"\t":
                ret.append(u" \t{:04x}\t{}\t{}".format(
                    ord(c), count, unicodedata.name(c, "[UNKNOWN]")))
            else:
                if unicodedata.combining(c):
                    ret.append(u" {}\t{:04x}\t{}\t{}".format(
                        c, ord(c), count, unicodedata.name(c, "[UNKNOWN]")))
                else:
                    ret.append(u"{}\t{:04x}\t{}\t{}".format(
                        c, ord(c), count, unicodedata.name(c, "[UNKNOWN]")))
                try:
                    ccounter = self.combdir[c]
                    comblist = [(x, y) for (x, y) in ccounter.items()]
                    comblist.sort(key=lambda x: ord(x[0]))
                    for (combc, combcount) in comblist:
                        ret.append(u"\t\t\t{} with: {}"\
                                .format(
                                    combcount,
                                    unicodedata.name(combc, "[UNKNOWN]")))
                except (KeyError, TypeError):
                    pass
        return "\n".join(ret)

    buf = ""
    def feed(self, line):
        for c in line:
            self.chars.update({c: self.chars.get(c, 0) + 1})
            if self.combining:
                if unicodedata.combining(c):
                    # @@@TODO: maybe other ranges too?
                    if buf:
                        if c not in self.combdir:
                            self.combdir[c] = {}
                        ccounter = self.combdir[c]
                        ccounter.update({buf: ccounter.get(buf, 0) + 1})
                    else:
                        logging.warning("Combining char at beginning of line.")
            buf = c


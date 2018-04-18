#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `filename_to_fontawesome` package."""

# import pytest


from filename_to_fontawesome.filename_to_fontawesome import ftfa


def test_ftfa_default():
    """Sample pytest test function with the pytest fixture as an argument."""
    ftfa_ = ftfa()
    assert ftfa_.getfontawesome("") == """far fa-file"""
    assert ftfa_.getfontawesome("noextension") == """far fa-file"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == """far fa-file"""
    assert ftfa_.getfontawesome("along.txt") == """far fa-file-text"""
    assert ftfa_.getfontawesome("boy.numbers") == """far fa-file"""
    assert ftfa_.getfontawesome("risk.odt") == """far fa-file-word"""
    assert ftfa_.getfontawesome("board.numbers") == """far fa-file"""
    assert ftfa_.getfontawesome("speech.mp3") == """far fa-file-audio"""
    assert ftfa_.getfontawesome("whether.jpg") == """far fa-file-image"""
    assert ftfa_.getfontawesome("continue.wav") == """far fa-file-audio"""
    assert ftfa_.getfontawesome("form.key") == """far fa-file"""
    assert ftfa_.getfontawesome("during.mp4") == """far fa-file-video"""
    assert ftfa_.getfontawesome("career.odt") == """far fa-file-word"""
    assert ftfa_.getfontawesome("computer.png") == """far fa-file-image"""
    assert ftfa_.getfontawesome("anything.html") == """far fa-file-code"""
    assert ftfa_.getfontawesome("edge.pages") == """far fa-file"""
    assert ftfa_.getfontawesome("somebody.wav") == """far fa-file-audio"""
    assert ftfa_.getfontawesome("well.bmp") == """far fa-file-image"""
    assert ftfa_.getfontawesome("fast.bmp") == """far fa-file-image"""
    assert ftfa_.getfontawesome("why.css") == """far fa-file-code"""
    assert ftfa_.getfontawesome("walk.txt") == """far fa-file-text"""
    assert ftfa_.getfontawesome("member.json") == """far fa-file-code"""
    assert ftfa_.getfontawesome("way.odt") == """far fa-file-word"""
    assert ftfa_.getfontawesome("imagine.csv") == """far fa-file-excel"""
    assert ftfa_.getfontawesome("cell.html") == """far fa-file-code"""
    assert ftfa_.getfontawesome("shoulder.webm") == """far fa-file-video"""
    assert ftfa_.getfontawesome("play.ods") == """far fa-file-excel"""
    assert ftfa_.getfontawesome("different.lxsx") == """far fa-file-excel"""
    assert ftfa_.getfontawesome("support.avi") == """far fa-file-video"""
    assert ftfa_.getfontawesome("claim.txt") == """far fa-file-text"""


def test_ftfa_no_prefa():
    ftfa_ = ftfa(prefa=False)
    assert ftfa_.getfontawesome("") == """fa-file"""
    assert ftfa_.getfontawesome("noextension") == """fa-file"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == """fa-file"""
    assert ftfa_.getfontawesome("seem.jpg") == """fa-file-image"""
    assert ftfa_.getfontawesome("five.webm") == """fa-file-video"""
    assert ftfa_.getfontawesome("other.mp4") == """fa-file-video"""
    assert ftfa_.getfontawesome("arm.mov") == """fa-file-video"""
    assert ftfa_.getfontawesome("during.key") == """fa-file"""


def test_ftfa_v4():
    ftfa_ = ftfa(fontversion="v4")
    assert ftfa_.getfontawesome("") == """fa fa-file-o"""
    assert ftfa_.getfontawesome("noextension") == """fa fa-file-o"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == """fa fa-file-o"""
    assert ftfa_.getfontawesome("across.html") == """fa fa-file-code-o"""
    assert ftfa_.getfontawesome("west.json") == """fa fa-file-code-o"""
    assert ftfa_.getfontawesome("many.mp3") == """fa fa-file-audio-o"""
    assert ftfa_.getfontawesome("front.wav") == """fa fa-file-audio-o"""
    assert ftfa_.getfontawesome("something.tiff") == """fa fa-file-image-o"""
    assert ftfa_.getfontawesome("huge.avi") == """fa fa-file-video-o"""
    assert ftfa_.getfontawesome("and.flac") == """fa fa-file-audio-o"""
    assert ftfa_.getfontawesome("candidate.wav") == """fa fa-file-audio-o"""
    assert ftfa_.getfontawesome("nor.tiff") == """fa fa-file-image-o"""
    assert ftfa_.getfontawesome("fund.doc") == """fa fa-file-word-o"""
    assert ftfa_.getfontawesome("almost.mp3") == """fa fa-file-audio-o"""
    assert ftfa_.getfontawesome("wear.webm") == """fa fa-file-video-o"""
    assert ftfa_.getfontawesome("statement.gif") == """fa fa-file-image-o"""


def test_ftfa_v4_solid():
    ftfa_ = ftfa(fontversion="v5solid")
    assert ftfa_.getfontawesome("") == """fas fa-file"""
    assert ftfa_.getfontawesome("noextension") == """fas fa-file"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == """fas fa-file"""
    assert ftfa_.getfontawesome("attack.html") == """fas fa-file-code"""
    assert ftfa_.getfontawesome("line.webm") == """fas fa-file-video"""
    assert ftfa_.getfontawesome("I.numbers") == """fas fa-file"""
    assert ftfa_.getfontawesome("large.bmp") == """fas fa-file-image"""
    assert ftfa_.getfontawesome("past.png") == """fas fa-file-image"""
    assert ftfa_.getfontawesome("increase.mp4") == """fas fa-file-video"""
    assert ftfa_.getfontawesome("pattern.wav") == """fas fa-file-audio"""
    assert ftfa_.getfontawesome("moment.png") == """fas fa-file-image"""


def test_ftfa_default_markup():
    ftfa_ = ftfa(markup=True)
    assert ftfa_.getfontawesome("") == \
        """<i class="far fa-file"></i>"""
    assert ftfa_.getfontawesome("noextension") == \
        """<i class="far fa-file"></i>"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == \
        """<i class="far fa-file"></i>"""
    assert ftfa_.getfontawesome("whose.html") == \
        """<i class="far fa-file-code"></i>"""
    assert ftfa_.getfontawesome("successful.avi") == \
        """<i class="far fa-file-video"></i>"""
    assert ftfa_.getfontawesome("why.css") == \
        """<i class="far fa-file-code"></i>"""
    assert ftfa_.getfontawesome("medical.js") == \
        """<i class="far fa-file-code"></i>"""
    assert ftfa_.getfontawesome("never.xlsx") == \
        """<i class="far fa-file-excel"></i>"""


def test_ftfa_v4_markup():
    ftfa_ = ftfa(fontversion="v4", markup=True)
    assert ftfa_.getfontawesome("") == \
        """<i class="fa fa-file-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("noextension") == \
        """<i class="fa fa-file-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("plenty.of.extension.s") == \
        """<i class="fa fa-file-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("increase.txt") == \
        """<i class="fa fa-file-text-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("despite.json") == \
        """<i class="fa fa-file-code-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("guy.odt") == \
        """<i class="fa fa-file-word-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("market.html") == \
        """<i class="fa fa-file-code-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("speech.pdf") == \
        """<i class="fa fa-file-pdf-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("national.numbers") == \
        """<i class="fa fa-file-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("part.avi") == \
        """<i class="fa fa-file-video-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("song.mp3") == \
        """<i class="fa fa-file-audio-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("away.xlsx") == \
        """<i class="fa fa-file-excel-o" aria-hidden="true"></i>"""
    assert ftfa_.getfontawesome("meeting.wav") == \
        """<i class="fa fa-file-audio-o" aria-hidden="true"></i>"""

# -*- coding: utf-8 -*-
# This file is part of bagent
#
# Copyright (C) 2018-present Jeremies Pérez Morata
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import re

class MessageHandler(object):
    def __init__(self, msg, sender, ctx):
        self.ctx = ctx
        self.msg = msg
        self.sender = sender

    def is_int(self):
        return self.is_type(int)
    def is_str(self):
        return self.is_type(str)
    def is_float(self):
        return self.is_type(float)
    def is_re(self, expr):
        if not self.is_type(str):
            return False
        else:
            p = re.compile(expr)
            return p.match(self.msg) is not None
    def is_type(self, clazz):
        return isinstance(self.msg, clazz)

    def match_int(self, fn):
        if self.is_int():
            fn(self.msg)
    def match_str(self, fn):
        if self.is_str():
            fn(self.msg)
    def match_float(self, fn):
        if self.is_float():
            fn(self.msg)
    def match_re(self, expr, fn):
        if self.is_re(expr):
            fn(self.msg)

    def match(self, obj, fn):
        for key, value in obj.items():
            print(key, value)

    def respond(self, resp_msg):
        self.respond_to(self.sender, resp_msg)

    def respond_to(self, resp_pid, resp_msg):
        self.ctx.send(resp_pid, resp_msg)


class MessageContext:
    def __init__(self, ctx):
        self.ctx = ctx

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass # pragma: no cover

    async def __aenter__(self):
        (sender, msg) = await self.ctx.recv()
        return MessageHandler(msg, sender, self.ctx)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

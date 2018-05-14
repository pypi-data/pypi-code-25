#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def get_exception_message(ex):
    """Build exception message with details.
    """
    template = "{0}: {1!r}"
    return template.format(type(ex).__name__, ex.args)
#!/usr/bin/env python
# coding: utf-8

import huepy


class Logger(object):

    def pass_through(self, classifier_name):

        pass_through = huepy.bold(huepy.orange("passed through"))
        msg = "The {0} classifier has {1}.\n"
        print huepy.info(msg.format(classifier_name, pass_through))

    def require(self, classifier_name):

        required = huepy.bold(huepy.red("required"))
        msg = "The {0} classifier is {1}.\n"
        print huepy.bad(msg.format(classifier_name, required))

    def error(self, error_name, error_msg):

        error_name = huepy.bold(huepy.red(error_name))
        msg = "{0}: {1}\n"
        print huepy.bad(msg.format(error_name, error_msg))


logger = Logger()

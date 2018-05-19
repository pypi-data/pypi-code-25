# -*- coding: utf-8 -*-

import logging

import requests


class SlackWebhookHandler(logging.Handler):

    def __init__(self, url: str, level: int = logging.NOTSET):
        self._url = url

        super(SlackWebhookHandler, self).__init__(level)

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)

        return requests.post(
            self._url,
            log_entry,
            headers={'Content-type': 'application/json'}
        ).content

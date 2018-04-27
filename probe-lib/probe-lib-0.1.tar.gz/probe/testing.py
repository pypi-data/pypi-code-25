# coding: utf-8
import json


class MockApi(object):
    def __init__(self):
        self.events = []
        self.mails = []
        self.state = {}
        self.config = {}

    def get_config(self, prefix=''):
        return dict((key[len(prefix):], value)
                        for key, value
                        in self.config.items()
                        if key.startswith(prefix))

    def get_state(self):
        return self.state

    def update_state(self, value):
        self.state = json.loads(json.dumps(value))

    def send_mail(self, to, subject, content):
        self.mails.append((
                    to,
                    subject.encode('utf-8'),
                    content.encode('utf-8')))

    def assert_mail(self, to=None,
                            subject=None,
                            content=None,
                            content_contains=None):

        exists = any((to in [None, mto]
               and subject in [None, msubject]
               and content in [None, mcontent]
               and (content_contains is None or content_contains in mcontent)
                    for mto, msubject, mcontent in self.mails))

        assert exists, 'no such mail sent.'

    def assert_state(self, data):
        assert data == self.state, '%r != %r' % (self.state, data)

    def assert_no_events_triggered(self):
        assert not self.events

    def trigger_event(self, type, data):
        self.events.append((type, data))

# coding: utf-8
import sys
import traceback
from datetime import timedelta, datetime
from smtplib import SMTP

from .model import (Event, MonitorState, MissingSinceTriggerState,
                    QueuedExecution)


class Api(object):

    def __init__(self, config, session, monitor_name):
        self.config = config
        self.session = session
        self.monitor_name = monitor_name
        self.enqueued_events = []

    def trigger_event(self, type, body):
        self.enqueued_events.append((type, body))

    def get_config(self, prefix=""):
        return dict((key[len(prefix):], value)
                    for key, value
                    in self.config.items()
                    if key.startswith(prefix))

    def get_state(self):
        return MonitorState.get_for_monitor(self.session, self.monitor_name)

    def update_state(self, state):
        MonitorState.set_for_monitor(self.session, self.monitor_name, state)

    def get_config(self, prefix=''):
        return dict((key[len(prefix):], value)
                        for key, value
                        in self.config.items()
                        if key.startswith(prefix))

    def send_mail(self, to, subject, content):
        from_ = self.config['MAIL_FROM']
        message = '\n'.join([
            'From: %s',
            'To: %s',
            'Subject: %s',
            'Content-Type: text/plain; charset=utf-8'
            '',
            '%s',
        ]) % (from_, to, subject.encode('utf-8'), content.encode('utf-8'))

        server = SMTP(self.config['MAIL_SERVER'])
        server.starttls()
        server.login(self.config['MAIL_USER'],
                     self.config['MAIL_PASSWORD'])
        problems = server.sendmail(from_, to, message)
        server.quit()
        if problems:
            raise Exception("Errors sending mail: %r" % problems)

    def request(self, url, method, payload):
        pass


class Registry(object):

    def __init__(self, config):
        self._config = config
        self._formatters = {}
        self._on = {}
        self._on_missing_since = []

    def formatter(self, type):
        def decorator(func):
            self._formatters[type] = func
            return func
        return decorator

    def on(self, type):
        def decorator(func):
            name = '%s.%s' % (func.__module__, func.__name__)
            self._on.setdefault(type, []).append((name, func))
            return func
        return decorator

    def on_missing_since(self, type, duration):
        def decorator(func):
            name = '%s.%s' % (func.__module__, func.__name__)
            self._on_missing_since.append((type, duration, name, func))
            return func
        return decorator

    def enqueue(self, session, type, data):
        event = Event(session, type=type, data=data)
        for name, monitor in self.get_monitors(type):
            QueuedExecution(session, name, event)

    def dispatch_execution(self, session, ex):
        monitor = self.get_monitor(ex.monitor)

        session.delete(ex)
        api = Api(self._config, session, ex.monitor)

        try:
            monitor(api, ex.event.data)

            for event_type, body in api.enqueued_events:
                self.enqueue(session, event_type, body)
        except Exception as exc:
            _, _, tb = sys.exc_info()
            self.enqueue(session, "error", {
                "exception": type(exc).__name__,
                "message": exc.message,
                "stack": traceback.extract_tb(tb)
            })

    def dispatch_missing(self, session):
        types = frozenset(type for type, _, _, _ in self._on_missing_since)

        last_executions = dict(Event.get_last_executions(session, types))
        now = datetime.now()

        events = []

        last_triggered_for = dict((m.monitor, m.last_triggered)
                            for m in MissingSinceTriggerState.get_all(session))

        for type, duration, name, monitor in self._on_missing_since:
            date = last_executions.get(type, datetime.min)
            if date + duration < now and date != last_triggered_for.get(name):
                api = Api(self._config, session, name)
                monitor(api, {})
                events.extend(api.enqueued_events)
                MissingSinceTriggerState.set_for_monitor(session, name, date)

        for type, body in events:
            self.enqueue(session, type, body)

    def get_monitor(self, name):
        for lst in self._on.values():
            for n, monitor in lst:
                if name == n:
                    return monitor
        raise Exception("monitor %r not found" % name)

    def get_monitors(self, type):
        return [(name, monitor)
                    for name, monitor
                    in self._on.get(type, [])]

    def get_format(self, type, body):
        func = self._formatters.get(type, lambda _: type)
        return func(body)

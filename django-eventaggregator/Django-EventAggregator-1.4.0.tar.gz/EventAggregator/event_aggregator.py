# coding: utf-8
from django.contrib.sessions.backends.db import SessionBase

from EventAggregator.event_dispatcher import EventDispatcher


class EventAggregator:
    @staticmethod
    def publish(message, session: SessionBase = None):
        """
        :param message: 发布的消息
        :param session: 有值时，对应的响应(response)没有异常时发布; 为None立即发布
        :return:
        """
        if isinstance(session, SessionBase):
            if not hasattr(session, '_dispatch_events'):
                session._dispatch_events = []
            session._dispatch_events.append(lambda: EventDispatcher.dispatch_event(type(message), message))
        else:
            EventDispatcher.dispatch_event(type(message), message)

    @staticmethod
    def subscribe(message_class, handler, times=3):
        """
        :param message_class: 
        :param handler: 
        :param times: 失败时，重试的次数， 取值>=0 
        :return: 
        """
        handler._times = times
        EventDispatcher.add_event_listener(message_class, handler)

    @staticmethod
    def unsubscribe(message_class, handler):
        EventDispatcher.remove_event_listener(message_class, handler)

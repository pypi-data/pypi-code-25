import datetime
import time

from open_publishing.core.enums import EventTarget, EventAction, EventType

class Events(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx

    def get(self,
            references=None,
            target=None,
            action=None,
            type=None,
            filters=None,
            since=None,
            till=None,
            history=False):
        """
        Return specified events.

        Since parameter filters all events since given timestamp.
        Till parameter filters all events till given timestamp.
        If history is set to False (default) per object only the latest event will be returned.
        If history is set to True all events will be returned.
        """
        event_types = self._get_event_types(target,
                                            action,
                                            type,
                                            filters)
        references = self._normalize_references(references)
        from_timestamp = self._normalize_timestamp(since)
        to_timestamp = self._normalize_timestamp(till)
        method= 'history' if history else 'list_status'
        response = self._ctx.gjp.fetch_events(method=method,
                                              event_types=event_types,
                                              references=references,
                                              from_timestamp=from_timestamp,
                                              to_timestamp=to_timestamp)
        execution_timestamp = datetime.datetime.fromtimestamp(response['execution_timestamp'])
        result = EventsList(execution_timestamp)

        def add_items(items):
            for item in items:
                timestamp = None
                if 'last_modified' in item:
                    timestamp = item['last_modified']
                if 'log_time' in item:
                    timestamp = item['log_time']
                result.append(EventsList.Event(target=EventTarget.from_id(item['target']),
                                               action=EventAction.from_id(item['action']),
                                               type=EventType.from_id(item['type']),
                                               timestamp=datetime.datetime.fromtimestamp(timestamp),
                                               guid=(item['source_type'] + '.' + str(item['reference_id'])).lower(),
                                               app=item.get('app', None),
                                               uuid=item.get('uuid', None)))

        add_items(response['items'])
        while 'resumption_token' in response:
            response = self._ctx.gjp.fetch_events(method=method,
                                                  resumption_token=response['resumption_token'])
            add_items(response['items'])

        result.sort(key=lambda a: a.timestamp)
        return result

    def last_event(self,
                   references,
                   target=None,
                   action=None,
                   type=None,
                   filters=None):
        event_types = self._get_event_types(target,
                                            action,
                                            type,
                                            filters)

        if isinstance(references, (list, tuple)):
            str_references = ','.join(set(references))
        else:
            raise TypeError('references: expected list or tuple, got: {0}'.format(type(references)))

        events = {}
        def add_items(items):
            for item in items:
                guid = (item['source_type'] + '.' + str(item['reference_id'])).lower()
                if guid not in events or events[guid]['last_modified'] < item['last_modified']:
                    events[guid] = item


        response = self._ctx.gjp.fetch_events(method='list_status',
                                              event_types=event_types,
                                              references=str_references)

        execution_timestamp = datetime.datetime.fromtimestamp(response['execution_timestamp'])

        add_items(response['items'])
        while 'resumption_token' in response:
            response = self._ctx.gjp.fetch_events('list_status',
                                                  resumption_token=response['resumption_token'])
            add_items(response['items'])

        result = EventsList(execution_timestamp)
        for ref in references:
            guid = ref.lower()
            if guid in events:
                result.append(EventsList.Event(target=EventTarget.from_id(events[guid]['target']),
                                               action=EventAction.from_id(events[guid]['action']),
                                               type=EventType.from_id(events[guid]['type']),
                                               timestamp=datetime.datetime.fromtimestamp(events[guid]['last_modified']),
                                               guid=guid))
            else:
                result.append(None)
        return result

    def _get_event_types(self,
                         target,
                         action,
                         type,
                         filters):
        if target is not None or action is not None or type is not None:
            if filters is not None:
                raise KeyError('filters or target/action/type should be set, not both')
            elif ((target is not None and target not in EventTarget) or
                  (action is not None and action not in EventAction) or
                  (type is not None and type not in EventType)):
                raise ValueError('target/action/type should be None or from op.events.target/action.type respectively, got: {0}, {1}, {2}'.format(target,
                                                                                                                                                  action,
                                                                                                                                                  type))
            else:
                event_types = '({target},{action},{type})'.format(target=target if target is not None else '',
                                                                  action=action if action is not None else '',
                                                                  type=type if type is not None else '')
        else:
            if filters is None:
                event_types = '(,,)' #All events
            else:
                if not isinstance(filters, list):
                    raise ValueError('filters should be list of tuples of (op.events.target, op.events.action, op.event.type), got: {0}'.format(filters))
                event_types = []
                for target, action, type in filters:
                    if ((target is not None and target not in EventTarget) or
                            (action is not None and action not in EventAction) or
                            (type is not None and type not in EventType)):
                        raise ValueError('filters should be list of tuples of (op.events.target|None, op.events.action|None, op.event.type|None), got: {0}'.format(filters))
                    else:
                        event_types.append('({target},{action},{type})'.format(target=target if target is not None else '',
                                                                               action=action if action is not None else '',
                                                                               type=type if type is not None else ''))
                event_types = ';'.join(event_types)
        return event_types

    @staticmethod
    def _normalize_timestamp(timestamp):
        """Normalize timestamp to the format needed by API."""
        if timestamp is None:
            return None
        if not isinstance(timestamp, (datetime.datetime, datetime.date)):
            raise TypeError('since should be datetime.datetime or datetime.date, got {0}'.format(timestamp))
        return int(time.mktime(timestamp.timetuple()))

    @staticmethod
    def _normalize_references(references):
        if references is None:
            return None
        if not isinstance(references, (list, tuple)):
            raise TypeError('references: expected list or tuple, got: {0}'.format(type(references)))
        return ','.join(references)

class EventsList(list):
    """List of Open Publishing Events."""

    class Event(object):
        """Open Publishing Event object."""

        def __init__(self,
                     target,
                     action,
                     type,
                     timestamp,
                     guid,
                     app=None,
                     uuid=None):
            self._target = target
            self._action = action
            self._type = type
            self._timestamp = timestamp
            self._guid = guid
            self._app = app
            self._uuid = uuid

        @property
        def target(self):
            return self._target

        @property
        def action(self):
            return self._action

        @property
        def type(self):
            return self._type

        @property
        def timestamp(self):
            return self._timestamp

        @property
        def guid(self):
            return self._guid

        @property
        def app(self):
            return self._app

        @property
        def uuid(self):
            return self._uuid

        def __repr__(self):
            '''Returns representation of the object'''
            return("{}(guid={}, target={}, action={}, type={}, app={})".format(self.__class__.__name__, self.guid, self.target, self.action, self.type, self.app))


    def __init__(self,
                 execution_timestamp):
        super(EventsList, self).__init__([])
        self._execution_timestamp = execution_timestamp

    @property
    def execution_timestamp(self):
        return self._execution_timestamp

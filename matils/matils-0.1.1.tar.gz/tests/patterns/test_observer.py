"""Tests for :mod:`observer` module's code."""

from unittest import mock
from unittest import TestCase
from matils.patterns.observer import Observable, Observer


class DummyObserver(Observer):
    """A dummy observer to be used in Observable tests."""

    def update(data, event='all'):
        """Act as a dummy update method."""
        pass


class TestObservable(TestCase):
    """Test cases for the class Obsevable from :mod:`observer`."""

    def test__init__(self):
        """
        Test :meth:`Observavle.__init__`.

        It is expected from :meth:`Observable.__init__()`

            * Create the property self.abservers as a dictionary;
            * To initialize self.observers with a dictionary
              containing an entry with key 'all' and value a
              blank list.
        """
        observable = Observable()

        # assert property type...
        self.assertIsInstance(observable.observers, dict)

        # assert presence of key all with a blak list as value
        self.assertTrue('all' in observable.observers.keys())
        self.assertIsInstance(observable.observers['all'], list)
        self.assertEqual(len(observable.observers['all']), 0)

    def test_register(self):
        """
        Test :meth:`Observable.register`.

        It is expected from :meth:`Observable.register`:
            * The default value for the event name must be 'all'
            * If no event name is given, register the observable in the list
              at key 'all' in the :attr:`Observable.observers`
            * If given an event name, register observable in the list at key
              '<event_name>': key IS the string given as event parameter.
            * If it is the first observer to register to a given event, create
              the entry in the :attr:`Observable.observers` dictionary.
        """
        observable = Observable()

        # registration to default
        observable.register(DummyObserver())
        self.assertEqual(len(observable.observers['all']), 1)

        # registration to default with string all
        observable.register(DummyObserver(), 'all')
        self.assertEqual(len(observable.observers['all']), 2)

        # registration to a given event
        observable.register(DummyObserver(), 'what_a_nice_event')
        self.assertTrue('what_a_nice_event' in observable.observers.keys())
        self.assertEqual(len(observable.observers['what_a_nice_event']), 1)

    def test_unregister(self):
        """
        Test :meth:`Observable.unregister`.

        It is expected from :meth:`Observable.unregister`:
            * Given a observer as argument remove all refences to it, from
              every event registerd in :attr:`Observable.observers` where it is
              registered, if no event name is given as second argument.
            * If a event name is given as second argument, remove the reference
              to the observer ONLY from the list of observers to that event.
            * Return true if the requested operation was successful
            * Return false if the given event or observer was not found
        """
        observable = Observable()

        # Register multiple times the same dummy observer...
        dummy1 = DummyObserver()
        observable.register(dummy1)
        observable.register(dummy1, 'shit_event')
        observable.register(dummy1, 'not_again')

        # Remove an observer from a given event...
        result = observable.unregister(dummy1, 'shit_event')
        self.assertTrue(result)
        self.assertEqual(len(observable.observers['shit_event']), 0)

        # Remove an observer from all events, by not giving an event name...
        result = observable.unregister(dummy1)
        self.assertTrue(result)
        self.assertEqual(len(observable.observers['all']), 0)
        self.assertEqual(len(observable.observers['not_again']), 0)

        # Checks if return false for an inexistent event...
        result = observable.unregister(dummy1, 'I_do_not_exist')
        self.assertFalse(result)

        # Checks if return false if ask for removal of inexistent observer...
        result = observable.unregister(DummyObserver())
        self.assertFalse(result)

    def test_notify(self):
        """
        Test :meth:`Observable.notify`.

        It is expected from Test :meth:`Observable.notify`.
            * To call the update method of all the registered observers for the
              given event, and all observers registered to all.
            * Do nothing if there is no observer is registered for a given
              given event.
        """
        observable = Observable()

        # Register some observers...
        observable.register(DummyObserver(), 'all')
        observable.register(DummyObserver(), 'los_geht')
        observable.register(DummyObserver(), 'vamos_la')
        observable.register(DummyObserver(), 'vamonos')

        # mock the update method
        with mock.patch.object(DummyObserver, 'update') as mock_update:
            data, event = dict(), 'los_geht'
            observable.notify(data, event)
            # Expected 2, one for the observer registered at the event entry,
            # an one for the observer registered in all...
            self.assertEqual(mock_update.call_count, 2)

            mock_update.reset_mock()
            data, event = dict(), 'some_event'
            observable.notify(data, event)
            # even though the event have no direct observers... it is expected
            # 1 call since there is some one registered to listen all
            self.assertEqual(mock_update.call_count, 1)

            mock_update.reset_mock()
            observable = Observable()
            observable.register(DummyObserver, 'de_novo')
            observable.register(DummyObserver, 'again')
            observable.notify(data, event)
            # expected no calls to update since 'all' is clean and the event
            # is not registered...
            mock_update.assert_not_called()

    def test_reset(self):
        """
        Test :meth:`Observable.reset`.

        It is expected from :meth:`Observable.reset`:
            * To remove all entries in :attr:`Observable.observers`: except
              and clean the 'all' entry.
            * The reference to the initial dictionary must be kept
        """
        observable = Observable()

        # Register some observers...
        observable.register(DummyObserver(), 'all')
        observable.register(DummyObserver(), 'los_geht')
        observable.register(DummyObserver(), 'vamos_la')
        observable.register(DummyObserver(), 'vamonos')

        observers_dict_original_ref = observable.observers
        observable.reset()
        # Must preserve 'all' with an empty list, size 1 expected
        self.assertEqual(len(observable.observers), 1)
        # 'all' must be present, not other events
        self.assertTrue('all' in observable.observers.keys())
        # reference to the original dict must be preserved
        self.assertIs(observable.observers, observers_dict_original_ref)

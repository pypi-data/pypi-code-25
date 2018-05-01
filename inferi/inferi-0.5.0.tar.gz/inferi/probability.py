"""Contains probability concept classes."""

import random
from fractions import Fraction

class EventSpace:
    """An abstract class for objects which are a container of simple events.

    Any class inheriting from this class should ensure its instances have a
    ``_simple_events`` property which is a set of :py:class:`.Simple Event`
    objects."""

    def __contains__(self, member):
        if isinstance(member, Event):
            return member.simple_events.issubset(self._simple_events)
        for event in self._simple_events:
            if event.outcome == member: return True


    @property
    def simple_events(self):
        """The set of simple events in this space.

        :rtype: ``set``"""

        return set(self._simple_events)


    def outcomes(self, p=False):
        """The set of outcomes that the event space's simple events can
        produce.

        :param bool p: if ``True``, the results will be returned as a dict with\
        probabilities associated.

        :rtype: ``set`` or ``dict``"""

        if p: return {e.outcome: e.probability() for e in self._simple_events}
        return set([e.outcome for e in self._simple_events])



class Event(EventSpace):
    """Base class: :py:class:`.EventSpace`

    An occurance that is made up of multiple simple events.

    Events are containers both of their simple events, and the outcomes of those
    simple events.

    :param \*events: The :py:class:`.Event` objects within this set.
    :param str name: The name of the event (default is 'E').
    :raises TypeError: if non-events are given.
    :raises TypeError: if the name is not a string."""

    def __init__(self, *events, name="E"):
        if any(not isinstance(e, Event) for e in events):
            raise TypeError(f"{events} contains non-events")
        if not isinstance(name, str):
            raise TypeError(f"Name {name} is not str")
        self._simple_events = set()
        for event in events: self._simple_events.update(event._simple_events)
        self._name = name


    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._name}>"


    def __or__(self, event):
        if not isinstance(event, Event):
            raise TypeError(f"{event} is not an Event")
        return Event(*(self._simple_events | event._simple_events))


    def __and__(self, event):
        if not isinstance(event, Event):
            raise TypeError(f"{event} is not an Event")
        return Event(*(self._simple_events & event._simple_events))


    @property
    def sample_space(self):
        """The sample space that the event is part of.

        :rtype: ``SampleSpace``"""

        for event in self._simple_events:
            return event._sample_space


    @property
    def name(self):
        """Returns the name of the Event.

        :rtype: ``str``"""

        return self._name


    @property
    def complement(self):
        """Returns the complement of the event - the event that this event does
        not happen.

        :rtype: ``Event``"""

        return Event(
         *(self.sample_space.simple_events - self._simple_events)
        )


    def probability(self, given=None, fraction=False):
        """Returns the probability of the event happening.

        :param Event given: an optional pre-condition to consider.
        :param bool fraction: If ``True``, the result will be returned as a\
        ``Fraction``.
        :raises TypeError: if the given event is not an :py:class:`.Event`
        :rtype: ``float``"""

        if given:
            if not isinstance(given, Event):
                raise TypeError(f"{given} is not an event")
            p = (self & given).probability(fraction=True)
            p /= given.probability(fraction=True)
        else:
            p = sum(event._probability for event in self._simple_events)
        return p if fraction else p.numerator / p.denominator


    def mutually_exclusive_with(self, event):
        """Looks at some other event and checks if this event is mutually
        exclusive with the other event. That is, whether it is impossible for
        them both to happen in a given statistical experiment.

        :param Event event: the other event to check with.
        :raises TypeError: if a non-Event is given.
        :rtype: ``bool``"""

        if not isinstance(event, Event):
            raise TypeError(f"{event} is not an event")
        return not self._simple_events & event._simple_events


    def independent_of(self, event):
        """Checks to see if this event is independent of some other event - that
        is, whether its probability is unaffacted by the occurence of the other
        event.

        :param Event event: the other event to check with.
        :raises TypeError: if a non-Event is given.
        :rtype: ``bool``"""

        if not isinstance(event, Event):
            raise TypeError(f"{event} is not an event")
        return self.probability(fraction=True) == self.probability(
         fraction=True, given=event
        )


    def dependent_on(self, event):
        """Checks to see if this event is dependent of some other event - that
        is, whether its probability is affacted by the occurence of the other
        event.

        :param Event event: the other event to check with.
        :raises TypeError: if a non-Event is given.
        :rtype: ``bool``"""

        return not self.independent_of(event)



class SimpleEvent(Event):
    """Base class: py:class:`.Event`

    A simple event - a single outcome of a statistical experiment.

    :param outcome: The result of this event occuring.
    :param float probability: The probability of this event occuring.
    :raises TypeError: if probability isn't numeric.
    :raises ValueError: if probability is not between 0 and 1."""

    def __init__(self, outcome, probability, space):
        self._outcome = self._name = outcome
        if not isinstance(probability, (int, float, Fraction)):
            raise TypeError("probability {} is not numeric".format(probability))
        if not 0 <= probability <= 1:
            raise ValueError("probability {} is invalid".format(probability))
        self._probability = probability
        self._sample_space = space
        self._simple_events = set((self,))


    @property
    def outcome(self):
        """The result of this event occuring."""

        return self._outcome



class SampleSpace(EventSpace):
    """Base class: :py:class:`.EventSpace`

    The set of all possible things that can result from a statistical
    experiment.

    :param \*outcomes: All the possible outcomes.
    :param dict p: The probabilities for the supplied outcomes. If not given,\
    these will be weighted equally.
    :raises ValueError: if you supply probabilities that don't add up to 1."""

    def __init__(self, *outcomes, p=None):
        if not outcomes and not p:
            raise ValueError("Sample spaces need at least one outcome")
        if p is None:
            p_per_event = Fraction(1, len(outcomes))
            fraction_p = {event: p_per_event for event in outcomes}
        else:
            fraction_p = {k: Fraction(str(p[k])) for k in p}
            unaccounted_outcomes = [o for o in outcomes if o not in p]
            if unaccounted_outcomes:
                remaining_p = 1 - sum(fraction_p.values())
                p_per_event = (remaining_p / len(unaccounted_outcomes))
                for e in unaccounted_outcomes:
                    fraction_p[e] = p_per_event
        if sum(fraction_p.values()) != 1:
            raise ValueError(f"Probabilities do not add up to 1: {fraction_p}")
        self._simple_events = set([
         SimpleEvent(e, fraction_p[e], self) for e in fraction_p
        ])


    def __repr__(self):
        return f"<SampleSpace ({len(self._simple_events)} simple events)>"


    def event(self, *outcomes, name=None):
        """If a single outcome is given, this function will return the
        :py:class:`.SimpleEvent` corresponding to that outcome.

        If multiple outcomes are given, the function will return the
        :py:class:`.Event` corresponding to one of those outcomes occuring.

        If a callable is provided, the function will return the
        :py:class:`.Event` of all the simple events that return ``True`` when
        the callable is applied to their outcome.

        :param \*outcomes: The outcome(s) to look for.
        :param str name: The name to apply if a :py:class:`.Event` is returned.
        :rtype: ``SimpleEvent`` or ``Event``"""

        if len(outcomes) == 1:
            if callable(outcomes[0]):
                f = outcomes[0]
                outcomes = [
                 e.outcome for e in self._simple_events if f(e.outcome)
                ]
            else:
                for event in self._simple_events:
                    if event.outcome == outcomes[0]: return event
                else: return None
        simple = [e for e in self._simple_events if e.outcome in outcomes]
        return Event(*simple, name=name) if name else Event(*simple)


    def chances_of(self, *outcomes):
        """Returns the probability of the given outcome or outcomes occuring in
        a single statistical experiment.

        If multiple outcomes are given, the function will return the
        :py:class:`.Event` corresponding to one of those outcomes occuring.

        If a callable is provided, the function will return the
        :py:class:`.Event` of all the simple events that return ``True`` when
        the callable is applied to their outcome.

        :param \*outcomes: The outcome(s) to look for.
        :rtype: ``float``"""

        event = self.event(*outcomes)
        return event.probability() if event is not None else 0


    def experiment(self):
        """Generate an outcome."""

        outcomes = self.outcomes(p=True)
        outcomes = [(o, p) for o, p in outcomes.items()]
        outcomes, odds = zip(*outcomes)
        return random.choices(outcomes, weights=odds, k=1)[0]
